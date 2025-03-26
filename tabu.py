import random
import pygame
from greedy import greedy_start
from parse import parse_results



def score(solution: dict, endpoint_data_description: list, endpoint_cache_description: dict, request_description: dict) -> int:
    total_time_saved = 0
    total_requests = 0

    for (endpoint, video), request_number in request_description.items():
        request_number = int(request_number)
        total_requests += request_number

        data_center_latency = int(endpoint_data_description[int(endpoint)])
        best_latency = data_center_latency

        # Consider only caches connected to this endpoint
        for cache, cache_latency in endpoint_cache_description.items():
            if int(cache[0]) == int(endpoint):  # Check if this cache is linked to the endpoint
                cache_id = cache[1]
                if video in solution[int(cache_id)]:  # Ensure `video` is a string
                    # print(best_latency,int(cache_latency))
                    best_latency = min(best_latency, int(cache_latency))
                    # print(best_latency)

        time_saved = (data_center_latency - best_latency) * request_number
        total_time_saved += time_saved

    if total_requests == 0:
        return 0  # Avoid division by zero

    # Convert to microseconds and round down
    return total_time_saved * 1000 // total_requests

def get_neighbors(state: dict, video_size: list, endpoint_data_description: list, endpoint_cache_description: dict, request_description: dict, cache_capacity: int):
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

# def get_neighbors_all():
#     neighbo


def state_to_key(state: dict) -> frozenset:
    return frozenset((cache, frozenset(videos)) for cache, videos in state.items())

def tabu_search(initial_solution: dict, video_size: list, endpoint_data_description: list, endpoint_cache_description: dict, request_description: dict, cache_capacity: int, max_iterations=500, tabu_tenure=8):

    tabu = {}  # Tabu dictionary (stores states and their remaining forbidden tenure)
    best = initial_solution
    best_score = score(initial_solution, endpoint_data_description, endpoint_cache_description, request_description)
    print(best_score)
    
    iterations_without_improvement = 0  # Track stagnation
    iteration = 0  # Count iterations
    
    while iteration < max_iterations and iterations_without_improvement < 100:  # Prevent infinite loops
        iteration += 1

        # **Decrease tabu tenure and remove expired entries**
        tabu = {k: v - 1 for k, v in tabu.items() if v > 1}

        candidate_list = []  # Stores all valid neighbors
        best_candidate = None
        best_candidate_score = float('-inf')
        aspiration_candidate = None
        aspiration_score = float('-inf')
        
        # **Step 1: Generate all neighbors**
        for neighbor in get_neighbors(best, video_size, endpoint_data_description, 
                                      endpoint_cache_description, request_description, cache_capacity):
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
    print(best_score)
    return best

problem_description, video_size, endpoint_data_description, endpoint_cache_description, request_description = parse_results('me_at_the_zoo.in')
print(tabu_search(greedy_start(),video_size,endpoint_data_description,endpoint_cache_description,request_description,problem_description[4]))
