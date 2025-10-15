# analysis.py
import matplotlib.pyplot as plt
import numpy as np

class SearchAnalyzer:
    def __init__(self):
        self.results = {}
        
    def add_result(self, algorithm_name, result_data):
        """Store results from any algorithm"""
        self.results[algorithm_name] = result_data
    
    def print_general_statistics(self):
        """Print statistics applicable to all algorithms"""
        print("\n" + "="*50)
        print("SEARCH STATISTICS")
        print("="*50)
        
        for algo_name, data in self.results.items():
            print(f"\n{algo_name}:")
            print(f"  Initial Objective Value: {data.get('initial_obj', 'N/A'):.2f}")
            print(f"  Final Objective Value: {data['obj_value']:.2f}")
            print(f"  Search Duration: {data['time']:.2f} seconds")
    
    def plot_objective_history(self):
        """Plot objective function value vs iterations for all algorithms"""
        plt.figure(figsize=(10, 6))
        
        for algo_name, data in self.results.items():
            history = data.get('history', [])
            if history:
                iterations = range(len(history))
                plt.plot(iterations, history, label=algo_name, linewidth=2)
        
        plt.xlabel('Iterations')
        plt.ylabel('Objective Function Value')
        plt.title('Objective Function Value vs Iterations')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def print_hill_climbing_stats(self):
        """Print Hill Climbing specific statistics"""
        hc_algorithms = [name for name in self.results.keys() if 'Hill Climbing' in name]
        
        if not hc_algorithms:
            return
            
        print("\n" + "="*50)
        print("HILL CLIMBING STATISTICS")
        print("="*50)
        
        for algo_name in hc_algorithms:
            data = self.results[algo_name]
            mode = data.get('mode', 1)
            
            print(f"\n{algo_name} (Mode {mode}):")
            print(f"  Iterations: {data.get('iterations', 'N/A')}")
            
            # Steepest Ascent and Stochastic
            # if mode in [1, 4]:
            #     # print(f"  Iterations: {data.get('iterations', 'N/A')}")
            
            # Sideways Move
            if mode == 2:
                max_sideways = data.get('max_sideways', 'N/A')
                actual_sideways = data.get('sideways_moves', 'N/A')
                print(f" Sideways Moves: {actual_sideways}")
            
            # Random Restart
            elif mode == 3:
                max_restart = data.get('max_restart', 'N/A')
                actual_restarts = data.get('restarts', 'N/A')
                iter_per_restart = data.get('iter_per_restart', [])
                print(f"  Restarts: {actual_restarts}")
                if iter_per_restart:
                    print(f"  Iterations per Restart: {iter_per_restart}")
          
    def print_genetic_algorithm_stats(self):
        """Print Genetic Algorithm specific statistics"""
        ga_algorithms = [name for name in self.results.keys() if 'Genetic Algorithm' in name]
        
        if not ga_algorithms:
            return
        
        print("\n" + "="*50)
        print("GENETIC ALGORITHM STATISTICS")
        print("="*50)
        
        for algo_name in ga_algorithms:
            data = self.results[algo_name]
            print(f"\n{algo_name}:")
            print(f"  Population Size: {data.get('population_size', 'N/A')}")
            print(f"  Generations: {data.get('iterations', 'N/A')}")
            print(f"  Elitism Ratio: {data.get('elitisism_ratio', 'N/A')}")
            print(f"  Tournament Group Size: {data.get('n_tournament', 'N/A')}")
            print(f"  Best per Tournament: {data.get('best_tournament', 'N/A')}")
            print(f"  Final Objective Value: {data['obj_value']:.4f}")
            print(f"  Duration: {data['time']:.2f}s")

    def plot_simulated_annealing_temperature(self):
        """Plot exp(ΔE / T) vs iterations for Simulated Annealing"""
        sa_algorithms = [name for name in self.results.keys() if 'Simulated Annealing' in name]
        
        if not sa_algorithms:
            return
            
        plt.figure(figsize=(10, 6))
        
        for algo_name in sa_algorithms:
            data = self.results[algo_name]
            temp_history = data.get('prob_history', [])
            
            if temp_history:
                iterations = range(len(temp_history))
                plt.plot(iterations, temp_history, label=algo_name, linewidth=2)
        
        plt.xlabel('Iterations')
        plt.ylabel('exp(ΔE / T)')
        plt.title('Simulated Annealing: exp(ΔE / T) vs Iterations')
        plt.legend()
        plt.grid(True, alpha=0.3)
        # plt.yscale('log')
        plt.tight_layout()
        plt.show()

    def plot_genetic_algorithm_progress(self):
        """Plot Genetic Algorithm best and average cost history"""
        ga_algorithms = [name for name in self.results.keys() if 'Genetic Algorithm' in name]
        
        if not ga_algorithms:
            return
        
        plt.figure(figsize=(10, 6))
        
        for algo_name in ga_algorithms:
            data = self.results[algo_name]
            best_history = data.get('history', [])
            avg_history = data.get('avg_history', [])
            if best_history:
                plt.plot(best_history, label=f"{algo_name} (Best)", linewidth=2)
            if avg_history:
                plt.plot(avg_history, '--', label=f"{algo_name} (Average)", linewidth=1.5)
        
        plt.xlabel('Generations')
        plt.ylabel('Cost')
        plt.title('Genetic Algorithm: Best vs Average Cost per Generation')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def generate_report(self):
        """Generate analysis report with relevant graphs"""
        self.print_general_statistics()
        self.print_hill_climbing_stats()
        
        # Show relevant plots based on algorithms used
        if any('Hill Climbing' in name for name in self.results.keys()):
            self.plot_objective_history()
        
        if any('Simulated Annealing' in name for name in self.results.keys()):
            self.plot_objective_history()
            self.plot_simulated_annealing_temperature()
            
        if any('Genetic Algorithm' in name for name in self.results.keys()):
            self.print_genetic_algorithm_stats()
            self.plot_genetic_algorithm_progress()
      