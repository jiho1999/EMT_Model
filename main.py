# main.py

from simulation import run_simulation
from constants import *
from utils import plot_combined_results

if __name__ == "__main__":

     # Directory where Excel files are saved
    input_dir = '/Users/jihopark/Desktop/Jiho_IS/Lung_Epithelial_Simulation/EMT Model'  # Current directory

    try:
        for senescent_prob in constant_senescence_probability:
            run_simulation(senescent_prob, NUM_STEPS)

        # Generate the combined plots for all senescence probabilities
        plot_combined_results(input_dir)
    
    except Exception as e:
        print(f"An error occurred: {e}")
