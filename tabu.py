import csv
import json
import os
import random
import re

from get_neighbours import get_neighbors, get_neighbors_all, state_to_key
from score_functions import score
from visual import update_plot_batch


def tabu_search(initial_solution: dict, video_size: list, endpoint_data_description: list, endpoint_cache_description: dict, request_description: dict, cache_capacity: int,dataset: str,get_all:bool,max_neighbors, max_iterations,iteration_without_improvement, tabu_tenure,show_plot,ax=None,fig=None):
    
    folder_path_scores = "results/"+dataset+"/tabu"
    folder_path = "scores/" + dataset  
    os.makedirs(folder_path, exist_ok=True)
    os.makedirs(folder_path_scores,exist_ok=True)
    
    solution_positions = {}
    max_json_number = 0
    result_file = None


    for file2 in os.listdir(folder_path_scores):
        match = re.match(r"solution_(\d+)\.json$", file2)
        if match:
            file_id = int(match.group(1))
            if file_id > max_json_number:
                max_json_number = file_id
                result_file = file2

    print(f"Best file: {result_file}")

    tabu = {}  
    best = initial_solution
    best_score = score(initial_solution, endpoint_data_description, endpoint_cache_description, request_description)
    initial_score = best_score
    solution_id = ""
    neighbors = []
    
    iterations_without_improvement = 0  
    iteration = 0  
    with open(os.path.join(folder_path, "tabu.csv"), "a", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        if(not os.path.exists(folder_path_scores)):
            csv_writer.writerow(["algorithm", "solution_id", "score"])
        prev_solution = {} 
        while iteration < max_iterations and iterations_without_improvement < iteration_without_improvement:  
            iteration += 1
            # print(iterations_without_improvement)

            tabu = {k: v - 1 for k, v in tabu.items() if v > 1}

            candidate_list = []  # Stores all valid neighbors
            best_candidate = None
            best_candidate_score = float('-inf')
            aspiration_candidate = None
            aspiration_score = float('-inf')
            
            if(get_all):
                # **Step 1: Generate all neighbors**
                neighbors = get_neighbors_all(best, video_size,  cache_capacity,max_neighbors)
                for neighbor in neighbors:
                    # prev_solution = update_plot(best, neighbor, solution_positions, ax, fig, prev_solution)
                    neighbor_score = score(neighbor, endpoint_data_description, endpoint_cache_description, request_description)
                    candidate_list.append((neighbor, neighbor_score))
            else:
                # **Step 1: Generate all neighbors**
                neighbors = get_neighbors(best, video_size,  cache_capacity)
                for neighbor in neighbors:
                    # prev_solution = update_plot(best, neighbor, solution_positions, ax, fig, prev_solution)
                    neighbor_score = score(neighbor, endpoint_data_description, endpoint_cache_description, request_description)
                    candidate_list.append((neighbor, neighbor_score))
            # **Step 2: Choose the best candidate**
            for candidate, candidate_score in candidate_list:
                candidate_key = state_to_key(candidate)

                if candidate_key not in tabu:
                    if candidate_score > best_candidate_score:
                        best_candidate = candidate
                        best_candidate_score = candidate_score
                else:
                    # **Aspiration: If move is tabu but improves the global best, allow it**
                    if candidate_score > best_score and candidate_score > aspiration_score:
                        aspiration_candidate = candidate
                        aspiration_score = candidate_score

            # **Step 3: Decide whether to use the best move or an aspiration move**
            if best_candidate:
                if(best_candidate_score>best_score):
                    best = best_candidate
                    best_score = best_candidate_score
                    tabu[state_to_key(best)] = tabu_tenure  # Mark as tabu
                    iterations_without_improvement = 0  # Reset stagnation counter
                else:
                    best = best_candidate
                    best_score = best_candidate_score
                    tabu[state_to_key(best)] = tabu_tenure  # Mark as tabu
                    iterations_without_improvement += 1  # Reset stagnation counter

            elif aspiration_candidate:
                best = aspiration_candidate
                best_score = aspiration_score
                tabu[state_to_key(best)] = tabu_tenure  # Override tabu
                iterations_without_improvement = 0  # Reset stagnation counter
            else:
                # **Fallback: Pick a random neighbor if no valid candidates exist**
                if candidate_list:
                    best, best_score = random.choice(candidate_list)
                iterations_without_improvement += 1  # Increment stagnation counter
            solution_id = f"solution_{max_json_number+iteration}.json"
            solution_path = os.path.join(folder_path_scores, solution_id)
            with open(solution_path, "a") as sol_file:
                json.dump(best, sol_file)
            csv_writer.writerow(["TabuSearch", solution_id, best_score])
            csvfile.flush()  
    
            neighbor_edges = []  # Store tuples (current_solution, neighbor)
            plotted_solutions = set()
            
            if show_plot:
                for idx, neighbor in enumerate(neighbors):
                    neighbor_edges.append((best, neighbor))
                    
                    if idx % 300 == 0:  # Adjust this number as needed for performance
                        update_plot_batch(neighbor_edges, solution_positions, ax, fig, plotted_solutions)
                        neighbor_edges.clear()  # Clear edges after drawing

    if best_score > int(initial_score):
        print(best_score)
        return best 
    else:
        print(initial_score)
        return initial_solution
