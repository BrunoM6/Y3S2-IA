import random


def parse_results(file_name: str):
    problem_description = []
    video_size = []
    endpoint_data_description = []
    endpoint_cache_description = {}
    request_description = {}
    with open('data/' + file_name, 'r') as file:
        line = file.readline()
        tokens = line.strip().split()
        for token in tokens:
            problem_description.append(int(token))
        line = file.readline()
        tokens = line.strip().split()
        for token in tokens:
            video_size.append(int(token))
        i = 0
        while i != problem_description[1]:
            line = file.readline()
            tokens = line.strip().split()
            endpoint_data_description.append(int(tokens[0]))
            connections = int(tokens[1])
            j = 0
            while j < connections:
                line = file.readline()
                tokens = line.strip().split()
                endpoint_cache_description[(i, tokens[0])] = tokens[1]
                j += 1
            i += 1
        i = 0
        while i != problem_description[2]:
            i+=1
            line = file.readline()
            tokens = line.strip().split()
            key = (tokens[1], tokens[0])
            if key in request_description:
                request_description[key] += tokens[2]
            else:
                request_description[key] = tokens[2]
    return problem_description, video_size, endpoint_data_description, endpoint_cache_description, request_description

def score(problem_state: dict, endpoint_data_description: list, endpoint_cache_description: dict, request_description: dict) -> int:
    total_time_saved = 0
    total_requests = 0

    for (endpoint, video), request_number in request_description.items():
        request_number = int(request_number)
        total_requests += request_number

        data_center_latency = int(endpoint_data_description[int(endpoint)])
        best_latency = data_center_latency

        for cache, videos in problem_state.items():
            if video in videos:
                cache_latency = int(endpoint_cache_description.get((int(endpoint), int(cache)), data_center_latency))
                best_latency = min(best_latency, cache_latency)

        time_saved = (data_center_latency - best_latency) * request_number
        total_time_saved += time_saved

    if total_requests == 0:
        return 0  # Avoid division by zero

    average_time_saved_per_request = total_time_saved / total_requests
    score_in_microseconds = int(average_time_saved_per_request * 1000)  # Convert to microseconds and round down
    return score_in_microseconds


def compute_benefit(video, cache, endpoint_data_description, endpoint_cache_description, request_description):
    benefit = 0
    for (endpoint, v), requests in request_description.items():
        if int(v) != int(video):
            continue
        # Get the data center latency for this endpoint.
        dc_latency = int(endpoint_data_description[int(endpoint)])
        # Get the latency from this cache to the endpoint (or use dc_latency if not connected)
        cache_latency = int(endpoint_cache_description.get((int(endpoint), int(cache)), dc_latency))
        improvement = dc_latency - cache_latency
        if improvement > 0:
            benefit += improvement * int(requests)
    return benefit

def get_neighbors(state: dict, video_size: list,
                  endpoint_data_description: list, endpoint_cache_description: dict,
                  request_description: dict, cache_capacity: int):
    neighbors = []
    cache_ids = list(state.keys())
    
    # Precompute current load for each cache to avoid repeated summation.
    current_loads = {
        cache: sum(video_size[v] for v in state[cache])
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
                    new_load_a = current_loads[cache_a] - video_size[video_a] + video_size[video_b]
                    new_load_b = current_loads[cache_b] - video_size[video_b] + video_size[video_a]
                    if new_load_a > cache_capacity or new_load_b > cache_capacity:
                        continue  # Skip swaps that violate capacity
                    
                    # Compute the heuristic benefit for each video in its current cache
                    # and in the swapped cache.
                    benefit_a_in_a = compute_benefit(video_a, cache_a, endpoint_data_description,
                                                      endpoint_cache_description, request_description)
                    benefit_a_in_b = compute_benefit(video_a, cache_b, endpoint_data_description,
                                                      endpoint_cache_description, request_description)
                    benefit_b_in_b = compute_benefit(video_b, cache_b, endpoint_data_description,
                                                      endpoint_cache_description, request_description)
                    benefit_b_in_a = compute_benefit(video_b, cache_a, endpoint_data_description,
                                                      endpoint_cache_description, request_description)
                    
                    # Calculate the net benefit delta of swapping:
                    # (benefit of video_b in cache_a + benefit of video_a in cache_b)
                    # minus (benefit of video_a in cache_a + benefit of video_b in cache_b)
                    delta = (benefit_b_in_a + benefit_a_in_b) - (benefit_a_in_a + benefit_b_in_b)
                    
                    # Only consider promising swaps (delta > 0).
                    if delta > 0:
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


def state_to_key(state: dict) -> frozenset:
    return frozenset((cache, frozenset(videos)) for cache, videos in state.items())

def tabu_search(initial_solution: dict, video_size: list, endpoint_data_description: list, endpoint_cache_description: dict, request_description: dict, cache_capacity: int, max_iterations=500, tabu_tenure=8):

    tabu = {}  # Tabu dictionary (stores states and their remaining forbidden tenure)
    best = initial_solution
    best_score = score(initial_solution, endpoint_data_description, endpoint_cache_description, request_description)
    
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
        
    return best




problem_description, video_size, endpoint_data_description, endpoint_cache_description, request_description = parse_results('kittens.in.txt')

print(tabu_search({},video_size,endpoint_data_description,endpoint_cache_description,request_description,problem_description[4]))
