import random
import os
import csv
import json
from parse import parse_results
from get_solutions import get_init_solution
from score_functions import score




def get_neighbors(state: dict, video_size: list, cache_capacity: int):
    neighbors = []
    cache_ids = list(state.keys())
    
    # Precompute current load for each cache to avoid repeated summation.
    current_loads = {
        cache: sum(video_size[int(v)] for v in state[cache])
        for cache in state
    }
    
    # Iterate over each pair of caches (without duplicates).
    for i in range(len(cache_ids)):
        for j in range(i + 1, len(cache_ids)):
            cache_a = cache_ids[i]
            cache_b = cache_ids[j]
            
            # For every video in cache_a, try swapping with every video in cache_b.
            for video_a in state[cache_a]:
                for video_b in state[cache_b]:
                    # Check if swapping maintains capacity constraints:
                    new_load_a = current_loads[cache_a] - video_size[int(video_a)] + video_size[int(video_b)]
                    new_load_b = current_loads[cache_b] - video_size[int(video_b)] + video_size[int(video_a)]
                    if new_load_a > cache_capacity or new_load_b > cache_capacity:
                        continue  # Skip swaps that violate capacity
                    
                    # Instead of a full deep copy, copy only the affected caches.
                    new_state = state.copy()  # shallow copy of the dictionary
                    new_state[cache_a] = state[cache_a].copy()
                    new_state[cache_b] = state[cache_b].copy()
                    
                    new_state[cache_a].remove(video_a)
                    new_state[cache_b].remove(video_b)
                    new_state[cache_a].append(video_b)
                    new_state[cache_b].append(video_a)
                    
                    neighbors.append(new_state)
                        
    return neighbors

def get_neighbors_all(state: dict, video_size: list, cache_capacity: int, max_neighbors: int = 500):
    neighbors = []
    cache_ids = list(state.keys())
    all_videos = set(range(len(video_size)))  # All video IDs (assuming videos are indexed from 0)
    
    current_loads = {
        cache: sum(video_size[int(v)] for v in state[cache])
        for cache in state
    }
    
    cached_videos = set(video for videos in state.values() for video in videos)
    uncached_videos = all_videos - cached_videos  # Videos not currently in any cache

    # Limit the number of operations to explore
    total_combinations = 0
    
    # Iterate over each cache and try adding uncached videos or removing videos from the current cache
    while total_combinations < max_neighbors:
        # Randomly select a cache to operate on
        cache = random.choice(cache_ids)
        
        # Randomly choose whether to remove or add a video
        operation_type = random.choice(['remove', 'add'])
        
        if operation_type == 'remove' and state[cache]:
            # Remove a random video from the cache
            video = random.choice(state[cache])
            new_load = current_loads[cache] - video_size[int(video)]
            
            if new_load >= 0:  # Ensure that removing the video does not cause negative load
                new_state = state.copy()  # Shallow copy of the dictionary
                new_state[cache] = state[cache].copy()
                new_state[cache].remove(video)  # Remove video from cache
                
                # Update the cache load
                current_loads[cache] = new_load
                neighbors.append(new_state)
                total_combinations += 1
        
        elif operation_type == 'add' and uncached_videos:
            # Add a random uncached video to the cache
            video = random.choice(list(uncached_videos))
            new_load = current_loads[cache] + video_size[video]
            
            if new_load <= cache_capacity:
                new_state = state.copy()  # Shallow copy of the dictionary
                new_state[cache] = state[cache].copy()
                new_state[cache].append(video)  # Add uncached video to the cache
                
                # Update the cache load
                current_loads[cache] = new_load
                neighbors.append(new_state)
                total_combinations += 1
        
        # Stop if we've reached the maximum number of neighbors to generate
        if total_combinations >= max_neighbors:
            break
    
    return neighbors


def state_to_key(state: dict) -> frozenset:
    return frozenset((cache, frozenset(videos)) for cache, videos in state.items())

def tabu_search(initial_solution: dict, video_size: list, endpoint_data_description: list, 
                 endpoint_cache_description: dict, request_description: dict, cache_capacity: int, 
                 max_iterations=1000, tabu_tenure=8):
    
    global file
    os.makedirs(folder_path, exist_ok=True)
    os.makedirs(folder_path_scores,exist_ok=True)
    
    tabu = {}  # Tabu dictionary (stores states and their remaining forbidden tenure)
    best = initial_solution
    best_score = score(initial_solution, endpoint_data_description, endpoint_cache_description, request_description)
    solution_id = ""
    
    iterations_without_improvement = 0  # Track stagnation
    iteration = 0  # Count iterations
    
    with open(os.path.join(folder_path, "tabu_search_results.csv"), "a", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["algorithm", "solution_id", "score"])
        
        while iteration < max_iterations and iterations_without_improvement < 500:  # Prevent infinite loops
            iteration += 1

            # **Decrease tabu tenure and remove expired entries**
            tabu = {k: v - 1 for k, v in tabu.items() if v > 1}

            candidate_list = []  # Stores all valid neighbors
            best_candidate = None
            best_candidate_score = float('-inf')
            aspiration_candidate = None
            aspiration_score = float('-inf')
            
            # **Step 1: Generate all neighbors**
            for neighbor in get_neighbors_all(best, video_size,  cache_capacity):
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
                best = best_candidate
                best_score = best_candidate_score
                tabu[state_to_key(best)] = tabu_tenure  # Mark as tabu
                iterations_without_improvement = 0  # Reset stagnation counter
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
            
            solution_id = f"solution_{iteration*1000000}.json"
            solution_path = os.path.join(folder_path_scores, solution_id)
            with open(solution_path, "a") as sol_file:
                json.dump(best, sol_file)
            csv_writer.writerow(["TabuSearch", solution_id, best_score])
            csvfile.flush()  
    print(best_score)
    
    return best


file = 'me_at_the_zoo.in'
folder_path = "tabu"
folder_path_scores = os.path.join("tabu/scores", file)
folder_path_greedy_scores = os.path.join("tabu/greedy", file)
problem_description, video_size, endpoint_data_description, endpoint_cache_description, request_description = parse_results(file)
initial_solution = get_init_solution(
    folder_path_scores=folder_path_scores,
    file_name=file,
    endpoint_data_description=endpoint_data_description,
    endpoint_cache_description=endpoint_cache_description,
    request_description=request_description
)

print(tabu_search(initial_solution, video_size, endpoint_data_description, endpoint_cache_description, request_description, problem_description[4]))
