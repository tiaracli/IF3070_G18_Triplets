# IF3070_G18_Triplets

Tugas Besar 1 IF3070 Dasar Inteligensi Artifisial 2026/2027.

Program ini menata kendaraan di geladak kapal kargo pakai algoritma local search. Program memilih kendaraan mana yang diangkut, posisinya, dan orientasinya (H atau V) supaya total ShippingFee sebesar mungkin. Kendaraan tidak boleh bertumpuk, harus ada di dalam geladak, dan total beratnya tidak boleh lebih dari kapasitas kapal.

Algoritma: hill climbing (steepest ascent, stochastic, sideways move, random restart), simulated annealing, dan genetic algorithm.

Bonus: semua varian hill climbing, objective function berbasis ETA, dan multi-kapal.

## Cara menjalankan

```bash
pip3 install -r requirements.txt
python3 src/data/make_data.py
python3 src/run_hill_climbing.py
python3 src/run_sa.py
python3 src/run_geneticalgorithm.py
python3 src/run_visual.py
```

`run_visual.py` dijalankan paling akhir karena gambarnya diambil dari file hasil hill climbing dan simulated annealing.

## Isi folder `src`

| File | Isinya |
|---|---|
| `data/make_data.py` | Membuat file data kapal dan kendaraan |
| `data/kasus_1.json` | 1 kapal (8x8, kapasitas 22) dan 13 kendaraan |
| `data/kasus_multi.json` | 2 kapal (8x8 dan 6x8) dan 20 kendaraan |
| `core.py` | Cek constraint dan hitung nilai objective (fee dan ETA) |
| `neighbor.py` | State awal acak dan langkah neighbor (tukar, pindah, ubah orientasi) |
| `hill_climbing.py` | Empat varian hill climbing |
| `sa.py` | Simulated annealing |
| `geneticalgorithm.py` | Genetic algorithm |
| `data_io.py` | Lokasi file data dan output, simpan tabel CSV |
| `visual.py` | Gambar posisi kendaraan di kapal dan grafik |
| `run_hill_climbing.py` | Menjalankan eksperimen hill climbing |
| `run_sa.py` | Menjalankan eksperimen simulated annealing |
| `run_geneticalgorithm.py` | Menjalankan eksperimen genetic algorithm dan bonusnya |
| `run_visual.py` | Membuat gambar kapal dan grafik untuk hasil hill climbing dan simulated annealing |

## Isi folder `output/ga`

| File | Isinya |
|---|---|
| `hasil.csv` | Percobaan A (populasi 50, iterasi 100/200/400) dan percobaan B (iterasi 200, populasi 20/50/100), 3 run tiap variasi |
| `hasil_bonus.csv` | GA untuk bonus ETA (`kasus_1`) dan bonus multi-kapal (`kasus_multi`), 3 run |
| `..._awal.png` | Posisi kendaraan di state awal |
| `..._akhir.png` | Posisi kendaraan di state akhir |
| `..._grafik.png` | Nilai objective maksimum dan rata-rata populasi terhadap iterasi |

Contoh: `A_pop50_iter100_run1_akhir.png` artinya percobaan A, populasi 50, iterasi 100, run 1, state akhir.

## Gambar hill climbing dan simulated annealing

| Folder | Nama gambar |
|---|---|
| `output/hc` | `<varian>_fee_seed<seed>_{awal,akhir,grafik}.png` |
| `output/bonus_eta` | `<varian>_eta_seed<seed>_{awal,akhir,grafik}.png` |
| `output/sa` | `<kasus>_run<k>_{awal,akhir,grafik,peluang}.png` |

`_peluang.png` adalah grafik e^(dE/T) terhadap iterasi untuk simulated annealing.

## Pembagian tugas

| Nama | NIM | Tugas |
|---|---|---|
| Indah Ramadhani | 18224037 | Core, hill climbing, objective ETA |
| Tiara Clianta Andiwi | 18224078 | Neighbor, simulated annealing, multi-kapal |
| Salsabila Shofiyah | 18224088 | Data, genetic algorithm, visualisasi, README |
