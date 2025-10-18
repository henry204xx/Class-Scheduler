<br/>
<h1 align="center">Eksplorasi Implementasi Algoritma Hill Climbing, Simulated Annealing, dan Genetic dalam Problem Penjadwalan Kelas</h1>

<br/>

> Tugas Besar 1 IF3170 - Kecerdasan Buatan
> By Kelompok 23, Pendaki Handal - IF'23

<br/>

## Deskripsi
Repositori ini berisi implementasi berbagai algoritma local search untuk menyelesaikan masalah optimasi penjadwalan kuliah. Algoritma yang diimplementasikan meliputi:
- Hill Climbing (Steepest Ascent, Sideways Move, Random Restart, Stochastic)
- Simulated Annealing
- Genetic Algorithm

Program ini bertujuan untuk menemukan jadwal kuliah optimal yang meminimalkan konflik waktu mahasiswa dan dosen, memaksimalkan penggunaan kapasitas ruangan, serta mempertimbangkan prioritas mata kuliah.

<br/>

## Setup dan Cara Menjalankan Program

### Prerequisites
- Python 3.8 atau lebih tinggi
- pip (Python package manager)

### Instalasi Dependencies
```bash
pip install numpy matplotlib
```

### Menjalankan Program
1. Clone repository ini lalu arahkan ke root direktori:
```bash
git clone <repository-url>
cd Tubes1AI_PendakiHandal
```

2. Pada repositori ini sudah disiapkan beberapa test case, yaitu `tc1.json` hingga `tc5.json` dengan tingkat kesulitan yang semakin meningkat. Namun, jika Anda ingin membuat test case sendiri, silakan buat file `.json` dengan struktur berikut:
```json
{
  "kelas_mata_kuliah": [
    {
      "kode": "IF3071_K01",
      "jumlah_mahasiswa": 60,
      "sks": 3
    }
  ],
  "ruangan": [
    {
      "kode": "7609",
      "kuota": 60
    }
  ],
  "mahasiswa": [
    {
      "nim": "13523001",
      "daftar_mk": ["IF3071_K01", "IF3130_K01"],
      "prioritas": [1, 2]
    }
  ],
  "jadwal_dosen": [
    {
      "nama": "Bu Fariska",
      "mengajar": ["IF3071_K01"],
      "waktu_tidak_bisa": [["Senin", 9], ["Rabu", 13]]
    }
  ]
}
```
Penjelasan struktur:
- `kelas_mata_kuliah`: Array berisi mata kuliah dengan kode, jumlah mahasiswa, dan SKS
- `ruangan`: Array berisi ruangan dengan kode dan kuota kapasitas
- `mahasiswa`: Array berisi mahasiswa dengan NIM, daftar mata kuliah yang diambil, dan prioritas (1-7, dimana 1 = prioritas tertinggi)
- `jadwal_dosen`: Array berisi dosen dengan nama, mata kuliah yang diajar, dan waktu tidak tersedia (format: [["Hari", jam]])
  - Hari: "Senin", "Selasa", "Rabu", "Kamis", "Jumat"
  - Jam: 7-17 (jam kuliah yang tersedia)

3. Jalankan program utama:
```bash
python src/main.py
```

4. Ikuti alur input yang diminta oleh program
5. Jika program menampilkan window baru untuk menampilkan grafik analisis hasil plotting, tutup terlebih dahulu jendela tersebut untuk lanjut menggunakan program

<br/>

## Pembagian Tugas

| Nama | NIM | Tugas |
|------|-----|-------|
| 13523058 | Noumisyifa Nabila Nareswari | - Membangun kelas Jadwal<br/> - Menyusun algoritma Hill Climbing jenis Steepest Ascent, Sideways Move, dan Random Restart <br/> - Menyusun laporan |
| 13523072 | Sabilul Huda | - Menyusun algoritma genetik<br/> - Menyusun laporan|
| 13523108 | Henry Filberto Shinelo | - Menyusun algoritma Hill Climbing jenis Stochastic, simulated annealing<br/> -  Membuat main progra<br/> - Membantu membangun kelas Jadwal<br/> - Menyusun laporan |

