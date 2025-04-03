import random
import copy
import os
import json
import csv
from greedy import greedy_start
from population import generate_population, mutate_solution
from score_functions import score
from parse import parse_results

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
    max_json_number = 0
    best_solution = max(population, key=fitness_func) 
    best_score = fitness_func(best_solution)
    os.makedirs(folder_path, exist_ok=True)
    os.makedirs(folder_path_scores, exist_ok=True)

    csv_path = os.path.join(folder_path, "genetic.csv")

    # Ensure the CSV file exists and has a header
    if not os.path.exists(csv_path):
        with open(csv_path, "w", newline="") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["algorithm", "solution_id", "score"])

    for generation in range(generations):
        new_population = []

        # Keep the best solution
        if elitism:
            new_population.append(best_solution)

        # Generate the rest of the population
        while len(new_population) < population_size:
            parent1 = tournament_selection(population, fitness_func, tournament_size)
            parent2 = tournament_selection(population, fitness_func, tournament_size)
            offspring = crossover(parent1, parent2)
            mutated_offspring = mutate_solution(offspring, video_size, problem_description, mutation_rate)
            new_population.append(mutated_offspring)

        population = new_population

        # Best solution in the current generation
        current_best_solution = max(population, key=fitness_func)
        current_best_score = fitness_func(current_best_solution)

        # If a new best solution is found, update CSV
        if current_best_score > best_score:
            best_solution = current_best_solution
            best_score = current_best_score
            solution_id = f"solution_{max_json_number+generation}.json"
            solution_path = os.path.join(folder_path_scores, solution_id)

            # Save the solution as JSON (overwrite previous content)
            with open(solution_path, "w") as sol_file:
                json.dump(best_solution, sol_file)

            # **Read existing CSV and update the specific generation**
            updated_rows = []
            found = False

            # Read and update existing rows
            with open(csv_path, "r", newline="") as csvfile:
                csv_reader = csv.reader(csvfile)
                if os.path.getsize(csv_path) > 0:
                    header = next(csv_reader)  # Read header
                for row in csv_reader:
                    if row[1] == solution_id:  # If the solution exists, update the score
                        row[2] = str(best_score)
                        found = True
                    updated_rows.append(row)

            # If the solution wasn't in the CSV, add it as a new row
            if not found:
                updated_rows.append(["GeneticAlgorithm", solution_id, str(best_score)])

            # Write the updated CSV back
            with open(csv_path, "w", newline="") as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(["algorithm", "solution_id", "score"])
                csv_writer.writerows(updated_rows)  # Write updated data
            
            print(f"Generation {generation + 1}: Best score = {best_score}")

    return best_solution
