import random

from core import OUT, ukuran_vehicle, cek_placement

P_KELUAR = 0.15

def cek_samevehicle(a, b):
    return all(a[k] == b[k] for k in ("w", "l", "weight", "fee", "eta"))

def action_move(state, move):
    s = list(state)
    if move[0] == "swap":
        _, i, j = move
        s[i], s[j] = s[j], s[i]
    elif move[0] == "move":
        _, i, placement = move
        s[i] = placement
    else:
        _, i = move
        ship, r, c, o = s[i]
        s[i] = (ship, r, c, "V" if o == "H" else "H")
    return tuple(s)


def random_placement(problem, vehicle, orient):
    ships = problem["ships"]
    s = random.randrange(len(ships))
    h, wd = ukuran_vehicle(vehicle, orient)
    if h > ships[s]["w"] or wd > ships[s]["l"]:
        return None
    r = random.randint(0, ships[s]["w"] - h)
    c = random.randint(0, ships[s]["l"] - wd)
    return (s, r, c, orient)

def random_state(problem, p_masuk=0.6, max_coba=30):
    vehicles = problem["vehicles"]
    state = [OUT] * len(vehicles)
    urutan = list(range(len(vehicles)))
    random.shuffle(urutan)
    for i in urutan:
        if random.random() > p_masuk:
            continue
        for _ in range(max_coba):
            p = random_placement(problem, vehicles[i], random.choice("HV"))
            if p is None:
                continue
            coba = state.copy()
            coba[i] = p
            if cek_placement(problem, tuple(coba)):
                state[i] = p
                break
    return tuple(state)

def random_move(problem, state):
    vehicles = problem["vehicles"]
    n = len(state)
    jenis = random.choice(["swap", "move", "rotate"])

    if jenis == "swap":
        i, j = random.sample(range(n), 2)
        if state[i][0] == -1 and state[j][0] == -1:
            return None
        if cek_samevehicle(vehicles[i], vehicles[j]):
            return None
        return ("swap", i, j)

    i = random.randrange(n)
    if jenis == "rotate":
        if state[i][0] == -1:
            return None
        return ("rotate", i)
    # move
    if state[i][0] != -1 and random.random() < P_KELUAR:
        return ("move", i, OUT)
    if state[i][0] == -1:
        orient = random.choice("HV")
    else:
        orient = state[i][3]
    p = random_placement(problem, vehicles[i], orient)
    if p is None or p == state[i]:
        return None
    return ("move", i, p)

def random_neighbor(problem, state, max_coba=100):
    for _ in range(max_coba):
        move = random_move(problem, state)
        if move is None:
            continue
        nxt = action_move(state, move)
        if cek_placement(problem, nxt):
            return nxt
    return None


def all_neighbors(problem, state):
    vehicles = problem["vehicles"]
    ships = problem["ships"]
    n = len(state)
    kandidat = []

    # swap
    for i in range(n):
        for j in range(i + 1, n):
            if state[i][0] == -1 and state[j][0] == -1:
                continue
            if cek_samevehicle(vehicles[i], vehicles[j]):
                continue
            kandidat.append(action_move(state, ("swap", i, j)))

    for i in range(n):
        v = vehicles[i]
        di_dalam = state[i][0] != -1

        # rotate
        if di_dalam:
            kandidat.append(action_move(state, ("rotate", i)))
        # move keluar kapal
        if di_dalam:
            kandidat.append(action_move(state, ("move", i, OUT)))
        # move ke semua posisi
        daftar_orient = [state[i][3]] if di_dalam else ["H", "V"]
        for o in daftar_orient:
            h, wd = ukuran_vehicle(v, o)
            for s, ship in enumerate(ships):
                for r in range(ship["w"] - h + 1):
                    for c in range(ship["l"] - wd + 1):
                        p = (s, r, c, o)
                        if p != state[i]:
                            kandidat.append(action_move(state, ("move", i, p)))

    return [k for k in kandidat if cek_placement(problem, k)]
