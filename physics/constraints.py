"""
Constraints and Joints module for the 2D Physics Engine.
Implements Distance Joints (Rods), Springs, Pin/Hinge Joints, and Mouse Drag constraints.
"""

import math
from .vector import Vec2
from .body import BodyType

class JointType:
    DISTANCE = "distance"
    SPRING = "spring"
    PIN = "pin"

class Joint:
    _id_counter = 0

    def __init__(self, body_a, body_b=None, anchor_a=None, anchor_b=None, joint_type=JointType.DISTANCE, joint_id=None):
        if joint_id is not None:
            self.id = str(joint_id)
        else:
            Joint._id_counter += 1
            self.id = f"j_{Joint._id_counter}"

        self.joint_type = joint_type
        self.body_a = body_a
        self.body_b = body_b  # None if connected to fixed world anchor

        # Local anchor offsets (relative to body center) or absolute world positions
        self.anchor_a = anchor_a if isinstance(anchor_a, Vec2) else Vec2(anchor_a[0], anchor_a[1]) if anchor_a else Vec2(0, 0)
        self.anchor_b = anchor_b if isinstance(anchor_b, Vec2) else Vec2(anchor_b[0], anchor_b[1]) if anchor_b else Vec2(0, 0)

        # In world coordinates:
        pos_a = self.get_anchor_a_world()
        pos_b = self.get_anchor_b_world()
        self.target_length = pos_a.distance(pos_b)
        if self.target_length < 1e-3:
            self.target_length = 0.0

        # Physical properties
        self.stiffness = 1.0       # 1.0 = rigid constraint, < 1.0 = springy
        self.spring_k = 150.0      # Hooke's constant (for spring joint)
        self.damping = 5.0         # Velocity damping factor
        self.color = "#38bdf8"
        self.breaking_force = float('inf')
        self.is_broken = False

    def get_anchor_a_world(self):
        return self.body_a.position + self.anchor_a.rotate(self.body_a.angle)

    def get_anchor_b_world(self):
        if self.body_b is not None:
            return self.body_b.position + self.anchor_b.rotate(self.body_b.angle)
        return self.anchor_b  # Fixed world point

    def solve_velocity(self, dt):
        """Applies velocity corrections / spring forces."""
        if self.is_broken:
            return

        p_a = self.get_anchor_a_world()
        p_b = self.get_anchor_b_world()
        diff = p_b - p_a
        dist = diff.length()

        if dist < 1e-6:
            return

        direction = diff / dist

        if self.joint_type == JointType.SPRING:
            # Hooke's Law: F = -k * (x - x0) - c * v_rel
            stretch = dist - self.target_length

            # Relative velocity at anchors
            r_a = p_a - self.body_a.position
            v_a = self.body_a.velocity + Vec2.cross_scalar_vec(self.body_a.angular_velocity, r_a)

            if self.body_b is not None:
                r_b = p_b - self.body_b.position
                v_b = self.body_b.velocity + Vec2.cross_scalar_vec(self.body_b.angular_velocity, r_b)
            else:
                v_b = Vec2(0, 0)

            v_rel = (v_b - v_a).dot(direction)
            force_mag = self.spring_k * stretch + self.damping * v_rel

            force_vec = direction * force_mag
            self.body_a.apply_force_at_point(force_vec, p_a)
            if self.body_b is not None:
                self.body_b.apply_force_at_point(-force_vec, p_b)

    def solve_position(self):
        """Positional relaxation for distance and pin joints (Verlet/PBD style)."""
        if self.is_broken or self.joint_type == JointType.SPRING:
            return

        p_a = self.get_anchor_a_world()
        p_b = self.get_anchor_b_world()
        diff = p_b - p_a
        dist = diff.length()

        if dist < 1e-6:
            diff = Vec2(0, 1e-4)
            dist = 1e-4

        direction = diff / dist
        error = dist - self.target_length

        inv_a = self.body_a.inv_mass if self.body_a.body_type == BodyType.DYNAMIC and not self.body_a.pinned else 0.0
        inv_b = (self.body_b.inv_mass if self.body_b.body_type == BodyType.DYNAMIC and not self.body_b.pinned else 0.0) if self.body_b else 0.0
        inv_sum = inv_a + inv_b

        if inv_sum < 1e-9:
            return

        correction = direction * (error * self.stiffness / inv_sum)

        if inv_a > 0:
            self.body_a.position = self.body_a.position + correction * inv_a
        if self.body_b and inv_b > 0:
            self.body_b.position = self.body_b.position - correction * inv_b

    def to_dict(self):
        p_a = self.get_anchor_a_world()
        p_b = self.get_anchor_b_world()
        current_len = p_a.distance(p_b)

        return {
            "id": self.id,
            "type": self.joint_type,
            "bodyA": self.body_a.id,
            "bodyB": self.body_b.id if self.body_b else None,
            "anchorA": p_a.to_dict(),
            "anchorB": p_b.to_dict(),
            "target_length": round(self.target_length, 2),
            "current_length": round(current_len, 2),
            "stiffness": self.stiffness,
            "spring_k": self.spring_k,
            "is_broken": self.is_broken
        }
