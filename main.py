import os

from parse import parse_results
from get_solutions import get_init_solution
from random_start import random_start

from annealing import simulated_annealing
from population import generate_population
from genetic import genetic_algorithm
from score_functions import score
from tabu import tabu_search

from visual import update_plot

def print_menu():
  print("Assignment 1 - T12G6")
  print("1 - Choose a dataset")
  print("2 - Choose a starting point")
  print("3 - Run an algorithm")
  print("4 - Visualize your results")
  print("5 - Quit")

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
  print("4 - Quit")

def print_annealing_parameters(max_iterations: int, initial_temperature: int, cooling_rate: float):
  print("Change any parameter")
  print(f"1 - Max Iterations (current: {max_iterations})")
  print(f"2 - Initial Temperature (current: {initial_temperature})")
  print(f"3 - Cooling Rate (current: {cooling_rate})")
  print("4 - Resume")

def print_genetic_parameters(generations: int, mutation_rate: float, tournament_size: int):
  print("Change any parameter")
  print(f"1 - Generations (current: {generations})")
  print(f"2 - Mutation Rate (current: {mutation_rate})")
  print(f"3 - Tournament Size (current: {tournament_size})")
  print("4 - Resume")

run = True
datasets = {1: 'kittens.in.txt', 2: 'me_at_the_zoo.in', 3: 'trending_today.in', 4: 'videos_worth_spreading.in'}

while (run):
  dataset = "None"
  start_position_flag = 2
  print_menu()

  # choose dataset
  input_command = int(input())
  match input_command:
    case 1:
      dataset_command = 0
      while (dataset_command != 5):
        print_datasets()
        dataset_command = int(input())
        if (datasets[input_command]):
          dataset = datasets
          problem_description, video_size, endpoint_data_description, endpoint_cache_description, request_description = parse_results(dataset)
    
    # choose starting point
    case 2:
      while start_position_flag != 1 or start_position_flag != 2:
        print_start_menu()
        start_position_flag = int(input())

    # choose algorithm
    case 3:
      algorithm_command = 0
      while algorithm_command != 4:
        print_algorithms(dataset)
        algorithm_command = int(input())
        match algorithm_command:
          # annealing, with parameter control
          case 1:
            max_iterations=1000
            initial_temperature=100
            cooling_rate=0.99

            parameter_command = 0
            while parameter_command != 4:
              print_annealing_parameters()
              parameter_command = int(input())
              new_value = input("What is the new value you want to set?")
              match parameter_command:
                case 1:
                  max_iterations = int(new_value)
                case 2:
                  initial_temperature = int(new_value)
                case 3:
                  cooling_rate = float(new_value)

            # get the correct starting position depending on flag
            folder_path = "annealing"
            folder_path_scores = os.path.join("annealing/scores", dataset)
            if start_position_flag == 1:
              starting_position = get_init_solution(
                folder_path_scores,
                dataset,
                'annealing',
                endpoint_data_description,
                endpoint_cache_description,
                request_description
              )
            elif start_position_flag == 2:
              starting_position = random_start(problem_description, video_size)
            
            solution = simulated_annealing(starting_position, video_size, endpoint_data_description, 
                                endpoint_cache_description, request_description, problem_description[4])
          
          # genetic, with parameter control
          case 2:
            generations=1000
            mutation_rate=0.1
            tournament_size=5
            population_size=66

            parameter_command = 0
            while parameter_command != 5:
              print_genetic_parameters()
              parameter_command = int(input())
              new_value = input("What is the new value you want to set?")
              match parameter_command:
                case 1:
                  generations = int(new_value)
                case 2:
                  mutation_rate = float(new_value)
                case 3:
                  tournament_size = int(new_value)
                case 4:
                  population_size = int(new_value)
            
            # get the correct starting position depending on flag
            folder_path = "genetic"
            folder_path_scores = os.path.join("genetic/scores", dataset)
            if start_position_flag == 1:
              starting_position = get_init_solution(
                folder_path_scores,
                dataset,
                'genetic',
                endpoint_data_description,
                endpoint_cache_description,
                request_description
              )
            elif start_position_flag == 2:
              starting_position = random_start(problem_description, video_size)
            
            population = generate_population(starting_position, population_size, dataset)
            solution = genetic_algorithm(
              population, 
              generations, 
              lambda solution: score(solution, endpoint_data_description, endpoint_cache_description, request_description),
              mutation_rate,
              tournament_size
              )

          # tabu
          case 3: 
            folder_path = "tabu"
            folder_path_scores = os.path.join("tabu/scores", dataset)
            
            # get the correct starting position
            folder_path_greedy_scores = os.path.join("tabu/greedy", dataset)
            if start_position_flag == 1:
              starting_position = get_init_solution(
                folder_path_scores,
                dataset,
                'tabu',
                endpoint_data_description,
                endpoint_cache_description,
                request_description
              )
            elif start_position_flag == 2:
              starting_position = random_start(problem_description, video_size)

            solution = tabu_search(starting_position, video_size, endpoint_data_description, endpoint_cache_description, request_description, problem_description[4])

      case 4:
        print("Showing last solution")
        update_plot(solution, )
      
    case 5:
      run = False

print("Exited sucessfully :D")