from Jadwal import Jadwal

json_name = input("Enter the name of the json: ")

jadwal = Jadwal(json_name=json_name)
print()
jadwal.print_schedule()

# print("\njadwal mahasiswa yang konflik ada: ", end="")
# print(jadwal.objf_waktu_konflik_mhs())
# print("\njadwal dosen yang konflik ada: ", end="")
# print(jadwal.objf_waktu_konflik_dosen())
# print("\nobj function kapasitas: ", end="")
# print(jadwal.objf_kapasitas_ruang())
print("\nget_conflict_slots: ", end="")

conflict_slots = jadwal.get_conflict_slots()
print(conflict_slots, "\n\n")

for pair in conflict_slots:
    hari, jam = jadwal.slot_to_day_hour(pair[0])
    print(f"hari: {hari}, jam: {jam}")
    
    
print("\nobj function prioritas: ", end="")
print(jadwal.objf_priotitas())