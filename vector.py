"""
2D Vector mathematics module for the Physics Engine.
Provides high-performance 2D vector operations.
"""

import math

class Vec2:
    __slots__ = ('x', 'y')

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def __add__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self.x + other.x, self.y + other.y)
        return Vec2(self.x + other, self.y + other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self.x - other.x, self.y - other.y)
        return Vec2(self.x - other, self.y - other)

    def __rsub__(self, other):
        return Vec2(other - self.x, other - self.y)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vec2(self.x * other, self.y * other)
        raise TypeError("Multiplication only supported with scalar")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            if other == 0:
                return Vec2(0.0, 0.0)
            return Vec2(self.x / other, self.y / other)
        raise TypeError("Division only supported with scalar")

    def __neg__(self):
        return Vec2(-self.x, -self.y)

    def __repr__(self):
        return f"Vec2({self.x:.3f}, {self.y:.3f})"

    def dot(self, other):
        """Dot product of two vectors."""
        return self.x * other.x + self.y * other.y

    def cross(self, other):
        """2D Cross product (scalar z-component)."""
        return self.x * other.y - self.y * other.x

    @staticmethod
    def cross_scalar_vec(s, v):
        """Cross product of scalar (z) and vector (xy), produces vector perpendicular to v."""
        return Vec2(-s * v.y, s * v.x)

    @staticmethod
    def cross_vec_scalar(v, s):
        """Cross product of vector (xy) and scalar (z), produces vector perpendicular to v."""
        return Vec2(s * v.y, -s * v.x)

    def length_sq(self):
        """Squared Euclidean length."""
        return self.x * self.x + self.y * self.y

    def length(self):
        """Euclidean length."""
        return math.sqrt(self.x * self.x + self.y * self.y)

    def distance_sq(self, other):
        """Squared distance between two vectors."""
        dx = self.x - other.x
        dy = self.y - other.y
        return dx * dx + dy * dy

    def distance(self, other):
        """Distance between two vectors."""
        return math.sqrt(self.distance_sq(other))

    def normalized(self):
        """Returns a unit vector in the same direction, or zero vector if length is 0."""
        l = self.length()
        if l < 1e-9:
            return Vec2(0.0, 0.0)
        return Vec2(self.x / l, self.y / l)

    def perpendicular(self):
        """Returns perpendicular vector rotated 90 degrees counter-clockwise."""
        return Vec2(-self.y, self.x)

    def rotate(self, angle_rad):
        """Rotates vector by angle in radians."""
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        return Vec2(self.x * cos_a - self.y * sin_a, self.x * sin_a + self.y * cos_a)

    def to_dict(self):
        return {"x": round(self.x, 3), "y": round(self.y, 3)}

    @classmethod
    def from_dict(cls, data):
        if not data:
            return cls(0.0, 0.0)
        return cls(data.get("x", 0.0), data.get("y", 0.0))
