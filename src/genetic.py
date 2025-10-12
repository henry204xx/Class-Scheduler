"""
Genetic Algorithm for scheduling (integrates with Jadwal.py)

Usage example:
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
                 seed=None):
        """
        base_jadwal: instance of Jadwal loaded with json test case
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

        # Default equal weights (can be tuned)
        if weights is None:
            weights = {"mhs": 1.0, "dosen": 1.0, "kapasitas": 1.0, "prioritas": 1.0}
        self.weights = weights

        # Tracking progress
        self.best_history = []
        self.avg_history = []

    # ----------------- Fitness / Cost -----------------
    def cost(self, jadwal: Jadwal):
        """Compute combined cost (lower is better)"""
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
        """Convert cost to fitness (higher fitness = better)"""
        c = self.cost(jadwal)
        return 1.0 / (1.0 + c)

    # ----------------- Population initialization -----------------
    def init_population(self):
        pop = []
        for _ in range(self.population_size):
            ind = copy.deepcopy(self.base)
            ind.random_schedule()
            pop.append(ind)
        return pop

    # ----------------- Selection (Roulette Wheel) -----------------
    def roulette_select(self, population, fitnesses):
        """Roulette wheel selection — probabilistic selection by fitness proportion."""
        total_fit = sum(fitnesses)
        if total_fit == 0:
            # if all fitness are zero, select randomly
            return copy.deepcopy(random.choice(population))

        probs = [f / total_fit for f in fitnesses]
        cumulative = []
        cumsum = 0
        for p in probs:
            cumsum += p
            cumulative.append(cumsum)

        r = random.random()  # random number in [0, 1)
        for i, cum in enumerate(cumulative):
            if r <= cum:
                return copy.deepcopy(population[i])

        # fallback (floating point edge case)
        return copy.deepcopy(population[-1])

    # ----------------- Crossover -----------------
    def crossover(self, parent_a: Jadwal, parent_b: Jadwal):
        """Create a child by inheriting pertemuan locations from parents."""
        child = copy.deepcopy(self.base)

        # Clear child schedule
        num_slots = child.schedule_matrix.shape[0]
        num_ruang = child.schedule_matrix.shape[1]
        for i in range(num_slots):
            for j in range(num_ruang):
                child.schedule_matrix[i, j] = []
        child.schedule_matkul = {mk["kode"]: [] for mk in child.mata_kuliah}

        # For each course, inherit meetings from parent A or B
        for mk in child.mata_kuliah:
            kode = mk["kode"]
            per_a = parent_a.schedule_matkul.get(kode, [])
            per_b = parent_b.schedule_matkul.get(kode, [])
            max_len = max(len(per_a), len(per_b), mk.get("sks", 0))

            for idx in range(max_len):
                choice_parent = random.choice(["a", "b"])
                selected = None

                if choice_parent == "a" and idx < len(per_a):
                    selected = per_a[idx]
                elif choice_parent == "b" and idx < len(per_b):
                    selected = per_b[idx]
                else:
                    slot = random.randint(0, num_slots - 1)
                    ruang_idx = random.randint(0, num_ruang - 1)
                    selected = {
                        "slot": slot,
                        "hari": child.slot_to_day_hour(slot)[0],
                        "jam": child.slot_to_day_hour(slot)[1],
                        "ruang": child.idx_to_ruangan[ruang_idx],
                        "ruang_idx": ruang_idx
                    }

                slot = selected["slot"]
                ruang_idx = selected["ruang_idx"]
                child.schedule_matrix[slot, ruang_idx].append(kode)
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
        """Apply mutation via get_random_neighbor()."""
        if random.random() < self.mutation_rate:
            return individual.get_random_neighbor()
        return individual

    # ----------------- Run GA -----------------
    def run(self, verbose=True):
        population = self.init_population()

        for gen in range(self.generations):
            fitnesses = [self.fitness(ind) for ind in population]
            costs = [self.cost(ind) for ind in population]

            best_idx = int(np.argmax(fitnesses))
            best_cost = costs[best_idx]
            avg_cost = float(np.mean(costs))
            self.best_history.append(best_cost)
            self.avg_history.append(avg_cost)

            if verbose and (gen % max(1, self.generations // 10) == 0 or gen == self.generations - 1):
                print(f"Gen {gen:4d}: best_cost={best_cost:.4f}, avg_cost={avg_cost:.4f}")

            # Elitism: keep top individuals
            sorted_pop = sorted(zip(population, fitnesses, costs), key=lambda x: x[1], reverse=True)
            new_population = [copy.deepcopy(x[0]) for x in sorted_pop[:self.elitism]]

            # Fill the rest with crossover and mutation
            while len(new_population) < self.population_size:
                parent_a = self.roulette_select(population, fitnesses)
                parent_b = self.roulette_select(population, fitnesses)

                if random.random() < self.crossover_rate:
                    child = self.crossover(parent_a, parent_b)
                else:
                    child = copy.deepcopy(parent_a)

                child = self.mutate(child)
                new_population.append(child)

            population = new_population

        # Final evaluation
        fitnesses = [self.fitness(ind) for ind in population]
        costs = [self.cost(ind) for ind in population]
        best_idx = int(np.argmax(fitnesses))
        best_ind = population[best_idx]

        if verbose:
            print("-- GA finished --")
            print(f"Best final cost: {costs[best_idx]:.4f}")

        return best_ind


# ----------------- Example Runner -----------------
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
