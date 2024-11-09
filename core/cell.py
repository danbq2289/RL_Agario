import math

class Cell:
    def __init__(self, x, y, color, name, mass, vx=0, vy=0):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.mass = mass
        self.radius = math.sqrt(mass * 100)
        self.vx = vx
        self.vy = vy
        self.merge_time = 0

    def move(self, px, py):
        dx = px - self.x
        dy = py - self.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            speed = 30 / math.sqrt(self.radius)
            self.x += (dx / distance) * speed
            self.y += (dy / distance) * speed

    def split(self, px, py):
        if self.mass >= 32:
            new_mass = self.mass / 2
            self.mass = new_mass
            self.radius = math.sqrt(self.mass * 100)
            
            dx = px - self.x
            dy = py - self.y
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                speed = 40
                vx = (dx / distance) * speed
                vy = (dy / distance) * speed
                return Cell(self.x, self.y, self.color, self.name, new_mass, vx, vy)
        return None

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.9
        self.vy *= 0.9
        self.merge_time += dt

    def can_merge(self, other):
        return self.merge_time > 30 and other.merge_time > 30

    def merge(self, other):
        self.mass += other.mass
        self.radius = math.sqrt(self.mass * 100)

    def get_state(self):
        return {
            "x": self.x,
            "y": self.y,
            "color": self.color,
            "name": self.name,
            "mass": self.mass,
            "radius": self.radius
        }