# =======================================================
# KALAU ADA YANG DIRASA KURENG PLS GANTI AJA GK APA APA
# =======================================================

import json
import random

class PenjadwalanKelas:
    def __init__(self, json_name: str):
        path_to_json = '../tests/' + json_name
        with open(path_to_json, "r") as f:
            data = json.load(f)

        self.mata_kuliah = data.get("kelas_mata_kuliah", [])
        self.ruangan = data.get("ruangan", [])
        self.mahasiswa = data.get("mahasiswa", [])
        self.dosen = data.get("jadwal_dosen", []) 
        self.schedule = self.random_schedule()
        # print(self.schedule)

    def print_attr(self):
        print(f"mata kuliah: {self.mata_kuliah}")
        print(f"ruangan: {self.ruangan}")
        print(f"mahasiswa: {self.mahasiswa}")
        print(f"dosen: {self.dosen}")
        
        
    def random_schedule(self):
        matkul = sorted(
            self.mata_kuliah,
            key=lambda x: ( x["sks"], x["jumlah_mahasiswa"]),
            reverse=True
        )
        result = {}
        jadwal_terpakai = set() #nanti diisi array (x, y) dengan x angka hari 1..5 dan y angka jam mulai 7..17
        
        for cur_matkul in matkul:
            valid_ruang = [ruang for ruang in self.ruangan if ruang["kuota"] >= cur_matkul["jumlah_mahasiswa"]]
            
            if not(valid_ruang):
                print(f"Tidak ada ruangan valid untuk {cur_matkul['kode']}")
                return False
            
            # print(f"{cur_matkul["kode"]} bisa di ruang: {valid_ruang}")
            
            ruang_idx = random.randint(0, len(valid_ruang)-1)
            ruang_choosen = valid_ruang[ruang_idx]
            
            while True:
                hari = random.randint(1, 5)  # 1=senin ... 5=jumat
                jam_mulai = random.randint(7, 17 - cur_matkul["sks"] + 1)

                slots = {(hari, jam_mulai + offset) for offset in range(cur_matkul["sks"])}

                if not (slots & jadwal_terpakai):
                    jadwal_terpakai |= slots
                    break
            
            result[cur_matkul["kode"]] = {
                "ruang": ruang_choosen,
                "hari": hari,
                "jam_mulai": jam_mulai,
                "jam_akhir": jam_mulai + cur_matkul["sks"] -1
            }
        
        return result
                
    