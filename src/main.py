from Jadwal import Jadwal
from genetic import GeneticScheduler
from hillclimbing import HillClimbing
from simulated_annealing import SimulatedAnnealing
import time
import sys

def main():
    print("=" * 70)
    print("SCHEDULING OPTIMIZATION SYSTEM")
    print("=" * 70)
    
    # Get JSON file name
    json_name = input("Enter the name of the JSON file (e.g., tc1.json): ").strip()
    
    # Load the base schedule
    print(f"\nLoading schedule from {json_name}...")
    try:
        jadwal = Jadwal(json_name=json_name)
        print("✓ Schedule loaded successfully!")
    except Exception as e:
        print(f"✗ Error loading schedule: {e}")
        return
    
    # Display initial schedule information
    print("\n" + "=" * 50)
    print("INITIAL SCHEDULE")
    print("=" * 50)
    jadwal.print_schedule()
    print(f"\nInitial Objective Function Value: {jadwal.get_objective_func_value():.2f}")
    jadwal.validate_schedule()
    
    # Method selection
    print("\n" + "=" * 50)
    print("OPTIMIZATION METHODS")
    print("=" * 50)
    print("1. Hill Climbing")
    print("2. Genetic Algorithm") 
    print("3. Simulated Annealing")
    print("4. Compare All Methods")
    
    while True:
        try:
            choice = int(input("\nSelect method (1-4): "))
            if 1 <= choice <= 4:
                break
            else:
                print("Please enter a number between 1 and 4")
        except ValueError:
            print("Please enter a valid number")
    
    # Initialize parameters
    hc_params = {}
    ga_params = {}
    sa_params = {}
    
    # Hill Climbing parameters
    if choice in [1, 4]:
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
            
            if hc_params['mode'] == 1:
                hc_params['max_iter'] = int(input("Max iterations (default=100): ") or "100")
            elif hc_params['mode'] == 2:
                hc_params['max_sideways'] = int(input("Max sideways moves (default=10): ") or "10")
            elif hc_params['mode'] == 3:
                hc_params['max_restart'] = int(input("Number of restarts (default=5): ") or "5")
            elif hc_params['mode'] == 4:
                hc_params['max_iter'] = int(input("Max iterations (default=100): ") or "100")
                
        except ValueError:
            print("Using default values")
            # Set defaults
            if 'mode' not in hc_params:
                hc_params['mode'] = 1
            if hc_params['mode'] in [1, 4]:
                hc_params['max_iter'] = 100
            elif hc_params['mode'] == 2:
                hc_params['max_sideways'] = 10
            elif hc_params['mode'] == 3:
                hc_params['max_restart'] = 5
    
    # Genetic Algorithm parameters  
    if choice in [2, 4]:
        print("\n" + "-" * 30)
        print("GENETIC ALGORITHM PARAMETERS")
        print("-" * 30)
        try:
            ga_params['population_size'] = int(input("Population size (default=30): ") or "30")
            ga_params['generations'] = int(input("Generations (default=100): ") or "100")
            ga_params['crossover_rate'] = float(input("Crossover rate (0-1, default=0.8): ") or "0.8")
            ga_params['mutation_rate'] = float(input("Mutation rate (0-1, default=0.2): ") or "0.2")
            ga_params['elitism'] = int(input("Elitism count (default=2): ") or "2")
        except ValueError:
            print("Using default values")
            ga_params = {
                'population_size': 30,
                'generations': 100,
                'crossover_rate': 0.8,
                'mutation_rate': 0.2,
                'elitism': 2
            }
    
    # Simulated Annealing parameters
    if choice in [3, 4]:
        print("\n" + "-" * 30)
        print("SIMULATED ANNEALING PARAMETERS")
        print("-" * 30)
        try:
            sa_params['initial_temp'] = float(input("Initial temperature (default=100): ") or "100")
            sa_params['min_temp'] = float(input("Minimum temperature (default=0.001): ") or "0.001")
            sa_params['alpha'] = float(input("Cooling rate (0-1, default=0.95): ") or "0.95")
        except ValueError:
            print("Using default values")
            sa_params = {
                'initial_temp': 100,
                'min_temp': 0.001,
                'alpha': 0.95
            }
    
    # Run selected optimization method(s)
    print("\n" + "=" * 50)
    print("RUNNING OPTIMIZATION")
    print("=" * 50)
    
    results = {}
    initial_obj = jadwal.get_objective_func_value()
    
    # Hill Climbing
    if choice in [1, 4]:
        print(f"\nRunning Hill Climbing (Mode {hc_params.get('mode', 1)})...")
        start_time = time.time()
        
        # Set appropriate max_iter based on mode
        if hc_params['mode'] == 2:
            max_iter_param = hc_params.get('max_sideways', 10)
        elif hc_params['mode'] == 3:
            max_iter_param = hc_params.get('max_restart', 5)
        else:
            max_iter_param = hc_params.get('max_iter', 100)
        
        hc = HillClimbing(mode=hc_params['mode'], n_max_iter=max_iter_param)
        
        if hc_params['mode'] == 1:
            result_jadwal, obj_value, history, iterations = hc.predict(jadwal=jadwal)
        elif hc_params['mode'] == 2:
            result_jadwal, obj_value, history, iterations = hc.predict(jadwal=jadwal)
        elif hc_params['mode'] == 3:
            result_jadwal, obj_value, history, restarts, iter_per_restart = hc.predict(jadwal=jadwal)
            iterations = f"{restarts} restarts"
        else:  # mode 4
            result_jadwal, obj_value, history = hc.predict(jadwal=jadwal)
            iterations = hc_params.get('max_iter', 100)
        
        end_time = time.time()
        hc_time = end_time - start_time
        
        results['Hill Climbing'] = {
            'jadwal': result_jadwal,
            'obj_value': obj_value,
            'time': hc_time,
            'iterations': iterations,
            'history': history,
            'improvement': obj_value - initial_obj
        }
        
        print(f"✓ Hill Climbing completed in {hc_time:.2f} seconds")
        print(f"  Final objective value: {obj_value:.2f}")
        print(f"  Improvement: {obj_value - initial_obj:+.2f}")
    
    # Genetic Algorithm
    if choice in [2, 4]:
        print(f"\nRunning Genetic Algorithm...")
        start_time = time.time()
        
        ga = GeneticScheduler(
            base_jadwal=jadwal,
            population_size=ga_params['population_size'],
            generations=ga_params['generations'],
            crossover_rate=ga_params['crossover_rate'],
            mutation_rate=ga_params['mutation_rate'],
            elitism=ga_params['elitism'],
            verbose=False
        )
        
        result_jadwal = ga.run(verbose=False)
        obj_value = result_jadwal.get_objective_func_value()
        
        end_time = time.time()
        ga_time = end_time - start_time
        
        results['Genetic Algorithm'] = {
            'jadwal': result_jadwal,
            'obj_value': obj_value,
            'time': ga_time,
            'iterations': ga_params['generations'],
            'history': ga.best_history,
            'improvement': obj_value - initial_obj
        }
        
        print(f"✓ Genetic Algorithm completed in {ga_time:.2f} seconds")
        print(f"  Final objective value: {obj_value:.2f}")
        print(f"  Improvement: {obj_value - initial_obj:+.2f}")
    
    # Simulated Annealing
    if choice in [3, 4]:
        print(f"\nRunning Simulated Annealing...")
        start_time = time.time()
        
        sa = SimulatedAnnealing(
            cur_jadwal=jadwal,
            T=sa_params['initial_temp'],
            T_min=sa_params['min_temp'],
            alpha=sa_params['alpha']
        )
        
        result_jadwal, obj_value, history = sa.predict()
        
        end_time = time.time()
        sa_time = end_time - start_time
        
        results['Simulated Annealing'] = {
            'jadwal': result_jadwal,
            'obj_value': obj_value,
            'time': sa_time,
            'iterations': sa.num_of_iteration,
            'history': history,
            'improvement': obj_value - initial_obj
        }
        
        print(f"✓ Simulated Annealing completed in {sa_time:.2f} seconds")
        print(f"  Final objective value: {obj_value:.2f}")
        print(f"  Improvement: {obj_value - initial_obj:+.2f}")
    
    # Display Results
    print("\n" + "=" * 70)
    print("OPTIMIZATION RESULTS")
    print("=" * 70)
    
    print(f"Initial objective value: {initial_obj:.2f}")
    print()
    
    for method_name, result in results.items():
        print(f"{method_name}:")
        print(f"  Final objective value: {result['obj_value']:.2f}")
        print(f"  Improvement: {result['improvement']:+.2f}")
        print(f"  Time: {result['time']:.2f} seconds")
        print(f"  Iterations: {result['iterations']}")
        print()
    
    # Show detailed results for the best method or selected method
    if choice == 4:  # Compare all
        if results:
            best_method = max(results.keys(), key=lambda x: results[x]['obj_value'])
            print(f"Best method: {best_method}")
            result_jadwal = results[best_method]['jadwal']
    elif choice == 1:  # Hill Climbing
        result_jadwal = results['Hill Climbing']['jadwal']
    elif choice == 2:  # Genetic Algorithm
        result_jadwal = results['Genetic Algorithm']['jadwal']
    else:  # Simulated Annealing
        result_jadwal = results['Simulated Annealing']['jadwal']
    
    # Display optimized schedule
    print("\n" + "=" * 50)
    print("OPTIMIZED SCHEDULE")
    print("=" * 50)
    result_jadwal.print_schedule()
    
    print(f"\nFinal Objective Function Value: {result_jadwal.get_objective_func_value():.2f}")
    
    # Validation and debugging
    print("\n" + "=" * 50)
    print("VALIDATION & DEBUGGING")
    print("=" * 50)
    result_jadwal.validate_schedule()
    
    print("\nObjective Function Components:")
    result_jadwal.debug_objective_components()
    
    # Ask if user wants to see detailed conflicts
    show_details = input("\nShow detailed conflict analysis? (y/n): ").lower().strip()
    if show_details == 'y':
        print("\nDetailed Lecturer Conflicts:")
        result_jadwal.debug_lecturer_conflicts()
        
        print("\nDetailed Student Conflicts:")
        result_jadwal.debug_student_conflicts()
    
    # Ask if user wants to save the result
    save_result = input("\nSave optimized schedule to file? (y/n): ").lower().strip()
    if save_result == 'y':
        # This would require implementing a save method in Jadwal class
        filename = input("Enter filename to save (without extension): ").strip()
        print(f"Schedule would be saved to {filename}.json (save functionality to be implemented)")
    
    print("\n" + "=" * 70)
    print("OPTIMIZATION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()