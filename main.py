import pygame
import sys

import matplotlib.pyplot as plt

from annealing import simulated_annealing
from genetic import genetic_algorithm
from get_solutions import get_init_solution
from hill_climb import hill_climb
from parse import parse_results
from population import generate_population
from random_start import random_start
from score_functions import score
from tabu import tabu_search


def print_menu():
  print("Assignment 1 - T12G6")
  print("1 - Choose a dataset")
  print("2 - Choose a starting point")
  print("3 - Run an algorithm")
  print("4 - Quit")

def print_datasets():
  print("Choose a dataset")
  print("1 - Kittens (Large)")
  print("2 - Me at the Zoo (Small)")
  print("3 - Trending Today (Medium w/ larger caches)")
  print("4 - Videos worth Spreading (Medium w/ smaller caches)")
  print("5 - quit")

def print_start_menu():
  print("Choose a starting point")
  print("1 - Greedy")
  print("2 - Random")

def print_algorithms(dataset: str):
  print("Choose an algorithm")
  print(f"Current dataset is {dataset}")
  print("1 - Simulated Annealing")
  print("2 - Genetic Algorithm")
  print("3 - Tabu Search")
  print("4 - Hill Climb")
  print("5 - Quit")

def print_annealing_parameters(max_iterations: int, iterations_without_improvement_cap: int, initial_temperature: int, cooling_rate: float, minimum_temperature: float, neighbors_generated: int):
  print("Change any parameter")
  print(f"1 - Max Iterations (current: {max_iterations})")
  print(f"2 - Iterations without improvement cap (current: {iterations_without_improvement_cap})")
  print(f"3 - Initial Temperature (current: {initial_temperature})")
  print(f"4 - Cooling Rate (current: {cooling_rate})")
  print(f"5 - Minimum Temperature (current: {minimum_temperature})")
  print(f"6 - Generated Neighbors in each iteration (current: {neighbors_generated})")
  print("7 - Resume")

def print_genetic_parameters(generations: int, mutation_rate: float, tournament_size: int):
  print("Change any parameter")
  print(f"1 - Generations (current: {generations})")
  print(f"2 - Mutation Rate (current: {mutation_rate})")
  print(f"3 - Tournament Size (current: {tournament_size})")
  print("4 - Resume")

def print_tabu(neighbors_generated_all:bool, max_iterations: int, tabu_tenure: int,max_neighbors:int,plot:bool,it_without_improvement:int):
  print("Change any parameter")
  print(f"1 - Generate all neighbors (current: {neighbors_generated_all})")
  print(f"2 - Max Iterations (current: {max_iterations})")
  print(f"3 - Tabu Tenure (current: {tabu_tenure})")
  print(f"4 - Max_neighbors (current: {max_neighbors})")
  print(f"5 - Iterations without improvement (current: {it_without_improvement})")
  print(f"6 - Show plots (current: {plot})")
  print("7 - Resume")

def print_hillclimb( max_iterations: int, max_neighbors: int,show_plot:bool):
  print("Change any parameter")
  print(f"1 - Max Iterations (current: {max_iterations})")
  print(f"2 - Max_neighbors (current: {max_neighbors})")
  print(f"3 - Show plots (current: {show_plot})")
  print("4 - Resume")

datasets = {1: 'kittens.in.txt', 2: 'me_at_the_zoo.in', 3: 'trending_today.in', 4: 'videos_worth_spreading.in'}
dataset = 'me_at_the_zoo.in'
problem_description, video_size, endpoint_data_description, endpoint_cache_description, request_description = parse_results(dataset)
start_position_flag = 1

def handle_dataset_selection():
    global dataset, problem_description, video_size, endpoint_data_description, endpoint_cache_description, request_description
    dataset_command = 0
    while dataset_command != 5:
        print_datasets()
        try:
            dataset_command = int(input("Dataset:"))
            if dataset_command in datasets:
                dataset = datasets[dataset_command]
                problem_description, video_size, endpoint_data_description, endpoint_cache_description, request_description = parse_results(dataset)
                break
        except ValueError:
            print("Invalid input. Please try again.")

def handle_starting_point_selection():
    global start_position_flag
    print_start_menu()
    start_position_flag = int(input("Starting Point:"))
    while start_position_flag not in [1, 2]:
        print_start_menu()
        start_position_flag = int(input("Starting Point:"))

def handle_algorithm_menu():
    algorithm_command = 0
    while algorithm_command != 5:
        print_algorithms(dataset)
        try:
            algorithm_command = int(input("Algorithm:"))
            match algorithm_command:
                case 1:
                    run_simulated_annealing()
                case 2:
                    run_genetic_algorithm()
                case 3:
                    run_tabu_search()
                case 4:
                    run_hill_climb()
                case 5:
                    print("Returning to main menu.")
        except ValueError:
            print("Invalid input.")


def get_starting_position(algorithm_name):
    if start_position_flag == 1:
        return get_init_solution(
            problem_description,
            video_size,
            dataset,
            algorithm_name,
            endpoint_data_description,
            endpoint_cache_description,
            request_description
        )
    else:
        return random_start(problem_description, video_size)
def run_hill_climb():
    max_iterations = 1000
    max_neighbors = 500
    show_plot = False

    parameter_command = 0
    while parameter_command != 4:
        print_hillclimb(max_iterations, max_neighbors, show_plot)
        parameter_command = int(input("Action:"))
        match parameter_command:
            case 1:
                max_iterations = int(input("New value:"))
            case 2:
                max_neighbors = int(input("New value:"))
            case 3:
                show_plot = input("True/False:").strip().lower() == "true"

    starting_position = get_starting_position('hill_climb')

    if show_plot:
        fig, ax = plt.subplots()
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title("Hill Climbing Solution Mapping")
        solution = hill_climb(starting_position, video_size, endpoint_data_description, endpoint_cache_description,
                              request_description, problem_description[4], dataset, max_iterations, max_neighbors, show_plot, ax, fig)
        fig.canvas.draw()
        plt.show(block=True)
        plt.close("all")
    else:
        solution = hill_climb(starting_position, video_size, endpoint_data_description, endpoint_cache_description,
                              request_description, problem_description[4], dataset, max_iterations, max_neighbors, show_plot)
def run_tabu_search():
    generate_neighbors_all = False
    max_iterations = 1000
    tabu_tenure = 8
    max_neighbors = 500
    show_plot = False
    it_without_improvement = 50

    parameter_command = 0
    while parameter_command != 7:
        print_tabu(generate_neighbors_all, max_iterations, tabu_tenure, max_neighbors, show_plot, it_without_improvement)
        parameter_command = int(input("Action:"))
        match parameter_command:
            case 1:
                generate_neighbors_all = input("True/False:").strip().lower() == "true"
            case 2:
                max_iterations = int(input("New value:"))
            case 3:
                tabu_tenure = int(input("New value:"))
            case 4:
                max_neighbors = int(input("New value:"))
            case 5:
                it_without_improvement = int(input("New value:"))
            case 6:
                show_plot = input("True/False:").strip().lower() == "true"

    starting_position = get_starting_position('tabu')

    if show_plot:
        fig, ax = plt.subplots()
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title("Tabu Search Solution Mapping")
        solution = tabu_search(starting_position, video_size, endpoint_data_description, endpoint_cache_description,
                               request_description, problem_description[4], dataset, generate_neighbors_all,
                               max_neighbors, max_iterations, it_without_improvement, tabu_tenure, show_plot, ax, fig)
        fig.canvas.draw()
        plt.show(block=True)
        plt.close("all")
    else:
        solution = tabu_search(starting_position, video_size, endpoint_data_description, endpoint_cache_description,
                               request_description, problem_description[4], dataset, generate_neighbors_all,
                               max_neighbors, max_iterations, it_without_improvement, tabu_tenure, show_plot)
def run_genetic_algorithm():
    generations = 1000
    mutation_rate = 0.1
    tournament_size = 5
    population_size = 66

    parameter_command = 0
    while parameter_command != 5:
        print_genetic_parameters(generations, mutation_rate, tournament_size)
        parameter_command = int(input("Action:"))
        match parameter_command:
            case 1:
                generations = int(input("New value:"))
            case 2:
                mutation_rate = float(input("New value:"))
            case 3:
                tournament_size = int(input("New value:"))
            case 4:
                population_size = int(input("New value:"))

    starting_position = get_starting_position('genetic')
    population = generate_population(starting_position, population_size, dataset)

    solution = genetic_algorithm(
        population,
        generations,
        lambda solution: score(solution, endpoint_data_description, endpoint_cache_description, request_description),
        "./genetic",
        video_size,
        problem_description,
        mutation_rate,
        tournament_size
    )

def run_simulated_annealing():
    # Parameters
    max_iterations = 1000
    iterations_without_improvement_cap = 50
    initial_temperature = 100
    cooling_rate = 0.995
    minimum_temperature = 1e-4
    neighbors_generated = 5

    parameter_command = 0
    while parameter_command != 7:
        print_annealing_parameters(max_iterations, iterations_without_improvement_cap,
                                   initial_temperature, cooling_rate, minimum_temperature, neighbors_generated)
        parameter_command = int(input("Action:"))
        match parameter_command:
            case 1:
                max_iterations = int(input("New value:"))
            case 2:
                iterations_without_improvement_cap = int(input("New value:"))
            case 3:
                initial_temperature = int(input("New value:"))
            case 4:
                cooling_rate = float(input("New value:"))
            case 5:
                minimum_temperature = float(input("New value:"))
            case 6:
                neighbors_generated = int(input("New value:"))

    starting_position = get_starting_position('annealing')

    fig, ax = plt.subplots()
    ax.set_xlabel("iteration")
    ax.set_ylabel("score")
    ax.set_title("Simulated Annealing Solution Mapping")

    solution = simulated_annealing(
        starting_position, video_size, endpoint_data_description,
        endpoint_cache_description, request_description,
        problem_description[4], dataset, ax, fig,
        max_iterations, initial_temperature, cooling_rate,
        neighbors_generated
    )

    fig.canvas.draw()
    plt.show(block=True)
    plt.close("all")






def main_loop():
    while True:
        print_menu()
        try:
            input_command = int(input("Action:"))
        except ValueError:
            print("Please enter a valid number.")
            continue

        match input_command:
            case 1:
                handle_dataset_selection()
            case 2:
                handle_starting_point_selection()
            case 3:
                handle_algorithm_menu()
            case 4:
                print("Exited successfully :D")
                break


import pygame
import sys

pygame.init()

# Config
WIDTH, HEIGHT = 800, 600
WHITE, GRAY, BLUE = (255, 255, 255), (200, 200, 200), (0, 150, 255)
font = pygame.font.SysFont(None, 36)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Optimization Solver")

# State management
current_screen = "main_menu"

# Generic Button class
class Button:
    def __init__(self, text, x, y, w, h, callback):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.callback = callback

    def draw(self, surface):
        pygame.draw.rect(surface, GRAY, self.rect, border_radius=10)
        txt = font.render(self.text, True, (0, 0, 0))
        surface.blit(txt, (self.rect.x + 10, self.rect.y + 10))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()

# Callbacks for navigation
def go_to_algorithm_menu():
    global current_screen
    current_screen = "algorithm_menu"

def go_back():
    global current_screen
    current_screen = "main_menu"

def exit_game():
    pygame.quit()
    sys.exit()

# Placeholder for each algorithm selection
def pick_algorithm(name):
    print(f"Selected algorithm: {name}")
    # Here you'd change state to show sliders for the selected algorithm

# Main menu buttons
main_buttons = [
    Button("Select Dataset", 250, 150, 300, 50, lambda: print("Dataset menu coming soon")),
    Button("Select Starting Point", 250, 220, 300, 50, lambda: print("Starting point menu coming soon")),
    Button("Choose Algorithm", 250, 290, 300, 50, go_to_algorithm_menu),
    Button("Exit", 250, 360, 300, 50, exit_game)
]

# Algorithm selection screen
algo_buttons = [
    Button("Simulated Annealing", 250, 120, 300, 50, lambda: pick_algorithm("annealing")),
    Button("Genetic Algorithm", 250, 190, 300, 50, lambda: pick_algorithm("genetic")),
    Button("Tabu Search", 250, 260, 300, 50, lambda: pick_algorithm("tabu")),
    Button("Hill Climbing", 250, 330, 300, 50, lambda: pick_algorithm("hill_climbing")),
    Button("Back", 250, 420, 300, 50, go_back)
]

# Main loop
def run_menu():
    while True:
        screen.fill(WHITE)

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game()

            if current_screen == "main_menu":
                for b in main_buttons:
                    b.handle_event(event)
            elif current_screen == "algorithm_menu":
                for b in algo_buttons:
                    b.handle_event(event)

        # Draw UI
        if current_screen == "main_menu":
            for b in main_buttons:
                b.draw(screen)
        elif current_screen == "algorithm_menu":
            for b in algo_buttons:
                b.draw(screen)

        pygame.display.flip()

run_menu()
print("Exited sucessfully :D")
