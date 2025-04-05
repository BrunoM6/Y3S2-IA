import matplotlib.pyplot as plt
import random
import hashlib

def get_solution_hash(solution):
    """Create a hash for a solution."""
    return hashlib.md5(str(solution).encode()).hexdigest()

def get_random_offset():
    """Generate a small random offset for visualization."""
    return random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1)

def update_plot_batch(edges, solution_positions, ax, fig, plotted_solutions):
    for parent, neighbor in edges:
        parent_hash = get_solution_hash(parent)
        neighbor_hash = get_solution_hash(neighbor)

        if parent_hash not in solution_positions:
            x_offset, y_offset = get_random_offset()
            solution_positions[parent_hash] = (x_offset, y_offset)

        if neighbor_hash not in solution_positions:
            parent_x, parent_y = solution_positions[parent_hash]
            x_offset, y_offset = get_random_offset()
            solution_positions[neighbor_hash] = (parent_x + x_offset, parent_y + y_offset)

        parent_x, parent_y = solution_positions[parent_hash]
        neighbor_x, neighbor_y = solution_positions[neighbor_hash]

        if parent_hash not in plotted_solutions:
            ax.scatter(parent_x, parent_y, color="red", s=10)
            plotted_solutions.add(parent_hash)

        if neighbor_hash not in plotted_solutions:
            ax.scatter(neighbor_x, neighbor_y, color="blue", s=10)
            plotted_solutions.add(neighbor_hash)

        ax.plot([parent_x, neighbor_x], [parent_y, neighbor_y], color="gray", linestyle="dashed", linewidth=0.5)

    fig.canvas.draw_idle()
    plt.pause(0.01)

def update_score(new_point, ax, fig):
    (iteration, score) = new_point
    ax.scatter(iteration, score, color='red')
    
    fig.canvas.draw_idle()
    plt.pause(0.01)