# Assignment 1 - T12G6

## Topic 3: Optimization Problems - Streaming Videos

### How to run the project
The project has two graphical components, the simple console based component is used to run parsing of different datasets, choose starting points, tune and run algorithms, and the graphical representation of our solution search space and of each solution for a chosen or the current solution reached. To run the project, just run `python main.py` on the terminal. Inputs are always just one number, and the program behaves expecting that. By default, the small dataset with greedy starting point is what starts as selected.

### Problem Description
The problem at hand consists of, given a description of cache servers, network endpoints and videos, along with predicted requests for individual videos, decide which videos to put in which cache server in order to minimize average waiting time for all requests.
The network endpoints have a specified number of requests for certain videos, with associated latencies for both the data center and the cache servers.

### Input Specification
The specification provided consists of several data files of varying sizes and complexity. 
The first line of every file contains five values: the number of videos, the number of endpoints, the ammount of request descriptions and size of all caches.<br>
##### Example 
'5 2 4 3 100' -> 5 videos, 2 endpoints, 4 request descriptions, 3 caches 100MB each.

The second line contains a value for each video, with the value corresponding to the video size, ordered by index.
#### Example
'50 100' -> video 0 has size of 50MB, video 1 has size of 100MB.<br>

The next lines hold the descriptions of the latency, in order of endpoint, of the connections to the datacenter and caches. First line of each endpoint description holds two values, the latency to the datacenter and ammount of connections to caches. Then, for each connection declared, we have a line with two values, the index of the cache being described, and the associated latency.
#### Example
'1000 3' -> endpoint 0 has 1000ms datacenter latency and is connected to 3 caches <br>
'0 100' -> cache 0 is connected to endpoint 0 and has latency of 100ms<br>
'2 200' -> cache 2 is connected to endpoint 0 and has latency of 200ms<br>
'1 300' -> cache 1 is connected to endpoint 0 and has latency of 300ms<br>

In the end of the file we have the request descriptions, which hold three values, the video being requested, the endpoint requesting the video and the ammount of requests.
#### Example
'3 0 1500' -> 1500 requests for video 3 coming from endpoint 0<br>
'0 1 1000' -> 1000 requests for video 0 coming from endpoint 1<br>

To parse the given file, we followed a line by line, token by token methodology.

### Data Structures
The parsing function `parse_results` is in the `parse.py` file. It takes in, as a string type parameter, the file name, assumed to be in the /data directory, and it returns the problem_description, video_size, endpoint_data_description, endpoint_cache_description and request description structures.
- problem_description: list of integers, always with the first five values that describe the problem at hand;
- video_size: list of integers, the index of the video is the index at the array, and the associated value is the list size, so size of video 0 is video_size[0];
- endpoint_data_description: list of integers, the index of the list is the endpoint being described and the value is the latency to the datacenter;
- endpoint_cache_description: dictionary of tuple (int, int) mapped to int, key is a tuple (endpoint_index, cache_index) that maps an endpoint-cache pair to a latency, not every combination of endpoint and cache is described;
- request_description: dictionary of tuple (int, int) mapped to int, key is a tuple (endpoint_index, video_index) that maps an endpoint-video pair to a request number;
- solution: dictionary of int (cache_index) to list of int (videos on the cache).

### Starting Point - Greedy Heuristic
To provide our solution space with a decent starting position, we apply a greedy heuristic to our solution before any other algorithms. In the `greedy.py` file, we use as parameters the data structures that describe the problem by running the parsing function once and define the starting point heuristic.  It works like so: 
- Initialize empty solution;
- Compute score (total time saved) for every potential placement of videos in every cache based on the description;
- Sort these potential placements and greedily assign videos to cache while there is enough capacity based on this.
- Return the solution.
Also, in program lifespans where you explore multiple algorithms for the same dataset, the Greedy solution used is the best solution found up to that point with any of the algorithms previously used. We found that this heuristic performs worse on larger caches and better on smaller ones. This is the default starting point used. 

### Random Point - Comparison Heuristic
A random starting point from a function defined in our `random.py` file serves as a control group for our algorithms, in which we fill every single cache with a maximal random ammount of videos, respecting the constraints of size. It works like so:
- Initialize empty solution;
- For each cache, get a random selection of videos;
- Keep adding the video until the cache can't take in the next random;
- Skip to next cache while we have caches to fill;
- Return the solution.
This similar starting point can be used to check how these algorithms perform in a balanced scenario. 

### Algorithms
We explored three different algorithms to solve the problem, simulated annealing, genetic algorithm and tabu search. 

#### Simulated Annealing
The annealing algorithm implemented iteratively explores the solution space using neighbor-generating functions that perform swap, add, and remove operations. It uses the annealing criteria that utilizes current temperature to define odds of acceptance of worse solutions.
Key parameters—including the maximum number of iterations, iterations without improvement, initial temperature, cooling rate, minimum temperature, and the number of generated neighbors per iteration—are configurable, enabling fine-tuning for different dataset sizes and performance requirements. This configurability allows the method to be effectively adapted to large-scale problems, such as those involving thousands of videos, numerous endpoints, and a complex network of cache servers. By combining heuristic exploration with adaptive parameter tuning, the algorithm incrementally improves its solution quality, making it a more robust tool. We found that annealing didn't do that well starting from the Greedy Heuristicin smaller cached datasets, since the Greedy starting point was already a local (possible global for the smaller dataset) peak. We also found that this algorithm didn't work too well for large cache sizes and was slower at increasing the score. This is due to the neighbors explored changing only one video at a time, making it so that each iteration is not felt as much since there is much more cache space to distribute.

#### Genetic Algorithm


#### Tabu Searc

### Generating Neighbors
We generate neighbors for current states through three actions, adding a video to a random cache where it is not present, removing a video from a non-empty cache and swapping two videos between two non-empty caches such that videos don't get repeated.

### Scoring
Our scoring function has two components, the base scoring, that runs through all the request descriptions and computes the total time saved to obtain the score, and a rescoring component that, upon taking in the optional parameters of the changes, previous solution score and state, we only calculate the difference in total time made, we reverse the score calculation to obtain the original total time, and re-calculate the score after adding this delta. This is fundamental for the efficiency of every algorithm, since calling the total scoring function every time would make running our implementations unfeasible for medium and large datasets.