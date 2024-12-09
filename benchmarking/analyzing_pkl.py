import pickle
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import numpy as np

def plot_size_evolutions(player_size_evolution, prefix):
    plt.figure(figsize=(12, 8))
    
    for player, size_lists in player_size_evolution.items():
        for sizes in size_lists:
            if sizes[-1] is None:
                sizes = sizes[:-1]  # Remove the None at the end
            x = range(len(sizes))
            plt.plot(x, sizes) # , label=f"{player} (Game {i+1})" if i == 0 else "_nolegend_")
    
    plt.title("Bot Size Evolutions")
    plt.xlabel("Time Steps")
    plt.ylabel("Size")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{prefix}.png")
    plt.close()


def analyze_and_plot(player_size_evolution, prefix):
    max_sizes = []
    avg_sizes = []

    for player, episodes in player_size_evolution.items():
        for episode in episodes:
            if episode[-1] is None:
                episode = episode[:-1]  # Remove the None at the end
            if episode:  # Check if the episode is not empty
                max_sizes.append(max(episode))
                avg_sizes.append(sum(episode) / len(episode))

    # Plot histogram for max sizes
    plt.figure(figsize=(10, 6))
    plt.hist(max_sizes, bins=30, edgecolor='black')
    plt.title("Distribution of Maximum Sizes per Episode")
    plt.xlabel("Maximum Size")
    plt.ylabel("Frequency")
    plt.savefig(f"{prefix}_max_sizes_histogram.png")
    plt.close()

    # Plot histogram for average sizes
    plt.figure(figsize=(10, 6))
    plt.hist(avg_sizes, bins=30, edgecolor='black')
    plt.title("Distribution of Average Sizes per Episode")
    plt.xlabel("Average Size")
    plt.ylabel("Frequency")
    plt.savefig(f"{prefix}_avg_sizes_histogram.png")
    plt.close()

# Load the data and call the function
prefix = "benchmarking/dummies_benchmrk_20_frames50000_games3"
with open(f'{prefix}.pkl', 'rb') as f:
    player_size_evolution = pickle.load(f)

analyze_and_plot(player_size_evolution, prefix)
# plot_size_evolutions(player_size_evolution, prefix)