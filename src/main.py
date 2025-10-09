from Jadwal import Jadwal
from genetic import GeneticScheduler
from hillclimbing import HillClimbing

json_name = input("Enter the name of the json: ")

jadwal = Jadwal(json_name=json_name)
print()
jadwal.print_schedule()
print("\nobj function: ", end="")
print(jadwal.get_objective_func_value())



print('\n\n\n jadwal result: ')
hc = HillClimbing(mode=3)
jadwal_res = hc.predict(jadwal= jadwal)
jadwal_res.print_schedule()
print("\nobj function result: ", end="")
print(jadwal_res.get_objective_func_value())

# print("\njadwal mahasiswa yang konflik ada: ", end="")
# print(jadwal.objf_waktu_konflik_mhs())
# print("\njadwal dosen yang konflik ada: ", end="")
# print(jadwal.objf_waktu_konflik_dosen())
# print("\nobj function kapasitas: ", end="")
# print(jadwal.objf_kapasitas_ruang())
# print("\nobj function prioritas: ", end="")
# print(jadwal.objf_prioritas())



