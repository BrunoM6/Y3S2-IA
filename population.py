import random
import copy
import csv
import json
import os
from get_solutions import convert_keys_to_int
from parse import parse_results

def mutate_solution(solution, video_size, problem_description, mutation_rate=0.2):
    """Apply small mutations to greedy."""
    new_solution = copy.deepcopy(solution)

    for cache_id in new_solution:
        if random.random() < mutation_rate and new_solution[cache_id]:  
            # Remove random video
            removed_video = random.choice(new_solution[cache_id])
            new_solution[cache_id].remove(removed_video)

            # Check current cache load
            current_load = sum(video_size[v] for v in new_solution[cache_id])

            # Try adding new video (if it fits, else ignore)
            new_video = random.randint(0, len(video_size) - 1)
            if new_video not in new_solution[cache_id] and (current_load + video_size[new_video] <= problem_description[4]):
                new_solution[cache_id].append(new_video)

    return new_solution

def random_solution(video_size, problem_description):
    """Generate a random solution."""
    solution = {}

    for cache_id in range(problem_description[3]):  
        solution[cache_id] = []
        current_load = 0 

        # Shuffle video IDs and add them until cap is reached
        available_videos = list(range(len(video_size)))
        random.shuffle(available_videos)

        for video in available_videos:
            if current_load + video_size[video] <= problem_description[4]:
                solution[cache_id].append(video)
                current_load += video_size[video]

    return solution

def import_existent(file, video_size, problem_description):
    csv_path = "genetic/genetic.csv"
    solutions = []
    
    # Read the CSV file to get available solutions
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)
        for row in reader:
            if len(row) >= 2:
                solutions.append(row[1])
    
    if not solutions:
        return random_solution(video_size, problem_description)
    
    # Select a random solution
    selected_solution = random.choice(solutions)
    solution_path = os.path.join(f"genetic/scores/{file}", selected_solution)
    
    # Load and parse the JSON solution file
    with open(solution_path, 'r') as jsonfile:
        solution = convert_keys_to_int(json.load(jsonfile))
    
    return solution

def generate_population(greedy_solution, population_size=15, file='me_at_the_zoo.in'):
    """Generate a population of solutions with a mix of greedy, mutated, and pre-computed solutions."""
    problem_description, video_size, endpoint_data_description, endpoint_cache_description, request_description = parse_results(file)
    population = []

    if(population_size % 3 != 0):
        portion_sizes = [population_size //3, population_size//3 + population_size % 3, population_size //3]
    else:
        portion_sizes = [population_size // 3 for i in range (3)]

    # greedy duplicates
    for _ in range(portion_sizes[0]):
        population.append(copy.deepcopy(greedy_solution))

    # Mutated Greedy Solutions
    for _ in range(portion_sizes[1]):
        mutated = mutate_solution(greedy_solution, video_size, problem_description)
        population.append(mutated)

    # Pre computed solutions (if not enough, fill with)
    for _ in range(portion_sizes[2]):
        random_sol = import_existent(file,video_size, problem_description)
        population.append(random_sol)

    return population



