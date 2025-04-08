import csv
import json
import os
import random
import re

from get_neighbours import get_neighbors, get_neighbors_all, state_to_key
from score_functions import score
from visual import update_plot_batch


def tabu_search(initial_solution: dict, video_size: list, endpoint_data_description: list, endpoint_cache_description: dict, request_description: dict, cache_capacity: int, dataset: str, get_all: bool, max_neighbors: int, max_iterations: int, iteration_without_improvement: int, tabu_tenure: int, show_plot: bool, ax=None, fig=None):

    folder_path_scores = f"results/{dataset}/tabu"
    folder_path = f"scores/{dataset}"
    os.makedirs(folder_path, exist_ok=True)
    os.makedirs(folder_path_scores, exist_ok=True)

    solution_positions = {}
    max_json_number = 0
    result_file = None

    for file2 in os.listdir(folder_path_scores):
        match = re.match(r"solution_(\d+)\.json$", file2)
        if match:
            file_id = int(match.group(1))
            if file_id > max_json_number:
                max_json_number = file_id
                result_file = file2

    print(f"Best file: {result_file}")

    # Initial score with full computation
    best_latencies = None
    best_score, best_latencies = score(initial_solution, endpoint_data_description, endpoint_cache_description, request_description)
    best = initial_solution
    initial_score = best_score
    tabu = {}
    iteration = 0
    iterations_without_improvement = 0

    with open(os.path.join(folder_path, "tabu.csv"), "a", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        if not os.path.exists(folder_path_scores):
            csv_writer.writerow(["algorithm", "solution_id", "score"])

        while iteration < max_iterations and iterations_without_improvement < iteration_without_improvement:
            iteration += 1
            tabu = {k: v - 1 for k, v in tabu.items() if v > 1}
            candidate_list = []
            best_candidate = None
            best_candidate_score = float('-inf')
            best_candidate_latencies = None
            aspiration_candidate = None
            aspiration_score = float('-inf')
            aspiration_latencies = None

            # Generate neighbors
            if get_all:
                neighbors = get_neighbors_all(best, video_size, cache_capacity, max_neighbors)
            else:
                neighbors = get_neighbors(best, video_size, cache_capacity)

            for neighbor, change in neighbors:
                neighbor_score, neighbor_latencies = score(
                    neighbor,
                    endpoint_data_description,
                    endpoint_cache_description,
                    request_description,
                    old_solution=best,
                    old_score=int(best_score),
                    change=change,
                    old_best_latencies=best_latencies
                )
                candidate_key = state_to_key(neighbor)
                if candidate_key not in tabu:
                    if neighbor_score > best_candidate_score:
                        best_candidate = neighbor
                        best_candidate_score = neighbor_score
                        best_candidate_latencies = neighbor_latencies
                elif neighbor_score > best_score and neighbor_score > aspiration_score:
                    aspiration_candidate = neighbor
                    aspiration_score = neighbor_score
                    aspiration_latencies = neighbor_latencies

            if best_candidate:
                best = best_candidate
                best_score = best_candidate_score
                best_latencies = best_candidate_latencies
                tabu[state_to_key(best)] = tabu_tenure
                if best_score > initial_score:
                    iterations_without_improvement = 0
                else:
                    iterations_without_improvement += 1
            elif aspiration_candidate:
                best = aspiration_candidate
                best_score = aspiration_score
                best_latencies = aspiration_latencies
                tabu[state_to_key(best)] = tabu_tenure
                iterations_without_improvement = 0
            elif neighbors:
                random_neighbor, _ = random.choice(neighbors)
                best = random_neighbor
                best_score, best_latencies = score(best, endpoint_data_description, endpoint_cache_description, request_description)
                iterations_without_improvement += 1
            else:
                iterations_without_improvement += 1

            solution_id = f"solution_{max_json_number + iteration}.json"
            solution_path = os.path.join(folder_path_scores, solution_id)
            with open(solution_path, "w") as sol_file:
                json.dump(best, sol_file)
            csv_writer.writerow(["TabuSearch", solution_id, best_score])
            csvfile.flush()

            # Optional plotting
            if show_plot:
                neighbor_edges = [(best, neighbor) for neighbor, _ in neighbors]
                plotted_solutions = set()
                for idx, edge in enumerate(neighbor_edges):
                    if idx % 300 == 0:
                        update_plot_batch([edge], solution_positions, ax, fig, plotted_solutions)

    if best_score > initial_score:
        print(best_score)
        return best
    else:
        print(initial_score)
        return initial_solution
