"""
RigidBody representation for the 2D Physics Engine.
Supports circles, boxes, and static walls with mass, inertia, friction, and restitution.
"""

import math
from .vector import Vec2

class BodyType:
    DYNAMIC = "dynamic"
    STATIC = "static"

class ShapeType:
    CIRCLE = "circle"
    BOX = "box"

class RigidBody:
    _id_counter = 0

    def __init__(self,
                 shape_type=ShapeType.CIRCLE,
                 body_type=BodyType.DYNAMIC,
                 position=None,
                 velocity=None,
                 mass=1.0,
                 restitution=0.7,
                 friction=0.3,
                 radius=20.0,
                 width=40.0,
                 height=40.0,
                 angle=0.0,
                 angular_velocity=0.0,
                 color=None,
                 label=None,
                 body_id=None):

        if body_id is not None:
            self.id = str(body_id)
        else:
            RigidBody._id_counter += 1
            self.id = f"b_{RigidBody._id_counter}"

        self.label = label or f"{shape_type.capitalize()}-{self.id}"
        self.shape_type = shape_type
        self.body_type = body_type

        self.position = position if isinstance(position, Vec2) else Vec2(position[0], position[1]) if position else Vec2(0, 0)
        self.velocity = velocity if isinstance(velocity, Vec2) else Vec2(velocity[0], velocity[1]) if velocity else Vec2(0, 0)
        self.force = Vec2(0.0, 0.0)

        self.angle = float(angle)
        self.angular_velocity = float(angular_velocity)
        self.torque = 0.0

        # Physical dimensions
        self.radius = float(radius)
        self.width = float(width)
        self.height = float(height)

        # Restitution (elasticity) [0 = no bounce, 1 = perfectly elastic]
        self.restitution = float(restitution)
        # Friction [0 = frictionless ice, 1 = very rough]
        self.friction = float(friction)

        # Mass and Moment of Inertia
        if self.body_type == BodyType.STATIC:
            self.mass = float('inf')
            self.inv_mass = 0.0
            self.inertia = float('inf')
            self.inv_inertia = 0.0
        else:
            self.mass = max(0.01, float(mass))
            self.inv_mass = 1.0 / self.mass

            # Moment of inertia calculation:
            if self.shape_type == ShapeType.CIRCLE:
                # Solid disk: I = 1/2 * m * r^2
                self.inertia = 0.5 * self.mass * (self.radius ** 2)
            else:
                # Rectangle: I = 1/12 * m * (w^2 + h^2)
                self.inertia = (1.0 / 12.0) * self.mass * (self.width ** 2 + self.height ** 2)

            self.inv_inertia = 1.0 / self.inertia if self.inertia > 0 else 0.0

        # Appearance & Telemetry
        self.color = color or self._default_color()
        self.pinned = False  # Fixed in place even if dynamic

    def _default_color(self):
        if self.body_type == BodyType.STATIC:
            return "#4b5563"
        palette = [
            "#38bdf8", "#818cf8", "#f43f5e", "#fb923c",
            "#4ade80", "#a855f7", "#06b6d4", "#eab308"
        ]
        return palette[hash(self.id) % len(palette)]

    def apply_force(self, force_vec):
        """Applies a continuous force (F = m*a) at center of mass."""
        if self.body_type == BodyType.STATIC or self.pinned:
            return
        self.force = self.force + force_vec

    def apply_force_at_point(self, force_vec, world_point):
        """Applies force at a specific world coordinate, generating torque."""
        if self.body_type == BodyType.STATIC or self.pinned:
            return
        self.force = self.force + force_vec
        r = world_point - self.position
        self.torque += r.cross(force_vec)

    def apply_impulse(self, impulse_vec, contact_vector=None):
        """Applies an instantaneous impulse (J = m * delta_v)."""
        if self.body_type == BodyType.STATIC or self.pinned:
            return
        self.velocity = self.velocity + (impulse_vec * self.inv_mass)
        if contact_vector is not None:
            # contact_vector is r = point - position
            self.angular_velocity += contact_vector.cross(impulse_vec) * self.inv_inertia

    def get_vertices(self):
        """Returns the 4 world-coordinate vertices for a box."""
        if self.shape_type != ShapeType.BOX:
            return []

        hw = self.width / 2.0
        hh = self.height / 2.0

        # Local corners
        local_pts = [
            Vec2(-hw, -hh),
            Vec2(hw, -hh),
            Vec2(hw, hh),
            Vec2(-hw, hh)
        ]

        # Rotate and translate
        return [self.position + pt.rotate(self.angle) for pt in local_pts]

    def get_axes(self):
        """Returns the 2 unique face normal unit vectors for SAT."""
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        # Normal 1: (cos, sin)
        # Normal 2: (-sin, cos)
        return [Vec2(cos_a, sin_a), Vec2(-sin_a, cos_a)]

    def kinetic_energy(self):
        """Calculates kinetic energy: 1/2 m v^2 + 1/2 I w^2."""
        if self.body_type == BodyType.STATIC:
            return 0.0
        lin_ke = 0.5 * self.mass * self.velocity.length_sq()
        rot_ke = 0.5 * self.inertia * (self.angular_velocity ** 2)
        return lin_ke + rot_ke

    def to_dict(self):
        data = {
            "id": self.id,
            "label": self.label,
            "shape_type": self.shape_type,
            "body_type": self.body_type,
            "position": self.position.to_dict(),
            "velocity": self.velocity.to_dict(),
            "speed": round(self.velocity.length(), 2),
            "angle": round(self.angle, 3),
            "angular_velocity": round(self.angular_velocity, 3),
            "mass": round(self.mass, 2) if self.body_type != BodyType.STATIC else "inf",
            "restitution": round(self.restitution, 2),
            "friction": round(self.friction, 2),
            "color": self.color,
            "kinetic_energy": round(self.kinetic_energy(), 2),
            "pinned": self.pinned
        }
        if self.shape_type == ShapeType.CIRCLE:
            data["radius"] = round(self.radius, 1)
        else:
            data["width"] = round(self.width, 1)
            data["height"] = round(self.height, 1)
            # Send rotated vertices for easy rendering
            data["vertices"] = [v.to_dict() for v in self.get_vertices()]

        return data
