/**
 * Physics Engine - Gravity, Friction, Collisions, Constraints & Joints
 * Clean & lightweight implementation with Flask REST API.
 */

document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('gravityCanvas');
  const ctx = canvas.getContext('2d');

  // Canvas bounds
  const WIDTH = 700;
  const HEIGHT = 500;
  const FLOOR_Y = 460;
  const PIXELS_PER_METER = 40;

  // Simulation Parameters
  let gravity = 9.8;          // m/s^2
  let gravityScale = 600.0;   // px/s^2
  let gravityName = "Earth";

  let friction = 0.35;        // Coulomb friction coefficient (0.0 to 1.0)
  let frictionName = "Normal";

  let totalCollisions = 0;
  let sparks = [];

  // State: Balls & Joints
  let balls = [
    { id: 1, x: 260, y: 120, vx: 100, vy: 0, radius: 24, mass: 2.0, bounce: 0.8, color: "#38bdf8" },
    { id: 2, x: 440, y: 120, vx: -100, vy: 0, radius: 24, mass: 2.0, bounce: 0.8, color: "#f43f5e" }
  ];

  let joints = [];

  // DOM Elements
  const statGravity = document.getElementById('statGravity');
  const statFriction = document.getElementById('statFriction');
  const statCollisions = document.getElementById('statCollisions');
  const statJoints = document.getElementById('statJoints');
  const apiLog = document.getElementById('apiLog');

  const sliderGravity = document.getElementById('sliderGravity');
  const customGVal = document.getElementById('customGVal');
  const sliderFriction = document.getElementById('sliderFriction');
  const customFricVal = document.getElementById('customFricVal');

  // API Activity Logger
  function logApi(method, endpoint, message) {
    const entry = document.createElement('div');
    entry.className = `log-entry ${method.toLowerCase()}`;
    entry.textContent = `[${method}] ${endpoint} → ${message}`;
    apiLog.prepend(entry);
    if (apiLog.children.length > 25) {
      apiLog.removeChild(apiLog.lastChild);
    }
  }

  // 1. Fetch Initial State from API
  async function loadInitialState() {
    try {
      const res = await fetch('/api/state');
      const data = await res.json();
      if (data.status === 'success') {
        gravity = data.gravity.value;
        gravityScale = data.gravity.scale;
        gravityName = data.gravity.name;

        friction = data.friction.value;
        frictionName = data.friction.name;

        balls = data.objects;
        joints = data.joints || [];
        updateUI();
        logApi('GET', '/api/state', `Connected! Gravity: ${gravityName}, Friction: ${frictionName}`);
      }
    } catch (err) {
      logApi('ERROR', '/api/state', 'Could not reach server');
    }
  }

  // 2. Set Gravity via API
  async function apiSetGravity(presetOrValue) {
    try {
      let bodyData = (typeof presetOrValue === 'string')
        ? { preset: presetOrValue }
        : { value: presetOrValue };

      const res = await fetch('/api/gravity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bodyData)
      });
      const data = await res.json();

      if (data.status === 'success') {
        gravity = data.gravity.value;
        gravityScale = data.gravity.scale;
        gravityName = data.gravity.name;
        updateUI();
        logApi('POST', '/api/gravity', `${gravityName} (${gravity} m/s²)`);
      }
    } catch (err) {
      console.error(err);
    }
  }

  // 3. Set Friction via API
  async function apiSetFriction(presetOrValue) {
    try {
      let bodyData = (typeof presetOrValue === 'string')
        ? { preset: presetOrValue }
        : { value: presetOrValue };

      const res = await fetch('/api/friction', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bodyData)
      });
      const data = await res.json();

      if (data.status === 'success') {
        friction = data.friction.value;
        frictionName = data.friction.name;
        updateUI();
        logApi('POST', '/api/friction', `${frictionName} (μ = ${friction})`);
      }
    } catch (err) {
      console.error(err);
    }
  }

  // 4. Drop Single Ball via API
  async function apiDropBall(x = 350, y = 80) {
    try {
      const palette = ["#38bdf8", "#4ade80", "#fbbf24", "#f43f5e", "#a855f7", "#ec4899", "#06b6d4"];
      const color = palette[balls.length % palette.length];

      const res = await fetch('/api/objects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          x: x,
          y: y,
          vx: (Math.random() - 0.5) * 160,
          vy: 0,
          mass: 1.5 + Math.random(),
          radius: 20 + Math.floor(Math.random() * 6),
          bounce: 0.75,
          color: color
        })
      });
      const data = await res.json();

      if (data.status === 'success') {
        balls.push(data.object);
        updateUI();
        logApi('POST', '/api/objects', `Dropped Ball #${data.object.id} at (${Math.round(x)}, ${Math.round(y)})`);
      }
    } catch (err) {
      console.error(err);
    }
  }

  // 5. Drop Multi Balls for Collision Demo via API
  async function apiDropMultiBalls() {
    try {
      const res = await fetch('/api/objects/multi', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ count: 3 })
      });
      const data = await res.json();

      if (data.status === 'success') {
        for (const b of data.objects) {
          balls.push(b);
        }
        updateUI();
        logApi('POST', '/api/objects/multi', `Added 3 balls for collision demo`);
      }
    } catch (err) {
      console.error(err);
    }
  }

  // 6. Load Constraint / Joint Presets via API
  async function apiLoadJointPreset(preset) {
    try {
      const res = await fetch('/api/joints/preset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preset })
      });
      const data = await res.json();

      if (data.status === 'success') {
        balls = data.objects;
        joints = data.joints;
        totalCollisions = 0;
        sparks = [];
        updateUI();
        logApi('POST', '/api/joints/preset', data.message);
      }
    } catch (err) {
      console.error(err);
    }
  }

  // 7. Push Up / Jump Force via API
  async function apiPushUp() {
    if (balls.length === 0) return;
    const target = balls[balls.length - 1];

    try {
      const pushForce = -500;
      const res = await fetch(`/api/objects/${target.id}/force`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fy: pushForce, fx: (Math.random() - 0.5) * 200 })
      });
      const data = await res.json();

      if (data.status === 'success') {
        target.vy = data.new_vy;
        target.vx = data.new_vx;
        logApi('POST', `/api/objects/${target.id}/force`, `Push impulse applied to Ball #${target.id}`);
      }
    } catch (err) {
      console.error(err);
    }
  }

  // 8. Reset Simulation via API
  async function apiReset() {
    try {
      const res = await fetch('/api/reset', { method: 'POST' });
      const data = await res.json();
      if (data.status === 'success') {
        balls = data.objects;
        joints = data.joints || [];
        totalCollisions = 0;
        sparks = [];
        draggedBall = null;
        hoveredBall = null;
        updateUI();
        logApi('POST', '/api/reset', 'Reset simulation');
      }
    } catch (err) {
      console.error(err);
    }
  }

  // 9. Remove a Particular Ball via API
  async function apiRemoveBall(ballId) {
    try {
      const res = await fetch(`/api/objects/${ballId}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.status === 'success') {
        const target = balls.find(b => b.id === ballId);
        if (target) {
          createSparks(target.x, target.y);
        }
        balls = balls.filter(b => b.id !== ballId);
        joints = joints.filter(j => j.ball1_id !== ballId && j.ball2_id !== ballId);
        if (hoveredBall && hoveredBall.id === ballId) hoveredBall = null;
        if (draggedBall && draggedBall.id === ballId) draggedBall = null;
        updateUI();
        logApi('DELETE', `/api/objects/${ballId}`, `Removed Ball #${ballId}`);
      }
    } catch (err) {
      console.error(err);
    }
  }

  // Update UI Stats
  function updateUI() {
    statGravity.textContent = `${gravity} m/s² (${gravityName})`;
    statFriction.textContent = `μ = ${friction} (${frictionName})`;
    statCollisions.textContent = totalCollisions;
    statJoints.textContent = joints.length;

    sliderGravity.value = gravity;
    customGVal.textContent = `${gravity} m/s²`;

    sliderFriction.value = friction;
    customFricVal.textContent = friction;
  }

  // Gravity Presets
  document.querySelectorAll('.grav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.grav-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      apiSetGravity(btn.dataset.preset);
    });
  });

  sliderGravity.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    customGVal.textContent = `${val} m/s²`;
    document.querySelectorAll('.grav-btn').forEach(b => b.classList.remove('active'));
    apiSetGravity(val);
  });

  // Friction Presets
  document.querySelectorAll('.fric-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.fric-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      apiSetFriction(btn.dataset.preset);
    });
  });

  sliderFriction.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    customFricVal.textContent = val;
    document.querySelectorAll('.fric-btn').forEach(b => b.classList.remove('active'));
    apiSetFriction(val);
  });

  // Joint Presets
  document.querySelectorAll('.joint-preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      apiLoadJointPreset(btn.dataset.preset);
    });
  });

  // Canvas Action Buttons
  document.getElementById('btnDropBall').addEventListener('click', () => {
    const rx = 150 + Math.random() * (WIDTH - 300);
    apiDropBall(rx, 70);
  });

  document.getElementById('btnDropMulti').addEventListener('click', () => {
    apiDropMultiBalls();
  });

  document.getElementById('btnPendulum').addEventListener('click', () => {
    apiLoadJointPreset('pendulum');
  });

  document.getElementById('btnSpring').addEventListener('click', () => {
    apiLoadJointPreset('spring');
  });

  document.getElementById('btnPushUp').addEventListener('click', () => {
    apiPushUp();
  });

  document.getElementById('btnReset').addEventListener('click', () => {
    apiReset();
  });

  // Mouse Interaction State (Drag to Move/Fling, Hover, & Remove)
  let draggedBall = null;
  let hoveredBall = null;
  let dragOffsetX = 0;
  let dragOffsetY = 0;
  let isMouseDown = false;
  let hasMovedDuringDrag = false;
  let dragPositions = [];

  function getBallAt(x, y) {
    for (let i = balls.length - 1; i >= 0; i--) {
      const b = balls[i];
      const dist = Math.hypot(x - b.x, y - b.y);
      if (dist <= b.radius + 5) {
        return b;
      }
    }
    return null;
  }

  // Mouse Down: Start dragging if clicked on a ball
  canvas.addEventListener('mousedown', (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) * (WIDTH / rect.width);
    const y = (e.clientY - rect.top) * (HEIGHT / rect.height);

    if (e.button === 0) { // Left-click
      isMouseDown = true;
      hasMovedDuringDrag = false;
      const clicked = getBallAt(x, y);

      if (clicked) {
        draggedBall = clicked;
        dragOffsetX = clicked.x - x;
        dragOffsetY = clicked.y - y;
        draggedBall.vx = 0;
        draggedBall.vy = 0;
        dragPositions = [{ x: clicked.x, y: clicked.y, time: performance.now() }];
        canvas.style.cursor = 'grabbing';
      }
    }
  });

  // Mouse Move: Drag ball or update hover indicator
  window.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) * (WIDTH / rect.width);
    const y = (e.clientY - rect.top) * (HEIGHT / rect.height);

    if (draggedBall) {
      hasMovedDuringDrag = true;
      const targetX = x + dragOffsetX;
      const targetY = y + dragOffsetY;

      // Constrain inside world bounds
      const clampedX = Math.max(draggedBall.radius, Math.min(WIDTH - draggedBall.radius, targetX));
      const clampedY = Math.max(draggedBall.radius, Math.min(FLOOR_Y - draggedBall.radius, targetY));

      const now = performance.now();
      dragPositions.push({ x: clampedX, y: clampedY, time: now });
      dragPositions = dragPositions.filter(p => now - p.time < 120);

      draggedBall.x = clampedX;
      draggedBall.y = clampedY;
      draggedBall.vx = 0;
      draggedBall.vy = 0;
      canvas.style.cursor = 'grabbing';
    } else {
      if (x >= 0 && x <= WIDTH && y >= 0 && y <= HEIGHT) {
        hoveredBall = getBallAt(x, y);
        canvas.style.cursor = hoveredBall ? 'grab' : 'crosshair';
      } else {
        hoveredBall = null;
      }
    }
  });

  // Mouse Up: Release drag (with fling impulse) or drop ball if clicked empty area
  window.addEventListener('mouseup', (e) => {
    if (e.button === 0) {
      if (draggedBall) {
        const now = performance.now();
        const recent = dragPositions.filter(p => now - p.time < 100);
        if (recent.length >= 2) {
          const oldest = recent[0];
          const latest = recent[recent.length - 1];
          const dt = (latest.time - oldest.time) / 1000;
          if (dt > 0.01) {
            const rawVx = (latest.x - oldest.x) / dt;
            const rawVy = (latest.y - oldest.y) / dt;
            draggedBall.vx = Math.max(-900, Math.min(900, rawVx));
            draggedBall.vy = Math.max(-900, Math.min(900, rawVy));
          }
        }
        draggedBall = null;
        canvas.style.cursor = hoveredBall ? 'grab' : 'crosshair';
      } else if (isMouseDown && !hasMovedDuringDrag) {
        // Clicked on empty space inside canvas -> drop a ball!
        const rect = canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left) * (WIDTH / rect.width);
        const y = (e.clientY - rect.top) * (HEIGHT / rect.height);
        if (x >= 20 && x <= WIDTH - 20 && y >= 20 && y < FLOOR_Y - 20) {
          apiDropBall(x, y);
        }
      }
      isMouseDown = false;
      hasMovedDuringDrag = false;
    }
  });

  // Right-Click to Remove Ball
  canvas.addEventListener('contextmenu', (e) => {
    e.preventDefault();
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) * (WIDTH / rect.width);
    const y = (e.clientY - rect.top) * (HEIGHT / rect.height);
    const target = getBallAt(x, y);
    if (target) {
      apiRemoveBall(target.id);
    }
  });

  // Double-Click to Remove Ball
  canvas.addEventListener('dblclick', (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) * (WIDTH / rect.width);
    const y = (e.clientY - rect.top) * (HEIGHT / rect.height);
    const target = getBallAt(x, y);
    if (target) {
      apiRemoveBall(target.id);
    }
  });

  // Collision Spark Spawner
  function createSparks(x, y) {
    for (let i = 0; i < 8; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 20 + Math.random() * 60;
      sparks.push({
        x: x,
        y: y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        life: 1.0
      });
    }
  }

  // Physics Simulation Step
  let lastTime = performance.now();

  function updatePhysics(dt) {
    // 1. Solve Springs (Hooke's Law Forces before integration)
    for (const j of joints) {
      if (j.type === "spring") {
        const b = balls.find(ball => ball.id === j.ball1_id);
        if (b) {
          const ax = j.anchor_x;
          const ay = j.anchor_y;
          const dx = b.x - ax;
          const dy = b.y - ay;
          const dist = Math.hypot(dx, dy);
          if (dist > 0.001) {
            const stretch = dist - j.length;
            // Hooke's Law: F = -k * stretch - c * v_rel
            const k = j.stiffness || 100.0;
            const c = 2.0; // damping
            const nx = dx / dist;
            const ny = dy / dist;
            const radialV = b.vx * nx + b.vy * ny;
            const f = -k * stretch - c * radialV;

            b.vx += (nx * (f / b.mass)) * dt;
            b.vy += (ny * (f / b.mass)) * dt;
          }
        }
      }
    }

    // 2. Integrate Motion (Gravity & Velocities)
    for (const b of balls) {
      // If user is actively dragging this ball with cursor, skip physics integration
      if (b === draggedBall) {
        continue;
      }

      // Gravity
      b.vy += gravityScale * dt;

      // Position update
      b.x += b.vx * dt;
      b.y += b.vy * dt;

      // Floor & Friction
      if (b.y + b.radius >= FLOOR_Y) {
        b.y = FLOOR_Y - b.radius;
        b.vy = -b.vy * b.bounce;

        // Friction resistance
        b.vx *= Math.max(0.0, 1.0 - friction * 3.5 * dt);

        if (Math.abs(b.vx) < 1.0) b.vx = 0.0;
        if (Math.abs(b.vy) < 15.0) b.vy = 0.0;
      }

      // Air resistance
      b.vx *= 0.9995;

      // Wall bounces
      if (b.x - b.radius <= 0) {
        b.x = b.radius;
        b.vx = -b.vx * b.bounce;
      } else if (b.x + b.radius >= WIDTH) {
        b.x = WIDTH - b.radius;
        b.vx = -b.vx * b.bounce;
      }
    }

    // 3. Solve Distance Constraints / Rod Joints (Verlet / PBD relaxation)
    for (let iter = 0; iter < 4; iter++) {
      for (const j of joints) {
        if (j.type === "rod") {
          const b1 = balls.find(ball => ball.id === j.ball1_id);
          if (!b1) continue;

          if (j.ball2_id) {
            // Rod connecting two balls (Dumbbell)
            const b2 = balls.find(ball => ball.id === j.ball2_id);
            if (!b2) continue;

            const dx = b2.x - b1.x;
            const dy = b2.y - b1.y;
            const dist = Math.hypot(dx, dy);
            if (dist > 0.001) {
              const diff = dist - j.length;
              const nx = dx / dist;
              const ny = dy / dist;

              b1.x += nx * diff * 0.5;
              b1.y += ny * diff * 0.5;
              b2.x -= nx * diff * 0.5;
              b2.y -= ny * diff * 0.5;

              // Constrain velocity
              const relV = (b2.vx - b1.vx) * nx + (b2.vy - b1.vy) * ny;
              b1.vx += relV * nx * 0.4;
              b1.vy += relV * ny * 0.4;
              b2.vx -= relV * nx * 0.4;
              b2.vy -= relV * ny * 0.4;
            }
          } else {
            // Rod attached to fixed ceiling anchor (Pendulum)
            const ax = j.anchor_x;
            const ay = j.anchor_y;
            const dx = b1.x - ax;
            const dy = b1.y - ay;
            const dist = Math.hypot(dx, dy);
            if (dist > 0.001) {
              const diff = dist - j.length;
              const nx = dx / dist;
              const ny = dy / dist;

              b1.x -= nx * diff;
              b1.y -= ny * diff;

              // Cancel velocity component along rod constraint
              const radialV = b1.vx * nx + b1.vy * ny;
              b1.vx -= radialV * nx;
              b1.vy -= radialV * ny;
            }
          }
        }
      }
    }

    // 4. Circle-to-Circle Collision Detection
    const numBalls = balls.length;
    for (let i = 0; i < numBalls; i++) {
      for (let j = i + 1; j < numBalls; j++) {
        const b1 = balls[i];
        const b2 = balls[j];

        const dx = b2.x - b1.x;
        const dy = b2.y - b1.y;
        const dist = Math.hypot(dx, dy);
        const minDist = b1.radius + b2.radius;

        if (dist < minDist && dist > 0.001) {
          totalCollisions++;
          statCollisions.textContent = totalCollisions;

          const nx = dx / dist;
          const ny = dy / dist;

          // If one ball is actively held/dragged by cursor
          if (b1 === draggedBall) {
            b2.x += nx * (minDist - dist);
            b2.y += ny * (minDist - dist);
            b2.vx = nx * Math.max(140, Math.hypot(b2.vx, b2.vy));
            b2.vy = ny * Math.max(140, Math.hypot(b2.vx, b2.vy));
            createSparks(b1.x + nx * b1.radius, b1.y + ny * b1.radius);
            continue;
          }
          if (b2 === draggedBall) {
            b1.x -= nx * (minDist - dist);
            b1.y -= ny * (minDist - dist);
            b1.vx = -nx * Math.max(140, Math.hypot(b1.vx, b1.vy));
            b1.vy = -ny * Math.max(140, Math.hypot(b1.vx, b1.vy));
            createSparks(b1.x + nx * b1.radius, b1.y + ny * b1.radius);
            continue;
          }

          const overlap = (minDist - dist) * 0.5;
          b1.x -= nx * overlap;
          b1.y -= ny * overlap;
          b2.x += nx * overlap;
          b2.y += ny * overlap;

          const kx = b1.vx - b2.vx;
          const ky = b1.vy - b2.vy;
          const vNorm = kx * nx + ky * ny;

          if (vNorm > 0) {
            const restitution = (b1.bounce + b2.bounce) * 0.5;
            const impulseMag = (1.0 + restitution) * vNorm / (1.0 / b1.mass + 1.0 / b2.mass);

            b1.vx -= (impulseMag / b1.mass) * nx;
            b1.vy -= (impulseMag / b1.mass) * ny;
            b2.vx += (impulseMag / b2.mass) * nx;
            b2.vy += (impulseMag / b2.mass) * ny;

            createSparks(b1.x + nx * b1.radius, b1.y + ny * b1.radius);
          }
        }
      }
    }

    // 5. Update Sparks
    for (let i = sparks.length - 1; i >= 0; i--) {
      const s = sparks[i];
      s.x += s.vx * dt;
      s.y += s.vy * dt;
      s.life -= dt * 2.5;
      if (s.life <= 0) sparks.splice(i, 1);
    }
  }

  // Draw Constraints & Joints
  function drawJoints() {
    for (const j of joints) {
      if (j.type === "rod") {
        let ax, ay, bx, by;
        if (j.ball2_id) {
          const b1 = balls.find(b => b.id === j.ball1_id);
          const b2 = balls.find(b => b.id === j.ball2_id);
          if (!b1 || !b2) continue;
          ax = b1.x; ay = b1.y;
          bx = b2.x; by = b2.y;
        } else {
          const b1 = balls.find(b => b.id === j.ball1_id);
          if (!b1) continue;
          ax = j.anchor_x; ay = j.anchor_y;
          bx = b1.x; by = b1.y;

          // Draw Fixed Anchor Pin
          ctx.beginPath();
          ctx.arc(ax, ay, 8, 0, Math.PI * 2);
          ctx.fillStyle = "#475569";
          ctx.fill();
          ctx.lineWidth = 2;
          ctx.strokeStyle = "#ffffff";
          ctx.stroke();

          ctx.beginPath();
          ctx.arc(ax, ay, 3, 0, Math.PI * 2);
          ctx.fillStyle = "#38bdf8";
          ctx.fill();
        }

        // Draw Rod Line
        ctx.beginPath();
        ctx.moveTo(ax, ay);
        ctx.lineTo(bx, by);
        ctx.lineWidth = 4;
        ctx.strokeStyle = "#38bdf8";
        ctx.stroke();

      } else if (j.type === "spring") {
        const b1 = balls.find(b => b.id === j.ball1_id);
        if (!b1) continue;

        const ax = j.anchor_x;
        const ay = j.anchor_y;
        const bx = b1.x;
        const by = b1.y;

        // Draw Anchor Pin
        ctx.beginPath();
        ctx.arc(ax, ay, 8, 0, Math.PI * 2);
        ctx.fillStyle = "#475569";
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = "#10b981";
        ctx.stroke();

        // Draw Dynamic Zigzag Spring Coils
        const dx = bx - ax;
        const dy = by - ay;
        const dist = Math.hypot(dx, dy);
        const angle = Math.atan2(dy, dx);

        ctx.save();
        ctx.translate(ax, ay);
        ctx.rotate(angle);

        ctx.beginPath();
        ctx.moveTo(0, 0);
        const coils = 12;
        const step = dist / coils;
        const amp = 8;

        for (let c = 1; c < coils; c++) {
          const cx = c * step;
          const cy = (c % 2 === 0 ? 1 : -1) * amp;
          ctx.lineTo(cx, cy);
        }
        ctx.lineTo(dist, 0);

        ctx.strokeStyle = "#10b981";
        ctx.lineWidth = 2.5;
        ctx.stroke();
        ctx.restore();
      }
    }
  }

  // Main Render Routine
  function draw() {
    ctx.clearRect(0, 0, WIDTH, HEIGHT);

    // 1. Grid & Height Ruler
    ctx.strokeStyle = "rgba(51, 65, 85, 0.25)";
    ctx.lineWidth = 1;
    for (let y = FLOOR_Y; y >= 40; y -= PIXELS_PER_METER * 2) {
      ctx.beginPath();
      ctx.moveTo(35, y);
      ctx.lineTo(WIDTH, y);
      ctx.stroke();

      const meters = Math.round((FLOOR_Y - y) / PIXELS_PER_METER);
      ctx.fillStyle = "#64748b";
      ctx.font = "10px JetBrains Mono";
      ctx.fillText(`${meters}m`, 8, y + 3);
    }

    // 2. Draw Constraints & Joints
    drawJoints();

    // 3. Ground Surface
    ctx.fillStyle = "#1e293b";
    ctx.fillRect(0, FLOOR_Y, WIDTH, HEIGHT - FLOOR_Y);

    ctx.strokeStyle = friction < 0.1 ? "#38bdf8" : (friction > 0.6 ? "#d97706" : "#10b981");
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(0, FLOOR_Y);
    ctx.lineTo(WIDTH, FLOOR_Y);
    ctx.stroke();

    ctx.fillStyle = "#94a3b8";
    ctx.font = "11px Inter";
    ctx.fillText(`GROUND (Friction μ = ${friction})`, WIDTH - 180, FLOOR_Y + 22);

    // 4. Draw Balls
    for (const b of balls) {
      const distFromFloor = FLOOR_Y - (b.y + b.radius);
      if (distFromFloor < 140) {
        const shadowAlpha = Math.max(0, 0.45 * (1 - distFromFloor / 140));
        const shadowWidth = b.radius * (1 + distFromFloor / 90);
        ctx.fillStyle = `rgba(0, 0, 0, ${shadowAlpha})`;
        ctx.beginPath();
        ctx.ellipse(b.x, FLOOR_Y + 2, shadowWidth, 5, 0, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.beginPath();
      ctx.arc(b.x, b.y, b.radius, 0, Math.PI * 2);
      ctx.fillStyle = b.color;
      ctx.shadowColor = b.color;
      ctx.shadowBlur = 10;
      ctx.fill();
      ctx.shadowBlur = 0;

      ctx.lineWidth = 2;
      ctx.strokeStyle = "#ffffff";
      ctx.stroke();

      // Visual feedback: Highlight when hovered or dragged
      if (b === draggedBall) {
        ctx.beginPath();
        ctx.arc(b.x, b.y, b.radius + 6, 0, Math.PI * 2);
        ctx.strokeStyle = "rgba(56, 189, 248, 0.9)";
        ctx.lineWidth = 2.5;
        ctx.setLineDash([4, 4]);
        ctx.stroke();
        ctx.setLineDash([]);
      } else if (b === hoveredBall) {
        ctx.beginPath();
        ctx.arc(b.x, b.y, b.radius + 5, 0, Math.PI * 2);
        ctx.strokeStyle = "rgba(255, 255, 255, 0.85)";
        ctx.lineWidth = 2;
        ctx.stroke();

        // Small remove indicator tag on hover
        const tagX = b.x + b.radius * 0.7;
        const tagY = b.y - b.radius * 0.7;
        ctx.beginPath();
        ctx.arc(tagX, tagY, 7, 0, Math.PI * 2);
        ctx.fillStyle = "#ef4444";
        ctx.fill();
        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 9px sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("✕", tagX, tagY);
      }

      ctx.fillStyle = "#0f172a";
      ctx.font = "bold 10px JetBrains Mono";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(`#${b.id}`, b.x, b.y);

      const speed = Math.hypot(b.vx, b.vy);
      if (speed > 15) {
        ctx.strokeStyle = "rgba(255, 255, 255, 0.5)";
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(b.x, b.y);
        ctx.lineTo(b.x + Math.min(30, b.vx * 0.1), b.y + Math.min(30, b.vy * 0.1));
        ctx.stroke();
      }
    }

    // 5. Draw Collision Sparks
    for (const s of sparks) {
      ctx.fillStyle = `rgba(244, 63, 94, ${s.life})`;
      ctx.beginPath();
      ctx.arc(s.x, s.y, 3 * s.life, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  // Animation Loop
  function loop(currentTime) {
    const dt = Math.min(0.05, (currentTime - lastTime) / 1000);
    lastTime = currentTime;

    updatePhysics(dt);
    draw();

    requestAnimationFrame(loop);
  }

  // Start!
  loadInitialState();
  requestAnimationFrame(loop);
});
