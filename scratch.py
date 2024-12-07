import math
import random

def generate_points(square_size, min_distance, num_points):
    points = []
    attempts = 0
    max_attempts = num_points * 10  # Limit total attempts to avoid infinite loop

    while len(points) < num_points and attempts < max_attempts:
        x = random.uniform(0, square_size)
        y = random.uniform(0, square_size)
        new_point = (x, y)

        if all(math.dist(new_point, p) >= min_distance for p in points):
            points.append(new_point)
        
        attempts += 1

    while len(points) < num_points:
        x = random.uniform(0, square_size)
        y = random.uniform(0, square_size)
        points.append((x, y))

    return points

# Parameters
square_size = 6000
min_distance = 1000
num_points = 18

# Generate points
result = generate_points(square_size, min_distance, num_points)

print(f"Generated {len(result)} points")
print("First 5 points:", result[:5])