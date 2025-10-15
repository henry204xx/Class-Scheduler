import copy
import random
import numpy as np
from Jadwal import Jadwal
import time

class GeneticScheduler:
    def __init__(self, base_jadwal: Jadwal,
                 population_size=30,
                 generations=200,
                 elitisism_ratio=0.1,
                 n_tournament=5,
                 best_tournament=2,
                 weights=None,
                 seed=None):
        self.base = base_jadwal
        self.population_size = population_size
        self.generations = generations
        self.elitisism_ratio = elitisism_ratio
        self.n_tournament = n_tournament
        self.best_tournament = best_tournament
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)


        if weights is None:
            weights = {"mhs": 1.0, "dosen": 1.0, "kapasitas": 1.0, "prioritas": 1.0}
        self.weights = weights

        self.best_history = []
        self.avg_history = []

    def cost(self, jadwal: Jadwal):
        c1 = jadwal.objf_waktu_konflik_mhs()
        c2 = jadwal.objf_waktu_konflik_dosen()
        c3 = jadwal.objf_kapasitas_ruang()
        c4 = jadwal.objf_prioritas()
        total = (self.weights["mhs"] * c1 +
                 self.weights["dosen"] * c2 +
                 self.weights["kapasitas"] * c3 +
                 self.weights["prioritas"] * c4)
        return float(total)

    def fitness(self, jadwal: Jadwal):
        c = self.cost(jadwal)
        return 1.0 / (1.0 + c)

    def init_population(self):
        pop = []
        for _ in range(self.population_size):
            ind = copy.deepcopy(self.base)
            ind.random_schedule()
            pop.append(ind)
        return pop

    def tournament_population(self, population):
        new_population = []
        random.shuffle(population)
        groups = [population[i:i+self.n_tournament] for i in range(0, len(population), self.n_tournament)]
        for group in groups:
            fitnesses = [self.fitness(ind) for ind in group]
            if len(group) < self.best_tournament:
                selected = [copy.deepcopy(ind) for ind in group]
            else:
                sorted_indices = np.argsort(fitnesses)[-self.best_tournament:]
                selected = [copy.deepcopy(group[i]) for i in sorted_indices]
            new_population.extend(selected)
        self.population_size = len(new_population)
        return new_population

    def selection(self, population, fitnesses):
        total_fit = sum(fitnesses)
        if total_fit == 0:
            return [copy.deepcopy(random.choice(population)) for _ in range(self.population_size)]
        probs = [f / total_fit for f in fitnesses]
        cumulative = np.cumsum(probs)
        new_pop = []
        for _ in range(self.population_size):
            r = random.random()
            for i, cum in enumerate(cumulative):
                if r <= cum:
                    new_pop.append(copy.deepcopy(population[i]))
                    break
        return new_pop

    def crossover_population(self, population):
        new_population = []
        for i in range(0, len(population), 2):
            parent_a = population[i]
            parent_b = population[(i + 1) % len(population)]
            child_a, child_b = self.crossover(parent_a, parent_b)
            new_population.extend([child_a, child_b])
        return new_population[:len(population)]

    def mutation_population(self, population):
        new_population = []
        for ind in population:
            n = len(ind.mata_kuliah)
            point = random.randint(0, n)
            if point != n:
                mk = ind.mata_kuliah[point]
                kode = mk["kode"]
                if kode in ind.schedule_matkul and len(ind.schedule_matkul[kode]) > 0:
                    for pertemuan in ind.schedule_matkul[kode]:
                        slot_lama = pertemuan["slot"]
                        ruang_idx_lama = pertemuan["ruang_idx"]
                        new_slot = random.randint(0, ind.schedule_matrix.shape[0] - 1)
                        new_ruang_idx = random.randint(0, ind.schedule_matrix.shape[1] - 1)
                        if kode in ind.schedule_matrix[slot_lama, ruang_idx_lama]:
                            ind.schedule_matrix[slot_lama, ruang_idx_lama].remove(kode)
                        ind.schedule_matrix[new_slot, new_ruang_idx].append(kode)
                        pertemuan["slot"] = new_slot
                        pertemuan["hari"], pertemuan["jam"] = ind.slot_to_day_hour(new_slot)
                        pertemuan["ruang_idx"] = new_ruang_idx
                        pertemuan["ruang"] = ind.idx_to_ruangan[new_ruang_idx]
            new_population.append(ind)
        return new_population

    def crossover(self, parent_a: Jadwal, parent_b: Jadwal):
        n = len(parent_a.mata_kuliah)
        point = random.randint(0, n)
        if point == n:
            return copy.deepcopy(parent_a), copy.deepcopy(parent_b)
        child_a = copy.deepcopy(self.base)
        child_b = copy.deepcopy(self.base)
        num_slots = child_a.schedule_matrix.shape[0]
        num_ruang = child_a.schedule_matrix.shape[1]
        for i in range(num_slots):
            for j in range(num_ruang):
                child_a.schedule_matrix[i, j] = []
                child_b.schedule_matrix[i, j] = []
        child_a.schedule_matkul = {mk["kode"]: [] for mk in child_a.mata_kuliah}
        child_b.schedule_matkul = {mk["kode"]: [] for mk in child_b.mata_kuliah}
        for idx, mk in enumerate(child_a.mata_kuliah):
            kode = mk["kode"]
            if idx < point:
                src_a, src_b = parent_a, parent_b
            else:
                src_a, src_b = parent_b, parent_a
            per_a = src_a.schedule_matkul.get(kode, [])
            per_b = src_b.schedule_matkul.get(kode, [])
            for per in per_a:
                slot = per["slot"]
                ruang_idx = per["ruang_idx"]
                child_a.schedule_matrix[slot, ruang_idx].append(kode)
                child_a.schedule_matkul[kode].append(per)
            for per in per_b:
                slot = per["slot"]
                ruang_idx = per["ruang_idx"]
                child_b.schedule_matrix[slot, ruang_idx].append(kode)
                child_b.schedule_matkul[kode].append(per)
        return child_a, child_b

    def run(self, verbose=True):
        population = self.init_population()
        population = self.tournament_population(population)
        t0 = time.time()
        elitism_count = int(self.elitisism_ratio * (self.population_size * self.best_tournament / self.n_tournament))
        for gen in range(self.generations):
            fitnesses = [self.fitness(ind) for ind in population]
            costs = [self.cost(ind) for ind in population]
            best_idx = int(np.argmax(fitnesses))
            best_cost = costs[best_idx]
            avg_cost = float(np.mean(costs))
            self.best_history.append(best_cost)
            self.avg_history.append(avg_cost)
            t1 = time.time()
            print(f"Gen {gen:4d}: best_cost={best_cost:.4f}, avg_cost={avg_cost:.4f}, time={t1-t0:.3f}")
            elite_indices = np.argsort(fitnesses)[-elitism_count:]
            elites = [copy.deepcopy(population[i]) for i in elite_indices]
            selected_pop = self.selection(population, fitnesses)
            crossed_pop = self.crossover_population(selected_pop)
            mutated_pop = self.mutation_population(crossed_pop)
            survivors = mutated_pop[:max(0, self.population_size - elitism_count)]
            population = elites + survivors
        fitnesses = [self.fitness(ind) for ind in population]
        costs = [self.cost(ind) for ind in population]
        best_idx = int(np.argmax(fitnesses))
        best_ind = population[best_idx]
        if verbose:
            print("-- GA finished --")
            print(f"Best final cost: {costs[best_idx]:.4f}")
            print(f"Iteration : {self.generations}")
            print(f"Population : {self.population_size}")
        return best_ind

if __name__ == "__main__":
    json_name = input("Enter json name (e.g., tc1.json): ")
    base = Jadwal(json_name=json_name)
    # weight = {"mhs": 10.0, "dosen": 5.0, "kapasitas": 1.0, "prioritas": 1.0}
    ga = GeneticScheduler(base,
                          population_size=200,
                          generations=100,
                          elitisism_ratio=0.2,
                          n_tournament=5,
                          best_tournament=2
                          )
    t0 = time.time()
    best = ga.run(verbose=True)
    t1 = time.time()
    print(f"Elapsed: {t1-t0:.2f}s")
    print("Best schedule:")
    best.print_schedule()
