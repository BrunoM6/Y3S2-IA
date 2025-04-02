import random
import copy
from greedy import greedy_start
from population import generate_population, mutate_solution
from score_functions import score
from parse import parse_results

# Set parameters (can adjust these to test what results different parameters can achieve)
generations = 100  # Number of generations
mutation_rate = 0.2  # Mutation rate
tournament_size = 3  # Tournament selection size
file = 'me_at_the_zoo.in' # Data file
population_size = 15 # Population size

def tournament_selection(population, fitness_func, tournament_size=3):
    """Selects a parent using tournament selection."""
    tournament = random.sample(population, tournament_size)
    best_individual = max(tournament, key=fitness_func)
    return best_individual

def crossover(parent1, parent2):
    """Perform crossover (swap videos between caches) to produce an offspring."""
    # avoid modifying the original solutions
    offspring = copy.deepcopy(parent1)

    # Select random cache ids 
    cache1, cache2 = random.sample(list(parent1.keys()), 2)

    # Swap the videos between these two caches
    offspring[cache1], offspring[cache2] = parent2[cache1], parent2[cache2]

    return offspring

def genetic_algorithm(population, generations, fitness_func, mutation_rate=0.2, tournament_size=3, elitism=True):
    best_solution = max(population, key=fitness_func) 
    best_score = fitness_func(best_solution)

    for generation in range(generations):
        new_population = []

        # Keep the best solution
        if elitism:
            new_population.append(best_solution)

        # Generate the rest of the population
        while len(new_population) < population_size:
            # Tournament selection to choose parents
            parent1 = tournament_selection(population, fitness_func, tournament_size)
            parent2 = tournament_selection(population, fitness_func, tournament_size)

            # produce offspring
            offspring = crossover(parent1, parent2)

            mutated_offspring = mutate_solution(offspring,video_size, problem_description, mutation_rate)

            new_population.append(mutated_offspring)

        # Update population
        population = new_population

        # best solution in the current generation
        current_best_solution = max(population, key=fitness_func)
        current_best_score = fitness_func(current_best_solution)

        # If the new best solution is better, update the global best 
        if current_best_score > best_score:
            best_solution = current_best_solution
            best_score = current_best_score

        print(f"Generation {generation + 1}: Best score = {best_score}")

    return best_solution


problem_description, video_size, endpoint_data_description, endpoint_cache_description, request_description = parse_results(file)

# Generate initial population 
greedy_solution = greedy_start() 
population = generate_population(greedy_solution, population_size, file) 

# Run the genetic algorithm
best_solution = genetic_algorithm(
    population,
    generations,
    lambda solution: score(solution, endpoint_data_description, endpoint_cache_description, request_description),
    mutation_rate,
    tournament_size
)

print("Best solution found:", best_solution)