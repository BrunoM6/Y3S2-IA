import matplotlib.pyplot as plt
import random
import hashlib



def get_solution_hash(solution):
    """Create a hash for a solution."""
    return hashlib.md5(str(solution).encode()).hexdigest()

def get_random_offset():
    """Generate a small random offset for visualization."""
    return random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1)





def update_plot(solution, neighbor, solution_positions, ax, fig, prev_solution=None):
    sol_hash = get_solution_hash(solution)

    # If solution is new, assign a random position
    if sol_hash not in solution_positions:
        parent_x, parent_y = (0, 0)  # Default to center
        x_offset, y_offset = get_random_offset()
        solution_positions[sol_hash] = (parent_x + x_offset, parent_y + y_offset)

    parent_x, parent_y = solution_positions[sol_hash]

    if prev_solution is not None:
        prev_solution_hash = get_solution_hash(prev_solution)
        if prev_solution_hash in solution_positions:
            prev_x, prev_y = solution_positions[prev_solution_hash]
            ax.scatter(prev_x, prev_y, color="blue", s=10)  # Old main solution -> blue

    ax.scatter(parent_x, parent_y, color="red", s=10)

    # Plot neighbors
    neighbor_hash = get_solution_hash(neighbor)


    if neighbor_hash not in solution_positions:
        x_offset, y_offset = get_random_offset()
        solution_positions[neighbor_hash] = (parent_x + x_offset, parent_y + y_offset)

    neighbor_x, neighbor_y = solution_positions[neighbor_hash]

    # Draw connection
    ax.plot([parent_x, neighbor_x], [parent_y, neighbor_y], color="gray", linestyle="dashed", linewidth=0.5)
    ax.scatter(neighbor_x, neighbor_y, color="blue", s=10)  # Neighbor points should be blue

    fig.canvas.flush_events()  # Ensures real-time updates without creating new figures

    plt.draw()
    plt.pause(0.05)

    return solution 
