# IF3070_G18_Triplets

Tugas Besar 1 IF3070 Dasar Inteligensi Artifisial 2026/2027
Kelompok 18 Triplets, Institut Teknologi Bandung

Repository ini berisi program untuk menata kendaraan di geladak kapal kargo memakai algoritma local search. Program memilih kendaraan mana yang diangkut, lalu menentukan posisi dan orientasinya, supaya total ShippingFee setinggi mungkin tanpa melanggar batasan kapal.

## Deskripsi Tugas Besar

Setiap kendaraan punya ukuran, berat, ShippingFee, dan ETA yang berbeda. Kapal punya geladak berbentuk grid dengan luas dan kapasitas berat yang terbatas, jadi tidak semua kendaraan bisa ikut. Susunan kendaraan dianggap valid kalau kendaraan tidak saling bertumpuk, semua bagiannya ada di dalam geladak, dan total beratnya tidak melebihi kapasitas kapal.

Pencarian solusi memakai tiga algoritma, yaitu Hill-Climbing, Simulated Annealing, dan Genetic Algorithm. Selain bagian wajib, kami juga mengerjakan tiga bonus, yaitu keempat varian Hill-Climbing, objective function tambahan berbasis ETA, dan penataan untuk lebih dari satu kapal.

## Persiapan Demo Tugas Besar

Program ditulis dengan Python 3 dan sudah dicoba di Python 3.13. Library tambahan yang dipakai hanya matplotlib untuk membuat gambar kapal dan grafik.

Clone repository lalu masuk ke foldernya.

```bash
git clone https://github.com/tiaracli/IF3070_G18_Triplets.git
cd IF3070_G18_Triplets
```

Install library yang dibutuhkan.

```bash
python3 -m pip install -r requirements.txt
```

Kalau memakai Windows, ganti `python3` dengan `python` di semua perintah.

## Menjalankan Program Demo

```bash
python3 src/main.py
```

Program akan menampilkan menu di terminal. Pengguna memilih kasus, algoritma, objective function, seed, lalu parameter algoritmanya. Setiap pertanyaan menampilkan batas angka yang boleh diisi, dan kalau langsung menekan Enter, program memakai nilai bawaan.

Pilihan algoritma di menu adalah sebagai berikut.

| Nomor | Algoritma |
| --- | --- |
| 1 | Steepest Ascent Hill Climbing |
| 2 | Stochastic Hill Climbing |
| 3 | Sideways Move Hill Climbing |
| 4 | Random Restart Hill Climbing |
| 5 | Simulated Annealing |
| 6 | Genetic Algorithm |

Setelah selesai, program menampilkan state awal dan state akhir dalam bentuk grid teks, lengkap dengan daftar kendaraan yang tidak terangkut. Di bawahnya ada ringkasan berisi nilai ShippingFee, nilai ETA, jumlah kendaraan mendesak yang jauh dari pintu masuk, jumlah iterasi, dan durasi. Gambar state awal, state akhir, dan grafik disimpan otomatis ke folder `output/hc`, `output/sa`, atau `output/ga` sesuai algoritma yang dipilih. Nama filenya memuat kasus, algoritma, objective, dan seed, jadi hasil run sebelumnya tidak tertimpa.

## Menjalankan Eksperimen

Setiap algoritma punya skrip eksperimen sendiri yang menjalankan semua percobaan dengan seed tetap.

| Skrip | Isi | Folder hasil |
| --- | --- | --- |
| `python3 src/run_hill_climbing.py` | Keempat varian Hill-Climbing dengan objective ShippingFee dan ETA | `output/hc` dan `output/bonus_eta` |
| `python3 src/run_sa.py` | Simulated Annealing pada kasus satu kapal dan multi-kapal | `output/sa` |
| `python3 src/run_geneticalgorithm.py` | Genetic Algorithm dengan variasi iterasi dan populasi, ditambah eksperimen bonus | `output/ga` |
| `python3 src/run_visual.py` | Membuat gambar dan grafik Hill-Climbing serta Simulated Annealing dari hasil eksperimen | `output/hc`, `output/bonus_eta`, dan `output/sa` |

Skrip `run_visual.py` membaca file JSON hasil eksperimen, jadi jalankan `run_hill_climbing.py` dan `run_sa.py` lebih dulu. Karena seed-nya tetap, angka yang keluar akan selalu sama. Hanya durasinya yang bisa sedikit berbeda tergantung laptop.

## Dataset

Dataset dibuat dengan `src/data/make_data.py` dan disimpan dalam format JSON di folder `src/data`.

| File | Kapal | Kendaraan | Kegunaan |
| --- | --- | --- | --- |
| `kasus_1.json` | 1 kapal 8 × 8, kapasitas 22 | 13 kendaraan | Pengujian utama |
| `kasus_multi.json` | 2 kapal, 8 × 8 kapasitas 22 dan 6 × 8 kapasitas 16 | 20 kendaraan | Pengujian bonus multi-kapal |

Kendaraan terdiri dari empat jenis, yaitu motor, sedan, SUV, dan truk. Setiap kendaraan menyimpan id, lebar, panjang, berat, ShippingFee, dan ETA.

## Representasi State

State disimpan sebagai tuple yang berisi posisi setiap kendaraan dengan bentuk `(ship_idx, x, y, orientation)`. Isinya nomor kapal, koordinat pojok kendaraan di grid, dan orientasi `H` atau `V`. Kendaraan yang tidak diangkut ditulis sebagai `(-1, 0, 0, "H")`. Karena nomor kapal ikut disimpan, bentuk state yang sama langsung bisa dipakai untuk kasus multi-kapal.

Setiap state baru selalu diperiksa oleh fungsi `cek_placement` di `src/core.py`, jadi semua state yang diproses pasti valid.

## Objective Function

Objective utama adalah total ShippingFee dari kendaraan yang diangkut. Objective kedua adalah objective bonus berbasis ETA. Kendaraan dengan ETA paling lama 3 hari dianggap mendesak dan sebaiknya diletakkan di setengah geladak yang dekat dengan pintu masuk. Kalau kendaraan mendesak diletakkan di luar zona itu, ShippingFee-nya hanya dihitung setengah. Potongan ini cuma dipakai untuk menilai susunan, bukan mengubah biaya pengiriman yang sebenarnya.

## Struktur Repository

```
IF3070_G18_Triplets/
├── docs/                         laporan dalam format PDF
├── output/
│   ├── hc/                       hasil Hill-Climbing
│   ├── bonus_eta/                hasil Hill-Climbing dengan objective ETA
│   ├── sa/                       hasil Simulated Annealing
│   └── ga/                       hasil Genetic Algorithm dan eksperimen bonus GA
├── src/
│   ├── data/
│   │   ├── kasus_1.json
│   │   ├── kasus_multi.json
│   │   └── make_data.py
│   ├── core.py                   pembacaan data, constraint, objective function
│   ├── neighbor.py               initial state dan neighbor
│   ├── hill_climbing.py          keempat varian Hill-Climbing
│   ├── sa.py                     Simulated Annealing
│   ├── geneticalgorithm.py       Genetic Algorithm
│   ├── data_io.py                lokasi file data dan output
│   ├── visual.py                 gambar kapal dan grafik
│   ├── main.py                   program demo
│   ├── run_hill_climbing.py
│   ├── run_sa.py
│   ├── run_geneticalgorithm.py
│   └── run_visual.py
├── requirements.txt
└── README.md
```

## Pembagian Tugas

| Nama | NIM | Tugas |
| --- | --- | --- |
| Indah Ramadhani | 18224037 | Pemeriksaan constraint dan objective function, keempat varian Hill-Climbing beserta eksperimennya, bonus objective ETA |
| Tiara Clianta Andiwi | 18224078 | Initial state dan neighbor, Simulated Annealing beserta eksperimennya, bonus multi-kapal |
| Salsabila Shofiyah | 18224088 | Dataset, Genetic Algorithm beserta eksperimennya, visualisasi, program demo, pengelolaan repository |

Integrasi kode, pengujian, dan penyusunan laporan dikerjakan bersama oleh ketiga anggota.