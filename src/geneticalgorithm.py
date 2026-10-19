import random

from core import OUT, check_placement, value_fee, eta_value
from neighbor import random_state, random_neighbor


def hitung_nilai(problem, state, objective):
    if objective == "eta":
        return eta_value(problem, state)
    return value_fee(problem, state)


def pilih_induk(populasi, fitness):
    return random.choices(populasi, weights=fitness)[0]


def crossover(a, b):
    titik = random.randint(1, len(a) - 1)
    return a[:titik] + b[titik:], b[:titik] + a[titik:]


def perbaiki(problem, anak, cadangan):
    hasil = [OUT] * len(anak)
    urutan = list(range(len(anak)))
    random.shuffle(urutan)
    for i in urutan:
        for posisi in [anak[i], cadangan[i]]:
            if posisi == OUT:
                continue
            hasil[i] = posisi
            if check_placement(problem, tuple(hasil)):
                break
            hasil[i] = OUT
    return tuple(hasil)


def mutasi(problem, state):
    baru = random_neighbor(problem, state)
    if baru is None:
        return state
    return baru


def genetic_algorithm(problem, objective="fee", jumlah_populasi=50, iterasi=200):
    populasi = []
    for i in range(jumlah_populasi):
        populasi.append(random_state(problem))
    fitness = [hitung_nilai(problem, s, objective) for s in populasi]

    terbaik = populasi[fitness.index(max(fitness))]
    awal = terbaik
    riwayat_max = [max(fitness)]
    riwayat_rata = [sum(fitness) / jumlah_populasi]

    for gen in range(iterasi):
        baru = [populasi[fitness.index(max(fitness))]]

        while len(baru) < jumlah_populasi:
            a = pilih_induk(populasi, fitness)
            b = pilih_induk(populasi, fitness)
            anak1, anak2 = crossover(a, b)
            if not check_placement(problem, anak1):
                anak1 = perbaiki(problem, anak1, b)
            if not check_placement(problem, anak2):
                anak2 = perbaiki(problem, anak2, a)

            for anak in [anak1, anak2]:
                if random.random() < 0.3:
                    anak = mutasi(problem, anak)
                if len(baru) < jumlah_populasi:
                    baru.append(anak)

        populasi = baru
        fitness = [hitung_nilai(problem, s, objective) for s in populasi]

        if max(fitness) > hitung_nilai(problem, terbaik, objective):
            terbaik = populasi[fitness.index(max(fitness))]

        riwayat_max.append(max(fitness))
        riwayat_rata.append(sum(fitness) / jumlah_populasi)

    return awal, terbaik, riwayat_max, riwayat_rata
