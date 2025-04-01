import os
import csv
import json
from greedy import greedy_start
from score_functions import score

def convert_keys_to_int(d):
    """Convert dictionary keys from strings to integers."""
    return {int(k): v for k, v in d.items()} if isinstance(d, dict) else d

def get_best_stored_solution(csv_path, folder_path):
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
                    solution_path = os.path.join(folder_path, solution_id)
                    
                    if os.path.exists(solution_path):
                        with open(solution_path, "r") as sol_file:
                            best_solution = json.load(sol_file)

    return (convert_keys_to_int(best_solution), best_score) if best_solution else (None, float('-inf'))


def get_init_solution(folder_path_scores, file_name, algorithm_name, endpoint_data_description, endpoint_cache_description, request_description):
    """
    Determine the best initial solution:
    - If a stored solution exists with a higher score, use it.
    - Otherwise, use the greedy solution.
    """
    folder_path_greedy_scores = os.path.join(algorithm_name, "greedy_scores")
    os.makedirs(folder_path_greedy_scores, exist_ok=True)
    
    score_file_path = os.path.join(folder_path_greedy_scores, f'score_{file_name}.txt')
    greedy_score = 0
    
    if os.path.exists(score_file_path):
        with open(score_file_path, "r") as file_score:
            greedy_score = float(file_score.read().strip())
    else:
        greedy_score = score(greedy_start(), endpoint_data_description, endpoint_cache_description, request_description)
        with open(score_file_path, "w") as file_score:
            file_score.write(str(greedy_score))
    
    csv_path = os.path.join(algorithm_name, f'{algorithm_name}.csv')
    best_stored_solution, best_stored_score = get_best_stored_solution(csv_path, folder_path_scores)

    if best_stored_solution is not None and isinstance(best_stored_score, (int, float)) and best_stored_score >= greedy_score:
        print("Best Stored Solution", best_stored_score)
        print("Best Stored Score solution", best_stored_score)
        return best_stored_solution  # Use the best stored solution

    return greedy_start()  # Use the greedy solution if it's better
