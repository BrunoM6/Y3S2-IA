def greedy_start(problem_description:list, video_size: list, endpoint_data_description: list, endpoint_cache_description: dict, request_description: dict):
    # initialize important values 
    num_caches = problem_description[3]
    cache_capacity = problem_description[4]

    # empty solution dictionary
    solution = {cache: [] for cache in range(num_caches)}
    current_loads = {cache: 0 for cache in range(num_caches)}

    # precomputed map endpoint to list of cache and latencies for speed
    endpoint_to_caches = {}
    for (endpoint, cache), latency in endpoint_cache_description.items():
        endpoint_to_caches.setdefault(endpoint, []).append((cache, latency))

    # precomputed score for each video candidate (total saved time if that video is stored in the cache)
    scores = {}
    for (endpoint, video), request_number in request_description.items():
        data_center_latency = endpoint_data_description[endpoint]

        for cache, cache_latency in endpoint_to_caches.get(endpoint, []):
            if cache_latency < data_center_latency:
                saved_time = (data_center_latency - cache_latency) * request_number
                scores[(cache, video)] = scores.get((cache, video), 0) + saved_time
    
    # create candidate list and sort by saved time
    candidates = [(cache, video, saved_time) for (cache, video), saved_time in scores.items()]
    candidates.sort(key=lambda x: x[2], reverse=True)
    
    # assign videos to caches 
    for cache, video, saved_time in candidates:
        # if video is in cache, skip
        if video in solution[cache]:
            continue
        # if fits, add
        if current_loads[cache] + video_size[video] <= cache_capacity:
            solution[cache].append(video)
            current_loads[cache] += video_size[video]
    
    return solution