"""
Collision detection and impulse-based resolution algorithms.
Handles Circle-Circle, Circle-Box, and Box-Box (SAT) collisions with elasticity and Coulomb friction.
"""

import math
from .vector import Vec2
from .body import ShapeType, BodyType

class ContactManifold:
    """Stores contact information for collision resolution."""
    def __init__(self, body_a, body_b):
        self.body_a = body_a
        self.body_b = body_b
        self.normal = Vec2(0.0, 0.0)  # Points from A to B
        self.depth = 0.0              # Penetration depth
        self.contacts = []            # World contact points [Vec2]
        self.restitution = 0.0        # Combined elasticity
        self.friction = 0.0           # Combined friction

    def to_dict(self):
        return {
            "bodyA": self.body_a.id,
            "bodyB": self.body_b.id,
            "normal": self.normal.to_dict(),
            "depth": round(self.depth, 3),
            "contact_points": [p.to_dict() for p in self.contacts]
        }

def project_polygon_on_axis(vertices, axis):
    """Projects polygon vertices onto a unit axis and returns (min, max)."""
    min_proj = float('inf')
    max_proj = float('-inf')
    for v in vertices:
        proj = v.dot(axis)
        if proj < min_proj:
            min_proj = proj
        if proj > max_proj:
            max_proj = proj
    return min_proj, max_proj

def circle_vs_circle(b1, b2):
    """Detects collision between two circles."""
    diff = b2.position - b1.position
    dist_sq = diff.length_sq()
    radius_sum = b1.radius + b2.radius

    if dist_sq >= radius_sum * radius_sum:
        return None

    distance = math.sqrt(dist_sq)
    manifold = ContactManifold(b1, b2)

    if distance < 1e-6:
        manifold.depth = b1.radius
        manifold.normal = Vec2(0.0, 1.0)
        manifold.contacts = [b1.position]
    else:
        manifold.depth = radius_sum - distance
        manifold.normal = diff / distance
        # Contact point halfway along the penetration overlap
        contact_pt = b1.position + manifold.normal * (b1.radius - manifold.depth * 0.5)
        manifold.contacts = [contact_pt]

    manifold.restitution = min(b1.restitution, b2.restitution)
    manifold.friction = math.sqrt(b1.friction * b2.friction)
    return manifold

def circle_vs_box(circle, box):
    """Detects collision between a circle and an oriented box."""
    # Transform circle center into box's local space
    rel_pos = circle.position - box.position
    cos_a = math.cos(-box.angle)
    sin_a = math.sin(-box.angle)
    local_circle = Vec2(
        rel_pos.x * cos_a - rel_pos.y * sin_a,
        rel_pos.x * sin_a + rel_pos.y * cos_a
    )

    hw = box.width * 0.5
    hh = box.height * 0.5

    # Clamp local circle center to box bounds
    clamped_x = max(-hw, min(hw, local_circle.x))
    clamped_y = max(-hh, min(hh, local_circle.y))
    closest_local = Vec2(clamped_x, clamped_y)

    is_inside = (local_circle.x == clamped_x and local_circle.y == clamped_y)

    if is_inside:
        # Circle center is inside the box: find closest edge
        dx = hw - abs(local_circle.x)
        dy = hh - abs(local_circle.y)
        if dx < dy:
            closest_local.x = hw if local_circle.x > 0 else -hw
        else:
            closest_local.y = hh if local_circle.y > 0 else -hh

    diff_local = local_circle - closest_local
    dist_sq = diff_local.length_sq()

    if not is_inside and dist_sq > circle.radius * circle.radius:
        return None

    dist = math.sqrt(dist_sq)

    # Convert closest point back to world space
    cos_box = math.cos(box.angle)
    sin_box = math.sin(box.angle)
    closest_world = Vec2(
        closest_local.x * cos_box - closest_local.y * sin_box,
        closest_local.x * sin_box + closest_local.y * cos_box
    ) + box.position

    manifold = ContactManifold(circle, box)

    if is_inside:
        # Normal points from circle to box
        normal_local = -diff_local.normalized() if dist > 1e-6 else Vec2(0, 1)
        normal_world = Vec2(
            normal_local.x * cos_box - normal_local.y * sin_box,
            normal_local.x * sin_box + normal_local.y * cos_box
        )
        manifold.normal = normal_world
        manifold.depth = circle.radius + dist
    else:
        diff_world = circle.position - closest_world
        d_world = diff_world.length()
        if d_world < 1e-6:
            manifold.normal = Vec2(0.0, -1.0)
            manifold.depth = circle.radius
        else:
            # Circle -> Box normal points from Circle into Box
            manifold.normal = -diff_world.normalized()
            manifold.depth = circle.radius - d_world

    manifold.contacts = [closest_world]
    manifold.restitution = min(circle.restitution, box.restitution)
    manifold.friction = math.sqrt(circle.friction * box.friction)
    return manifold

def box_vs_box(box_a, box_b):
    """Detects collision between two boxes using Separating Axis Theorem (SAT)."""
    axes = box_a.get_axes() + box_b.get_axes()
    verts_a = box_a.get_vertices()
    verts_b = box_b.get_vertices()

    min_overlap = float('inf')
    best_axis = None

    for axis in axes:
        min_a, max_a = project_polygon_on_axis(verts_a, axis)
        min_b, max_b = project_polygon_on_axis(verts_b, axis)

        overlap = min(max_a, max_b) - max(min_a, min_b)
        if overlap <= 0:
            return None  # Separating axis found, no collision!

        if overlap < min_overlap:
            min_overlap = overlap
            best_axis = axis

    # Ensure best_axis points from Box A to Box B
    dir_ab = box_b.position - box_a.position
    if dir_ab.dot(best_axis) < 0:
        best_axis = -best_axis

    manifold = ContactManifold(box_a, box_b)
    manifold.normal = best_axis
    manifold.depth = min_overlap

    # Find contact points: find vertices of B that penetrate into A
    contact_pts = []
    for v in verts_b:
        # Check if v is inside box_a
        # In local coordinates of box_a:
        rel = v - box_a.position
        cos_a = math.cos(-box_a.angle)
        sin_a = math.sin(-box_a.angle)
        local_v = Vec2(
            rel.x * cos_a - rel.y * sin_a,
            rel.x * sin_a + rel.y * cos_a
        )
        hw = box_a.width * 0.5 + 0.5
        hh = box_a.height * 0.5 + 0.5
        if -hw <= local_v.x <= hw and -hh <= local_v.y <= hh:
            contact_pts.append(v)

    if not contact_pts:
        # Check vertices of A inside B
        for v in verts_a:
            rel = v - box_b.position
            cos_b = math.cos(-box_b.angle)
            sin_b = math.sin(-box_b.angle)
            local_v = Vec2(
                rel.x * cos_b - rel.y * sin_b,
                rel.x * sin_b + rel.y * cos_b
            )
            hw = box_b.width * 0.5 + 0.5
            hh = box_b.height * 0.5 + 0.5
            if -hw <= local_v.x <= hw and -hh <= local_v.y <= hh:
                contact_pts.append(v)

    if not contact_pts:
        # Fallback to midpoint between centers along normal
        contact_pts = [box_a.position + best_axis * (min_overlap * 0.5)]

    manifold.contacts = contact_pts[:2]  # Max 2 contact points for 2D polygon edge
    manifold.restitution = min(box_a.restitution, box_b.restitution)
    manifold.friction = math.sqrt(box_a.friction * box_b.friction)
    return manifold

def check_collision(body_a, body_b):
    """Dispatches collision check based on body shape types."""
    if body_a.body_type == BodyType.STATIC and body_b.body_type == BodyType.STATIC:
        return None

    if body_a.shape_type == ShapeType.CIRCLE and body_b.shape_type == ShapeType.CIRCLE:
        return circle_vs_circle(body_a, body_b)

    elif body_a.shape_type == ShapeType.CIRCLE and body_b.shape_type == ShapeType.BOX:
        return circle_vs_box(body_a, body_b)

    elif body_a.shape_type == ShapeType.BOX and body_b.shape_type == ShapeType.CIRCLE:
        manifold = circle_vs_box(body_b, body_a)
        if manifold:
            manifold.body_a = body_a
            manifold.body_b = body_b
            manifold.normal = -manifold.normal
        return manifold

    elif body_a.shape_type == ShapeType.BOX and body_b.shape_type == ShapeType.BOX:
        return box_vs_box(body_a, body_b)

    return None

def resolve_collision_impulses(manifold):
    """
    Applies normal impulse (restitution) and tangential impulse (friction)
    for all contact points in the manifold.
    """
    a = manifold.body_a
    b = manifold.body_b
    normal = manifold.normal
    e = manifold.restitution
    mu = manifold.friction
    contacts = manifold.contacts

    if not contacts:
        return

    num_contacts = len(contacts)

    for p in contacts:
        r_a = p - a.position
        r_b = p - b.position

        # Relative velocity at contact point
        v_pa = a.velocity + Vec2.cross_scalar_vec(a.angular_velocity, r_a)
        v_pb = b.velocity + Vec2.cross_scalar_vec(b.angular_velocity, r_b)
        v_rel = v_pb - v_pa

        # Velocity along normal
        v_norm = v_rel.dot(normal)

        # If separating, do not apply normal impulse
        if v_norm < 0:
            # Effective mass for normal
            ra_cn = r_a.cross(normal)
            rb_cn = r_b.cross(normal)
            inv_mass_sum = a.inv_mass + b.inv_mass + (ra_cn * ra_cn) * a.inv_inertia + (rb_cn * rb_cn) * b.inv_inertia

            if inv_mass_sum > 1e-9:
                # Normal impulse magnitude
                j_n = -(1.0 + e) * v_norm / (inv_mass_sum * num_contacts)
                j_n = max(0.0, j_n)

                impulse_n = normal * j_n
                a.apply_impulse(-impulse_n, r_a)
                b.apply_impulse(impulse_n, r_b)

                # Tangential relative velocity (Friction)
                v_pa_new = a.velocity + Vec2.cross_scalar_vec(a.angular_velocity, r_a)
                v_pb_new = b.velocity + Vec2.cross_scalar_vec(b.angular_velocity, r_b)
                v_rel_new = v_pb_new - v_pa_new

                # Tangent vector perpendicular to normal
                tangent = v_rel_new - normal * v_rel_new.dot(normal)
                tangent_len = tangent.length()

                if tangent_len > 1e-6:
                    tangent = tangent / tangent_len

                    ra_ct = r_a.cross(tangent)
                    rb_ct = r_b.cross(tangent)
                    inv_mass_tan = a.inv_mass + b.inv_mass + (ra_ct * ra_ct) * a.inv_inertia + (rb_ct * rb_ct) * b.inv_inertia

                    if inv_mass_tan > 1e-9:
                        j_t = -v_rel_new.dot(tangent) / (inv_mass_tan * num_contacts)

                        # Coulomb friction law: |j_t| <= mu * j_n
                        max_friction = mu * j_n
                        j_t = max(-max_friction, min(max_friction, j_t))

                        impulse_t = tangent * j_t
                        a.apply_impulse(-impulse_t, r_a)
                        b.apply_impulse(impulse_t, r_b)

def resolve_positional_penetration(manifold):
    """Positional correction to avoid sinking / jittering."""
    a = manifold.body_a
    b = manifold.body_b
    normal = manifold.normal
    depth = manifold.depth

    slop = 0.05
    percent = 0.4
    inv_mass_sum = a.inv_mass + b.inv_mass

    if inv_mass_sum < 1e-9:
        return

    correction_mag = max(0.0, depth - slop) / inv_mass_sum * percent
    correction = normal * correction_mag

    if a.body_type == BodyType.DYNAMIC and not a.pinned:
        a.position = a.position - correction * a.inv_mass
    if b.body_type == BodyType.DYNAMIC and not b.pinned:
        b.position = b.position + correction * b.inv_mass
