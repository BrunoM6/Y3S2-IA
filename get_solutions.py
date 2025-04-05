import os
import csv
import json
from greedy import greedy_start
from score_functions import score

def convert_keys_to_int(d):
    """Convert dictionary keys from strings to integers."""
    return {int(k): v for k, v in d.items()} if isinstance(d, dict) else d

def get_best_stored_solution(csv_path, results_path):
    """Retrieve the best solution from stored JSON files based on the highest score in CSV."""
    best_solution = None
    best_score = float('-inf')
    
    if os.path.exists(csv_path):
        with open(csv_path, "r") as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader, None)  # Skip header
            
            for row in csv_reader:
                if len(row) < 3:
                    continue
                _, solution_id, score = row
                score = float(score)  # Convert from string to float
                
                if score > best_score:
                    best_score = score
                    solution_path = os.path.join(results_path, solution_id)
                    
                    if os.path.exists(solution_path):
                        with open(solution_path, "r") as sol_file:
                            best_solution = json.load(sol_file)

    return (convert_keys_to_int(best_solution), best_score) if best_solution else (None, float('-inf'))


def get_init_solution(problem_description, video_size, dataset, algorithm, endpoint_data_description, endpoint_cache_description, request_description):
    """Retrieve the initial solution from the dataset, use greedy solution in case there is none."""
    # deterministic heuristic, score can be stored previously (if not calculate and store it)
    os.makedirs("greedy_scores", exist_ok=True)
    folder_path_greedy_score = os.path.join("greedy_scores", f'score_{dataset}.txt')
    if os.path.exists(folder_path_greedy_score):
        with open(folder_path_greedy_score, "r") as file_score:
            greedy_score = float(file_score.read().strip())
    else:
        greedy_start_solution = greedy_start(problem_description, video_size, endpoint_data_description, endpoint_cache_description, request_description)
        greedy_score = score(greedy_start_solution, endpoint_data_description, endpoint_cache_description, request_description)
        with open(folder_path_greedy_score, "w") as file_score:
            file_score.write(str(greedy_score))
    
    # get best of the previous scores, if there aren't any, use the greedy heuristic score
    csv_path = os.path.join("scores", dataset, f'{algorithm}.csv')
    results_path = os.path.join("results", dataset,algorithm)
    best_stored_solution, best_stored_score = get_best_stored_solution(csv_path, results_path)


    if best_stored_solution is not None and isinstance(best_stored_score, (int, float)) and best_stored_score >= greedy_score:
        return best_stored_solution  # use the best stored solution associated with the best score

    return greedy_start(problem_description, video_size, endpoint_data_description, endpoint_cache_description, request_description) 
