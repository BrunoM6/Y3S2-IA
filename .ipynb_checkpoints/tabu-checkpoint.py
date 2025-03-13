def score(solution:dict):
    return 1


def tabu(initial_solution: dict):
    taboos = [] # List with the index of the dict
    best = initial_solution
    best_score = score(initial_solution)
    print("UIUI")




if __name__ == "__main__":
    initial_solution = dict() # Key is the cache indentification, the result is an array of videos that are within the cache
    tabu(initial_solution)





# function TabuSearch(initial_solution):
#     current = initial_solution
#     best = current
#     best_score = evaluate(best)
#     tabu_list = []  // will store forbidden moves (e.g., recently added/removed video IDs for caches)
#     while not stopping_condition:  // e.g., fixed iterations or no improvement for a while
#         // Generate candidate neighbors (feasible moves not violating capacity)
#         candidate_list = []
#         for neighbor in neighbors(current):
#             move = getMove(current, neighbor)  // the change from current to neighbor (e.g., "added video v to cache c" or "removed v from c")
#             if move not in tabu_list:
#                 candidate_list.append((neighbor, evaluate(neighbor), move))
#         if candidate_list is empty:
#             // If all neighbors are tabu, allow one (aspiration) or break (should not often happen if tabu tenure is reasonable)
#             candidate_list = ... // (possibly include the best tabu move if it improves over best_score)
#         // Select the best candidate neighbor by score
#         best_neighbor, best_neighbor_score, best_move = argmax(candidate_list by score)
#         // Move to this neighbor
#         current = best_neighbor
#         if best_neighbor_score > best_score:
#             best = best_neighbor
#             best_score = best_neighbor_score
#         // Update tabu list with the inverse of the performed move
#         tabu_list.append( inverse(best_move) )
#         if len(tabu_list) > TabuTenure: 
#             remove_oldest_entry(tabu_list)  // keep tabu list size bounded
#     return best
