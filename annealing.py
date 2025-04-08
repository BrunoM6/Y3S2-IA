import csv
import json
import math
import os
import random
import re

from get_neighbours import (get_neighbors, get_neighbors_all,
                            get_optimized_neighbors)
from score_functions import score
from visual import update_score


def simulated_annealing(initial_solution: dict, video_size: list, endpoint_data_description: list, endpoint_cache_description: dict, request_description: dict, cache_capacity: int, dataset: str, show_plot: bool, get_all: bool, max_iterations=10000, iterations_without_improvement_cap=500, initial_temperature=1000.0, cooling_rate=0.99, minimum_temperature=1e-4, neighbors_generated=5, ax=None, fig=None):
    # initialize the directories for results
    dataset_path_scores = os.path.join("scores", dataset)
    os.makedirs(dataset_path_scores, exist_ok=True)
    dataset_path_results = os.path.join("results", dataset, "annealing")
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
    current_score, best_latencies = score(
        initial_solution,
        endpoint_data_description,
        endpoint_cache_description,
        request_description
    )
    best_solution = current_solution
    best_score = current_score

    print(f"Starting score for this Simulated Annealing instance is {current_score}")
    
    # initialize tracking variables for algorithm
    temperature = initial_temperature
    iterations_without_improvement = 0

    with open(os.path.join(dataset_path_scores, "annealing.csv"), "a", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)

        if not os.path.exists(os.path.join(dataset_path_scores, "annealing.csv")) or os.path.getsize(os.path.join(dataset_path_scores, "annealing.csv")) == 0:
            csv_writer.writerow(["algorithm", "solution_id", "score"])

        # log the starting solution
        solution_id = "solution_0.json"
        solution_path = os.path.join(dataset_path_results, solution_id)
        with open(solution_path, "w") as sol_file:
            json.dump(current_solution, sol_file)
        csv_writer.writerow(["SimulatedAnnealing", solution_id, current_score])
        csvfile.flush()

        for iteration in range(1, max_iterations + 1):
            temperature *= cooling_rate  # Reduce temperature each iteration

            if temperature <= minimum_temperature or iterations_without_improvement >= iterations_without_improvement_cap:
                break  # Stop if the temperature is too low

            # Get neighbors based on chosen strategy
            if get_all:
                neighbors = get_neighbors_all(current_solution, video_size, cache_capacity, neighbors_generated)
            else:
                neighbors = get_neighbors(current_solution, video_size, cache_capacity)
            if not neighbors:
                continue

            best_neighbor_score = 0
            best_neighbor = None
            best_neighbor_latencies = None

            for neighbor, change in neighbors:
                new_score, new_latencies = score(
                    neighbor,
                    endpoint_data_description,
                    endpoint_cache_description,
                    request_description,
                    current_solution,
                    current_score,
                    change,
                    best_latencies
                )
                if new_score > best_neighbor_score:
                    best_neighbor = neighbor
                    best_neighbor_score = new_score
                    best_neighbor_latencies = new_latencies

            delta_score = best_neighbor_score - current_score
            if best_neighbor is not None and (delta_score > 0 or random.random() < math.exp(delta_score / temperature)):
                current_solution = best_neighbor
                current_score = best_neighbor_score
                best_latencies = best_neighbor_latencies

                print("Current Score", current_score)
                if current_score >= best_score:
                    best_solution = current_solution
                    best_score = current_score

                if show_plot:
                    update_score((max_json_number + iteration, current_score), ax, fig)

                solution_id = f"solution_{max_json_number + iteration}.json"
                solution_path = os.path.join(dataset_path_results, solution_id)
                with open(solution_path, "w") as sol_file:
                    json.dump(current_solution, sol_file)
                csv_writer.writerow(["SimulatedAnnealing", solution_id, current_score])
                csvfile.flush()
                iterations_without_improvement = 0
            else:
                iterations_without_improvement += 1

    print(f"Best score found during this Simulated Annealing instance is {best_score}")
    return best_solution
