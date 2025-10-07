from Jadwal import Jadwal

json_name = input("Enter the name of the json: ")

jadwal = Jadwal(json_name=json_name)
print()
jadwal.print_schedule()
print("\njadwal mahasiswa yang konflik ada: ", end="")
print(jadwal.objf_waktu_konflik_mhs())