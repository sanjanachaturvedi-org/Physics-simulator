"""
Simple & Lightweight Physics Engine API:
- Gravity Simulation (Earth, Moon, Mars, Jupiter, Zero-G)
- Friction Simulation (Ice, Normal, Rough)
- Ball-to-Ball Collision Detection
- Constraints & Joints (Rods / Pendulum & Springs)
- Creating objects & applying forces
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import random

app = Flask(__name__, static_folder="static")
CORS(app)

# 1. Gravity Settings
GRAVITY_PRESETS = {
    "earth": {"name": "Earth", "value": 9.8, "scale": 600.0},
    "moon": {"name": "Moon", "value": 1.62, "scale": 100.0},
    "mars": {"name": "Mars", "value": 3.72, "scale": 230.0},
    "jupiter": {"name": "Jupiter", "value": 24.79, "scale": 1500.0},
    "zero": {"name": "Zero-G (Space)", "value": 0.0, "scale": 0.0}
}

current_gravity = {
    "name": "Earth",
    "value": 9.8,
    "scale": 600.0
}

# 2. Friction Settings
FRICTION_PRESETS = {
    "ice": {"name": "Ice (Frictionless)", "value": 0.01},
    "normal": {"name": "Normal Surface", "value": 0.35},
    "rough": {"name": "Rough / Wood", "value": 0.85}
}

current_friction = {
    "name": "Normal Surface",
    "value": 0.35
}

# 3. Objects State
objects = []
object_id_counter = 0

# 4. Constraints & Joints State
joints = []
joint_id_counter = 0

def create_ball(x=350, y=100, vx=0.0, vy=0.0, mass=1.5, radius=22, bounce=0.75, color="#38bdf8"):
    global object_id_counter
    object_id_counter += 1
    return {
        "id": object_id_counter,
        "x": float(x),
        "y": float(y),
        "vx": float(vx),
        "vy": float(vy),
        "mass": float(mass),
        "radius": float(radius),
        "bounce": float(bounce),
        "color": color
    }

def create_joint(joint_type="rod", ball1_id=1, ball2_id=None, anchor_x=350, anchor_y=40, length=180, stiffness=1.0):
    global joint_id_counter
    joint_id_counter += 1
    return {
        "id": joint_id_counter,
        "type": joint_type,         # 'rod' (fixed distance) or 'spring' (Hooke's law)
        "ball1_id": ball1_id,
        "ball2_id": ball2_id,       # None if attached to world anchor
        "anchor_x": float(anchor_x),
        "anchor_y": float(anchor_y),
        "length": float(length),
        "stiffness": float(stiffness)
    }

# Initial state: 2 balls for collision demo
def init_default_scene():
    global objects, joints, object_id_counter, joint_id_counter
    objects = []
    joints = []
    object_id_counter = 0
    joint_id_counter = 0
    objects.append(create_ball(x=260, y=120, vx=100, vy=0, mass=2.0, radius=24, bounce=0.8, color="#38bdf8"))
    objects.append(create_ball(x=440, y=120, vx=-100, vy=0, mass=2.0, radius=24, bounce=0.8, color="#f43f5e"))

init_default_scene()

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("static", path)

# 1. GET FULL STATE (Gravity + Friction + Objects + Joints)
@app.route("/api/state", methods=["GET"])
def get_state():
    return jsonify({
        "status": "success",
        "gravity": current_gravity,
        "friction": current_friction,
        "objects": objects,
        "joints": joints
    })

# 2. SET GRAVITY (API)
@app.route("/api/gravity", methods=["POST"])
def set_gravity():
    data = request.get_json(force=True)
    preset_key = data.get("preset", "").lower()

    if preset_key in GRAVITY_PRESETS:
        p = GRAVITY_PRESETS[preset_key]
        current_gravity["name"] = p["name"]
        current_gravity["value"] = p["value"]
        current_gravity["scale"] = p["scale"]
    else:
        val = float(data.get("value", 9.8))
        current_gravity["name"] = data.get("name", "Custom")
        current_gravity["value"] = val
        current_gravity["scale"] = val * 61.22

    return jsonify({
        "status": "success",
        "message": f"Gravity: {current_gravity['name']} ({current_gravity['value']} m/s²)",
        "gravity": current_gravity
    })

# 3. SET FRICTION (API)
@app.route("/api/friction", methods=["POST"])
def set_friction():
    data = request.get_json(force=True)
    preset_key = data.get("preset", "").lower()

    if preset_key in FRICTION_PRESETS:
        p = FRICTION_PRESETS[preset_key]
        current_friction["name"] = p["name"]
        current_friction["value"] = p["value"]
    else:
        val = max(0.0, min(1.0, float(data.get("value", 0.35))))
        current_friction["name"] = "Custom"
        current_friction["value"] = round(val, 2)

    return jsonify({
        "status": "success",
        "message": f"Friction: {current_friction['name']} (μ = {current_friction['value']})",
        "friction": current_friction
    })

# 4. CREATE / DROP AN OBJECT (API)
@app.route("/api/objects", methods=["POST"])
def add_object():
    data = request.get_json(silent=True) or {}
    x = data.get("x", 350)
    y = data.get("y", 80)
    vx = data.get("vx", (random.random() - 0.5) * 120)
    vy = data.get("vy", 0)
    mass = data.get("mass", 1.5)
    radius = data.get("radius", 20)
    bounce = data.get("bounce", 0.75)
    color = data.get("color", "#38bdf8")

    ball = create_ball(x=x, y=y, vx=vx, vy=vy, mass=mass, radius=radius, bounce=bounce, color=color)
    objects.append(ball)

    return jsonify({
        "status": "success",
        "message": f"Dropped Ball #{ball['id']}",
        "object": ball
    }), 201

# 5. DROP MULTIPLE BALLS FOR COLLISIONS (API)
@app.route("/api/objects/multi", methods=["POST"])
def add_multi_objects():
    data = request.get_json(silent=True) or {}
    count = int(data.get("count", 3))
    new_balls = []
    colors = ["#38bdf8", "#4ade80", "#fbbf24", "#f43f5e", "#a855f7"]

    for i in range(count):
        x = 180 + i * 150
        y = 60 + (i % 2) * 40
        vx = (random.random() - 0.5) * 160
        ball = create_ball(
            x=x, y=y, vx=vx, vy=0,
            mass=1.5 + random.random(),
            radius=20 + random.randint(0, 4),
            color=colors[(object_id_counter + i) % len(colors)]
        )
        objects.append(ball)
        new_balls.append(ball)

    return jsonify({
        "status": "success",
        "message": f"Added {count} balls for collision demo",
        "objects": new_balls
    }), 201

# 6. CONSTRAINTS & JOINTS (API)
@app.route("/api/joints", methods=["GET"])
def list_joints():
    return jsonify({"status": "success", "joints": joints})

@app.route("/api/joints", methods=["POST"])
def add_joint():
    """
    Creates a constraint or joint.
    JSON: { "type": "rod"|"spring", "ball1_id": 1, "ball2_id": null, "anchor_x": 350, "anchor_y": 40, "length": 180 }
    """
    data = request.get_json(force=True)
    jtype = data.get("type", "rod")
    b1_id = data.get("ball1_id")
    b2_id = data.get("ball2_id")
    ax = data.get("anchor_x", 350)
    ay = data.get("anchor_y", 40)
    length = data.get("length", 180)
    stiffness = data.get("stiffness", 1.0)

    j = create_joint(joint_type=jtype, ball1_id=b1_id, ball2_id=b2_id, anchor_x=ax, anchor_y=ay, length=length, stiffness=stiffness)
    joints.append(j)

    return jsonify({
        "status": "success",
        "message": f"Created {jtype.upper()} Joint #{j['id']}",
        "joint": j
    }), 201

@app.route("/api/joints/preset", methods=["POST"])
def joint_preset():
    """Quick presets: 'pendulum', 'spring', or 'dumbbell'."""
    global objects, joints, object_id_counter, joint_id_counter
    data = request.get_json(force=True)
    preset = data.get("preset", "pendulum").lower()

    objects = []
    joints = []
    object_id_counter = 0
    joint_id_counter = 0

    if preset == "pendulum":
        # Ball pulled to the side connected by rod joint
        b = create_ball(x=200, y=100, vx=0, vy=0, mass=2.5, radius=24, bounce=0.5, color="#f59e0b")
        objects.append(b)
        j = create_joint(joint_type="rod", ball1_id=b["id"], anchor_x=350, anchor_y=40, length=200)
        joints.append(j)
        msg = "Loaded Pendulum Distance Joint"

    elif preset == "spring":
        # Ball hanging from spring
        b = create_ball(x=350, y=180, vx=0, vy=0, mass=2.0, radius=22, bounce=0.6, color="#10b981")
        objects.append(b)
        j = create_joint(joint_type="spring", ball1_id=b["id"], anchor_x=350, anchor_y=40, length=120, stiffness=120.0)
        joints.append(j)
        msg = "Loaded Oscillating Spring Joint (Hooke's Law)"

    elif preset == "dumbbell":
        # Two balls linked together by a rod
        b1 = create_ball(x=300, y=150, vx=50, vy=0, mass=2.0, radius=20, bounce=0.7, color="#38bdf8")
        b2 = create_ball(x=420, y=150, vx=-50, vy=0, mass=2.0, radius=20, bounce=0.7, color="#a855f7")
        objects.append(b1)
        objects.append(b2)
        j = create_joint(joint_type="rod", ball1_id=b1["id"], ball2_id=b2["id"], length=120)
        joints.append(j)
        msg = "Loaded Linked Dumbbell (Two-Body Rod Constraint)"
    else:
        init_default_scene()
        msg = "Reset to default scene"

    return jsonify({
        "status": "success",
        "message": msg,
        "objects": objects,
        "joints": joints
    })

# 7. APPLY FORCE (PUSH UP / JUMP)
@app.route("/api/objects/<int:ball_id>/force", methods=["POST"])
def apply_force(ball_id):
    data = request.get_json(force=True)
    fy = float(data.get("fy", -450.0))
    fx = float(data.get("fx", 0.0))

    target = next((b for b in objects if b["id"] == ball_id), None)
    if not target:
        return jsonify({"status": "error", "message": "Object not found"}), 404

    target["vy"] += fy / target["mass"]
    target["vx"] += fx / target["mass"]

    return jsonify({
        "status": "success",
        "message": f"Applied force to Ball #{ball_id}",
        "new_vx": target["vx"],
        "new_vy": target["vy"]
    })

# 8. REMOVE A PARTICULAR BALL (API)
@app.route("/api/objects/<int:ball_id>", methods=["DELETE"])
def delete_object(ball_id):
    global objects, joints
    target = next((b for b in objects if b["id"] == ball_id), None)
    if not target:
        return jsonify({"status": "error", "message": "Object not found"}), 404

    objects = [b for b in objects if b["id"] != ball_id]
    # Clean up connected joints
    joints = [j for j in joints if j.get("ball1_id") != ball_id and j.get("ball2_id") != ball_id]

    return jsonify({
        "status": "success",
        "message": f"Removed Ball #{ball_id}",
        "ball_id": ball_id
    })

# 9. RESET SIMULATION
@app.route("/api/reset", methods=["POST"])
def reset_simulation():
    init_default_scene()
    return jsonify({
        "status": "success",
        "message": "Reset to 2-ball collision setup",
        "objects": objects,
        "joints": joints
    })

if __name__ == "__main__":
    print("Physics API running on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
