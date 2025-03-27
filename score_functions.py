
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
                if video in solution[(cache_id)]:  
                    # print(best_latency,int(cache_latency))
                    best_latency = min(best_latency, int(cache_latency))
                    # print(best_latency)

        time_saved = (data_center_latency - best_latency) * request_number
        total_time_saved += time_saved

    if total_requests == 0:
        return 0  # Avoid division by zero

    # Convert to microseconds and round down
    return total_time_saved * 1000 // total_requests
