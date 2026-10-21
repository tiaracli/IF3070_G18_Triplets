import json


OUT = (-1, 0, 0, "H")
ETA_URGENT = 3
ETA_PENALTY = 0.5


def read_data(path):
    with open(path, "r") as f:
        return json.load(f)


def ukuran_vehicle(vehicle, orientation):
    w = vehicle["w"]
    l = vehicle["l"]
    if orientation == "H":
        return w, l
    elif orientation == "V":
        return l, w
    return None


def posisi_vehicle(vehicle, placement):
    ship_idx, x, y, orientation = placement
    size = ukuran_vehicle(vehicle, orientation)
    if size is None:
        return None

    w, l = size
    cells = set()
    for dx in range(w):
        for dy in range(l):
            cells.add((x + dx, y + dy))
    return cells


def cek_placement(problem, state):
    ships = problem["ships"]
    vehicles = problem["vehicles"]

    if not isinstance(state, (tuple, list)):
        return False
    if len(state) != len(vehicles):
        return False

    used_cells = []
    ship_weights = []
    for ship in ships:
        used_cells.append(set())
        ship_weights.append(0)

    for i in range(len(vehicles)):
        vehicle = vehicles[i]
        placement = state[i]

        if not isinstance(placement, (tuple, list)):
            return False
        if len(placement) != 4:
            return False

        ship_idx, x, y, orientation = placement

        if type(ship_idx) != int:
            return False
        if type(x) != int or type(y) != int:
            return False
        if orientation not in ("H", "V"):
            return False

        if ship_idx == -1:
            if tuple(placement) != OUT:
                return False
            continue

        if ship_idx < 0 or ship_idx >= len(ships):
            return False
        if x < 0 or y < 0:
            return False

        ship = ships[ship_idx]
        cells = posisi_vehicle(vehicle, placement)
        if cells is None:
            return False

        for cx, cy in cells:
            if cx >= ship["w"] or cy >= ship["l"]:
                return False

        if len(cells.intersection(used_cells[ship_idx])) > 0:
            return False
        used_cells[ship_idx].update(cells)

        ship_weights[ship_idx] += vehicle["weight"]
        if ship_weights[ship_idx] > ship["capacity"]:
            return False

    return True


def value_fee(problem, state):
    vehicles = problem["vehicles"]
    total_fee = 0
    for i in range(len(vehicles)):
        placement = state[i]
        if placement[0] != -1:
            total_fee += vehicles[i]["fee"]
    return total_fee


def dekat_ramp(problem, vehicle, placement):
    ship_idx, x, y, orientation = placement
    size = ukuran_vehicle(vehicle, orientation)
    if size is None or ship_idx < 0 or ship_idx >= len(problem["ships"]):
        return False

    w, l = size
    ship_length = problem["ships"][ship_idx]["l"]
    front_limit = ship_length // 2
    return y + l <= front_limit


def value_eta(problem, state):
    vehicles = problem["vehicles"]
    total_score = 0
    for i in range(len(vehicles)):
        placement = state[i]
        if placement[0] == -1:
            continue

        vehicle = vehicles[i]
        fee = vehicle["fee"]
        if vehicle["eta"] <= ETA_URGENT and not dekat_ramp(problem, vehicle, placement):
            fee = fee * (1 - ETA_PENALTY)
        total_score += fee
    return total_score


def count_salahzona(problem, state):
    vehicles = problem["vehicles"]
    count = 0
    for i in range(len(vehicles)):
        placement = state[i]
        if placement[0] == -1:
            continue

        vehicle = vehicles[i]
        if vehicle["eta"] <= ETA_URGENT and not dekat_ramp(problem, vehicle, placement):
            count += 1
    return count


def show_layout(problem, state):
    if not cek_placement(problem, state):
        return "State tidak valid"

    simbol = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    out = []

    for s, ship in enumerate(problem["ships"]):
        grid = [["." for _ in range(ship["l"])] for _ in range(ship["w"])]
        muatan = 0
        for idx in range(len(problem["vehicles"])):
            vehicle = problem["vehicles"][idx]
            placement = state[idx]
            if placement[0] != s:
                continue
            muatan += vehicle["weight"]
            for x, y in posisi_vehicle(vehicle, placement):
                grid[x][y] = simbol[idx % len(simbol)]

        out.append(f'{ship["id"]} (muatan {muatan}/{ship["capacity"]})')
        out.extend(" ".join(baris) for baris in grid)
        out.append("")

    luar = []
    for i in range(len(problem["vehicles"])):
        if state[i][0] == -1:
            luar.append(problem["vehicles"][i]["id"])
    out.append("Di luar: " + (", ".join(luar) if luar else "-"))

    legenda = []
    for i, vehicle in enumerate(problem["vehicles"]):
        legenda.append(f"{simbol[i % len(simbol)]}={vehicle['id']}")
    out.append("Legenda: " + ", ".join(legenda))

    return "\n".join(out)