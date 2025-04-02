from parse import parse_results

def greedy_start():
    # empty solution dictionary
    solution = {cache: [] for cache in range(problem_description[3])}
    cache_cap = problem_description[4]
    scores = {}

    # calculate scores
    for (endpoint, video) in request_description.keys():
        for element in endpoint_cache_description.keys():
            if int(element[0]) == int(endpoint):
                cache = element[1]
                saved_time = get_saved_time(element, video)
                #if exists
                if (cache, video) in scores:
                    scores[(cache,video)] += saved_time
                #if not
                else:
                    scores[(cache, video)] = saved_time
                    
    scores = [(cache,video,saved_time) for (cache, video), saved_time in scores.items()]


    # sort (video, cache, cost) by cost (desc)
    scores.sort(key=lambda a: a[2], reverse=True)

    # iterate through scores and fill caches
    for (cache, video, sc) in scores:
        curr_cap = current_cap(cache, solution)
        if (curr_cap < cache_cap) and (video_size[int(video)] + curr_cap <= cache_cap) and (video not in solution[int(cache)]):
            solution[int(cache)].append(video)


    # return greedy solution
    return solution

def get_saved_time(element, video):
    (endpoint, cache) = element

    data_center_latency = endpoint_data_description[int(endpoint)]
    cache_latency = endpoint_cache_description[element]
    
    request_number = request_description.get((f"{endpoint}", f"{video}"), 0)
    
    return (int(data_center_latency) - int(cache_latency)) * int(request_number)


def current_cap(cache, solution):
    return sum(video_size[int(v)] for v in solution[int(cache)])

problem_description, video_size, endpoint_data_description, endpoint_cache_description, request_description = parse_results('me_at_the_zoo.in')

