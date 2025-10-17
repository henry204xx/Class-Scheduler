from Jadwal import Jadwal
from genetic import GeneticScheduler
from hillclimbing import HillClimbing
from simulated_annealing import SimulatedAnnealing
from analysis import SearchAnalyzer
import time

def main():
    print("=" * 70)
    print("SCHEDULING SYSTEM")
    print("=" * 70)
    
    json_name = input("Enter the name of the JSON file (e.g., tc1.json): ").strip()
    
    print(f"\nLoading schedule from {json_name}...")
    try:
        jadwal = Jadwal(json_name=json_name)
        print(" Schedule loaded successfully!")
    except Exception as e:
        print(f" Error loading schedule: {e}")
        return
    
    print("\n" + "=" * 50)
    print("INITIAL SCHEDULE")
    print("=" * 50)
    jadwal.print_schedule()
    initial_obj = jadwal.get_objective_func_value()
    print(f"\nInitial Objective Function Value: {initial_obj:.2f}")
    
    # Initialize analysis tool
    analyzer = SearchAnalyzer()
    
    print("\n" + "=" * 50)
    print("METHODS")
    print("=" * 50)
    print("1. Hill Climbing")
    print("2. Genetic Algorithm") 
    print("3. Simulated Annealing")
    
    while True:
        try:
            choice = int(input("\nSelect method (1-3): "))
            if 1 <= choice <= 3:
                break
            else:
                print("Please enter a number between 1 and 3")
        except ValueError:
            print("Please enter a valid number")
    
    hc_params = {}
    ga_params = {}
    sa_params = {}
    
    if choice in [1]:
        print("\n" + "-" * 30)
        print("HILL CLIMBING PARAMETERS")
        print("-" * 30)
        print("Modes:")
        print("1 - Steepest Ascent")
        print("2 - Sideways Move") 
        print("3 - Random Restart")
        print("4 - Stochastic")
        
        try:
            hc_params['mode'] = int(input("Select Hill Climbing mode (1-4, default=1): ") or "1")
            if hc_params['mode'] < 1 or hc_params['mode'] > 4:
                raise ValueError
            
            if hc_params['mode'] == 2:
                hc_params['max_sideways'] = int(input("Max sideways moves (default=10): ") or "10")
                if hc_params['max_sideways'] <= 0:
                    raise ValueError
            elif hc_params['mode'] == 3:
                hc_params['max_restart'] = int(input("Number of restarts (default=5): ") or "5")
                if hc_params['max_restart'] <= 0:
                    raise ValueError
            elif hc_params['mode'] == 4:
                hc_params['max_iterations'] = int(input("Max iterations (default=100): ") or "100")
                if hc_params['max_iterations'] <= 0:
                    raise ValueError
                
        except ValueError:
            print("Using default values")
            if 'mode' not in hc_params:
                hc_params['mode'] = 1
            if hc_params['mode'] == 2:
                hc_params['max_sideways'] = 10
            elif hc_params['mode'] == 3:
                hc_params['max_restart'] = 5
            elif hc_params['mode'] == 4:
                hc_params['max_iterations'] = 100
    
    if choice in [2]:
        print("\n" + "-" * 30)
        print("GENETIC ALGORITHM PARAMETERS")
        print("-" * 30)
        try:
            ga_params['population_size'] = int(input("Population size (default=30): ") or "30")
            if ga_params['population_size'] <= 0:
                raise ValueError
            ga_params['generations'] = int(input("Generations (default=100): ") or "100")
            if ga_params['generations'] <= 0:
                raise ValueError
            ga_params['elitisism_ratio'] = float(input("Elitism ratio (0-1, default=0.2): ") or "0.2")
            if not (0 <= ga_params['elitisism_ratio'] <= 1):
                raise ValueError
            ga_params['n_tournament'] = int(input("Tournament group size (default=5): ") or "5")
            if ga_params['n_tournament'] <= 0:
                raise ValueError
            ga_params['best_tournament'] = int(input("Best individuals per group (default=2): ") or "2")
            if ga_params['best_tournament'] <= 0:
                raise ValueError
            
        except ValueError:
            print("Using default values")
            ga_params = {
                'population_size': 30,
                'generations': 100,
                'crossover_rate': 0.8
            }
    
    if choice in [3]:
        print("\n" + "-" * 30)
        print("SIMULATED ANNEALING PARAMETERS")
        print("-" * 30)
        try:
            sa_params['initial_temp'] = float(input("Initial temperature (default=100): ") or "100")
            if sa_params['initial_temp'] <= 0:
                raise ValueError
            sa_params['min_temp'] = float(input("Minimum temperature (default=0.001): ") or "0.001")
            if sa_params['min_temp'] <= 0:
                raise ValueError
            sa_params['alpha'] = float(input("Cooling rate (0-1, default=0.95): ") or "0.95")
            if not (0 < sa_params['alpha'] < 1):
                raise ValueError
        except ValueError:
            print("Using default values")
            sa_params = {
                'initial_temp': 100,
                'min_temp': 0.001,
                'alpha': 0.95
            }
    
    print("\n" + "=" * 50)
    print("RUNNING LOCAL SEARCH")
    print("=" * 50)
    
    results = {}
    
    if choice == 1:
        print(f"\nRunning Hill Climbing (Mode {hc_params.get('mode', 1)})...")
        start_time = time.time()
        
        if hc_params['mode'] == 2:
            max_iter_param = hc_params.get('max_sideways', 10)
        elif hc_params['mode'] == 3:
            max_iter_param = hc_params.get('max_restart', 5)
        elif hc_params['mode'] == 4:
            max_iter_param = hc_params.get('max_iterations', 100)
        else:
            max_iter_param = 100
        
        hc = HillClimbing(mode=hc_params['mode'], n_max_iter=max_iter_param)
        
        if hc_params['mode'] == 1:
            result_jadwal, obj_value, history, iterations = hc.predict(jadwal=jadwal)
            result_data = {
                'initial_obj': initial_obj,
                'obj_value': obj_value,
                'time': time.time() - start_time,
                'iterations': iterations,
                'history': history,
                'mode': hc_params['mode']
            }
            
        elif hc_params['mode'] == 2:
            result_jadwal, obj_value, history, iterations, sideways_moves = hc.predict(jadwal=jadwal)
            result_data = {
                'initial_obj': initial_obj,
                'obj_value': obj_value,
                'time': time.time() - start_time,
                'iterations': iterations,
                'history': history,
                'mode': hc_params['mode'],
                'max_sideways': hc_params.get('max_sideways', 10),
                'sideways_moves': sideways_moves
            }
            
        elif hc_params['mode'] == 3:
            result_jadwal, obj_value, history, restarts, iter_per_restart = hc.predict(jadwal=jadwal)
            result_data = {
                'initial_obj': initial_obj,
                'obj_value': obj_value,
                'time': time.time() - start_time,
                'iterations': restarts,
                'history': history,
                'mode': hc_params['mode'],
                'max_restart': hc_params.get('max_restart', 5),
                'restarts': restarts,
                'iter_per_restart': iter_per_restart
            }
            
        else:  # mode 4
            result_jadwal, obj_value, history, iterations = hc.predict(jadwal=jadwal)
            result_data = {
                'initial_obj': initial_obj,
                'obj_value': obj_value,
                'time': time.time() - start_time,
                'iterations': iterations,
                'history': history,
                'mode': hc_params['mode']
            }
        
        # Add to analyzer
        analyzer.add_result('Hill Climbing', result_data)
        results['Hill Climbing'] = {'jadwal': result_jadwal, 'obj_value': obj_value}
        # print(f" Hill Climbing completed in {result_data['time']:.2f} seconds")
        # print(f"  Final objective value: {obj_value:.2f}")
    
    elif choice == 2:
        print(f"\nRunning Genetic Algorithm...")
        start_time = time.time()
        
        ga = GeneticScheduler(
            base_jadwal=jadwal,
            population_size=ga_params['population_size'],
            generations=ga_params['generations'],
            elitisism_ratio=ga_params['elitisism_ratio'],
            n_tournament=ga_params['n_tournament'],
            best_tournament=ga_params['best_tournament'],
            seed=42
)
        
        result_jadwal = ga.run(verbose=False)
        obj_value = result_jadwal.get_objective_func_value()
        ga_time = time.time() - start_time
        
        result_data = {
            'initial_obj': initial_obj,
            'obj_value': obj_value,
            'time': ga_time,
            'iterations': ga_params['generations'],
            'history': ga.best_history
        }
        
        analyzer.add_result('Genetic Algorithm', result_data)
        results['Genetic Algorithm'] = {'jadwal': result_jadwal, 'obj_value': obj_value}
        # print(f" Genetic Algorithm completed in {ga_time:.2f} seconds")
        # print(f"  Final objective value: {obj_value:.2f}")
    
    else:
        print(f"\nRunning Simulated Annealing...")
        start_time = time.time()
        
        sa = SimulatedAnnealing(
            cur_jadwal=jadwal,
            T=sa_params['initial_temp'],
            T_min=sa_params['min_temp'],
            alpha=sa_params['alpha']
        )
        
        result_jadwal, obj_value, history, arr_delta = sa.predict()
        sa_time = time.time() - start_time
        
        result_data = {
            'initial_obj': initial_obj,
            'obj_value': obj_value,
            'time': sa_time,
            'iterations': sa.num_of_iteration,
            'history': history,
            'prob_history': arr_delta,
            'initial_temp': sa_params['initial_temp'],
            'min_temp': sa_params['min_temp'],
            'alpha': sa_params['alpha']
        }
        
        analyzer.add_result('Simulated Annealing', result_data)
        results['Simulated Annealing'] = {'jadwal': result_jadwal, 'obj_value': obj_value}
        # print(f" Simulated Annealing completed in {sa_time:.2f} seconds")
        # print(f"  Final objective value: {obj_value:.2f}")
    

    
    print("\n" + "=" * 50)
    print("OPTIMIZED SCHEDULE")
    print("=" * 50)
    result_jadwal = results[list(results.keys())[0]]['jadwal']
    result_jadwal.print_schedule()
    
    print(f"\nFinal Objective Function Value: {result_jadwal.get_objective_func_value():.2f}")

    show_analysis = input("\nShow full analysis report? (y/n): ").lower().strip()
    while show_analysis not in ['y', 'n']:
        show_analysis = input("Please enter 'y' or 'n': ").lower().strip()
    if show_analysis == 'y':
        analyzer.generate_report()
    
    # print("\n" + "=" * 50)
    # print("VALIDATION & DEBUGGING")
    # print("=" * 50)
    # result_jadwal.validate_schedule()
    
    # print("\nObjective Function Components:")
    # result_jadwal.debug_objective_components()
    
    # show_details = input("\nShow detailed conflict analysis? (y/n): ").lower().strip()
    # if show_details == 'y':
    #     # print("\nDetailed Lecturer Conflicts:")
    #     # result_jadwal.debug_lecturer_conflicts()
        
    #     # print("\nDetailed Student Conflicts:")
    #     # result_jadwal.debug_student_conflicts()
    #     pass
    
    save_result = input("\nSave optimized schedule to file? (y/n): ").lower().strip()
    while save_result not in ['y', 'n']:
        save_result = input("Please enter 'y' or 'n': ").lower().strip()
    if save_result == 'y':
        while True:
            filename = input("Enter filename to save (without extension): ").strip()
            if filename and all(c not in filename for c in r'\/:*?"<>|'):
                result_jadwal.save_schedule_table(filename)
                print(f"Schedule saved to {filename}.txt")
                break
            else:
                print("Invalid filename.")
    
    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()