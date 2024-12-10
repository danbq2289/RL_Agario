import pickle

# Read the pickle file
# with open('rewards/ddqn_rewards_20eps_lvl0.pkl', 'rb') as file:
#     data = pickle.load(file)

with open('feudal_rewards/Agario_baseline_rewards_step=3840.pkl', 'rb') as file:
    data = pickle.load(file)
print(data)