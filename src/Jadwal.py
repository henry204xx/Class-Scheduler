import json
import random
import numpy as np

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
        
        self.schedule = self.random_schedule()

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
        - Cell: Kode mata kuliah atau None
        """
        num_slots = 55  # 5 hari * 11 jam (7-17)
        num_ruangan = len(self.ruangan)
        schedule_matrix = np.full((num_slots, num_ruangan), "", dtype=object)
        
        pertemuan_assigned = {}
        
        for matkul in self.mata_kuliah:
            kode = matkul["kode"]
            sks = matkul["sks"]
            
            pertemuan_assigned[kode] = []
            
            for _ in range(sks):
                placed = False
                attempts = 0
                max_attempts = 1000
                
                while not placed and attempts < max_attempts:
                    slot = random.randint(0, num_slots - 1)
                    ruang_idx = random.randint(0, num_ruangan - 1)
                    
                    if schedule_matrix[slot, ruang_idx] == "":
                        schedule_matrix[slot, ruang_idx] = kode
                        hari, jam = self.slot_to_day_hour(slot)
                        pertemuan_assigned[kode].append({
                            "slot": slot,
                            "hari": hari,
                            "jam": jam,
                            "ruang": self.idx_to_ruangan[ruang_idx]
                        })
                        placed = True
                    
                    attempts += 1
                
                if not placed:
                    print(f"Warning: Tidak bisa menempatkan pertemuan untuk {kode} setelah {max_attempts} percobaan")
        
        return {
            "matrix": schedule_matrix,
            "pertemuan": pertemuan_assigned
        }
    
    def print_schedule(self):
        days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
        
        for ruang_idx, ruang in enumerate(self.ruangan):
            print(f"\n{'='*60}")
            print(f"Ruangan: {ruang['kode']} (Kapasitas: {ruang['kuota']})")
            print(f"{'='*60}")
            print(f"{'Jam':<5}", end="")
            for day in days:
                print(f"{day:<12}", end="")
            print()
            print("-" * 60)
            
            for jam in range(7, 18):
                print(f"{jam:<5}", end="")
                for hari in range(1, 6):
                    slot = self.day_hour_to_slot(hari, jam)
                    matkul = self.schedule["matrix"][slot, ruang_idx]
                    if matkul:
                        print(f"{matkul:<12}", end="")
                    else:
                        print(f"{'':<12}", end="")
                print()
                
    
    
    """
    the following adalah a bunch of helper methods yang gue gk tau bakal kepake or nah
    nanti kalo gk kepake apus aja
    """
    
    def get_matkul_schedule(self, kode_matkul):
        "Buat dapetin semua pertemuan untuk suatu mata kuliah" 
        return self.schedule["pertemuan"].get(kode_matkul, [])
    
    def get_cell(self, slot, ruang_idx):
        "Buat dapetin isi cell pada posisi tertentu"
        val = self.schedule["matrix"][slot, ruang_idx]
        if (val != ""): return val
        else: return None
    
    def set_cell(self, slot, ruang_idx, kode_matkul):
        "buat ngeset suatu cell"
        self.schedule["matrix"][slot, ruang_idx] = kode_matkul if kode_matkul else ""
    
    def get_empty_slots(self):
        "Buat dapetin semua slot kosong"
        empty_mask = self.schedule["matrix"] == ""
        empty_indices = np.argwhere(empty_mask)
        return empty_indices  # Returns array of pairs of [slot, ruang_idx] 
    
    def get_occupied_slots(self):
        "buat dapetin semua slot yang terisi"
        occupied_mask = self.schedule["matrix"] != ""
        occupied_indices = np.argwhere(occupied_mask)
        return occupied_indices  # Returns array of [slot, ruang_idx] pairs
    
    def swap_slots(self, slot1, ruang1, slot2, ruang2):
        "buat Swap dua slot"
        temp = self.schedule["matrix"][slot1, ruang1].copy()
        self.schedule["matrix"][slot1, ruang1] = self.schedule["matrix"][slot2, ruang2]
        self.schedule["matrix"][slot2, ruang2] = temp
    
    def copy_schedule(self):
        "Buat dapetin copy of the schedule"
        return self.schedule["matrix"].copy()
