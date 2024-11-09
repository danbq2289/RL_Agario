import random
import time
import math
from scipy import stats
from scipy.optimize import brentq

def find_q(p, n):
    if n % 2 == 0:
        raise ValueError("n must be an odd number")
    
    def objective(q):
        k = math.ceil(n / 2)  # Minimum number of tails for majority
        return stats.binom.cdf(n - k, n, 1 - q) - p
    
    # Use Brent's method to find the root of the objective function
    q = brentq(objective, 0, 1)
    return q

#  p = find_q(0.70, 7)
# print(p)
# for i in range(6):

print("Replica...")
time.sleep(5)

print("CHUTY BICAMPEON" if random.random() < 0.6 else "MECHA CAMPEON")

# Chuty
# Mecha

# Katacrist (3ro)
# El Menor (4to)
