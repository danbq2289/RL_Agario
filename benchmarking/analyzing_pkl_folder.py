import pickle
import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

def analyze_and_plot_folder(folder_path, output_prefix):
    max_sizes = []
    avg_sizes = []

    for filename in os.listdir(folder_path):
        if filename.endswith('.pkl'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'rb') as f:
                player_size_evolution = pickle.load(f)
            
            for player, episodes in player_size_evolution.items():
                for episode in episodes:
                    if episode[-1] is None:
                        episode = episode[:-1]
                    if episode:
                        max_sizes.append(max(episode))
                        avg_sizes.append(sum(episode) / len(episode))

    plt.figure(figsize=(10, 6))
    plt.hist(max_sizes, bins=30, edgecolor='black')
    plt.title("Distribution of Maximum Sizes per Episode (All Files)")
    plt.xlabel("Maximum Size")
    plt.ylabel("Frequency")
    plt.savefig(f"{output_prefix}_max_sizes_histogram.png")
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.hist(avg_sizes, bins=30, edgecolor='black')
    plt.title("Distribution of Average Sizes per Episode (All Files)")
    plt.xlabel("Average Size")
    plt.ylabel("Frequency")
    plt.savefig(f"{output_prefix}_avg_sizes_histogram.png")
    plt.close()

    # plt.figure(figsize=(10, 6))
    # plt.hist([x for x in max_sizes if x < 2500], bins=30, edgecolor='black')
    # plt.title("Distribution of Maximum Sizes per Episode (All Files)")
    # plt.xlabel("Maximum Size")
    # plt.ylabel("Frequency")
    # plt.savefig(f"{output_prefix}_max_sizes_histogram_max2500.png")
    # plt.close()

    # plt.figure(figsize=(10, 6))
    # plt.hist([x for x in max_sizes if x < 2500], bins=30, edgecolor='black')
    # plt.title("Distribution of Average Sizes per Episode (All Files)")
    # plt.xlabel("Average Size")
    # plt.ylabel("Frequency")
    # plt.savefig(f"{output_prefix}_avg_sizes_histogram_max2500.png")
    # plt.close()

# Usage
folder_path = "benchmarking"
output_prefix = "benchmarking/merged_results"
analyze_and_plot_folder(folder_path, output_prefix)