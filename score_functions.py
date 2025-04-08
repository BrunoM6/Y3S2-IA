def score(
    solution: dict,
    endpoint_data_description: list,
    endpoint_cache_description: dict,
    request_description: dict,
    old_solution: dict = None,
    old_score: int = None,
    change=None,
    old_best_latencies: dict = None
) -> tuple[int, dict]:
    """
    Returns a tuple (score, best_latencies), so you can reuse best_latencies in future calls.
    """
    # Precompute endpoint → [ (cache_id, latency) ]
    endpoint_to_caches = {}
    for (endpoint_id, cache_id), latency in endpoint_cache_description.items():
        endpoint_to_caches.setdefault(endpoint_id, []).append((cache_id, latency))

    total_requests = sum(request_description.values())
    if total_requests == 0:
        print("Something went wrong! Division by 0 in scoring")
        return 0, {}

    # Helper to get best latency of a video at an endpoint
    def best_latency(endpoint, video, sol):
        dc_latency = endpoint_data_description[endpoint]
        for cache_id, latency in sorted(endpoint_to_caches.get(endpoint, []), key=lambda x: x[1]):
            if video in sol.get(cache_id, []):
                return latency
        return dc_latency

    # If no prior score/caching, do full evaluation
    if old_solution is None or old_score is None or change is None or old_best_latencies is None:
        best_latencies = {}
        total_saved = 0

        for (endpoint, video), reqs in request_description.items():
            best_lat = best_latency(endpoint, video, solution)
            best_latencies[(endpoint, video)] = best_lat
            total_saved += (endpoint_data_description[endpoint] - best_lat) * reqs

        return (total_saved * 1000) // total_requests, best_latencies

    # Incremental fast update
    modified_caches = set()
    op = change[0]

    if op in ("add", "remove"):
        modified_caches.add(change[2])
    elif op == "swap":
        modified_caches.update([change[2], change[4]])

    affected_endpoints = {
        e for (e, c) in endpoint_cache_description if c in modified_caches
    }

    delta_saved = 0
    new_best_latencies = old_best_latencies.copy()

    for (endpoint, video), reqs in request_description.items():
        if endpoint not in affected_endpoints:
            continue  # no change in latency for this endpoint

        old_lat = old_best_latencies.get((endpoint, video), endpoint_data_description[endpoint])
        new_lat = best_latency(endpoint, video, solution)
        new_best_latencies[(endpoint, video)] = new_lat

        delta_saved += (old_lat - new_lat) * reqs

    # Apply delta
    old_total_saved = (old_score * total_requests) // 1000
    new_total_saved = old_total_saved + delta_saved
    return (new_total_saved * 1000) // total_requests, new_best_latencies
