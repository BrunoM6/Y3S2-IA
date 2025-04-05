def parse_results(file_name: str):
    # Initialize data structures 
    problem_description = []
    video_size = []
    endpoint_data_description = []
    endpoint_cache_description = {}
    request_description = {}

    # Loop through the file
    with open('data/' + file_name, 'r') as file:
        # Problem description
        line = file.readline()
        tokens = line.strip().split()
        for token in tokens:
            problem_description.append(int(token))

        # Video size description 
        line = file.readline()
        tokens = line.strip().split()
        for token in tokens:
            video_size.append(int(token))
        
        # Endpoint -> Data & Endpoint -> Cache latency description
        i = 0
        while i != problem_description[1]:
            line = file.readline()
            tokens = line.strip().split()
            endpoint_data_description.append(int(tokens[0]))
            connections = int(tokens[1])
            j = 0
            while j < connections:
                line = file.readline()
                tokens = line.strip().split()
                endpoint_cache_description[(int(i), int(tokens[0]))] = int(tokens[1])
                j += 1
            i += 1
        
        # Request Description 
        i = 0
        while i != problem_description[2]:
            i+=1
            line = file.readline()
            tokens = line.strip().split()
            key = (int(tokens[1]), int(tokens[0]))
            if key in request_description:
                request_description[key] += int(tokens[2])
            else:
                request_description[key] = int(tokens[2])
    return problem_description, video_size, endpoint_data_description, endpoint_cache_description, request_description
