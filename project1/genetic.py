import random
import copy
import os
import json
import csv
import matplotlib.pyplot as plt
from population import mutate_solution
from visual import update_score

def tournament_selection(population, fitness_func, tournament_size=3):
    tournament = random.sample(population, tournament_size)
    best_individual = max(tournament, key=fitness_func)
    return best_individual

def crossover(parent1, parent2):
    offspring = copy.deepcopy(parent1)
    cache1, cache2 = random.sample(list(parent1.keys()), 2)
    offspring[cache1], offspring[cache2] = parent2[cache1], parent2[cache2]
    return offspring

def genetic_algorithm(population,generations,fitness_func,video_size,problem_description,dataset,mutation_rate=0.2,tournament_size=3,show_plot=False,elitism=True):
    max_json_number = 0
    folder_path_scores = f"results/{dataset}/genetic"
    population_size = len(population)
    best_solution = max(population, key=fitness_func) 
    best_score = fitness_func(best_solution)
    os.makedirs(f"scores/{dataset}", exist_ok=True)
    os.makedirs(folder_path_scores, exist_ok=True)

    csv_path = os.path.join(f"scores/{dataset}", "genetic.csv")

    # Setup score visualization
    if show_plot:
        plt.ion()
        fig_score, ax_score = plt.subplots()
        ax_score.set_title("Genetic Algorithm Progress")
        ax_score.set_xlabel("Generation")
        ax_score.set_ylabel("Best Fitness Score")

    # Ensure CSV exists
    if not os.path.exists(csv_path):
        with open(csv_path, "w", newline="") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["algorithm", "solution_id", "score"])

    for generation in range(generations):
        new_population = []

        if elitism:
            new_population.append(best_solution)

        while len(new_population) < population_size:
            parent1 = tournament_selection(population, fitness_func, tournament_size)
            parent2 = tournament_selection(population, fitness_func, tournament_size)
            offspring = crossover(parent1, parent2)
            mutated_offspring = mutate_solution(offspring, video_size, problem_description, mutation_rate)
            new_population.append(mutated_offspring)

        population = new_population
        current_best_solution = max(population, key=fitness_func)
        current_best_score = fitness_func(current_best_solution)

        if current_best_score > best_score:
            best_solution = current_best_solution
            best_score = current_best_score
            solution_id = f"solution_{max_json_number + generation}.json"
            solution_path = os.path.join(folder_path_scores, solution_id)

            with open(solution_path, "w") as sol_file:
                json.dump(best_solution, sol_file)

            updated_rows = []
            found = False

            with open(csv_path, "r", newline="") as csvfile:
                csv_reader = csv.reader(csvfile)
                if os.path.getsize(csv_path) > 0:
                    header = next(csv_reader)
                for row in csv_reader:
                    if row[1] == solution_id:
                        row[2] = str(best_score)
                        found = True
                    updated_rows.append(row)

            if not found:
                updated_rows.append(["GeneticAlgorithm", solution_id, str(best_score)])

            with open(csv_path, "w", newline="") as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(["algorithm", "solution_id", "score"])
                csv_writer.writerows(updated_rows)

        print(f"Generation {generation + 1}: Best score = {best_score}")

        if show_plot:
            update_score((generation + 1, current_best_score), ax_score, fig_score)

    if show_plot:
        plt.ioff()
        plt.show()

    return best_solution