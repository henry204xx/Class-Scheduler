from Jadwal import Jadwal

json_name = input("Enter the name of the json: ")

jadwal = Jadwal(json_name=json_name)
jadwal.print_schedule()