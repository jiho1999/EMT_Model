# utils.py

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.colors import ListedColormap
from constants import *
import os
import pandas as pd

# Update color map and legend for the new states
cmap = ListedColormap([
    'white',      # Empty
    'green',      # ALIVE/E
    'palegreen',  # ALIVE/H
    'red',        # Anything/DEAD
    'blue',       # DIVIDING/E
    'purple',     # DIVIDING/H
    'yellow',     # SENESCENT/E
    'orange',     # SENESCENT/H
    'pink'        # Anything/M
])

# Mapping cell states to color indices for the colormap
state_to_index = {
    (EMPTY, ''): 0,
    (ALIVE, 'E'): 1,
    (ALIVE, 'H'): 2,
    (DEAD, ''): 3,
    (DIVIDING, 'E'): 4,
    (DIVIDING, 'H'): 5,
    (SENESCENT, 'E'): 6,
    (SENESCENT, 'H'): 7,
    (ALIVE, 'M'): 8
}

# Create a custom legend based on the defined color map
def create_legend():
    legend_labels = [
        'ALIVE/E', 'ALIVE/H', 'DEAD', 'DIVIDING/E', 'DIVIDING/H', 
        'SENESCENT/E', 'SENESCENT/H', 'M'
    ]
    legend_colors = ['green', 'palegreen', 'red', 'blue', 'purple', 'yellow', 'orange', 'pink']
    return [mpatches.Patch(color=legend_colors[i], label=legend_labels[i]) for i in range(len(legend_labels))]

# Define the structured data type for the grid
dtype = [('primary_state', 'i4'), ('emt_state', 'U6')]  # 'U6' to accommodate the string 'EMPTY'

def update_grid(grid, cell_positions, cell_states, grid_size_x, grid_size_y):
    # Clear the grid by setting it to EMPTY values
    grid['primary_state'] = EMPTY
    grid['emt_state'] = ''
    
    # Update the grid based on cell positions and states
    for pos, state in zip(cell_positions, cell_states):
        grid[pos[0], pos[1]]['primary_state'] = state[0]
        grid[pos[0], pos[1]]['emt_state'] = state[1]

    # Create a color grid for visualization, using the state_to_index mapping
    color_grid = np.array([[state_to_index.get((cell['primary_state'], cell['emt_state']), 0) for cell in row] for row in grid])

    return grid, color_grid

# # Set non-interactive backend
# plt.switch_backend('Agg')  # Use 'Agg' for file rendering (non-interactive backend)
# def visualize_grid(color_grid, step, run_number, senescence_probability, save_images=False):
#     output_dir='simulation_images'

#     # Set up the plot with a larger figure size to provide space for the legend
#     plt.figure(figsize=(10, 8))  # Increase figure size for more space

#         # Plot the grid with the custom colormap
#     plt.imshow(color_grid, cmap=cmap, vmin=0, vmax=len(cmap.colors) - 1)
#     plt.title(f'Run {run_number + 1} - Step {step}')
#     plt.legend(handles=create_legend(), bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

#     # Save the image if required
#     if save_images:
#         # Ensure the output directory exists
#         if not os.path.exists(output_dir):
#             os.makedirs(output_dir)
#         # Save the image with a descriptive filename
#         filename = os.path.join(output_dir, f'run_{run_number + 1}_senescence_{senescence_probability:.1e}_step_{step:03d}.png')
#         plt.savefig(filename)

#     # Display the plot and clear it afterward
#     # plt.pause(0.1)
#     plt.clf()
#     plt.close()

def visualize_grid(color_grid, step, run_number, senescence_probability, save_images=False):
    output_dir = 'simulation_images'

    # Create the plot without axes or any extra elements
    plt.imshow(color_grid, cmap=cmap, vmin=0, vmax=len(cmap.colors) - 1)
    plt.axis('off')  # Turn off axis

    # Save the image if required
    if save_images:
        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        # Save the image with a descriptive filename
        filename = os.path.join(output_dir, f'run_{run_number + 1}_senescence_{senescence_probability:.1e}_step_{step:03d}.png')
        plt.savefig(filename, bbox_inches='tight', pad_inches=0, dpi=100)  # Set dpi for 100x100 pixels
    plt.clf()  # Clear the plot after saving

def calculate_permeability(grid):
    # Calculate the permeability
    edge_neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    avg_permeability_sum = 0
    cell_count = 0
    avg_permeability = 0

    # Cache grid dimensions to avoid repeated calls to len(grid)
    grid_rows = len(grid)
    grid_cols = len(grid[0])

    # Loop through every cell in the grid
    for width in range(grid_rows):
        for length in range(grid_cols):
            # Check if the grid cell is not EMPTY or DEAD
            if (grid[width, length]["primary_state"], grid[width, length]["emt_state"]) not in {(EMPTY, ''), (DEAD, '')}:
                cell_count += 1
                single_cell_permeability_sum = 0

                # Check neighboring cells
                for dx, dy in edge_neighbors:
                    nx, ny = width + dx, length + dy
                    # Ensure we stay within grid bounds
                    if 0 <= nx < grid_rows and 0 <= ny < grid_cols:
                        # Check if neighbor is EMPTY or SENESCENT
                        if (grid[nx, ny]["primary_state"], grid[nx, ny]["emt_state"]) in {(EMPTY, ''), (SENESCENT, E), (SENESCENT, H)}:
                            single_cell_permeability_sum += 1

                # Add the permeability score of the current cell
                avg_permeability_sum += single_cell_permeability_sum / 4  # Dividing by 4 to average the permeability score for the cell

    # Only calculate the final average if we have valid cells
    if cell_count > 0:
        avg_permeability = avg_permeability_sum / cell_count
    
    return avg_permeability

# # Function to plot Division Count and Migration Count vs Step
# def plot_results(input_dir, output_dir='wound_closure_plot_results'):
#     for file in os.listdir(input_dir):
#         if file.endswith('.xlsx') and 'division_migration_senescence' in file:
#             # Load the results from the Excel file
#             filepath = os.path.join(input_dir, file)
#             df = pd.read_excel(filepath)
    
#             # Extract data for plotting
#             step = df['Step']
#             division_count = df['Division Count']
#             migration_count = df['Migration Count']
#             avg_permeability = df['Average Permeability']
#             senescence_probability = df['Senescence Probability'].iloc[0]
#             wound_closure_step = df['Wound Closure Step'].iloc[0]

#             # Create the plot
#             plt.figure(figsize=(12, 6))

#             # Plot Division Count
#             plt.plot(step, division_count, label='Division Count', color='blue', linestyle='-', marker='o')

#             # Plot Migration Count
#             plt.plot(step, migration_count, label='Migration Count', color='green', linestyle='-', marker='x')

#             # Add titles and labels
#             plt.title(f'Division and Migration Counts vs Step (Senescence Probability: {senescence_probability:.1e})')
#             plt.xlabel('Step')
#             plt.ylabel('Count / Permeability')
#             plt.legend()

#             # Add text annotation for wound closure step
#             if wound_closure_step != 'Not closed yet':
#                 plt.axvline(x=wound_closure_step, color='red', linestyle='--', label=f'Wound Closure Step: {wound_closure_step}')
#                 plt.text(wound_closure_step + 1, max(division_count.max(), migration_count.max()) * 0.9,
#                         f'Wound Closure Step: {wound_closure_step}', color='red')

#             # Ensure the output directory exists
#             if not os.path.exists(output_dir):
#                 os.makedirs(output_dir)

#             # Save the plot to a file in the new directory
#             plot_filename = os.path.join(output_dir, os.path.basename('division_migration_step').replace('.xlsx', '.png'))
#             plt.savefig(plot_filename)

#             # Show the plot
#             plt.close()


#             # Plot Average Permeability separately
#             plt.figure(figsize=(12, 6))

#             # Plot Average Permeability
#             plt.plot(step, avg_permeability, label='Average Permeability', color='orange', linestyle='-', marker='s')

#             # Add titles and labels
#             plt.title(f'Average Permeability vs Step (Senescence Probability: {senescence_probability:.1e})')
#             plt.xlabel('Step')
#             plt.ylabel('Average Permeability')
#             plt.legend()

#             # Add text annotation for wound closure step (optional, since it may not make sense here)
#             if wound_closure_step != 'Not closed yet':
#                 plt.axvline(x=wound_closure_step, color='red', linestyle='--', label=f'Wound Closure Step: {wound_closure_step}')
#                 plt.text(wound_closure_step + 1, avg_permeability.max() * 0.9,
#                         f'Wound Closure Step: {wound_closure_step}', color='red')

#             # Save the Average Permeability plot
#             plot_filename = os.path.join(output_dir, os.path.basename('permeability_step').replace('.xlsx', '_avg_permeability.png'))
#             plt.savefig(plot_filename)
#             plt.close()

# Modified function to create plots for each run
def plot_combined_results(input_dir, output_dir='plot_results_each_run'):
    # Dictionary to store data for each run
    run_data = {}

    # Iterate through all Excel files in the input directory and extract data
    for file in os.listdir(input_dir):
        if file.endswith('.xlsx') and 'division_migration_senescence' in file:
            # Load the results from the Excel file
            filepath = os.path.join(input_dir, file)
            df = pd.read_excel(filepath)
            
            # Verify the dataframe is not empty and contains necessary columns
            if df.empty or 'Senescence Probability' not in df.columns:
                print(f"Skipping file {file} due to missing data or incorrect format.")
                continue

            # Extract run number from the filename
            run_number = file.split('_run_')[-1].replace('.xlsx', '')
            if run_number not in run_data:
                run_data[run_number] = {
                    'sen_probabilities': [],
                    'step_list': [],
                    'division_counts_list': [],
                    'migration_counts_list': [],
                    'avg_permeability_list': [],
                    'wound_area_list': []
                }

            senescence_probability = df['Senescence Probability'].iloc[0]
            print(f"Processing file: {file} with senescence probability: {senescence_probability} for run: {run_number}")

            # Store data for plotting
            run_data[run_number]['sen_probabilities'].append(senescence_probability)
            run_data[run_number]['step_list'].append(df['Step'])
            run_data[run_number]['division_counts_list'].append(df['Division Count'])
            run_data[run_number]['migration_counts_list'].append(df['Migration Count'])
            run_data[run_number]['avg_permeability_list'].append(df['Average Permeability'])
            run_data[run_number]['wound_area_list'].append(df['Wound Area'])

    # Create plots for each run
    for run_number, data in run_data.items():
        sen_probabilities = data['sen_probabilities']
        step_list = data['step_list']
        division_counts_list = data['division_counts_list']
        migration_counts_list = data['migration_counts_list']
        avg_permeability_list = data['avg_permeability_list']
        wound_area_list = data['wound_area_list']

        # Sort data by senescence probability
        sorted_indices = sorted(range(len(sen_probabilities)), key=lambda i: sen_probabilities[i])
        sen_probabilities = [sen_probabilities[i] for i in sorted_indices]
        step_list = [step_list[i] for i in sorted_indices]
        division_counts_list = [division_counts_list[i] for i in sorted_indices]
        migration_counts_list = [migration_counts_list[i] for i in sorted_indices]
        avg_permeability_list = [avg_permeability_list[i] for i in sorted_indices]
        wound_area_list = [wound_area_list[i] for i in sorted_indices]

        # Create a figure with 4 subplots in a 2x2 layout
        fig, axs = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Division, Migration, Permeability, and Wound Area vs Step', fontsize=16)

        # Plot Division Count for different senescence probabilities
        for i in range(len(sen_probabilities)):
            axs[0, 0].plot(step_list[i], division_counts_list[i], label=f'Senescence Probability: {sen_probabilities[i]:.1e}')
        axs[0, 0].set_xlabel('Step')
        axs[0, 0].set_ylabel('Division Count')
        axs[0, 0].set_title('Division Count vs Step')

        # Plot Migration Count for different senescence probabilities
        for i in range(len(sen_probabilities)):
            axs[0, 1].plot(step_list[i], migration_counts_list[i], label=f'Senescence Probability: {sen_probabilities[i]:.1e}')
        axs[0, 1].set_xlabel('Step')
        axs[0, 1].set_ylabel('Migration Count')
        axs[0, 1].set_title('Migration Count vs Step')

        # Plot Average Permeability for different senescence probabilities
        for i in range(len(sen_probabilities)):
            axs[1, 0].plot(step_list[i], avg_permeability_list[i], label=f'Senescence Probability: {sen_probabilities[i]:.1e}')
        axs[1, 0].set_xlabel('Step')
        axs[1, 0].set_ylabel('Average Permeability')
        axs[1, 0].set_title('Average Permeability vs Step')

        # Plot Wound Area (Empty/Dead Cells Count in Wound) for different senescence probabilities
        for i in range(len(sen_probabilities)):
            axs[1, 1].plot(step_list[i], wound_area_list[i], label=f'Senescence Probability: {sen_probabilities[i]:.1e}')
        axs[1, 1].set_xlabel('Step')
        axs[1, 1].set_ylabel('Wound Area (Empty/Dead Cells)')
        axs[1, 1].set_title('Wound Area vs Step')

        # Add legends to all subplots in a sorted order
        for ax in axs.flat:
            handles, labels = ax.get_legend_handles_labels()
            if handles:  # Check if there are any handles to add to the legend
                sorted_handles_labels = sorted(zip(handles, labels), key=lambda x: float(x[1].split(": ")[1]))
                sorted_handles, sorted_labels = zip(*sorted_handles_labels)
                ax.legend(sorted_handles, sorted_labels, loc='upper right')

        # Adjust layout
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])

        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Save the combined plot to a file in the new directory
        plot_filename = os.path.join(output_dir, f'combined_plot_run_{run_number}.png')
        plt.savefig(plot_filename)

        # Close the plot
        plt.close()
