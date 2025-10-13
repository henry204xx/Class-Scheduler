from Jadwal import Jadwal
from math import exp
import random

class SimulatedAnnealing:
    """
    perform simulated annealing
    
    returns: jadwal_result, result_objective_function, array of objective function
    """
           
    def __init__(self, cur_jadwal: Jadwal, T=100, T_min=1e-3, alpha=0.95):
        self.cur_jadwal = cur_jadwal
        self.T = T
        self.T_min = T_min
        self.alpha = alpha
        self.num_of_iteration = 1

    def temperature_function(self, current_temperature: float):
        # exponential decay
        return current_temperature * (self.alpha ** self.num_of_iteration)

    def predict(self):
        T = self.T
        cur_jadwal = self.cur_jadwal
        cur_obj_val = cur_jadwal.get_objective_func_value()
        arr_obj_val = [cur_obj_val]

        while T >= self.T_min:
            if T < self.T_min:
                return cur_jadwal, cur_obj_val, arr_obj_val

            best_neighbor = cur_jadwal.get_best_neighbor()
            # print(best_neighbor.get_objective_func_value_print)

            delta = best_neighbor.get_objective_func_value() - cur_jadwal.get_objective_func_value()
            if delta > 0:
                cur_jadwal = best_neighbor
                cur_obj_val = cur_jadwal.get_objective_func_value()
                arr_obj_val.append(cur_obj_val)
                
            else:
                prob_to_move = exp(delta / T)
                prob_threshold = random.random()
                if prob_to_move >= prob_threshold:
                    cur_jadwal = best_neighbor
                    cur_obj_val = cur_jadwal.get_objective_func_value()
                    arr_obj_val.append(cur_obj_val)

            T = self.temperature_function(T)
            self.num_of_iteration += 1

        return cur_jadwal, cur_obj_val, arr_obj_val
