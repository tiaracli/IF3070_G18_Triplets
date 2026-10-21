import json
import os
FOLDER = os.path.dirname(os.path.abspath(__file__))
TIPE_1 = {
    "motor": (1, 2, 1, 10, 4),
    "sedan": (2, 3, 2, 30, 4),
    "suv": (2, 4, 3, 38, 3),
    "truk": (3, 4, 5, 70, 2),
}


TIPE_MULTI = {
    "motor": (1, 2, 1, 10, 6),
    "sedan": (2, 3, 2, 30, 6),
    "suv": (2, 4, 3, 38, 5),
    "truk": (3, 4, 5, 70, 3),
}
def make_vehicle(tipe):
    hasil = []
    n = 0
    for nama in tipe:
        w, l, berat, fee, jumlah = tipe[nama]
        for i in range(jumlah):
            n += 1
            hasil.append({
                "id": nama + str(i + 1),
                "w": w,
                "l": l,
                "weight": berat,
                "fee": fee,
                "eta": (n % 10) + 1,
            })
    return hasil


kasus_1 = {
    "ships": [{"id": "kapal1", "w": 8, "l": 8, "capacity": 22}],
    "vehicles": make_vehicle(TIPE_1),
}
kasus_multi = {
    "ships": [
        {"id": "kapal1", "w": 8, "l": 8, "capacity": 22},
        {"id": "kapal2", "w": 6, "l": 8, "capacity": 16},
    ],
    "vehicles": make_vehicle(TIPE_MULTI),
}

for nama, data in [("kasus_1", kasus_1), ("kasus_multi", kasus_multi)]:
    with open(os.path.join(FOLDER, nama + ".json"), "w") as f:
        json.dump(data, f, indent=2)
    print("selesai bikin", nama + ".json")