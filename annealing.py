import csv
import matplotlib.pyplot as plt
import json
import os
import random
import re
import math

from get_neighbours import get_neighbors, get_neighbors_all
from get_solutions import get_init_solution
from parse import parse_results
from score_functions import score
from visual import update_plot

def simulated_annealing(initial_solution: dict, video_size: list, endpoint_data_description: list, 
                         endpoint_cache_description: dict, request_description: dict, cache_capacity: int, 
                         max_iterations=1000, initial_temperature=100, cooling_rate=0.99, max_no_improve_iterations=10):

    os.makedirs(folder_path, exist_ok=True)
    os.makedirs(folder_path_scores, exist_ok=True)

    # Find the highest existing solution number
    max_json_number = -1
    for file2 in os.listdir(folder_path_scores):
        match = re.match(r"solution_(\d+)\.json$", file2)
        if match:
            file_id = int(match.group(1))
            if file_id > max_json_number:
                max_json_number = file_id

    # Initialize variables
    current_solution = initial_solution
    current_score = score(initial_solution, endpoint_data_description, endpoint_cache_description, request_description)
    best_solution = current_solution
    best_score = current_score
    print(best_score)

    temperature = initial_temperature
    prev_solution = {}

    no_improve_count = 0  # Counter for iterations without improvement

    with open(os.path.join(folder_path, "annealing.csv"), "a", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        if not os.listdir(folder_path_scores):  # Check if the folder is empty
            csv_writer.writerow(["algorithm", "solution_id", "score"])

        for iteration in range(max_iterations):
            temperature *= cooling_rate  # Reduce temperature each iteration

            if temperature <= 1e-3:
                break  # Stop if the temperature is too low
            
            # Generate a neighboring solution
            neighbor = random.choice(get_neighbors_all(current_solution, video_size, cache_capacity))
            prev_solution = update_plot(current_solution, neighbor, solution_positions, ax, fig, prev_solution)
            neighbor_score = score(neighbor, endpoint_data_description, endpoint_cache_description, request_description)

            delta_score = neighbor_score - current_score

            # Accept the new solution if it's better or with probability based on temperature
            if delta_score > 0 or random.random() < math.exp(delta_score / temperature):
                current_solution = neighbor
                current_score = neighbor_score

                if current_score > best_score:
                    best_solution = current_solution
                    best_score = current_score
                    no_improve_count = 0  # Reset counter when improvement occurs
                else:
                    no_improve_count += 1  # Increment counter if no improvement
            
            # Stop early if max_no_improve_iterations is reached
            if no_improve_count >= max_no_improve_iterations:
                print("Stopping early due to no improvement.")
                break

            # Save solution to file
            solution_id = f"solution_{max_json_number + iteration}.json"
            solution_path = os.path.join(folder_path_scores, solution_id)
            with open(solution_path, "w") as sol_file:
                json.dump(current_solution, sol_file)
            
            csv_writer.writerow(["SimulatedAnnealing", solution_id, current_score])
            csvfile.flush()

    print("Best score:", best_score)
    return best_solution


file = 'me_at_the_zoo.in'
folder_path = "annealing"
folder_path_scores = os.path.join("annealing/scores", file)
problem_description, video_size, endpoint_data_description, endpoint_cache_description, request_description = parse_results(file)
initial_solution = get_init_solution(
    folder_path_scores=folder_path_scores,
    file_name=file,
    algorithm_name='annealing',
    endpoint_data_description=endpoint_data_description,
    endpoint_cache_description=endpoint_cache_description,
    request_description=request_description
)

#Create plot
# Store solution positions
solution_positions = {}

# Graph setup
fig, ax = plt.subplots()
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_title("Tabu Search Solution Mapping")
print(simulated_annealing(initial_solution, video_size, endpoint_data_description, endpoint_cache_description, request_description, problem_description[4]))
