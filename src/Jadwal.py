import json
import random
import numpy as np

from utils import hari_string_to_number

class Jadwal:
    def __init__(self, json_name: str):
        path_to_json = '../tests/' + json_name
        with open(path_to_json, "r") as f:
            data = json.load(f)

        self.mata_kuliah = data.get("kelas_mata_kuliah", [])
        
        # Sort ruangan based on kuota descending
        self.ruangan = sorted(data.get("ruangan", []), key=lambda x: x["kuota"], reverse=True)
        self.mahasiswa = data.get("mahasiswa", [])
        self.dosen = data.get("jadwal_dosen", []) 
        
        # Buat mapping ruangan ke index kolom
        self.ruangan_to_idx = {ruang["kode"]: idx for idx, ruang in enumerate(self.ruangan)}
        self.idx_to_ruangan = {idx: ruang["kode"] for idx, ruang in enumerate(self.ruangan)}
        
        self.schedule_matrix = None  # Matrix 55 x num_ruangan, cell berisi list of matkul
        self.schedule_matkul = {}    # Dict: kode_matkul -> list of pertemuan
        self.random_schedule()

    def print_attr(self):
        print(f"mata kuliah: {self.mata_kuliah}")
        print(f"ruangan: {self.ruangan}")
        print(f"mahasiswa: {self.mahasiswa}")
        print(f"dosen: {self.dosen}")
    
    def slot_to_day_hour(self, slot):
        """Konversi slot (0-54) ke (hari, jam)"""
        hari = (slot // 11) + 1  # 1=Senin, 2=Selasa, ..., 5=Jumat
        jam = (slot % 11) + 7     # 7-17
        return hari, jam
    
    def day_hour_to_slot(self, hari, jam):
        """Konversi (hari, jam) ke slot (0-54)"""
        return (hari - 1) * 11 + (jam - 7)
    
    def random_schedule(self):
        """
        Membuat jadwal random dalam bentuk matrix:
        - Row: 55 slot waktu (Senin jam 7 = 0, ..., Jumat jam 17 = 54)
        - Col: Jumlah ruangan
        - Cell: List of kode mata kuliah (bisa lebih dari 1 untuk konflik)
        
        Returns: None (langsung ubah self.schedule_matrix and self.schedule_matkul)
        
        """
        num_slots = 55  # 5 hari * 11 jam (7-17)
        num_ruangan = len(self.ruangan)
        self.schedule_matrix = np.array([[[] for _ in range(num_ruangan)] for _ in range(num_slots)], dtype=object)
        
        self.schedule_matkul = {}
        
        for matkul in self.mata_kuliah:
            kode = matkul["kode"]
            sks = matkul["sks"]
            
            self.schedule_matkul[kode] = []
            
            for _ in range(sks):
                slot = random.randint(0, num_slots - 1)
                ruang_idx = random.randint(0, num_ruangan - 1)
                
                self.schedule_matrix[slot, ruang_idx].append(kode)
                
                hari, jam = self.slot_to_day_hour(slot)
                self.schedule_matkul[kode].append({
                    "slot": slot,
                    "hari": hari,
                    "jam": jam,
                    "ruang": self.idx_to_ruangan[ruang_idx],
                    "ruang_idx": ruang_idx
                })
    
    def print_schedule(self):
        """Cetak jadwal dalam format yang mudah dibaca"""
        days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
        
        for ruang_idx, ruang in enumerate(self.ruangan):
            print(f"\n{'='*80}")
            print(f"Ruangan: {ruang['kode']} (Kapasitas: {ruang['kuota']})")
            print(f"{'='*80}")
            print(f"{'Jam':<5}", end="")
            for day in days:
                print(f"{day:<15}", end="")
            print()
            print("-" * 80)
            
            for jam in range(7, 18):
                print(f"{jam:<5}", end="")
                for hari in range(1, 6):
                    slot = self.day_hour_to_slot(hari, jam)
                    matkul_list = self.schedule_matrix[slot, ruang_idx]
                    if len(matkul_list) > 0:
                        matkul_str = ",".join(matkul_list)
                        if len(matkul_str) > 13:
                            matkul_str = matkul_str[:10] + "..."
                        print(f"{matkul_str:<15}", end="")
                    else:
                        print(f"{'':<15}", end="")
                print()
                
    
    
    """
    the followings are a bunch of helper methods yang gue gk tau bakal kepake or nah
    nanti kalo gk kepake apus aja
    """
    
    def get_matkul_schedule(self, kode_matkul):
        """
        
        Buat dapetin semua pertemuan untuk suatu mata kuliah
        
        Args: 
            kode_matkul (str): Kode mata kuliah (e.g., "IF3071_K01")
        
        Returns: 
            list: List of dict, setiap dict berisi info pertemuan:
                  - slot (int): Index slot waktu
                  - hari (int): Hari (1-5)
                  - jam (int): Jam mulai (7-17)
                  - ruang (str): Kode ruangan
                  - ruang_idx (int): Index ruangan
        
        """ 
        return self.schedule_matkul.get(kode_matkul, [])
    
    def get_cell(self, slot, ruang_idx):
        """
        Dapatkan isi cell pada posisi tertentu.
        
        Args:
            slot (int): Index slot waktu (0-54)
            ruang_idx (int): Index ruangan (0 - num_ruangan-1)
        
        Returns:
            list: List of str berisi kode matkul yang ada di cell tsb
        """
        return self.schedule_matrix[slot, ruang_idx]
    
    def set_cell(self, slot, ruang_idx, kode_matkul_list):
        """
        Set isi cell pada posisi tertentu.
        
        Args:
            slot (int): Index slot waktu (0-54)
            ruang_idx (int): Index ruangan (0 - num_ruangan-1)
            kode_matkul_list (list or str): List kode matkul
        
        Returns: None
        
        """
        if not isinstance(kode_matkul_list, list):
            kode_matkul_list = [kode_matkul_list] if kode_matkul_list else []
        self.schedule_matrix[slot, ruang_idx] = kode_matkul_list
        
    def add_to_cell(self, slot, ruang_idx, kode_matkul):
        """
        Tambah mata kuliah ke cell (append ke list di dalm cell).
        
        Args:
            slot (int): Index slot waktu (0-54)
            ruang_idx (int): Index ruangan (0 - num_ruangan-1)
            kode_matkul (str): Kode mata kuliah yang akan ditambahkan
        
        Returns: None
        """
        self.schedule_matrix[slot, ruang_idx].append(kode_matkul)

    def remove_from_cell(self, slot, ruang_idx, kode_matkul):
        """
        Hapus mata kuliah dari cell.
        
        Args:
            slot (int): Index slot waktu (0-54)
            ruang_idx (int): Index ruangan (0 - num_ruangan-1)
            kode_matkul (str): Kode mata kuliah yang akan dihapus
        
        Returns: None (hapus dari list jika ada, gk error kalau gk ada)
        """

        if kode_matkul in self.schedule_matrix[slot, ruang_idx]:
            self.schedule_matrix[slot, ruang_idx].remove(kode_matkul)
    

    def get_empty_slots(self):
        """
        Return semua slot kosong (gk ada matkul sama sekali).
        
        Args: None
        
        Returns:
            ndarray: Array of shape (N, 2) where each row adalah [slot, ruang_idx]
                     Return array kosong shape (0, 2) jika tidak ada slot kosong
        """
        empty_indices = []
        for i in range(self.schedule_matrix.shape[0]):
            for j in range(self.schedule_matrix.shape[1]):
                if len(self.schedule_matrix[i, j]) == 0:
                    empty_indices.append([i, j])
        return np.array(empty_indices) if empty_indices else np.array([]).reshape(0, 2)
    
    def get_occupied_slots(self):
        """
        Dapatkan semua slot yang terisi (ada mata kuliah listed in it).
        
        Args: None
        
        Returns:
            ndarray: Array of shape (N, 2) dimana setiap row adalah [slot, ruang_idx]
                     Return array kosong shape (0, 2) jika semua slot kosong
        """
        occupied_indices = []
        for i in range(self.schedule_matrix.shape[0]):
            for j in range(self.schedule_matrix.shape[1]):
                if len(self.schedule_matrix[i, j]) > 0:
                    occupied_indices.append([i, j])
        return np.array(occupied_indices) if occupied_indices else np.array([]).reshape(0, 2)

    def get_conflict_slots(self):
        """
        Dapatkan semua slot yang konflik (lebih dari 1 mata kuliah di cell yang sama).
        
        Args: None
        
        Returns:
            ndarray: Array of shape (N, 2) dimana setiap row adalah [slot, ruang_idx]
                     Return array kosong shape (0, 2) jika tidak ada konflik
        """
        conflict_indices = []
        for i in range(self.schedule_matrix.shape[0]):
            for j in range(self.schedule_matrix.shape[1]):
                if len(self.schedule_matrix[i, j]) > 1:
                    conflict_indices.append([i, j])
        return np.array(conflict_indices) if conflict_indices else np.array([]).reshape(0, 2)
    
    def swap_slots(self, slot1, ruang1, slot2, ruang2):
        """
        Swap isi dua slot.
        
        Args:
            slot1 (int): Index slot pertama (0-54)
            ruang1 (int): Index ruangan pertama
            slot2 (int): Index slot kedua (0-54)
            ruang2 (int): Index ruangan kedua
        
        Returns: None (swap in-place)
        """
        temp = self.schedule_matrix[slot1, ruang1].copy()
        self.schedule_matrix[slot1, ruang1] = self.schedule_matrix[slot2, ruang2].copy()
        self.schedule_matrix[slot2, ruang2] = temp
    
    def copy_schedule(self):
        "Buat dapetin copy of the schedule, returns self.schedule_matrix which ndarray"
        new_matrix = np.empty_like(self.schedule_matrix)
        for i in range(new_matrix.shape[0]):
            for j in range(new_matrix.shape[1]):
                new_matrix[i, j] = self.schedule_matrix[i, j].copy()
        return new_matrix

    
    def get_dosen_unavailable_slots(self, nama_dosen):
        """
        Dapatkan semua slot yang tidak bisa diisi untuk dosen tertentu.
        
        Args:
            nama_dosen (str): Nama dosen (e.g., "Bu Fariska")
        
        Returns:
            list: List of int berisi slot yang tidak tersedia untuk dosen tersebut
                  Return list kosong jika dosen tidak ditemukan atau tidak ada waktu tidak bisa
        """
        for dosen in self.dosen:
            if dosen["nama"] == nama_dosen:
                slots = []
                for waktu in dosen["waktu_tidak_bisa"]:
                    hari_num = hari_string_to_number(waktu[0])
                    jam = waktu[1]
                    slot = self.day_hour_to_slot(hari_num, jam)
                    slots.append(slot)
                return slots
        return []

    def get_dosen_for_matkul(self, kode_matkul):
        """
        Dapatkan nama dosen yang mengajar mata kuliah tertentu.
        
        Args:
            kode_matkul (str): Kode mata kuliah (e.g., "IF3071_K01")
        
        Returns:
            str or None: Nama dosen yang mengajar, atau None jika tidak ditemukan
        """
        for dosen in self.dosen:
            if kode_matkul in dosen["mengajar"]:
                return dosen["nama"]
        return None
