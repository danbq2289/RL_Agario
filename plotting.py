import pickle
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

matplotlib.use('Agg')  # Non-interactive backend
# Read the pickle file
with open('feudal_rewards/Agario_baseline_rewards_step=1584000.pkl', 'rb') as file:
    data = pickle.load(file)

batch_size = 10  # Adjust this based on how many elements you want in each batch

# Create the batched data by averaging over batches
data_batched = [
    np.mean(data[i:i + batch_size])
    for i in range(0, len(data), batch_size)
]

plt.figure(figsize=(10, 6))
plt.plot(data_batched, marker='o', linestyle='-')
plt.xlabel('Batched Episode')
plt.ylabel('Reward Value')
plt.title('Total rewards per episode, Feudal Training Session 4')
plt.legend()
plt.grid(True)

# Save the plot to a file
plt.savefig("fun_session4.png")