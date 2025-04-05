import csv
import json
import os
import random
import re
import math

from get_neighbours import get_optimized_neighbors
from score_functions import score
from visual import update_score

def simulated_annealing(initial_solution: dict, video_size: list, endpoint_data_description: list, 
                         endpoint_cache_description: dict, request_description: dict, cache_capacity: int, dataset: str, ax, fig, 
                         max_iterations=10000, iterations_without_improvement_cap=500, initial_temperature=1000.0, cooling_rate=0.99, minimum_temperature=1e-4, neighbors_generated=5):
    # initialize the directories for results
    dataset_path_scores = os.path.join("scores", dataset)
    os.makedirs(dataset_path_scores, exist_ok=True)
    dataset_path_results = os.path.join("results", dataset,"annealing")
    os.makedirs(dataset_path_results, exist_ok=True)
    
    # find highest solution number
    max_json_number = 0
    for file in os.listdir(dataset_path_results):
        match = re.match(r"solution_(\d+)\.json$", file)
        if match:
            file_id = int(match.group(1))
            if file_id > max_json_number:
                max_json_number = file_id
    
    # initialize the solutions and scores 
    current_solution = initial_solution
    best_solution = current_solution
    current_score = score(initial_solution, endpoint_data_description, endpoint_cache_description, request_description)
    best_score = current_score

    print(f"Starting score for this Simulated Annealing instance is {current_score}")
    
    # initialize tracking variables for algorithm
    temperature = initial_temperature
    iterations_without_improvement = 0

    with open(os.path.join(dataset_path_scores, "annealing.csv"), "a", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        
        # log the starting solution as solution 0 for annealing
        solution_id = "solution_0.json"
        solution_path = os.path.join(dataset_path_results, solution_id)
        with open(solution_path, "w") as sol_file:
            json.dump(current_solution, sol_file)
        csv_writer.writerow(["SimulatedAnnealing", solution_id, current_score])
        csvfile.flush()
        
        if not os.path.exists(os.path.join(dataset_path_scores, "annealing.csv")) or os.path.getsize(os.path.join(dataset_path_scores, "annealing.csv")) == 0:  # check if the folder is empty
                csv_writer.writerow(["algorithm", "solution_id", "score"])
        
        for iteration in range(1, max_iterations + 1):
            temperature *= cooling_rate  # Reduce temperature each iteration
            
            if temperature <= minimum_temperature or iterations_without_improvement >= iterations_without_improvement_cap:
                break  # Stop if the temperature is too low
            
            # optimized neighbor getting heuristic
            neighbors = get_optimized_neighbors(current_solution, video_size, cache_capacity, neighbors_generated)
            if not neighbors:
                continue
            
            # pick the best neighbor
            best_neighbor_score = 0
            for neighbor, change in neighbors:
                new_score = score(neighbor, endpoint_data_description, endpoint_cache_description, request_description, current_solution, current_score, change)
                if new_score > best_neighbor_score:
                    best_neighbor = neighbor
                    best_neighbor_score = new_score
            
            # get the delta and act accordingly
            delta_score = best_neighbor_score - current_score
            if delta_score > 0 or random.random() < math.exp(delta_score / temperature):
                current_solution = best_neighbor
                current_score = best_neighbor_score
                
                # check for improvement and save
                if current_score >= best_score:
                    best_solution = current_solution
                    best_score = current_score

                # plot new solution
                update_score((max_json_number + iteration, current_score), ax, fig)

                # log the state
                solution_id = f"solution_{max_json_number + iteration}.json"
                solution_path = os.path.join(dataset_path_results, solution_id)
                with open(solution_path, "w") as sol_file:
                    json.dump(current_solution, sol_file)
                csv_writer.writerow(["SimulatedAnnealing", solution_id, current_score])
                csvfile.flush()
            else:
                iterations_without_improvement += 1
    
    print(f"Best score found during this Simulated Annealing instance is {best_score}")
    return best_solution
