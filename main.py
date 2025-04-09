import os

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

def print_annealing_parameters(max_iterations: int, iterations_without_improvement_cap: int, initial_temperature: int, cooling_rate: float, minimum_temperature: float, neighbors_generated: int,show_plot:bool,get_all_neighbors:bool):
  print("Change any parameter")
  print(f"1 - Max Iterations (current: {max_iterations})")
  print(f"2 - Iterations without improvement cap (current: {iterations_without_improvement_cap})")
  print(f"3 - Initial Temperature (current: {initial_temperature})")
  print(f"4 - Cooling Rate (current: {cooling_rate})")
  print(f"5 - Minimum Temperature (current: {minimum_temperature})")
  print(f"6 - Generated Neighbors in each iteration (current: {neighbors_generated})")
  print(f"7 - Show plot (current: {show_plot})")
  print(f"8 - Search All Neighbors (current: {get_all_neighbors})")
  print("9 - Resume")

def print_genetic_parameters(generations: int, mutation_rate: float, tournament_size: int, population_size: int):
  print("Change any parameter")
  print(f"1 - Generations (current: {generations})")
  print(f"2 - Mutation Rate (current: {mutation_rate})")
  print(f"3 - Tournament Size (current: {tournament_size})")
  print(f"4 - Population Size (current: {population_size})")
  print(f"5 - Show plots (current: {show_plot})")
  print("6 - Resume")

def print_tabu(neighbors_generated_all:bool, max_iterations: int, tabu_tenure: int,max_neighbors:int,plot:bool,it_without_improvement:int):
  print("Change any parameter")
  print(f"1 - Generate all neighbors (current: {neighbors_generated_all})")
  print(f"2 - Max Iterations (current: {max_iterations})")
  print(f"3 - Tabu Tenure (current: {tabu_tenure})")
  print(f"4 - Max_neighbors (current: {max_neighbors})")
  print(f"5 - Iterations without improvement (current: {it_without_improvement})")
  print(f"6 - Show plots (current: {plot})")
  print("7 - Resume")

def print_hillclimb( max_iterations: int, max_neighbors: int,show_plot:bool,neighbors_generated_all:bool):
  print("Change any parameter")
  print(f"1 - Max Iterations (current: {max_iterations})")
  print(f"2 - Max_neighbors (current: {max_neighbors})")
  print(f"3 - Show plots (current: {show_plot})")
  print(f"4 - Generate all neighbors (current: {neighbors_generated_all})")
  print("5 - Resume")

datasets = {1: 'kittens.in.txt', 2: 'me_at_the_zoo.in', 3: 'trending_today.in', 4: 'videos_worth_spreading.in'}
dataset = 'me_at_the_zoo.in'
problem_description, video_size, endpoint_data_description, endpoint_cache_description, request_description = parse_results(dataset)
start_position_flag = 1

while True:
  print_menu()

  # menu commands
  input_command = int(input("Action:"))
  match input_command:
    # choose dataset
    case 1:
      dataset_command = 0
      while (dataset_command != 5):
        print_datasets()
        dataset_command = int(input("Dataset:"))
        if dataset_command in datasets:
          dataset = datasets[dataset_command]
          problem_description, video_size, endpoint_data_description, endpoint_cache_description, request_description = parse_results(dataset)
          break
    
    # choose starting point
    case 2:
      print_start_menu()
      start_position_flag = int(input("Starting Point:"))
      while start_position_flag != 1 and start_position_flag != 2:
        print_start_menu()
        start_position_flag = int(input("Starting Point:"))

    # choose algorithm
    case 3:
      algorithm_command = 0
      while algorithm_command != 4:
        print_algorithms(dataset)
        algorithm_command = int(input("Algorithm:"))
        match algorithm_command:
          # annealing, with parameter control
          case 1:
            max_iterations=1000
            iterations_without_improvement_cap = 50
            initial_temperature=100
            cooling_rate=0.995
            minimum_temperature=1e-4
            neighbors_generated = 5
            show_plots = False
            get_all_neighbors = False

            parameter_command = 0
            while parameter_command != 9:
              print_annealing_parameters(max_iterations, iterations_without_improvement_cap, initial_temperature, cooling_rate, minimum_temperature, neighbors_generated,show_plots,get_all_neighbors)
              parameter_command = int(input("Action:"))
              match parameter_command:
                case 1:
                  max_iterations = int(input("What is the new value you want to set?"))
                case 2:
                  iterations_without_improvement_cap = int(input("What is the new value you want to set?"))
                case 3:
                  initial_temperature = int(input("What is the new value you want to set?"))
                case 4:
                  cooling_rate = float(input("What is the new value you want to set?"))
                case 5:
                  minimum_temperature = float(input("What is the new value you want to set?"))
                case 6:
                  neighbors_generated = int(input("What is the new value you want to set?"))
                case 7:
                  user_input = input("Write true or false: ").strip().lower()
                  if user_input == "true":
                    show_plot = True
                  elif user_input == "false":
                    show_plot = False
                  else:
                    print("Invalid input, please enter 'true' or 'false'.")
                case 8:
                  user_input = input("Write true or false: ").strip().lower()
                  if user_input == "true":
                    get_all_neighbors = True
                  elif user_input == "false":
                    get_all_neighbors = False
                  else:
                    print("Invalid input, please enter 'true' or 'false'.")

            # get the correct starting position depending on flag
            starting_position = {}
            if start_position_flag == 1:
              starting_position = get_init_solution(
                problem_description, 
                video_size, 
                dataset,
                'annealing',
                endpoint_data_description,
                endpoint_cache_description,
                request_description
              )
            elif start_position_flag == 2:
              starting_position = random_start(problem_description, video_size)

            if show_plots:
                fig, ax = plt.subplots()
                ax.set_xlabel("iteration")
                ax.set_ylabel("score")
                ax.set_title("Simulated Annealing Solution Mapping")
                solution = simulated_annealing(starting_position, video_size, endpoint_data_description, endpoint_cache_description, request_description, problem_description[4], dataset,show_plots,get_all_neighbors, max_iterations, iterations_without_improvement_cap,initial_temperature, cooling_rate, minimum_temperature,neighbors_generated, ax, fig)
              
                fig.canvas.draw()
                plt.show(block=True)
                plt.close("all")
            else:
                solution = simulated_annealing(starting_position, video_size, endpoint_data_description, endpoint_cache_description, request_description, problem_description[4], dataset,show_plots,get_all_neighbors, max_iterations, iterations_without_improvement_cap,initial_temperature, cooling_rate, minimum_temperature,neighbors_generated)
                                
          # genetic, with parameter control
          case 2:
            generations=1000
            mutation_rate=0.1
            tournament_size=5
            population_size=99
            show_plot=False

            parameter_command = 0
            while parameter_command != 6:
              print_genetic_parameters(generations, mutation_rate, tournament_size, population_size)
              parameter_command = int(input("Action:"))
              match parameter_command:
                case 1:
                  generations = int(input("What is the new value you want to set?"))
                case 2:
                  mutation_rate = float(input("What is the new value you want to set?"))
                case 3:
                  tournament_size = int(input("What is the new value you want to set?"))
                case 4:
                  population_size = int(input("What is the new value you want to set?"))
                case 5:
                  user_input = input("Write true or false: ").strip().lower()
                  if user_input == "true":
                    show_plot = True
                  elif user_input == "false":
                    show_plot = False
                  else:
                    print("Invalid input, please enter 'true' or 'false'.")
            
            # get the correct starting position depending on flag
            starting_position = {}
            if start_position_flag == 1:
              starting_position = get_init_solution(
                problem_description, 
                video_size, 
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
              lambda solution: score(solution,endpoint_data_description,endpoint_cache_description,request_description)[0],
              video_size,
              problem_description,
              dataset,
              mutation_rate,
              tournament_size,
              show_plot
              )

          # tabu
          case 3: 
            starting_position = {}
            # get the correct starting position

            parameter_command = 0
            generate_neighbors_all = False
            max_iterations = 1000
            tabu_tenure = 8
            max_neighbors = 500
            show_plot = False
            it_without_improvement = 50

            while parameter_command != 7:
                print_tabu(generate_neighbors_all, max_iterations, tabu_tenure,max_neighbors,show_plot,it_without_improvement)
                parameter_command = int(input("Action:"))
                
                match parameter_command:
                    case 1:
                        user_input = input("Write true or false: ").strip().lower()
                        if user_input == "true":
                            generate_neighbors_all = True
                        elif user_input == "false":
                            generate_neighbors_all = False
                        else:
                            print("Invalid input, please enter 'true' or 'false'.")
                    case 2:
                      max_iterations = int(input("New value:"))
                    case 3:
                      tabu_tenure = int(input("New value:"))
                    case 4:
                      max_neighbors = int(input("New value:"))
                    case 5:
                      it_without_improvement = int(input("New value:"))
                    case 6:
                        user_input = input("Write true or false: ").strip().lower()
                        if user_input == "true":
                            show_plot = True
                        elif user_input == "false":
                            show_plot = False
                        else:
                            print("Invalid input, please enter 'true' or 'false'.")
            if start_position_flag == 1:
              starting_position = get_init_solution(
                problem_description, 
                video_size, 
                dataset,
                'tabu',
                endpoint_data_description,
                endpoint_cache_description,
                request_description
              )
            elif start_position_flag == 2:
              starting_position = random_start(problem_description, video_size)

            if show_plot:
                fig, ax = plt.subplots()
                ax.set_xlim(-1, 1)
                ax.set_ylim(-1, 1)
                ax.set_xlabel("X")
                ax.set_ylabel("Y")
                ax.set_title("Tabu Search Solution Mapping")
                solution = tabu_search(starting_position, video_size, endpoint_data_description, endpoint_cache_description, request_description, problem_description[4],dataset,generate_neighbors_all,max_neighbors, max_iterations,it_without_improvement, tabu_tenure,show_plot,ax,fig)
                fig.canvas.draw()
                plt.show(block=True)
                plt.close("all")
            else:
                            solution = tabu_search(starting_position, video_size, endpoint_data_description, endpoint_cache_description, request_description, problem_description[4],dataset,generate_neighbors_all,max_neighbors, max_iterations,it_without_improvement, tabu_tenure,show_plot)
            
    
          case 4:

            starting_position = {}
            parameter_command = 0
            generate_neighbors_all = False
            max_iterations = 1000
            max_neighbors = 500
            show_plot = False
            gen_all = False

            while parameter_command != 5:
                print_hillclimb( max_iterations, max_neighbors,show_plot,gen_all)
                parameter_command = int(input("Action:"))
                
                match parameter_command:
                    case 1:
                        max_iterations = int(input("New value:"))
                    case 2:
                        max_neighbors = int(input("New value:"))
                    case 3:
                        user_input = input("Write true or false: ").strip().lower()
                        if user_input == "true":
                            show_plot = True
                        elif user_input == "false":
                            show_plot = False
                        else:
                            print("Invalid input, please enter 'true' or 'false'.")
                    case 4:
                        user_input = input("Write true or false: ").strip().lower()
                        if user_input == "true":
                            gen_all = True
                        elif user_input == "false":
                            gen_all = False
                        else:
                            print("Invalid input, please enter 'true' or 'false'.")
            if start_position_flag == 1:
                starting_position = get_init_solution(
                    problem_description,
                    video_size,
                    dataset,
                    'hill_climb',
                    endpoint_data_description,
                    endpoint_cache_description,
                    request_description
                )
            elif start_position_flag == 2:
                starting_position = random_start(problem_description, video_size)

            if show_plot:
                fig, ax = plt.subplots()
                ax.set_xlim(-1, 1)
                ax.set_ylim(-1, 1)
                ax.set_xlabel("X")
                ax.set_ylabel("Y")
                ax.set_title("Hill Climbing Solution Mapping")
                solution = hill_climb( starting_position, video_size, endpoint_data_description, endpoint_cache_description, request_description, problem_description[4], dataset,gen_all, max_iterations, max_neighbors, show_plot, ax, fig)
                fig.canvas.draw()
                plt.show(block=True)
                plt.close("all")
            solution = hill_climb( starting_position, video_size, endpoint_data_description, endpoint_cache_description, request_description, problem_description[4], dataset,gen_all, max_iterations, max_neighbors, show_plot)
          case 5: break
    case 4:
      break

print("Exited sucessfully :D")
