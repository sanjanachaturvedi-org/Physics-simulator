"""
Preset scenarios demonstrating physics concepts:
Gravity, Friction, Collision Detection, Elasticity, and Constraints/Joints.
"""

from .vector import Vec2
from .body import RigidBody, BodyType, ShapeType
from .constraints import Joint, JointType

def load_newtons_cradle(world):
    """Demonstrates high elasticity (restitution ~1.0) and momentum conservation."""
    world.clear(keep_walls=True)
    world.gravity = Vec2(0.0, 600.0)

    n_balls = 5
    radius = 24.0
    cord_length = 240.0
    center_x = world.width * 0.5
    top_y = 120.0

    start_x = center_x - (n_balls - 1) * radius
    balls = []

    for i in range(n_balls):
        anchor_x = start_x + i * (radius * 2.0)
        # Pull the first ball to the left to initiate swing
        if i == 0:
            init_x = anchor_x - 160.0
            init_y = top_y + 150.0
        else:
            init_x = anchor_x
            init_y = top_y + cord_length

        ball = RigidBody(
            shape_type=ShapeType.CIRCLE,
            body_type=BodyType.DYNAMIC,
            position=Vec2(init_x, init_y),
            radius=radius,
            mass=3.0,
            restitution=0.99,  # Near perfect elasticity
            friction=0.02,
            label=f"Cradle Ball {i+1}",
            color="#38bdf8"
        )
        world.add_body(ball)
        balls.append(ball)

        # Distance joint connecting ball to fixed anchor point
        joint = Joint(
            body_a=ball,
            body_b=None,
            anchor_a=Vec2(0, 0),
            anchor_b=Vec2(anchor_x, top_y),
            joint_type=JointType.DISTANCE
        )
        joint.target_length = cord_length
        world.add_joint(joint)

def load_double_pendulum(world):
    """Demonstrates chaotic non-linear joint constraints."""
    world.clear(keep_walls=True)
    world.gravity = Vec2(0.0, 700.0)

    center_x = world.width * 0.5
    anchor_y = 140.0
    length1 = 150.0
    length2 = 140.0

    b1_pos = Vec2(center_x + length1, anchor_y)
    b2_pos = Vec2(center_x + length1 + length2, anchor_y)

    b1 = RigidBody(
        shape_type=ShapeType.CIRCLE,
        position=b1_pos,
        radius=20.0,
        mass=2.5,
        restitution=0.5,
        friction=0.1,
        label="Pendulum Bob 1",
        color="#f59e0b"
    )
    b2 = RigidBody(
        shape_type=ShapeType.CIRCLE,
        position=b2_pos,
        radius=18.0,
        mass=2.0,
        restitution=0.5,
        friction=0.1,
        label="Pendulum Bob 2",
        color="#ec4899"
    )
    world.add_body(b1)
    world.add_body(b2)

    # Joint 1: World anchor to Bob 1
    j1 = Joint(
        body_a=b1,
        body_b=None,
        anchor_a=Vec2(0, 0),
        anchor_b=Vec2(center_x, anchor_y),
        joint_type=JointType.DISTANCE
    )
    j1.target_length = length1
    world.add_joint(j1)

    # Joint 2: Bob 1 to Bob 2
    j2 = Joint(
        body_a=b2,
        body_b=b1,
        anchor_a=Vec2(0, 0),
        anchor_b=Vec2(0, 0),
        joint_type=JointType.DISTANCE
    )
    j2.target_length = length2
    world.add_joint(j2)

def load_rope_bridge(world):
    """Demonstrates linked distance constraints (chain/bridge) under gravity and load."""
    world.clear(keep_walls=True)
    world.gravity = Vec2(0.0, 600.0)

    num_links = 12
    start_x = 180.0
    end_x = world.width - 180.0
    y_pos = 320.0
    step_x = (end_x - start_x) / (num_links - 1)

    nodes = []
    for i in range(num_links):
        x = start_x + i * step_x
        is_fixed = (i == 0 or i == num_links - 1)
        node = RigidBody(
            shape_type=ShapeType.BOX,
            body_type=BodyType.STATIC if is_fixed else BodyType.DYNAMIC,
            position=Vec2(x, y_pos),
            width=28.0,
            height=12.0,
            mass=1.5,
            restitution=0.2,
            friction=0.6,
            label=f"Bridge Plank {i+1}",
            color="#64748b" if is_fixed else "#38bdf8"
        )
        world.add_body(node)
        nodes.append(node)

    # Connect adjacent planks with distance joints
    for i in range(num_links - 1):
        j = Joint(
            body_a=nodes[i],
            body_b=nodes[i+1],
            anchor_a=Vec2(14.0, 0),
            anchor_b=Vec2(-14.0, 0),
            joint_type=JointType.DISTANCE
        )
        j.target_length = step_x - 2.0
        world.add_joint(j)

    # Spawn heavy balls above to fall onto the bridge
    for i in range(3):
        ball = RigidBody(
            shape_type=ShapeType.CIRCLE,
            position=Vec2(start_x + (i + 1) * 180.0, 100.0 - i * 60.0),
            radius=26.0,
            mass=5.0,
            restitution=0.4,
            friction=0.5,
            label=f"Cargo Ball {i+1}",
            color="#e11d48"
        )
        world.add_body(ball)

def load_friction_ramp(world):
    """Demonstrates Coulomb friction (mu = 0.0, 0.2, 0.5, 0.85) on an incline."""
    world.clear(keep_walls=True)
    world.gravity = Vec2(0.0, 600.0)

    # Create inclined ramp (Box rotated 25 degrees)
    ramp = RigidBody(
        shape_type=ShapeType.BOX,
        body_type=BodyType.STATIC,
        position=Vec2(550.0, 420.0),
        width=750.0,
        height=30.0,
        angle=0.40,  # ~23 degrees
        restitution=0.1,
        friction=0.5,
        label="Inclined Ramp",
        color="#475569"
    )
    world.add_body(ramp)

    # Spawn 4 boxes on the incline with varying friction
    friction_configs = [
        {"mu": 0.02, "label": "Ice (μ=0.02)", "color": "#38bdf8", "offset_x": -260.0},
        {"mu": 0.20, "label": "Teflon (μ=0.20)", "color": "#34d399", "offset_x": -160.0},
        {"mu": 0.45, "label": "Wood (μ=0.45)", "color": "#fbbf24", "offset_x": -60.0},
        {"mu": 0.85, "label": "Rubber (μ=0.85)", "color": "#f87171", "offset_x": 40.0}
    ]

    import math
    cos_a = math.cos(ramp.angle)
    sin_a = math.sin(ramp.angle)

    for cfg in friction_configs:
        ox = cfg["offset_x"]
        # Position along ramp surface
        px = ramp.position.x + ox * cos_a - 30.0 * (-sin_a)
        py = ramp.position.y + ox * sin_a - 30.0 * cos_a

        box = RigidBody(
            shape_type=ShapeType.BOX,
            position=Vec2(px, py),
            width=38.0,
            height=38.0,
            angle=ramp.angle,
            mass=2.0,
            restitution=0.1,
            friction=cfg["mu"],
            label=cfg["label"],
            color=cfg["color"]
        )
        world.add_body(box)

def load_wrecking_ball(world):
    """Demonstrates swinging joint momentum destroying a stacked tower."""
    world.clear(keep_walls=True)
    world.gravity = Vec2(0.0, 650.0)

    # 1. Tower of stacked boxes
    tower_x = world.width - 320.0
    floor_y = world.height - 35.0
    box_w = 42.0
    box_h = 36.0
    rows = 7
    cols = 2

    for r in range(rows):
        for c in range(cols):
            x = tower_x + (c - 0.5) * (box_w + 4.0)
            y = floor_y - (r + 0.5) * (box_h + 2.0)
            box = RigidBody(
                shape_type=ShapeType.BOX,
                position=Vec2(x, y),
                width=box_w,
                height=box_h,
                mass=1.5,
                restitution=0.2,
                friction=0.6,
                label=f"Brick [{r},{c}]",
                color="#f97316" if (r + c) % 2 == 0 else "#ea580c"
            )
            world.add_body(box)

    # 2. Wrecking ball chain
    pivot_x = 350.0
    pivot_y = 120.0
    num_chain = 5
    chain_spacing = 50.0
    prev_body = None

    for i in range(num_chain):
        is_last = (i == num_chain - 1)
        cy = pivot_y + (i + 1) * chain_spacing
        cx = pivot_x - (i + 1) * 35.0

        if is_last:
            ball = RigidBody(
                shape_type=ShapeType.CIRCLE,
                position=Vec2(cx, cy),
                radius=40.0,
                mass=25.0,  # Massive ball
                restitution=0.4,
                friction=0.3,
                label="Heavy Wrecking Ball",
                color="#e11d48"
            )
            world.add_body(ball)
            curr_body = ball
        else:
            link = RigidBody(
                shape_type=ShapeType.CIRCLE,
                position=Vec2(cx, cy),
                radius=10.0,
                mass=0.8,
                restitution=0.1,
                friction=0.3,
                label=f"Chain Link {i+1}",
                color="#94a3b8"
            )
            world.add_body(link)
            curr_body = link

        # Joint
        if prev_body is None:
            j = Joint(
                body_a=curr_body,
                anchor_a=Vec2(0, 0),
                anchor_b=Vec2(pivot_x, pivot_y),
                joint_type=JointType.DISTANCE
            )
        else:
            j = Joint(
                body_a=curr_body,
                body_b=prev_body,
                anchor_a=Vec2(0, 0),
                anchor_b=Vec2(0, 0),
                joint_type=JointType.DISTANCE
            )
        world.add_joint(j)
        prev_body = curr_body

def load_elastic_gas(world):
    """Demonstrates perfect elasticity (e = 1.0) and kinetic energy preservation in Zero-G."""
    world.clear(keep_walls=True)
    world.gravity = Vec2(0.0, 0.0)  # Zero Gravity!

    import random
    random.seed(42)

    # 20 high-elasticity particles
    for i in range(18):
        rx = random.uniform(100.0, world.width - 100.0)
        ry = random.uniform(100.0, world.height - 100.0)
        vx = random.uniform(-250.0, 250.0)
        vy = random.uniform(-250.0, 250.0)
        rad = random.uniform(14.0, 24.0)

        ball = RigidBody(
            shape_type=ShapeType.CIRCLE,
            position=Vec2(rx, ry),
            velocity=Vec2(vx, vy),
            radius=rad,
            mass=rad * 0.15,
            restitution=1.0,  # Perfectly elastic!
            friction=0.0,    # Zero friction
            label=f"Gas Particle {i+1}",
            color="#06b6d4" if i % 2 == 0 else "#8b5cf6"
        )
        world.add_body(ball)

def load_preset(world, preset_name):
    """Loads a named scenario preset."""
    name = preset_name.lower().replace(" ", "_").replace("-", "_")
    if "cradle" in name:
        load_newtons_cradle(world)
    elif "pendulum" in name:
        load_double_pendulum(world)
    elif "bridge" in name or "rope" in name:
        load_rope_bridge(world)
    elif "friction" in name or "ramp" in name:
        load_friction_ramp(world)
    elif "wrecking" in name or "demolition" in name:
        load_wrecking_ball(world)
    elif "gas" in name or "elastic" in name:
        load_elastic_gas(world)
    else:
        load_newtons_cradle(world)
