/**
 * Main Application Controller for Aether-2D Physics Engine.
 * Manages simulation loop, canvas interactions, inspector, telemetry, and live API tester.
 */

document.addEventListener('DOMContentLoaded', async () => {
  const canvas = document.getElementById('simCanvas');
  const renderer = new PhysicsRenderer(canvas);

  // App State
  let simState = { bodies: [], joints: [], collisions: [], metrics: {} };
  let isRunning = true;
  let currentTool = 'drag'; // 'drag', 'inspect', 'spawn_ball', 'spawn_box', 'connect', 'blast'
  let selectedBody = null;
  let connectSourceBody = null;

  // Interaction tracking
  const interaction = {
    isDragging: false,
    start: null,
    current: null,
    body: null,
    mode: 'fling'
  };

  // Performance telemetry
  let lastFrameTime = performance.now();
  let frameCount = 0;
  let fps = 60;

  // Cache DOM elements
  const elStatusBadge = document.getElementById('statusBadge');
  const elStatusText = document.getElementById('statusText');
  const elFps = document.getElementById('fpsDisplay');
  const elSimTime = document.getElementById('simTime');
  const elBodyCount = document.getElementById('bodyCount');
  const elJointCount = document.getElementById('jointCount');
  const elCollisionCount = document.getElementById('collisionCount');
  const elKe = document.getElementById('kineticEnergy');
  const elPe = document.getElementById('potentialEnergy');
  const elTotalEnergy = document.getElementById('totalEnergy');
  const elBtnPlayPause = document.getElementById('btnPlayPause');
  const elGravityY = document.getElementById('gravityY');
  const elGravityYVal = document.getElementById('gravityYVal');
  const elGravityX = document.getElementById('gravityX');
  const elGravityXVal = document.getElementById('gravityXVal');
  const elCollisionsList = document.getElementById('collisionsList');

  // Inspector DOM
  const elInspectorEmpty = document.getElementById('inspectorEmpty');
  const elInspectorContent = document.getElementById('inspectorContent');
  const elInspId = document.getElementById('inspId');
  const elInspType = document.getElementById('inspType');
  const elInspPos = document.getElementById('inspPos');
  const elInspVel = document.getElementById('inspVel');
  const elInspSpeed = document.getElementById('inspSpeed');
  const elInspMass = document.getElementById('inspMass');
  const elInspRestitution = document.getElementById('inspRestitution');
  const elInspRestitutionVal = document.getElementById('inspRestitutionVal');
  const elInspFriction = document.getElementById('inspFriction');
  const elInspFrictionVal = document.getElementById('inspFrictionVal');

  // Initialize simulation
  async function init() {
    try {
      const resp = await API.getState();
      if (resp.status === 'success') {
        simState = resp.data;
        updateUI();
        elStatusBadge.classList.remove('error');
        elStatusText.textContent = 'API ONLINE (Flask)';
      }
    } catch (err) {
      console.error('Failed to connect to Physics Engine API:', err);
      elStatusBadge.classList.add('error');
      elStatusText.textContent = 'API OFFLINE';
    }

    startSimulationLoop();
  }

  // Find body at world coordinate
  function getBodyAt(pos) {
    if (!simState.bodies) return null;
    // Iterate in reverse (topmost first)
    for (let i = simState.bodies.length - 1; i >= 0; i--) {
      const b = simState.bodies[i];
      if (b.shape_type === 'circle') {
        const dx = pos.x - b.position.x;
        const dy = pos.y - b.position.y;
        if (dx * dx + dy * dy <= b.radius * b.radius) {
          return b;
        }
      } else if (b.shape_type === 'box') {
        // Point in box check
        const hw = (b.width || 40) / 2;
        const hh = (b.height || 40) / 2;
        const cos = Math.cos(-b.angle);
        const sin = Math.sin(-b.angle);
        const dx = pos.x - b.position.x;
        const dy = pos.y - b.position.y;
        const lx = dx * cos - dy * sin;
        const ly = dx * sin + dy * cos;
        if (Math.abs(lx) <= hw && Math.abs(ly) <= hh) {
          return b;
        }
      }
    }
    return null;
  }

  // Main animation / simulation loop
  let stepInFlight = false;

  async function startSimulationLoop() {
    async function loop(timestamp) {
      // FPS calculation
      frameCount++;
      if (timestamp - lastFrameTime >= 1000) {
        fps = frameCount;
        frameCount = 0;
        lastFrameTime = timestamp;
        if (elFps) elFps.textContent = `${fps} FPS`;
      }

      // Step physics via Python REST API if running
      if (isRunning && !stepInFlight) {
        stepInFlight = true;
        try {
          const resp = await API.step(0.016, 4);
          if (resp.status === 'success') {
            simState = resp.data;
            updateUI();
          }
        } catch (e) {
          // ignore transient connection issues
        } finally {
          stepInFlight = false;
        }
      }

      // Render world
      renderer.render(
        simState,
        selectedBody ? selectedBody.id : null,
        interaction
      );

      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);
  }

  // Update UI & Telemetry
  function updateUI() {
    if (!simState.metrics) return;

    if (elBodyCount) elBodyCount.textContent = simState.metrics.body_count || 0;
    if (elJointCount) elJointCount.textContent = simState.metrics.joint_count || 0;
    if (elCollisionCount) elCollisionCount.textContent = simState.metrics.active_collisions || 0;
    if (elKe) elKe.textContent = Math.round(simState.metrics.kinetic_energy || 0).toLocaleString();
    if (elPe) elPe.textContent = Math.round(simState.metrics.potential_energy || 0).toLocaleString();
    if (elTotalEnergy) elTotalEnergy.textContent = Math.round(simState.metrics.total_energy || 0).toLocaleString();
    if (elSimTime) elSimTime.textContent = `${simState.time || 0}s`;

    // Collisions list feed
    if (elCollisionsList && simState.collisions) {
      if (simState.collisions.length === 0) {
        elCollisionsList.innerHTML = '<div style="color: var(--text-muted); font-size:0.75rem; text-align:center; padding:10px;">No active collisions</div>';
      } else {
        elCollisionsList.innerHTML = simState.collisions.map(c => `
          <div class="collision-item">
            <span><strong>${c.bodyA}</strong> ⚡ <strong>${c.bodyB}</strong></span>
            <span>d=${c.depth.toFixed(1)}px</span>
          </div>
        `).join('');
      }
    }

    // Keep inspector updated if an object is selected
    if (selectedBody) {
      const refreshed = simState.bodies.find(b => b.id === selectedBody.id);
      if (refreshed) {
        selectedBody = refreshed;
        renderInspector(refreshed);
      } else {
        selectedBody = null;
        renderInspector(null);
      }
    }
  }

  // Inspector details render
  function renderInspector(body) {
    if (!body) {
      elInspectorEmpty.style.display = 'block';
      elInspectorContent.style.display = 'none';
      return;
    }

    elInspectorEmpty.style.display = 'none';
    elInspectorContent.style.display = 'block';

    elInspId.textContent = body.id;
    elInspType.textContent = `${body.shape_type} (${body.body_type})`;
    elInspPos.textContent = `(${Math.round(body.position.x)}, ${Math.round(body.position.y)})`;
    elInspVel.textContent = `(${Math.round(body.velocity.x)}, ${Math.round(body.velocity.y)})`;
    elInspSpeed.textContent = `${Math.round(body.speed)} px/s`;
    elInspMass.textContent = body.mass === 'inf' ? '∞' : `${body.mass} kg`;

    elInspRestitution.value = body.restitution;
    elInspRestitutionVal.textContent = body.restitution;
    elInspFriction.value = body.friction;
    elInspFrictionVal.textContent = body.friction;
  }

  // Mouse & Touch Interactions
  canvas.addEventListener('mousedown', (e) => {
    const worldPos = renderer.screenToWorld(e.clientX, e.clientY);
    const hitBody = getBodyAt(worldPos);

    if (currentTool === 'inspect') {
      selectedBody = hitBody;
      renderInspector(hitBody);
      return;
    }

    if (currentTool === 'drag' || currentTool === 'fling') {
      if (hitBody && hitBody.body_type !== 'static') {
        selectedBody = hitBody;
        renderInspector(hitBody);
        interaction.isDragging = true;
        interaction.start = worldPos;
        interaction.current = worldPos;
        interaction.body = hitBody;
        interaction.mode = 'fling';
      }
    } else if (currentTool === 'spawn_ball' || currentTool === 'spawn_box') {
      interaction.isDragging = true;
      interaction.start = worldPos;
      interaction.current = worldPos;
      interaction.body = null;
      interaction.mode = 'fling';
    } else if (currentTool === 'connect') {
      if (hitBody) {
        if (!connectSourceBody) {
          connectSourceBody = hitBody;
          interaction.isDragging = true;
          interaction.start = hitBody.position;
          interaction.current = worldPos;
          interaction.mode = 'connect';
        } else {
          // Connect connectSourceBody with hitBody
          if (connectSourceBody.id !== hitBody.id) {
            API.createJoint({
              type: 'distance',
              bodyA: connectSourceBody.id,
              bodyB: hitBody.id
            });
          }
          connectSourceBody = null;
          interaction.isDragging = false;
        }
      }
    } else if (currentTool === 'blast') {
      // Blast wave force applied to nearby bodies
      applyBlastForce(worldPos);
    }
  });

  window.addEventListener('mousemove', (e) => {
    if (!interaction.isDragging) return;
    const worldPos = renderer.screenToWorld(e.clientX, e.clientY);
    interaction.current = worldPos;
  });

  window.addEventListener('mouseup', async (e) => {
    if (!interaction.isDragging) return;
    const worldPos = renderer.screenToWorld(e.clientX, e.clientY);
    const start = interaction.start;
    const dx = worldPos.x - start.x;
    const dy = worldPos.y - start.y;

    if (interaction.mode === 'fling' && interaction.body) {
      // 5. Applying Forces / Impulses via API!
      const impulseX = dx * 6;
      const impulseY = dy * 6;
      if (Math.hypot(impulseX, impulseY) > 10) {
        await API.applyImpulse(interaction.body.id, impulseX, impulseY);
      }
    } else if (currentTool === 'spawn_ball') {
      // 2. Creating Objects via API!
      await API.createObject({
        shape_type: 'circle',
        x: start.x,
        y: start.y,
        vx: dx * 3,
        vy: dy * 3,
        radius: 20 + Math.random() * 8,
        mass: 2.0,
        restitution: 0.75,
        friction: 0.25
      });
    } else if (currentTool === 'spawn_box') {
      // 2. Creating Objects via API!
      await API.createObject({
        shape_type: 'box',
        x: start.x,
        y: start.y,
        vx: dx * 3,
        vy: dy * 3,
        width: 40 + Math.random() * 15,
        height: 40 + Math.random() * 15,
        mass: 2.5,
        restitution: 0.4,
        friction: 0.5
      });
    }

    interaction.isDragging = false;
    interaction.start = null;
    interaction.current = null;
    interaction.body = null;
  });

  // Blast wave physics via API
  async function applyBlastForce(pos) {
    if (!simState.bodies) return;
    for (const b of simState.bodies) {
      if (b.body_type === 'static') continue;
      const dx = b.position.x - pos.x;
      const dy = b.position.y - pos.y;
      const dist = Math.hypot(dx, dy);
      if (dist < 300 && dist > 1) {
        const factor = (1 - dist / 300) * 1200;
        const ix = (dx / dist) * factor;
        const iy = (dy / dist) * factor;
        API.applyImpulse(b.id, ix, iy);
      }
    }
  }

  // Tool buttons
  document.querySelectorAll('.tool-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentTool = btn.dataset.tool;
      connectSourceBody = null;
    });
  });

  // Play / Pause / Step / Reset
  if (elBtnPlayPause) {
    elBtnPlayPause.addEventListener('click', async () => {
      isRunning = !isRunning;
      elBtnPlayPause.innerHTML = isRunning ? '⏸ Pause' : '▶ Play';
      if (isRunning) await API.play();
      else await API.pause();
    });
  }

  const btnStep = document.getElementById('btnStep');
  if (btnStep) {
    btnStep.addEventListener('click', async () => {
      isRunning = false;
      if (elBtnPlayPause) elBtnPlayPause.innerHTML = '▶ Play';
      const res = await API.step(0.016, 6);
      if (res.status === 'success') {
        simState = res.data;
        updateUI();
      }
    });
  }

  const btnReset = document.getElementById('btnReset');
  if (btnReset) {
    btnReset.addEventListener('click', async () => {
      const res = await API.reset();
      if (res.status === 'success') {
        simState = res.data;
        selectedBody = null;
        renderInspector(null);
        updateUI();
      }
    });
  }

  // Presets selector
  document.querySelectorAll('.preset-chip').forEach(chip => {
    chip.addEventListener('click', async () => {
      document.querySelectorAll('.preset-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      const preset = chip.dataset.preset;
      const res = await API.loadPreset(preset);
      if (res.status === 'success') {
        simState = res.data;
        selectedBody = null;
        renderInspector(null);
        updateUI();
      }
    });
  });

  // 3. Applying Gravity via API!
  if (elGravityY) {
    elGravityY.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value);
      elGravityYVal.textContent = `${val} px/s²`;
      API.setGravity(parseFloat(elGravityX ? elGravityX.value : 0), val);
    });
  }
  if (elGravityX) {
    elGravityX.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value);
      elGravityXVal.textContent = `${val} px/s²`;
      API.setGravity(val, parseFloat(elGravityY ? elGravityY.value : 600));
    });
  }

  // Quick Gravity Presets
  document.querySelectorAll('.grav-preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const gy = parseFloat(btn.dataset.gy);
      const gx = parseFloat(btn.dataset.gx || 0);
      if (elGravityY) {
        elGravityY.value = gy;
        elGravityYVal.textContent = `${gy} px/s²`;
      }
      if (elGravityX) {
        elGravityX.value = gx;
        elGravityXVal.textContent = `${gx} px/s²`;
      }
      API.setGravity(gx, gy);
    });
  });

  // 4. Controlling Movement via Inspector (Speed, Restitution, Friction)
  if (elInspRestitution) {
    elInspRestitution.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value);
      elInspRestitutionVal.textContent = val;
      if (selectedBody) {
        API.updateMovement(selectedBody.id, { restitution: val });
      }
    });
  }

  if (elInspFriction) {
    elInspFriction.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value);
      elInspFrictionVal.textContent = val;
      if (selectedBody) {
        API.updateMovement(selectedBody.id, { friction: val });
      }
    });
  }

  // Force push buttons in inspector
  document.querySelectorAll('.insp-force-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      if (!selectedBody) return;
      const fx = parseFloat(btn.dataset.fx || 0);
      const fy = parseFloat(btn.dataset.fy || 0);
      API.applyImpulse(selectedBody.id, fx, fy);
    });
  });

  // Delete body button
  const btnDeleteBody = document.getElementById('btnDeleteBody');
  if (btnDeleteBody) {
    btnDeleteBody.addEventListener('click', async () => {
      if (!selectedBody) return;
      await API.deleteObject(selectedBody.id);
      selectedBody = null;
      renderInspector(null);
    });
  }

  // Tab switching in sidebar
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      const tabId = btn.dataset.tab;
      document.getElementById(tabId).classList.add('active');
    });
  });

  // View Toggles
  const chkVectors = document.getElementById('chkVectors');
  if (chkVectors) {
    chkVectors.addEventListener('change', (e) => renderer.showVectors = e.target.checked);
  }
  const chkCollisions = document.getElementById('chkCollisions');
  if (chkCollisions) {
    chkCollisions.addEventListener('change', (e) => renderer.showCollisions = e.target.checked);
  }
  const chkGrid = document.getElementById('chkGrid');
  if (chkGrid) {
    chkGrid.addEventListener('change', (e) => renderer.showGrid = e.target.checked);
  }

  // ==========================================
  // Interactive Live API Tester Modal
  // ==========================================
  const modalApi = document.getElementById('modalApi');
  const btnOpenApi = document.getElementById('btnOpenApi');
  const btnCloseApi = document.getElementById('btnCloseApi');
  const elApiMethod = document.getElementById('apiMethod');
  const elApiEndpoint = document.getElementById('apiEndpoint');
  const elApiPayload = document.getElementById('apiPayload');
  const elApiResponse = document.getElementById('apiResponse');
  const btnSendApi = document.getElementById('btnSendApi');

  const apiTemplates = {
    create_ball: {
      method: 'POST',
      url: '/api/objects',
      body: JSON.stringify({
        shape_type: "circle",
        x: 550, y: 150,
        vx: 120, vy: -50,
        radius: 25,
        mass: 3.0,
        restitution: 0.85,
        friction: 0.2,
        color: "#38bdf8",
        label: "SuperBall"
      }, null, 2)
    },
    create_box: {
      method: 'POST',
      url: '/api/objects',
      body: JSON.stringify({
        shape_type: "box",
        x: 500, y: 120,
        vx: 0, vy: 0,
        width: 50, height: 50,
        mass: 4.0,
        restitution: 0.5,
        friction: 0.4,
        color: "#f59e0b",
        label: "Crate"
      }, null, 2)
    },
    set_gravity: {
      method: 'POST',
      url: '/api/gravity',
      body: JSON.stringify({
        x: 0.0,
        y: 800.0
      }, null, 2)
    },
    get_collisions: {
      method: 'GET',
      url: '/api/collisions',
      body: ''
    },
    control_movement: {
      method: 'PUT',
      url: '/api/objects/b_1',
      body: JSON.stringify({
        x: 400,
        y: 200,
        vx: 250,
        vy: -150,
        restitution: 0.95
      }, null, 2)
    },
    apply_force: {
      method: 'POST',
      url: '/api/objects/b_1/force',
      body: JSON.stringify({
        fx: 1500.0,
        fy: -3000.0
      }, null, 2)
    },
    apply_impulse: {
      method: 'POST',
      url: '/api/objects/b_1/impulse',
      body: JSON.stringify({
        ix: 350.0,
        iy: -600.0
      }, null, 2)
    },
    get_simulation: {
      method: 'GET',
      url: '/api/simulation/state',
      body: ''
    }
  };

  if (btnOpenApi) {
    btnOpenApi.addEventListener('click', () => modalApi.classList.add('open'));
  }
  if (btnCloseApi) {
    btnCloseApi.addEventListener('click', () => modalApi.classList.remove('open'));
  }

  document.querySelectorAll('.api-endpoint-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.api-endpoint-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const key = btn.dataset.key;
      const tpl = apiTemplates[key];
      if (tpl) {
        elApiMethod.textContent = tpl.method;
        elApiMethod.className = `method-tag method-${tpl.method.toLowerCase()}`;
        elApiEndpoint.value = tpl.url;
        elApiPayload.value = tpl.body;
      }
    });
  });

  if (btnSendApi) {
    btnSendApi.addEventListener('click', async () => {
      const method = elApiMethod.textContent;
      const url = elApiEndpoint.value;
      const payloadStr = elApiPayload.value.trim();

      elApiResponse.textContent = 'Executing request...';
      const t0 = performance.now();

      try {
        const options = {
          method,
          headers: { 'Content-Type': 'application/json' }
        };
        if (method !== 'GET' && payloadStr) {
          options.body = payloadStr;
        }

        const resp = await fetch(url, options);
        const data = await resp.json();
        const duration = (performance.now() - t0).toFixed(1);

        elApiResponse.textContent = `// HTTP ${resp.status} OK (${duration}ms)\n` + JSON.stringify(data, null, 2);
      } catch (err) {
        elApiResponse.textContent = `Error executing request: ${err.message}`;
      }
    });
  }

  // Launch!
  init();
});
