#Fungsi dasar untuk penataan kendaraan pada kapal


ETA_URGENT = 3 #ETA yang <= 3 hari itu dianggap mendesak dan priority
ETA_PENALTY = 0.5 #nilai shipping fee nya dikurangin jadi 50% kalau ada kendaraan yang ETA <= 3 hari ditempatin jauh dari pintu bongkar kapal


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
    vehicles = {}


    for vehicle in problem["vehicles"]:
        vehicles[vehicle["id"]] = vehicle
    #memastikan semua kendaraan tercatat di state
    if set(state.keys()) != set(vehicles.keys()):
        return False
   
    used_cells = []
    ship_weights = []


    for ship in ships:
        used_cells.append(set())
        ship_weights.append(0)
    for vid, placement in state.items():
        if placement is None:
            continue
        if not isinstance(placement, (tuple, list)):
            return False
        if len(placement) != 4:
            return False


        ship_idx, x, y, orientation = placement


        if type(ship_idx) != int:
            return False
        if type(x) != int or type(y) != int:
            return False
        if ship_idx < 0 or ship_idx >= len(ships):
            return False
        if x < 0 or y < 0:
            return False


        vehicle = vehicles[vid]
        ship = ships[ship_idx]


        cells = get_vehicle_cells(vehicle, placement)
        if cells is None:
             return False


        #cek apakah kendaraan melewati batas kapapl
        for cx, cy in cells:
            if cx >= ship["w"] or cy >= ship["l"]:
                return False
        #cek apakah ada sel yang udah terpakai
        if len(cells.intersection(used_cells[ship_idx])) > 0:
            return False
        used_cells[ship_idx].update(cells)
        #hitung totall berat kendaraan di kapal
        ship_weights[ship_idx] += vehicle["weight"]
        if ship_weights[ship_idx] > ship["max_weight"]:
            return False
    return True
def value_fee(problem, state):
    #hitung total shipping fee kendaraaan yang berhasil diangkut
    vehicles = {}
    for vehicle in problem["vehicles"]:
        vehicles[vehicle["id"]] = vehicle
    total_fee = 0
    for vid, placement in state.items():
        if placement is not None:
            total_fee += vehicles[vid]["fee"]
    return total_fee
def is_near_ramp(problem, vehicle, placement):
    #cek apakaj selurh kendaraan berada di dekat pintu ramp
    #ramp dianggap berada di sisi y = 0
    ship_idx, x, y, orientation = placement
    size = get_vehicle_size(vehicle, orientation)
   
    if size is None:
        return False
   
    w, l = size
    ship_length = problem["ships"][ship_idx]["l"]
    front_limit = ship_length // 2
    return y + l <= front_limit
def eta_value(problem, state):
    #hiitung objt alt pakai eta
    #kendaraan mendesak yang jauh dari ramp, diberi penalti
    vehicles = {}


    for vehicle in problem["vehicles"]:
        vehicles[vehicle["id"]] = vehicle
    total_score = 0
    for vid, placement in state.items():
        if placement is None:
            continue
        vehicle = vehicles[vid]
        fee = vehicle["fee"]
        eta = vehicle["eta"]


        if eta <= ETA_URGENT and not is_near_ramp(problem, vehicle, placement):
            fee = fee * (1-ETA_PENALTY)
        total_score += fee
    return total_score
def count_misplaced_urgent(problem, state):
    #hitung kendaraan priority yang gaada di dekat ramp
    vehicles = {}
    for vehicle in problem["vehicles"]:
        vehicles[vehicle["id"]] = vehicle
    count = 0
    for vid, placement in state.items():
        if placement is None:
            continue
        vehicle = vehicles[vid]
        if vehicle["eta"] <= ETA_URGENT and not is_near_ramp(problem, vehicle, placement):
            count += 1
    return count
