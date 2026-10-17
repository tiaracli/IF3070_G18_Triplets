import json
#Fungsi dasar untuk penataan kendaraan pada kapal


ETA_URGENT = 3 #ETA yang <= 3 hari itu dianggap mendesak dan priority
ETA_PENALTY = 0.5 #nilai shipping fee nya dikurangin jadi 50% kalau ada kendaraan yang ETA <= 3 hari ditempatin jauh dari pintu bongkar kapal


def load_problem(path): #baca data kapal n kendaraan dari file JSON
    with open(path, "r") as f:
        return json.load(f)  
def get_vehicle_size(vehicle, orientation): #ambil ukuran asli kendaraan sesuai arah penempatannya
    w = vehicle["w"]
    l = vehicle["l"]


    if orientation == "H":
        return w, l
    elif orientation == "V": #kalau vertikal, lebar n panjangnya ditukar
        return l, w
    return None
def get_vehicle_cells(vehicle, placement): #ambil semua grid yang ditempatin kendaraan
    ship_idx, x, y, orientation = placement
    size = get_vehicle_size(vehicle, orientation)


    if size is None:
        return None


    w, l = size
    cells = set()


    #hitung koordinat based on lebar dan panjang
    for dx in range (w):
        for dy in range(l):
            cells.add((x+dx, y+dy))
    return cells


def check_placement(problem, state):
    #cek constraint
    ships = problem["ships"]
    vehicles = problem["vehicles"]


    #jumlah penempatan harus sama dengan jumlah kendaraan
    if not isinstance(state, (tuple, list)):
        return False


    if len(state) != len(vehicles):
        return False


    used_cells = []
    ship_weights = []


    # catat grid yang terpakai dan berat muatan tiap kapal
    for ship in ships:
        used_cells.append(set())
        ship_weights.append(0)


    #analisis dan cek penempatan kendaraan satu per satu
    for i in range(len(vehicles)):
        vehicle = vehicles[i]
        placement = state[i]


        if not isinstance(placement, (tuple, list)):
            return False
        if len(placement) != 4:
            return False


        ship_idx, x, y, orientation = placement


        #koordinat dan nomor kapal harus bilangan bulat
        if type(ship_idx) != int:
            return False
        if type(x) != int or type(y) != int:
            return False


        if orientation not in ("H", "V"):
            return False


        #ship_idx -1 = kendaraan tidak ikut diangkut
        if ship_idx == -1:
            if tuple(placement) != OUT:
                return False
            continue


        #cek nomor kapal n posisi awal kendaraan
        if ship_idx < 0 or ship_idx >= len(ships):
            return False
        if x < 0 or y < 0:
            return False


        ship = ships[ship_idx]
        cells = get_vehicle_cells(vehicle, placement)


        if cells is None:
            return False


        #kendaraan tidak boleh melewati batas grid kapal
        for cx, cy in cells:
            if cx >= ship["w"] or cy >= ship["l"]:
                return False


        #memastikan posisi kendaraan tidak overlap
        if len(cells.intersection(used_cells[ship_idx])) > 0:
            return False


        used_cells[ship_idx].update(cells)


        #tambah berat kendaraan, lalu cek kapasitas kapal
        ship_weights[ship_idx] += vehicle["weight"]


        if ship_weights[ship_idx] > ship["capacity"]:
            return False
    return True
def value_fee(problem, state):
    #hitung total shipping fee kendaraaan yang berhasil diangkut
    vehicles = problem["vehicles"]
    total_fee = 0


    for i in range(len(vehicles)):
        placement = state[i]


        if placement[0] != -1:
            total_fee += vehicles[i]["fee"]


    return total_fee
def is_near_ramp(problem, vehicle, placement):
    #cek apakaj selurh kendaraan berada di dekat pintu ramp
    #ramp dianggap berada di sisi y = 0
    ship_idx, x, y, orientation = placement
    size = get_vehicle_size(vehicle, orientation)
   
    if size is None or ship_idx < 0 or ship_idx >= len(problem["ships"]):
        return False
   
    w, l = size
    ship_length = problem["ships"][ship_idx]["l"]
    front_limit = ship_length // 2
    return y + l <= front_limit
def eta_value(problem, state):
    #hiitung objt alt pakai eta
    #kendaraan mendesak yang jauh dari ramp, diberi penalti
    vehicles = problem["vehicles"]
    total_score = 0


    for i in range(len(vehicles)):
        placement = state[i]


        if placement[0] == -1:
            continue


        vehicle = vehicles[i]
        fee = vehicle["fee"]
        eta = vehicle["eta"]


        if eta <= ETA_URGENT and not is_near_ramp(problem, vehicle, placement):
            fee = fee * (1 - ETA_PENALTY)
        total_score += fee
    return total_score
def count_misplaced_urgent(problem, state):
    #hitung kendaraan priority yang gaada di dekat ramp
    vehicles = problem["vehicles"]
    count = 0


    for i in range(len(vehicles)):
        placement = state[i]


        if placement[0] == -1:
            continue


        vehicle = vehicles[i]


        if vehicle["eta"] <= ETA_URGENT and not is_near_ramp(problem, vehicle, placement):
            count += 1
    return count


def render_text(problem, state):
    if not check_placement(problem, state):
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


            for x, y in get_vehicle_cells(vehicle, placement):
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



