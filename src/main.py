from problem import Problem
import json

json_name = input("Enter the name of the json: ")
# path_to_json = '../tests/' + json_name

# with open(path_to_json, "r") as f:
#     overall_problem = json.load(f)
    
# mata_kuliah = overall_problem.get("kelas_mata_kuliah", [])

problem = Problem(json_name=json_name)