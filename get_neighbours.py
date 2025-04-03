import random




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

def get_neighbors_all(state: dict, video_size: list, cache_capacity: int, max_neighbors: int = 10):
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
