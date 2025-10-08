"""
Genetic Algorithm for scheduling (integrates with Jadwal.py)

Usage:
    from Jadwal import Jadwal
    from genetic import GeneticScheduler

    base = Jadwal(json_name="tc1.json")
    ga = GeneticScheduler(base, population_size=30, generations=200,
                          crossover_rate=0.8, mutation_rate=0.2, elitism=2)
    result = ga.run()
    result.print_schedule()

This implementation keeps representation at the Jadwal object level. Crossover is
performed per-course: for each course and each of its pertemuan (sks), the child's
pertemuan location is inherited from one of the parents. Mutation uses the
existing get_random_neighbor() operator (swap or move).

Fitness: GA minimizes the same cost components used in Jadwal.py:
  - objf_waktu_konflik_mhs
  - objf_waktu_konflik_dosen
  - objf_kapasitas_ruang
  - objf_priotitas
We compute a weighted sum cost: cost = w1*c1 + w2*c2 + w3*c3 + w4*c4
and convert to fitness = 1 / (1 + cost) (higher fitness is better).

"""

import copy
import random
import numpy as np
from Jadwal import Jadwal


class GeneticScheduler:
    def __init__(self, base_jadwal: Jadwal,
                 population_size=30,
                 generations=200,
                 crossover_rate=0.8,
                 mutation_rate=0.2,
                 elitism=2,
                 weights=None,
                 tournament_k=3,
                 seed=None):
        """
        base_jadwal: an instance of Jadwal loaded with the target json (used to
                    create new individuals and to access meta information)
        weights: dict with keys 'mhs', 'dosen', 'kapasitas', 'prioritas'
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        self.base = base_jadwal
        self.population_size = population_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elitism = elitism
        self.tournament_k = tournament_k

        # Default equal weights (you can tune these)
        if weights is None:
            weights = {"mhs": 1.0, "dosen": 1.0, "kapasitas": 1.0, "prioritas": 1.0}
        self.weights = weights

        # containers to track progress
        self.best_history = []  # best cost per generation
        self.avg_history = []   # avg cost per generation

    # ----------------- Fitness / Cost -----------------
    def cost(self, jadwal: Jadwal):
        """Compute the combined cost (lower is better) using the same
        component functions available in Jadwal.py"""
        c1 = jadwal.objf_waktu_konflik_mhs()
        c2 = jadwal.objf_waktu_konflik_dosen()
        c3 = jadwal.objf_kapasitas_ruang()
        c4 = jadwal.objf_priotitas()

        total = (self.weights["mhs"] * c1 +
                 self.weights["dosen"] * c2 +
                 self.weights["kapasitas"] * c3 +
                 self.weights["prioritas"] * c4)
        return float(total)

    def fitness(self, jadwal: Jadwal):
        """Convert cost to fitness. We use a simple transform so that fitness
        is higher for lower costs. fitness in (0, 1]."""
        c = self.cost(jadwal)
        return 1.0 / (1.0 + c)

    # ----------------- Population initialization -----------------
    def init_population(self):
        pop = []
        for _ in range(self.population_size):
            # make new random schedule by deep-copying base and randomizing
            ind = copy.deepcopy(self.base)
            ind.random_schedule()
            pop.append(ind)
        return pop

    # ----------------- Selection -----------------
    def tournament_select(self, population, fitnesses):
        """Tournament selection returns one selected individual (deep-copied)."""
        chosen = random.sample(list(zip(population, fitnesses)), k=self.tournament_k)
        chosen.sort(key=lambda x: x[1], reverse=True)  # higher fitness better
        winner = copy.deepcopy(chosen[0][0])
        return winner

    # ----------------- Crossover -----------------
    def crossover(self, parent_a: Jadwal, parent_b: Jadwal):
        """
        Child creation by inheriting per-course per-pertemuan locations from
        parents. This keeps schedule_matkul consistent (each pertemuan belongs to
        some slot+ruang).
        """
        child = copy.deepcopy(self.base)

        # clear child schedule
        num_slots = child.schedule_matrix.shape[0]
        num_ruang = child.schedule_matrix.shape[1]
        for i in range(num_slots):
            for j in range(num_ruang):
                child.schedule_matrix[i, j] = []
        child.schedule_matkul = {mk["kode"]: [] for mk in child.mata_kuliah}

        # For each mata_kuliah, take each pertemuan (index order) from either parent
        for mk in child.mata_kuliah:
            kode = mk["kode"]
            per_a = parent_a.schedule_matkul.get(kode, [])
            per_b = parent_b.schedule_matkul.get(kode, [])

            # If parents contain different numbers of pertemuan (shouldn't), pad by random
            max_len = max(len(per_a), len(per_b), mk.get("sks", 0))
            for idx in range(max_len):
                choice_parent = random.choice(["a", "b"])
                selected = None

                if choice_parent == "a" and idx < len(per_a):
                    selected = per_a[idx]
                elif choice_parent == "b" and idx < len(per_b):
                    selected = per_b[idx]
                else:
                    # fallback: pick whichever parent has the idx, or random empty slot
                    if idx < len(per_a):
                        selected = per_a[idx]
                    elif idx < len(per_b):
                        selected = per_b[idx]
                    else:
                        # place randomly
                        slot = random.randint(0, num_slots - 1)
                        ruang_idx = random.randint(0, num_ruang - 1)
                        selected = {"slot": slot, "hari": child.slot_to_day_hour(slot)[0],
                                    "jam": child.slot_to_day_hour(slot)[1],
                                    "ruang": child.idx_to_ruangan[ruang_idx],
                                    "ruang_idx": ruang_idx}

                # place selected pertemuan into child's matrix
                slot = selected["slot"]
                ruang_idx = selected["ruang_idx"]
                child.schedule_matrix[slot, ruang_idx].append(kode)
                # append to schedule_matkul
                child.schedule_matkul[kode].append({
                    "slot": slot,
                    "hari": child.slot_to_day_hour(slot)[0],
                    "jam": child.slot_to_day_hour(slot)[1],
                    "ruang": child.idx_to_ruangan[ruang_idx],
                    "ruang_idx": ruang_idx
                })

        return child

    # ----------------- Mutation -----------------
    def mutate(self, individual: Jadwal):
        """Apply mutation via the get_random_neighbor operator. Returns mutated ind."""
        # small chance to apply multiple mutations depending on mutation_rate
        if random.random() < self.mutation_rate:
            return individual.get_random_neighbor()
        return individual

    # ----------------- Run GA -----------------
    def run(self, verbose=True):
        population = self.init_population()

        for gen in range(self.generations):
            fitnesses = [self.fitness(ind) for ind in population]
            costs = [self.cost(ind) for ind in population]

            # track
            best_idx = int(np.argmax(fitnesses))
            best_cost = costs[best_idx]
            avg_cost = float(np.mean(costs))
            self.best_history.append(best_cost)
            self.avg_history.append(avg_cost)

            if verbose and (gen % max(1, self.generations // 10) == 0 or gen == self.generations - 1):
                print(f"Gen {gen:4d}: best_cost={best_cost:.4f}, avg_cost={avg_cost:.4f}")

            # Elitism: keep top-k
            sorted_pop = sorted(zip(population, fitnesses, costs), key=lambda x: x[1], reverse=True)
            new_population = [copy.deepcopy(x[0]) for x in sorted_pop[:self.elitism]]

            # fill rest
            while len(new_population) < self.population_size:
                # selection
                parent_a = self.tournament_select(population, fitnesses)
                parent_b = self.tournament_select(population, fitnesses)

                # crossover
                if random.random() < self.crossover_rate:
                    child = self.crossover(parent_a, parent_b)
                else:
                    child = copy.deepcopy(parent_a)

                # mutation
                child = self.mutate(child)

                new_population.append(child)

            population = new_population

        # final evaluation
        fitnesses = [self.fitness(ind) for ind in population]
        costs = [self.cost(ind) for ind in population]
        best_idx = int(np.argmax(fitnesses))
        best_ind = population[best_idx]

        if verbose:
            print("-- GA finished --")
            print(f"Best final cost: {costs[best_idx]:.4f}")

        return best_ind


# ----------------- Example helper to run experiments -----------------
if __name__ == "__main__":
    import time
    json_name = input("Enter json name (e.g., tc1.json): ")
    base = Jadwal(json_name=json_name)
    ga = GeneticScheduler(base,
                          population_size=40,
                          generations=200,
                          crossover_rate=0.85,
                          mutation_rate=0.25,
                          elitism=3,
                          seed=42)

    t0 = time.time()
    best = ga.run(verbose=True)
    t1 = time.time()
    print(f"Elapsed: {t1-t0:.2f}s")
    print("Best schedule:")
    best.print_schedule()

    # optionally, you can access ga.best_history and ga.avg_history for plotting
