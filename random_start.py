from parse import parse_results
from random import randint

def random_start(problem_description: list[int], video_size: list[int]):
  # empty solution start and define the cap of each cache
  solution = {cache: [] for cache in range(problem_description[3])}
  video_number = problem_description[0]
  cache_number = problem_description[3]
  cache_size = problem_description[4]

  # fill each cache
  for cache in range(0, cache_number):
    total_capacity = 0
    while (total_capacity < cache_size):
      # choose a random video
      random_video = randint(0, video_number - 1)
      total_capacity += video_size[random_video]
      # skip to next cache if we would surpass cache capacity
      if total_capacity > cache_size:
        break
      else:
        solution[cache].append(random_video)

  return solution
