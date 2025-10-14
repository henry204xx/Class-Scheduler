import json
import random
import numpy as np
import copy

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
        
        self.schedule_matrix = np.empty((num_slots, num_ruangan), dtype=object)
        for i in range(num_slots):
            for j in range(num_ruangan):
                self.schedule_matrix[i, j] = []
        
        self.schedule_matkul = {}
        
        for matkul in self.mata_kuliah:
            kode = matkul["kode"]
            sks = matkul["sks"]
            
            self.schedule_matkul[kode] = []
            
            for _ in range(sks):
                slot = random.randint(0, num_slots - 1)
                ruang_idx = random.randint(0, num_ruangan - 1)
                
                # Append mata kuliah ke cell
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
        days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
        
        for ruang_idx, ruang in enumerate(self.ruangan):
            print(f"\n{'='*100}")
            print(f"Ruangan: {ruang['kode']} (Kapasitas: {ruang['kuota']})")
            print(f"{'='*100}")
            print(f"{'Jam':<5}", end="")
            for day in days:
                print(f"{day:<19}", end="")
            print()
            print("-" * 100)
            
            for jam in range(7, 18):
                print(f"{jam:<5}", end="")
                for hari in range(1, 6):
                    slot = self.day_hour_to_slot(hari, jam)
                    matkul_list = self.schedule_matrix[slot, ruang_idx]
                    
                    if len(matkul_list) == 0:
                        print(f"{'':<19}", end="")
                    elif len(matkul_list) == 1:
                        print(f"{matkul_list[0]:<19}", end="")
                    else:
                        print(f"[{len(matkul_list)} matkul]    ", end="")
                print()
            
            print("\nMatkul yang tabrakan di ruangan ini:")
            has_conflict = False
            for jam in range(7, 18):
                for hari in range(1, 6):
                    slot = self.day_hour_to_slot(hari, jam)
                    matkul_list = self.schedule_matrix[slot, ruang_idx]
                    if len(matkul_list) > 1:
                        has_conflict = True
                        hari_name = days[hari-1]
                        print(f"  {hari_name} jam {jam}: {', '.join(matkul_list)}")
            if not has_conflict:
                print("  No matkul tabrakan!")
    
    
    """
    
    OBJECTIVE FUNCTIONS RELATED METHODS
    
    """
    
    "TODO: blm di weghted kalau emg perlu"
    
    def get_objective_func_value_print(self):
        print('\n\n============================================')
        objf_mhs = self.objf_waktu_konflik_mhs()
        objf_r = self.objf_kapasitas_ruang()
        objf_dsn = self.objf_waktu_konflik_dosen()
        objf_p = self.objf_prioritas()
        print("waktu konflik mhs: ", objf_mhs)
        print("waktu konflik ruang: ", objf_r)
        print("waktu konflik dsn: ", objf_dsn)
        print("waktu konflik prioritas: ", objf_p)
        print("konflik total: ", objf_p + objf_r + objf_dsn + objf_mhs)
        return -(objf_mhs + objf_dsn + objf_p + objf_r)
    
    def get_objective_func_value(self):
        objf_mhs = self.objf_waktu_konflik_mhs()
        objf_r = self.objf_kapasitas_ruang()
        objf_dsn = self.objf_waktu_konflik_dosen()
        objf_p = self.objf_prioritas()
        return -(objf_mhs + objf_dsn + objf_p + objf_r)
    
    def objf_waktu_konflik_mhs(self):
        """
        Hitung total jumlah konflik waktu yang dialami semua mahasiswa.
        
        Returns:
            int: Total jumlah konflik waktu untuk semua mahasiswa
                 Lower is better (0 = no konflik)
        """
        sum_konflik = 0
        
        for mhs in self.mahasiswa:
            matkul_list = mhs.get("daftar_mk", [])
            slot_occupation = {}
            
            for kode_matkul in matkul_list:
                pertemuan_list = self.schedule_matkul.get(kode_matkul, [])
                
                for pertemuan in pertemuan_list:
                    slot = pertemuan["slot"]
                    
                    if slot not in slot_occupation:
                        slot_occupation[slot] = []
                    
                    slot_occupation[slot].append(kode_matkul)
            
            for slot, matkul_di_slot in slot_occupation.items():
                unique_matkul_di_slot = set(matkul_di_slot)
                n = len(unique_matkul_di_slot)
                if n > 1:
                    konflik_di_slot = n * (n - 1) // 2
                    sum_konflik += konflik_di_slot
        
        return sum_konflik

    def objf_waktu_konflik_dosen(self):
        """
        Hitung total jumlah konflik waktu yang dialami semua dosen.
        
        Returns:
            int: Total jumlah konflik waktu untuk semua mahasiswa
                 Lower is better (0 = no konflik)
        """
        sum_konflik = 0
        
        for dsn in self.dosen:
            matkul_list = dsn.get("mengajar", [])
            unavailable_slots = set(self.get_dosen_unavailable_slots(dsn["nama"]))
            slot_occupation = {}
            
            for kode_matkul in matkul_list:
                pertemuan_list = self.schedule_matkul.get(kode_matkul, [])
                
                for pertemuan in pertemuan_list:
                    slot = pertemuan["slot"]
                    
                    if slot in unavailable_slots:
                        sum_konflik += 1
                    
                    slot_occupation.setdefault(slot, []).append(kode_matkul)
            
            for slot, matkul_di_slot in slot_occupation.items():
                unique_matkul_di_slot = set(matkul_di_slot)
                n = len(unique_matkul_di_slot)
                if n > 1:
                    konflik_di_slot = n * (n - 1) // 2
                    sum_konflik += konflik_di_slot
        
        return sum_konflik



    "TODO: ini interpretasi gue bener kan ya? jadi per pertemuan bentrok memang dikali n sks?"
    
    def objf_kapasitas_ruang(self):
        """
        Hitung total ((jumlah_mhs_per_matkul - kapasitas_ruang) * sks_matkul) 
        when jumlah_mhs_per_matkul > kapasitas_ruang
        
        Returns:
            int: Total selisih kapasitas dengan jumlah mhs di kelas * sks
        """
        end_value = 0
        for mk_dict in self.mata_kuliah:
            kode = mk_dict.get('kode')
            n_mhs = mk_dict.get('jumlah_mahasiswa', 0)
            sks = mk_dict.get('sks', 0)
            
            pertemuan_list = self.schedule_matkul.get(kode, [])
            for pertemuan in pertemuan_list:
                kode_ruang = pertemuan.get('ruang', None)
                ruang_dict = next((r for r in self.ruangan if r["kode"] == kode_ruang), None)
                
                if ruang_dict:
                    kuota = ruang_dict.get('kuota', 0)                
                    if(n_mhs> kuota):
                        end_value += (n_mhs - kuota)
                        
        return end_value
    
    
    def objf_prioritas(self):
        """
        Jika ada matkul pada ruang dan jadwal yang sama, per pertemuan di dalam 1 ruang yang bentrok,
        hitung sum of (bobot_prioritas_x * n_mahasiswa_prioritas_x) lalu hitung sum untuk semua pertemuan
        yang bentrok di satu ruangan.
        
        Returns:
            int: Obj function prioritas
        
        """
        
        prioritas_bobot = {
            1: 1.75,
            2: 1.5,
            3: 1.25,
            4: 1,
            5: 0.75,
            6: 0.5,
            7: 0.25
        }
        
        value = 0
        
        conflict_slots = self.get_conflict_slots()
        for slot, ruang_idx in conflict_slots:
        
            list_kode_matkul = self.get_cell(slot= slot, ruang_idx= ruang_idx)
            for kode_matkul in list_kode_matkul:
                
                for mahasiswa_dict in self.mahasiswa:
                    mks = mahasiswa_dict.get("daftar_mk", [])
                    prioritas_list = mahasiswa_dict.get("prioritas", [])
                    
                    if kode_matkul in mks: 
                        idx_pos = mks.index(kode_matkul)
                        value += prioritas_bobot.get(prioritas_list[idx_pos], 0)
        
        return value
    
    
    
    
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

    def get_neighbors(self):
        """
        Generate semua neighbor dari current_state.

        Dengan move antara:
        1. Swap 2 matkul.
        2. Pindahkan 1 matkul ke empty slot.

        Returns:
            list[Jadwal]: List of Jadwal objects.
        """
        neighbors = []
        occupied = self.get_occupied_slots()
        empty = self.get_empty_slots()

        # === 1. SWAP 2 MATA KULIAH ===
        for idx1 in range(len(occupied)):
            for idx2 in range(idx1 + 1, len(occupied)):
                slot1, ruang1 = occupied[idx1]
                slot2, ruang2 = occupied[idx2]

                if len(self.schedule_matrix[slot1, ruang1]) > 0 and len(self.schedule_matrix[slot2, ruang2]) > 0:
                    # ambil 1 matkul dari dua slot berbeda
                    mk1 = self.schedule_matrix[slot1, ruang1][0]
                    mk2 = self.schedule_matrix[slot2, ruang2][0]

                    new_jadwal = copy.deepcopy(self)

                    # swap
                    new_jadwal.remove_from_cell(slot1, ruang1, mk1)
                    new_jadwal.remove_from_cell(slot2, ruang2, mk2)
                    new_jadwal.add_to_cell(slot1, ruang1, mk2)
                    new_jadwal.add_to_cell(slot2, ruang2, mk1)

                    # Update schedule_matkul
                    for p in new_jadwal.schedule_matkul[mk1]:
                        if p["slot"] == slot1 and p["ruang_idx"] == ruang1:
                            p["slot"], p["ruang_idx"], p["ruang"] = slot2, ruang2, new_jadwal.idx_to_ruangan[ruang2]
                            p["hari"], p["jam"] = new_jadwal.slot_to_day_hour(slot2)
                    for p in new_jadwal.schedule_matkul[mk2]:
                        if p["slot"] == slot2 and p["ruang_idx"] == ruang2:
                            p["slot"], p["ruang_idx"], p["ruang"] = slot1, ruang1, new_jadwal.idx_to_ruangan[ruang1]
                            p["hari"], p["jam"] = new_jadwal.slot_to_day_hour(slot1)

                    neighbors.append(new_jadwal)

        # === 2. MOVE 1 MATKUL KE EMPTY SLOT ===
        for occ in occupied:
            slot_occ, ruang_occ = occ
            if len(self.schedule_matrix[slot_occ, ruang_occ]) == 0:
                continue

            for mk in self.schedule_matrix[slot_occ, ruang_occ]:
                for emp in empty:
                    slot_emp, ruang_emp = emp
                    new_jadwal = copy.deepcopy(self)

                    # Move matkul ke cell kosong
                    new_jadwal.remove_from_cell(slot_occ, ruang_occ, mk)
                    new_jadwal.add_to_cell(slot_emp, ruang_emp, mk)

                    # Update schedule_matkul
                    for p in new_jadwal.schedule_matkul[mk]:
                        if p["slot"] == slot_occ and p["ruang_idx"] == ruang_occ:
                            p["slot"], p["ruang_idx"], p["ruang"] = slot_emp, ruang_emp, new_jadwal.idx_to_ruangan[ruang_emp]
                            p["hari"], p["jam"] = new_jadwal.slot_to_day_hour(slot_emp)

                    neighbors.append(new_jadwal)

        return neighbors


    def get_random_neighbor(self):
        """
        Generate 1 random neighbor dari current state.
        """
        new_jadwal = copy.deepcopy(self) 

        occupied_slot = self.get_occupied_slots()
        empty_slot = self.get_empty_slots()

        if len(occupied_slot) < 1:
            return new_jadwal

        # choice action
        action_type = random.choice(["swap", "move"])

        # === 1. Action: Swap ===
        if action_type == "swap" and len(occupied_slot) >= 2:
            occupied_slot_list = list(occupied_slot)
            if len(occupied_slot_list) >= 2:
                (slot1, ruang1), (slot2, ruang2) = random.sample(occupied_slot_list, 2)
            else:
                return self  # tidak ada cukup elemen untuk swap, kembalikan diri sendiri

            mk1 = self.schedule_matrix[slot1, ruang1][0]
            mk2 = self.schedule_matrix[slot2, ruang2][0]

            # swap
            new_jadwal.remove_from_cell(slot1, ruang1, mk1)
            new_jadwal.remove_from_cell(slot2, ruang2, mk2)
            new_jadwal.add_to_cell(slot1, ruang1, mk2)
            new_jadwal.add_to_cell(slot2, ruang2, mk1)

            # Update
            for mk, (old_slot, old_ruang, new_slot, new_ruang) in [
                (mk1, (slot1, ruang1, slot2, ruang2)),
                (mk2, (slot2, ruang2, slot1, ruang1))
            ]:
                for p in new_jadwal.schedule_matkul[mk]:
                    if p["slot"] == old_slot and p["ruang_idx"] == old_ruang:
                        p["slot"] = new_slot
                        p["ruang_idx"] = new_ruang
                        p["ruang"] = new_jadwal.idx_to_ruangan[new_ruang]
                        p["hari"], p["jam"] = new_jadwal.slot_to_day_hour(new_slot)

        # === 2. Pindah 1 matkul ke empty slot ===
        elif action_type == "move" and len(empty_slot) > 0:
            slot_from, ruang_from = random.choice(occupied_slot)
            slot_to, ruang_to = random.choice(empty_slot)

            if len(self.schedule_matrix[slot_from, ruang_from]) > 0:
                mk = self.schedule_matrix[slot_from, ruang_from][0]

                new_jadwal.remove_from_cell(slot_from, ruang_from, mk)
                new_jadwal.add_to_cell(slot_to, ruang_to, mk)

                for p in new_jadwal.schedule_matkul[mk]:
                    if p["slot"] == slot_from and p["ruang_idx"] == ruang_from:
                        p["slot"] = slot_to
                        p["ruang_idx"] = ruang_to
                        p["ruang"] = new_jadwal.idx_to_ruangan[ruang_to]
                        p["hari"], p["jam"] = new_jadwal.slot_to_day_hour(slot_to)

        return new_jadwal

    def get_best_neighbor(self):
        
        """
        Return one Jadwal neighbor that has the best objective function
        """
        best_neighbor = None
        best_value = float('-inf')
        
        
        for neighbor in self.get_neighbors():
            cur_objf_neighbor = neighbor.get_objective_func_value()
            if cur_objf_neighbor > best_value:
                best_neighbor = neighbor
                best_value = cur_objf_neighbor
        
        return best_neighbor if best_neighbor else self
    

    def save_schedule_table(self, filename="jadwal_table.txt"):
        """
        Save the schedule in a text file.
        """
        if not filename.lower().endswith(".txt"):
            filename += ".txt"
            
        days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
        times = list(range(7, 18))  # 7–17

        with open(filename, "w", encoding="utf-8") as f:
            # Iterate through each room
            for ruang_idx, ruang in enumerate(self.ruangan):
                ruang_kode = ruang["kode"]
                kapasitas = ruang["kuota"]
                f.write("=" * 100 + "\n")
                f.write(f"Ruangan: {ruang_kode} (Kapasitas: {kapasitas})\n")
                f.write("=" * 100 + "\n")
                f.write(f"{'Jam':<4} {'Senin':<18} {'Selasa':<18} {'Rabu':<18} {'Kamis':<18} {'Jumat':<18}\n")
                f.write("-" * 100 + "\n")

                for jam in times:
                    row = [str(jam)]
                    for hari_idx in range(5):  # 0-4 for Senin-Jumat
                        slot = hari_idx * 11 + (jam - 7)
                        matkul_in_slot = self.schedule_matrix[slot, ruang_idx]
                        
                        if len(matkul_in_slot) == 0:
                            # Empty slot
                            row.append("")
                        elif len(matkul_in_slot) == 1:
                            # Single course
                            row.append(matkul_in_slot[0])
                        else:
                            # Multiple courses (conflict)
                            row.append(f"[{len(matkul_in_slot)} matkul]")
                    
                    # Write the row for this time slot
                    f.write(f"{row[0]:<4} {row[1]:<18} {row[2]:<18} {row[3]:<18} {row[4]:<18} {row[5]:<18}\n")

                # Add conflict information for this room
                has_conflict = False
                for jam in times:
                    for hari_idx in range(5):
                        slot = hari_idx * 11 + (jam - 7)
                        matkul_list = self.schedule_matrix[slot, ruang_idx]
                        if len(matkul_list) > 1:
                            has_conflict = True
                            hari_name = days[hari_idx]
                            f.write(f"  {hari_name} jam {jam}: {', '.join(matkul_list)}\n")
                
                f.write("\n" + "=" * 100 + "\n\n")

        print(f"Jadwal berhasil disimpan dalam format tabel ke '{filename}'")

            

    def validate_schedule(self):
        """
        Check if this schedule has any conflicts.
        Conditions checked:
            1. Two or more matkul in the same room and same time.
            2. A student attends two classes at the same time.
            3. A lecturer teaches two classes at the same time or at unavailable time.
            4. Room capacity is smaller than number of students in that class.

        Prints detected problems and returns True if schedule is valid (no conflict),
        otherwise False.
        """
        print("\n=== VALIDATION REPORT ===")
        valid = True

        # 1. Room conflicts
        for slot in range(self.schedule_matrix.shape[0]):
            hari, jam = self.slot_to_day_hour(slot)
            for ruang_idx, ruang in enumerate(self.ruangan):
                matkul_list = self.schedule_matrix[slot, ruang_idx]
                if len(matkul_list) > 1:
                    valid = False
                    print(f"[ROOM CONFLICT] {ruang['kode']} at hari {hari}, jam {jam}: {', '.join(matkul_list)}")

        # 2. Student conflicts
        for mhs in self.mahasiswa:
            nim = mhs["nim"]
            matkul_list = mhs["daftar_mk"]
            slot_occupation = {}

            for kode in matkul_list:
                for p in self.schedule_matkul.get(kode, []):
                    slot = p["slot"]
                    slot_occupation.setdefault(slot, set()).add(kode)  

            for slot, codes in slot_occupation.items():
                if len(codes) > 1:
                    valid = False
                    hari, jam = self.slot_to_day_hour(slot)
                    print(f"[STUDENT CONFLICT] Mahasiswa {nim} has {', '.join(sorted(codes))} at hari {hari}, jam {jam}")

        # 3. Lecturer conflicts + unavailable time
        for dsn in self.dosen:
            nama = dsn["nama"]
            mengajar = dsn.get("mengajar", [])
            unavailable = set(self.get_dosen_unavailable_slots(nama))
            slot_occupation = {}

            for kode in mengajar:
                for p in self.schedule_matkul.get(kode, []):
                    slot = p["slot"]
                    if slot in unavailable:
                        valid = False
                        hari, jam = self.slot_to_day_hour(slot)
                        print(f"[LECTURER UNAVAILABLE] {nama} teaches {kode} at unavailable time (hari {hari}, jam {jam})")

                    slot_occupation.setdefault(slot, set()).add(kode) 

            for slot, codes in slot_occupation.items():
                if len(codes) > 1:
                    valid = False
                    hari, jam = self.slot_to_day_hour(slot)
                    print(f"[LECTURER CONFLICT] {nama} teaches {', '.join(sorted(codes))} at hari {hari}, jam {jam}")

        # 4. Room capacity
        for mk in self.mata_kuliah:
            kode = mk["kode"]
            n_mhs = mk["jumlah_mahasiswa"]
            for p in self.schedule_matkul.get(kode, []):
                ruang_kode = p["ruang"]
                ruang_dict = next((r for r in self.ruangan if r["kode"] == ruang_kode), None)
                if ruang_dict and n_mhs > ruang_dict["kuota"]:
                    valid = False
                    print(f"[ROOM CAPACITY] {kode} has {n_mhs} students, exceeds {ruang_kode}'s capacity {ruang_dict['kuota']}")

        if valid:
            print("Schedule is valid — no conflicts detected.")
        else:
            print("Schedule has conflicts (see above).")

        return valid
    

    def debug_objective_components(self):
        objf_mhs = self.objf_waktu_konflik_mhs()
        objf_r = self.objf_kapasitas_ruang()
        objf_dsn = self.objf_waktu_konflik_dosen()
        objf_p = self.objf_prioritas()
        
        print(f"DEBUG - Room Capacity Violations: {objf_r}")
        print(f"DEBUG - Student Conflicts: {objf_mhs}")
        print(f"DEBUG - Lecturer Conflicts: {objf_dsn}")
        print(f"DEBUG - Priority Conflicts: {objf_p}")
        print(f"DEBUG - Total Raw: {objf_mhs + objf_dsn + objf_p + objf_r}")
        
        return objf_mhs, objf_r, objf_dsn, objf_p
    

    def debug_student_conflicts(self):
        print("\n=== DEBUG STUDENT CONFLICTS ===")
        
        for mhs in self.mahasiswa:
            nim = mhs["nim"]
            matkul_list = mhs.get("daftar_mk", [])
            slot_occupation = {}
            
            for kode_matkul in matkul_list:
                pertemuan_list = self.schedule_matkul.get(kode_matkul, [])
                for pertemuan in pertemuan_list:
                    slot = pertemuan["slot"]
                    if slot not in slot_occupation:
                        slot_occupation[slot] = []
                    slot_occupation[slot].append({
                        'kode': kode_matkul,
                        'ruang': pertemuan['ruang'],
                        'hari': pertemuan['hari'], 
                        'jam': pertemuan['jam']
                    })
            
            conflicts_found = False
            for slot, courses in slot_occupation.items():
                unique_codes = set(c['kode'] for c in courses)
                if len(unique_codes) > 1:
                    conflicts_found = True
                    print(f"Student {nim} conflict at:")
                    for course in courses:
                        print(f"  - {course['kode']} in {course['ruang']} (hari {course['hari']}, jam {course['jam']})")
            
            if not conflicts_found:
                print(f"Student {nim}: No conflicts")

    def debug_lecturer_conflicts(self):
        print("\n=== DEBUG LECTURER CONFLICTS ===")
        
        for dsn in self.dosen:
            nama = dsn["nama"]
            matkul_list = dsn.get("mengajar", [])
            unavailable_slots = set(self.get_dosen_unavailable_slots(nama))
            slot_occupation = {}
            
            for kode_matkul in matkul_list:
                pertemuan_list = self.schedule_matkul.get(kode_matkul, [])
                for pertemuan in pertemuan_list:
                    slot = pertemuan["slot"]
                    if slot not in slot_occupation:
                        slot_occupation[slot] = []
                    slot_occupation[slot].append({
                        'kode': kode_matkul,
                        'ruang': pertemuan['ruang'],
                        'hari': pertemuan['hari'],
                        'jam': pertemuan['jam']
                    })
            
            conflicts_found = False
            for slot, courses in slot_occupation.items():
                unique_codes = set(c['kode'] for c in courses)
                if len(unique_codes) > 1:
                    conflicts_found = True
                    print(f"Lecturer {nama} TEACHING CONFLICT at:")
                    for course in courses:
                        print(f"  - {course['kode']} in {course['ruang']} (hari {course['hari']}, jam {course['jam']})")
            
            unavailable_conflicts = False
            for kode_matkul in matkul_list:
                pertemuan_list = self.schedule_matkul.get(kode_matkul, [])
                for pertemuan in pertemuan_list:
                    slot = pertemuan["slot"]
                    if slot in unavailable_slots:
                        unavailable_conflicts = True
                        hari, jam = self.slot_to_day_hour(slot)
                        print(f"Lecturer {nama} UNAVAILABLE CONFLICT:")
                        print(f"  - {kode_matkul} in {pertemuan['ruang']} at unavailable time (hari {hari}, jam {jam})")
            
            if not conflicts_found and not unavailable_conflicts:
                print(f"Lecturer {nama}: No conflicts")