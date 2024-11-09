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



for a, b in enumerate([4, 4, 6]):
    print(a, b)