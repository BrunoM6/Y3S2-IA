import csv
import json
import os
import re

from get_neighbours import get_neighbors_all,get_neighbors
from score_functions import score
from visual import update_plot_batch, update_score


def hill_climb(initial_solution: dict, video_size: list, endpoint_data_description: list, endpoint_cache_description: dict, request_description: dict, cache_capacity: int, dataset: str,get_all:bool,max_iterations, neighbors_generated,show_plot, ax=None, fig=None):
    # initialize the directories for results
    dataset_path_scores = os.path.join("scores", dataset)
    os.makedirs(dataset_path_scores, exist_ok=True)
    dataset_path_results = os.path.join("results", dataset,"hillclimb")
    os.makedirs(dataset_path_results, exist_ok=True)
    
    # find highest solution number
    solution_positions = {}
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

    print(f"Starting score for this Hill Climbing instance is {current_score}")

    with open(os.path.join(dataset_path_scores, "hillclimb.csv"), "a", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        
        # log the starting solution as solution 0 for annealing
        solution_id = "solution_0.json"
        solution_path = os.path.join(dataset_path_results, solution_id)
        with open(solution_path, "w") as sol_file:
            json.dump(current_solution, sol_file)
        csv_writer.writerow(["HillClimb", solution_id, current_score])
        csvfile.flush()
        
        if not os.path.exists(os.path.join(dataset_path_scores, "hillclimb.csv")) or os.path.getsize(os.path.join(dataset_path_scores, "hillclimb.csv")) == 0:  # check if the folder is empty
                csv_writer.writerow(["algorithm", "solution_id", "score"])
        
        for iteration in range(1, max_iterations + 1):          
            # optimized neighbor getting heuristic
            if get_all:
                neighbors = get_neighbors_all(current_solution, video_size, cache_capacity, neighbors_generated)
            else:
                neighbors = get_neighbors(current_solution, video_size, cache_capacity)
            if not neighbors:
                continue
            if not neighbors:
                break
            
            # pick the best neighbor
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
            
            # get the delta and act accordingly
            delta_score = best_neighbor_score - current_score
            if delta_score < 0:
              return current_solution
            else:
                current_solution = best_neighbor
                current_score = best_neighbor_score
                best_latencies = best_neighbor_latencies


            # log the state
            solution_id = f"solution_{max_json_number + iteration}.json"
            solution_path = os.path.join(dataset_path_results, solution_id)
            with open(solution_path, "w") as sol_file:
                json.dump(current_solution, sol_file)
            csv_writer.writerow(["HillClimb", solution_id, current_score])
            csvfile.flush()

            neighbor_edges = []  # Store tuples (current_solution, neighbor)
            plotted_solutions = set()

            if show_plot:
                # plot new solution
                # update_score((max_json_number + iteration, current_score), ax, fig)
                for idx, neighbor in enumerate(neighbors):
                    neighbor_edges.append((current_solution, neighbor))
                    
                    if idx % 300 == 0:  # Adjust this number as needed for performance
                        update_plot_batch(neighbor_edges, solution_positions, ax, fig, plotted_solutions)
                        neighbor_edges.clear()  # Clear edges after drawing
    
    print(f"Best score found during this Hill Climbing instance is {current_score}")
    return current_solution
