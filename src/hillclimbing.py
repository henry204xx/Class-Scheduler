
from Jadwal import Jadwal
import copy

class HillClimbing:
    
    """
    Perform hill climbing algorithm
    
    ATTRIBUTES:
        mode: int(1..4)
        types of hill climbing algorithm that user want to perform
            mode = 1 (steepest ascent HC)
            mode = 2 (sideways move HC)
            mode = 3 (random restart HC)
            mode = 4 (stochastic HC)
        
        n_max_iter: posint 
        the maximum number of iteration, specifically used for random restart and stochastic HC
        
        jadwal: Jadwal
        the initial jadwal that want to be predicted
    
    HOW TO USE:

        hc = HillClimbing(mode=1, n_max_iter=100)
        optimal_jadwal = hc.predict(jadwal: jadwal_input)

    """
    
    def __init__(self, mode: int, n_max_iter = 10):
        self.mode = mode
        self.n_max_iter = n_max_iter
        
    
    def predict(self, jadwal: Jadwal):
        self.jadwal = copy.deepcopy(jadwal)
        if(self.mode == 1): return self.steepest_ascent()
        elif(self.mode == 2): return self.sideways_move()
        elif(self.mode == 3): return self.random_restart()
        # elif(self.mode == 4): return self.stochastic()
        
        else:
            print("error: invalid mode, mode allowed are: \n1 for steepest ascent\n 2 for sideways move\n 3 random restart\n 4 stochastic")
    
    def steepest_ascent(self):
        cur_jadwal = self.jadwal
        cur_obj_val = cur_jadwal.get_objective_func_value()
        
        while True:
            neighbor = cur_jadwal.get_best_neighbor()
            neighbor_obj_val = neighbor.get_objective_func_value_print()
            
            if(neighbor_obj_val <= cur_obj_val): break
                
            cur_jadwal = neighbor
            cur_obj_val = neighbor_obj_val
            
        return cur_jadwal

    def sideways_move(self):
        cur_jadwal = self.jadwal
        cur_obj_val = cur_jadwal.get_objective_func_value()
        
        while True:
            neighbor = cur_jadwal.get_best_neighbor()
            neighbor_obj_val = neighbor.get_objective_func_value_print()
            
            if((neighbor_obj_val < cur_obj_val) or cur_obj_val == 0): break
                
            cur_jadwal = neighbor
            cur_obj_val = neighbor_obj_val
            
        return cur_jadwal
    

    def random_restart(self):
        
        """TODO: mau tanya, buat n_max_iterasi random restart berapa ya? mau biar bisa diatur sama user atau kita state aja?
    
        ini ada n_max_iterasi as safety net biar gk infinite loop kalau emang gk ada jawaban
        
        """
        
        if(self.n_max_iter <= 0):
            print("error: allowed n_max_iter value are positive non zero integer")
            return
        
        cur_jadwal = self.jadwal
        cur_obj_val = cur_jadwal.get_objective_func_value()
        
        best_neighbor = None
        best_value = float('-inf')

        i = 0
        
        while (i < self.n_max_iter):
            
            while True:
                neighbor = cur_jadwal.get_best_neighbor()
                neighbor_obj_val = neighbor.get_objective_func_value()
                
                if(neighbor_obj_val <= cur_obj_val):
                    if best_value < cur_obj_val: 
                        best_neighbor = copy.deepcopy(cur_jadwal)
                        best_value = cur_obj_val
                    break
                    
                cur_jadwal = neighbor
                cur_obj_val = neighbor_obj_val
            
            print(f'current best value at i-{i} = {best_value}')
            i += 1
            if(best_value == 0):
                return best_neighbor
            
            cur_jadwal.random_schedule()
                
        
        return best_neighbor