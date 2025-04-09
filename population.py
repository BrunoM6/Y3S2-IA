import random
import copy
import csv
import json
import os
from get_solutions import convert_keys_to_int
from parse import parse_results
from greedy import greedy_start
from get_neighbours import get_neighbors_all
from random_start import random_start



def mutate_solution(solution, video_size, problem_description, mutation_rate=0.2):
    """Mutate a solution by picking a random neighbor from get_neighbors_all based on mutation_rate."""
    if random.random() > mutation_rate:
        return copy.deepcopy(solution)  

    cache_capacity = problem_description[4]
    neighbors = get_neighbors_all(solution, video_size, cache_capacity, max_neighbors=50)

    if neighbors:
        mutated_solution, _ = random.choice(neighbors)
        return mutated_solution
    else:
        return copy.deepcopy(solution)  # fallback if no neighbors generated

def import_existent(file, video_size, problem_description):
    csv_path = "genetic/genetic.csv"
    solutions = []

    if not os.path.exists(csv_path):
        return random_start(problem_description, video_size)
    
    # Read the CSV file to get available solutions
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)
        for row in reader:
            if len(row) >= 2:
                solutions.append(row[1])
    
    if not solutions:
        return random_start(problem_description, video_size)
    
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

    # Pre computed solutions (if not enough, fill with random ones)
    for _ in range(portion_sizes[2]):
        random_sol = import_existent(file,video_size, problem_description)
        population.append(random_sol)

    return population



