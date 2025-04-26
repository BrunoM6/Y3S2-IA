def score(solution: dict, endpoint_data_description: list, endpoint_cache_description: dict, request_description: dict, old_solution: dict= None, old_score: int=None, change=None) -> int:
    # map endpoint to the cache latencies for ease of use 
    endpoint_to_caches = {}
    for (endpoint_id, cache_id), latency in endpoint_cache_description.items():
        endpoint_to_caches.setdefault(endpoint_id, []).append((cache_id, latency))
   
    # computing score for first time
    if old_solution is None or old_score is None or change is None:
        total_time_saved = 0
        total_requests = 0

        # in each request get the best latency and compare to the data center to get the score
        for (endpoint, video), request_number in request_description.items():
            data_center_latency = endpoint_data_description[endpoint]
            best_latency = data_center_latency

            for cache_id, cache_latency in endpoint_to_caches.get(endpoint, []):
                if cache_id in solution and video in solution[cache_id]:
                    if cache_latency < best_latency:
                        best_latency = cache_latency
                    if best_latency == 0:
                        break
            
            total_time_saved += (data_center_latency - best_latency) * request_number
            total_requests += request_number

        if total_requests == 0:
            print("Something went wrong! Division by 0 in scoring")
            return 0
        
        return (total_time_saved * 1000) // total_requests

    # optimization, compute the difference of latencies in the changes only and use weighted average
    else:
        total_requests = sum(int(request_number) for _, request_number in request_description.items())
        if total_requests == 0:
            print("Something went wrong! Division by 0 in scoring")
            return 0
        
        modified_caches = set()
        op = change[0]
        if op in ("add", "remove"):
            modified_caches.add(change[2])
        elif op == "swap":
            modified_caches.add(change[2])
            modified_caches.add(change[4])
        
        affected_endpoints = set()
        for (endpoint_id, cache_id), latency in endpoint_cache_description.items():
            if cache_id in modified_caches:
                affected_endpoints.add(endpoint_id)

        delta_time_saved = 0

        for (endpoint, video), request_number in request_description.items():
            if endpoint in affected_endpoints:
                request_number = int(request_number)
                
                data_center_latency = endpoint_data_description[endpoint]
                best_latency_old = data_center_latency
                best_latency_new = data_center_latency

                for cache_id, cache_latency in endpoint_to_caches.get(endpoint, []):
                    if cache_id in old_solution and video in old_solution[cache_id]:
                        best_latency_old = min(best_latency_old, cache_latency)
                    if cache_id in solution and video in solution[cache_id]:
                        best_latency_new = min(best_latency_new, cache_latency)
                
                delta_time_saved += (best_latency_old - best_latency_new) * request_number

        old_total_saved = (old_score * total_requests) // 1000
        return ((old_total_saved + delta_time_saved) * 1000) // total_requests
    