"""
PhysicsWorld simulation engine.
Integrates bodies, constraints, gravity, friction, and collision resolution with multi-substepping.
"""

import math
import time
from .vector import Vec2
from .body import RigidBody, BodyType, ShapeType
from .collisions import check_collision, resolve_collision_impulses, resolve_positional_penetration
from .constraints import Joint, JointType

class PhysicsWorld:
    def __init__(self, width=1100.0, height=650.0):
        self.width = float(width)
        self.height = float(height)
        self.gravity = Vec2(0.0, 600.0)  # Standard downward gravity in px/s^2

        self.bodies = {}      # id -> RigidBody
        self.joints = {}      # id -> Joint

        self.iterations = 6   # Impulse & constraint solver iterations
        self.substeps = 4     # Physics sub-stepping for extreme stability
        self.air_damping = 0.9995  # Linear & angular velocity retention per frame

        self.last_collisions = []
        self.step_count = 0
        self.sim_time = 0.0

        # Create boundary walls (bottom, left, right, top)
        self.create_boundary_walls()

    def create_boundary_walls(self, thickness=40.0):
        """Creates static boundary walls bounding the simulation canvas."""
        w = self.width
        h = self.height
        th = thickness

        # Bottom Wall
        self.add_body(RigidBody(
            shape_type=ShapeType.BOX,
            body_type=BodyType.STATIC,
            position=Vec2(w * 0.5, h + th * 0.5 - 5.0),
            width=w * 1.5,
            height=th,
            restitution=0.4,
            friction=0.5,
            label="Floor",
            body_id="wall_bottom",
            color="#334155"
        ))

        # Top Wall
        self.add_body(RigidBody(
            shape_type=ShapeType.BOX,
            body_type=BodyType.STATIC,
            position=Vec2(w * 0.5, -th * 0.5 + 5.0),
            width=w * 1.5,
            height=th,
            restitution=0.4,
            friction=0.5,
            label="Ceiling",
            body_id="wall_top",
            color="#334155"
        ))

        # Left Wall
        self.add_body(RigidBody(
            shape_type=ShapeType.BOX,
            body_type=BodyType.STATIC,
            position=Vec2(-th * 0.5 + 5.0, h * 0.5),
            width=th,
            height=h * 1.5,
            restitution=0.4,
            friction=0.5,
            label="Left Wall",
            body_id="wall_left",
            color="#334155"
        ))

        # Right Wall
        self.add_body(RigidBody(
            shape_type=ShapeType.BOX,
            body_type=BodyType.STATIC,
            position=Vec2(w + th * 0.5 - 5.0, h * 0.5),
            width=th,
            height=h * 1.5,
            restitution=0.4,
            friction=0.5,
            label="Right Wall",
            body_id="wall_right",
            color="#334155"
        ))

    def add_body(self, body):
        self.bodies[body.id] = body
        return body

    def remove_body(self, body_id):
        body_id = str(body_id)
        if body_id in self.bodies:
            # Also remove any joints connected to this body
            joints_to_remove = [
                j_id for j_id, j in self.joints.items()
                if j.body_a.id == body_id or (j.body_b and j.body_b.id == body_id)
            ]
            for j_id in joints_to_remove:
                del self.joints[j_id]
            del self.bodies[body_id]
            return True
        return False

    def get_body(self, body_id):
        return self.bodies.get(str(body_id))

    def add_joint(self, joint):
        self.joints[joint.id] = joint
        return joint

    def remove_joint(self, joint_id):
        joint_id = str(joint_id)
        if joint_id in self.joints:
            del self.joints[joint_id]
            return True
        return False

    def clear(self, keep_walls=True):
        """Clears all objects and joints."""
        self.joints.clear()
        if keep_walls:
            walls = {k: v for k, v in self.bodies.items() if k.startswith("wall_")}
            self.bodies = walls
        else:
            self.bodies.clear()
        self.last_collisions.clear()

    def step(self, dt=0.016):
        """Steps the physics simulation forward by dt seconds using sub-stepping."""
        if dt <= 0:
            return

        # Cap dt to avoid large instability
        dt = min(0.05, dt)
        sub_dt = dt / self.substeps

        current_collisions = []

        for _ in range(self.substeps):
            # 1. Integrate forces and apply gravity
            for body in self.bodies.values():
                if body.body_type == BodyType.STATIC or body.pinned:
                    continue

                # Velocity update from gravity and forces: v = v + (g + F/m) * dt
                accel = self.gravity + (body.force * body.inv_mass)
                body.velocity = body.velocity + accel * sub_dt
                body.angular_velocity += (body.torque * body.inv_inertia) * sub_dt

                # Subtle air damping
                body.velocity = body.velocity * self.air_damping
                body.angular_velocity *= self.air_damping

            # 2. Joint spring forces
            for joint in self.joints.values():
                joint.solve_velocity(sub_dt)

            # 3. Collision detection
            body_list = list(self.bodies.values())
            manifolds = []
            n_bodies = len(body_list)

            for i in range(n_bodies):
                for j in range(i + 1, n_bodies):
                    b1 = body_list[i]
                    b2 = body_list[j]

                    # Skip static-static collisions
                    if b1.body_type == BodyType.STATIC and b2.body_type == BodyType.STATIC:
                        continue

                    manifold = check_collision(b1, b2)
                    if manifold:
                        manifolds.append(manifold)

            # Store active collisions for telemetry & API
            current_collisions = [m.to_dict() for m in manifolds]

            # 4. Iterative impulse & constraint solving
            for _ in range(self.iterations):
                # Solve collision impulses (normal bounce + friction)
                for m in manifolds:
                    resolve_collision_impulses(m)

                # Solve joint distance/pin constraints
                for joint in self.joints.values():
                    joint.solve_position()

            # 5. Positional penetration resolution
            for m in manifolds:
                resolve_positional_penetration(m)

            # 6. Integrate positions: x = x + v * dt
            for body in self.bodies.values():
                if body.body_type == BodyType.STATIC or body.pinned:
                    continue

                body.position = body.position + body.velocity * sub_dt
                body.angle += body.angular_velocity * sub_dt

                # Clear forces for next substep
                body.force = Vec2(0.0, 0.0)
                body.torque = 0.0

        self.last_collisions = current_collisions
        self.step_count += 1
        self.sim_time += dt

    def get_state(self):
        """Returns comprehensive state for API and rendering."""
        total_ke = sum(b.kinetic_energy() for b in self.bodies.values())

        # Approximate potential energy relative to floor: m * g * (height - y)
        total_pe = sum(
            max(0.0, b.mass * self.gravity.y * (self.height - b.position.y))
            for b in self.bodies.values() if b.body_type == BodyType.DYNAMIC
        )

        return {
            "time": round(self.sim_time, 3),
            "step": self.step_count,
            "gravity": self.gravity.to_dict(),
            "world_size": {"width": self.width, "height": self.height},
            "metrics": {
                "body_count": len(self.bodies),
                "joint_count": len(self.joints),
                "active_collisions": len(self.last_collisions),
                "kinetic_energy": round(total_ke, 1),
                "potential_energy": round(total_pe, 1),
                "total_energy": round(total_ke + total_pe, 1)
            },
            "bodies": [b.to_dict() for b in self.bodies.values()],
            "joints": [j.to_dict() for j in self.joints.values()],
            "collisions": self.last_collisions
        }
