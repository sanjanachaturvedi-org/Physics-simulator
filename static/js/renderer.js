/**
 * High-performance Canvas Renderer for 2D Physics Engine.
 * Visualizes bodies, joints, contacts, velocity vectors, and interactive UI cues.
 */

class PhysicsRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.worldWidth = 1100;
    this.worldHeight = 650;

    // View settings
    this.showVectors = true;
    this.showCollisions = true;
    this.showJoints = true;
    this.showGrid = true;

    // Sparks for collisions
    this.sparks = [];

    // Trails history for pendulums / fast bodies
    this.trails = new Map(); // id -> array of {x, y, alpha}

    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
  }

  resizeCanvas() {
    const rect = this.canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.scaleX = this.canvas.width / this.worldWidth;
    this.scaleY = this.canvas.height / this.worldHeight;
    this.ctx.setTransform(this.scaleX, 0, 0, this.scaleY, 0, 0);
  }

  screenToWorld(clientX, clientY) {
    const rect = this.canvas.getBoundingClientRect();
    const x = (clientX - rect.left) * (this.worldWidth / rect.width);
    const y = (clientY - rect.top) * (this.worldHeight / rect.height);
    return { x, y };
  }

  clear() {
    this.ctx.clearRect(0, 0, this.worldWidth, this.worldHeight);
  }

  drawGrid() {
    if (!this.showGrid) return;
    const ctx = this.ctx;
    ctx.save();
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.04)';
    ctx.lineWidth = 1;

    const gridSize = 50;
    for (let x = 0; x <= this.worldWidth; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, this.worldHeight);
      ctx.stroke();
    }
    for (let y = 0; y <= this.worldHeight; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(this.worldWidth, y);
      ctx.stroke();
    }
    ctx.restore();
  }

  drawBody(b, isSelected = false) {
    const ctx = this.ctx;
    ctx.save();

    const isStatic = b.body_type === 'static';

    if (isSelected) {
      ctx.shadowColor = '#38bdf8';
      ctx.shadowBlur = 15;
    }

    if (b.shape_type === 'circle') {
      // Circle body
      ctx.beginPath();
      ctx.arc(b.position.x, b.position.y, b.radius, 0, Math.PI * 2);
      ctx.fillStyle = b.color || '#38bdf8';
      ctx.fill();

      ctx.lineWidth = isSelected ? 3 : 1.5;
      ctx.strokeStyle = isSelected ? '#ffffff' : 'rgba(255, 255, 255, 0.6)';
      ctx.stroke();

      // Orientation indicator line
      ctx.beginPath();
      ctx.moveTo(b.position.x, b.position.y);
      const angle = b.angle || 0;
      ctx.lineTo(
        b.position.x + Math.cos(angle) * b.radius,
        b.position.y + Math.sin(angle) * b.radius
      );
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.9)';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Center pivot point
      ctx.beginPath();
      ctx.arc(b.position.x, b.position.y, 3, 0, Math.PI * 2);
      ctx.fillStyle = '#ffffff';
      ctx.fill();

    } else if (b.shape_type === 'box') {
      // Box body
      const verts = b.vertices;
      if (verts && verts.length >= 4) {
        ctx.beginPath();
        ctx.moveTo(verts[0].x, verts[0].y);
        for (let i = 1; i < verts.length; i++) {
          ctx.lineTo(verts[i].x, verts[i].y);
        }
        ctx.closePath();

        ctx.fillStyle = b.color || '#818cf8';
        ctx.fill();

        ctx.lineWidth = isSelected ? 3 : 1.5;
        ctx.strokeStyle = isSelected ? '#ffffff' : (isStatic ? '#475569' : 'rgba(255, 255, 255, 0.5)');
        ctx.stroke();
      }
    }

    // Velocity Vector Arrow
    if (this.showVectors && !isStatic && (b.velocity.x !== 0 || b.velocity.y !== 0)) {
      const speed = Math.hypot(b.velocity.x, b.velocity.y);
      if (speed > 5) {
        const vLen = Math.min(speed * 0.15, 60);
        const vx = (b.velocity.x / speed) * vLen;
        const vy = (b.velocity.y / speed) * vLen;

        ctx.beginPath();
        ctx.moveTo(b.position.x, b.position.y);
        ctx.lineTo(b.position.x + vx, b.position.y + vy);
        ctx.strokeStyle = '#34d399';
        ctx.lineWidth = 1.8;
        ctx.stroke();

        // Arrow tip
        const headAngle = Math.atan2(vy, vx);
        ctx.beginPath();
        ctx.moveTo(b.position.x + vx, b.position.y + vy);
        ctx.lineTo(
          b.position.x + vx - 6 * Math.cos(headAngle - Math.PI / 6),
          b.position.y + vy - 6 * Math.sin(headAngle - Math.PI / 6)
        );
        ctx.lineTo(
          b.position.x + vx - 6 * Math.cos(headAngle + Math.PI / 6),
          b.position.y + vy - 6 * Math.sin(headAngle + Math.PI / 6)
        );
        ctx.fillStyle = '#34d399';
        ctx.fill();
      }
    }

    ctx.restore();
  }

  drawJoint(j) {
    if (!this.showJoints) return;
    const ctx = this.ctx;
    ctx.save();

    const ax = j.anchorA.x;
    const ay = j.anchorA.y;
    const bx = j.anchorB.x;
    const by = j.anchorB.y;

    if (j.type === 'spring') {
      // Draw zigzag spring
      const dx = bx - ax;
      const dy = by - ay;
      const dist = Math.hypot(dx, dy);
      const angle = Math.atan2(dy, dx);

      ctx.save();
      ctx.translate(ax, ay);
      ctx.rotate(angle);

      ctx.beginPath();
      ctx.moveTo(0, 0);
      const coils = 10;
      const step = dist / coils;
      const amplitude = 8;

      for (let i = 1; i < coils; i++) {
        const x = i * step;
        const y = (i % 2 === 0 ? 1 : -1) * amplitude;
        ctx.lineTo(x, y);
      }
      ctx.lineTo(dist, 0);

      ctx.strokeStyle = '#f43f5e';
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.restore();

    } else {
      // Distance Joint / Rod
      ctx.beginPath();
      ctx.moveTo(ax, ay);
      ctx.lineTo(bx, by);
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.7)';
      ctx.lineWidth = 2.5;
      ctx.stroke();

      // Connector pin ends
      ctx.beginPath();
      ctx.arc(ax, ay, 4, 0, Math.PI * 2);
      ctx.arc(bx, by, 4, 0, Math.PI * 2);
      ctx.fillStyle = '#ffffff';
      ctx.fill();
    }

    ctx.restore();
  }

  drawCollisions(collisions) {
    if (!this.showCollisions || !collisions) return;
    const ctx = this.ctx;
    ctx.save();

    for (const c of collisions) {
      if (!c.contact_points) continue;
      for (const p of c.contact_points) {
        // Glowing contact spark
        ctx.beginPath();
        ctx.arc(p.x, p.y, 5, 0, Math.PI * 2);
        ctx.fillStyle = '#f43f5e';
        ctx.shadowColor = '#f43f5e';
        ctx.shadowBlur = 12;
        ctx.fill();

        // Contact normal arrow
        if (c.normal) {
          const nx = c.normal.x * 20;
          const ny = c.normal.y * 20;
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p.x + nx, p.y + ny);
          ctx.strokeStyle = '#fbbf24';
          ctx.lineWidth = 2;
          ctx.stroke();
        }
      }
    }
    ctx.restore();
  }

  drawInteraction(dragStart, dragCurrent, mode) {
    if (!dragStart || !dragCurrent) return;
    const ctx = this.ctx;
    ctx.save();

    if (mode === 'fling' || mode === 'force') {
      // Arrow showing force/impulse vector
      ctx.beginPath();
      ctx.moveTo(dragStart.x, dragStart.y);
      ctx.lineTo(dragCurrent.x, dragCurrent.y);
      ctx.strokeStyle = '#f59e0b';
      ctx.lineWidth = 3;
      ctx.setLineDash([5, 5]);
      ctx.stroke();

      // Arrow head
      const angle = Math.atan2(dragCurrent.y - dragStart.y, dragCurrent.x - dragStart.x);
      ctx.beginPath();
      ctx.moveTo(dragCurrent.x, dragCurrent.y);
      ctx.lineTo(
        dragCurrent.x - 12 * Math.cos(angle - Math.PI / 6),
        dragCurrent.y - 12 * Math.sin(angle - Math.PI / 6)
      );
      ctx.lineTo(
        dragCurrent.x - 12 * Math.cos(angle + Math.PI / 6),
        dragCurrent.y - 12 * Math.sin(angle + Math.PI / 6)
      );
      ctx.fillStyle = '#f59e0b';
      ctx.fill();

    } else if (mode === 'connect') {
      ctx.beginPath();
      ctx.moveTo(dragStart.x, dragStart.y);
      ctx.lineTo(dragCurrent.x, dragCurrent.y);
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 2;
      ctx.setLineDash([4, 4]);
      ctx.stroke();
    }

    ctx.restore();
  }

  render(state, selectedBodyId = null, interaction = null) {
    this.clear();
    this.drawGrid();

    // 1. Draw Joints
    if (state.joints) {
      for (const j of state.joints) {
        this.drawJoint(j);
      }
    }

    // 2. Draw Bodies
    if (state.bodies) {
      for (const b of state.bodies) {
        this.drawBody(b, b.id === selectedBodyId);
      }
    }

    // 3. Draw Collisions
    if (state.collisions) {
      this.drawCollisions(state.collisions);
    }

    // 4. Draw Interactive drag lines
    if (interaction && interaction.isDragging) {
      this.drawInteraction(interaction.start, interaction.current, interaction.mode);
    }
  }
}
