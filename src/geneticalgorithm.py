import random
import time

from core import OUT, check_placement, value_fee, eta_value, count_misplaced_urgent
from neighbor import random_state, random_neighbor


def pilih_induk(populasi, fitness):
    terkecil = min(fitness)
    bobot = []
    for f in fitness:
        bobot.append(f - terkecil + 1)
    return random.choices(populasi, weights=bobot)[0]


def crossover(a, b):
    titik = random.randint(1, len(a) - 1)
    anak1 = a[:titik] + b[titik:]
    anak2 = b[:titik] + a[titik:]
    return anak1, anak2


def perbaiki(problem, anak, cadangan):
    hasil = [OUT] * len(anak)
    urutan = list(range(len(anak)))
    random.shuffle(urutan)
    for i in urutan:
        for pos in [anak[i], cadangan[i]]:
            if pos == OUT:
                continue
            hasil[i] = pos
            if check_placement(problem, tuple(hasil)):
                break
            hasil[i] = OUT
    return tuple(hasil)


def mutasi(problem, state):
    baru = random_neighbor(problem, state)
    if baru is None:
        return state
    return baru


def run_ga(problem, objective="fee", populasi=50, iterasi=200, seed=None,
           p_crossover=0.9, p_mutasi=0.3):
    if seed is not None:
        random.seed(seed)
    if objective == "eta":
        nilai = eta_value
    else:
        nilai = value_fee

    mulai = time.time()

    pop = []
    for _ in range(populasi):
        pop.append(random_state(problem))
    fitness = [nilai(problem, s) for s in pop]

    idx = fitness.index(max(fitness))
    state_awal = pop[idx]
    nilai_awal = fitness[idx]
    terbaik = pop[idx]
    nilai_terbaik = fitness[idx]

    riwayat_max = [max(fitness)]
    riwayat_rata = [sum(fitness) / populasi]

    for gen in range(iterasi):
        pop_baru = [pop[fitness.index(max(fitness))]]

        while len(pop_baru) < populasi:
            a = pilih_induk(pop, fitness)
            b = pilih_induk(pop, fitness)
            if random.random() < p_crossover:
                anak1, anak2 = crossover(a, b)
                if not check_placement(problem, anak1):
                    anak1 = perbaiki(problem, anak1, b)
                if not check_placement(problem, anak2):
                    anak2 = perbaiki(problem, anak2, a)
            else:
                anak1, anak2 = a, b

            for anak in [anak1, anak2]:
                if random.random() < p_mutasi:
                    anak = mutasi(problem, anak)
                if len(pop_baru) < populasi:
                    pop_baru.append(anak)

        pop = pop_baru
        fitness = [nilai(problem, s) for s in pop]

        if max(fitness) > nilai_terbaik:
            nilai_terbaik = max(fitness)
            terbaik = pop[fitness.index(nilai_terbaik)]

        riwayat_max.append(max(fitness))
        riwayat_rata.append(sum(fitness) / populasi)

    durasi = time.time() - mulai

    return {
        "algorithm": "ga",
        "objective": objective,
        "dataset": problem["name"],
        "seed": seed,
        "params": {"population": populasi, "iterations": iterasi,
                   "p_crossover": p_crossover, "p_mutasi": p_mutasi},
        "initial_state": state_awal,
        "final_state": terbaik,
        "initial_value": nilai_awal,
        "final_value": nilai_terbaik,
        "final_fee": value_fee(problem, terbaik),
        "zone_violations": count_misplaced_urgent(problem, terbaik),
        "history": riwayat_max,
        "duration_s": durasi,
        "extra": {"avg_history": riwayat_rata},
    }
