/**
 * Physics Engine API Client
 * Encapsulates all REST calls to the Python Flask backend.
 */

const API = {
  baseUrl: window.location.origin,

  /** 1. Getting Simulation Data */
  async getState() {
    const res = await fetch(`${this.baseUrl}/api/simulation/state`);
    return await res.json();
  },

  async step(dt = 0.016, substeps = 4) {
    const res = await fetch(`${this.baseUrl}/api/step`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dt, substeps })
    });
    return await res.json();
  },

  async play() {
    const res = await fetch(`${this.baseUrl}/api/simulation/play`, { method: 'POST' });
    return await res.json();
  },

  async pause() {
    const res = await fetch(`${this.baseUrl}/api/simulation/pause`, { method: 'POST' });
    return await res.json();
  },

  async reset() {
    const res = await fetch(`${this.baseUrl}/api/simulation/reset`, { method: 'POST' });
    return await res.json();
  },

  /** 2. Creating Objects */
  async createObject(params) {
    const res = await fetch(`${this.baseUrl}/api/objects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    return await res.json();
  },

  async listObjects() {
    const res = await fetch(`${this.baseUrl}/api/objects`);
    return await res.json();
  },

  async getObject(bodyId) {
    const res = await fetch(`${this.baseUrl}/api/objects/${bodyId}`);
    return await res.json();
  },

  async deleteObject(bodyId) {
    const res = await fetch(`${this.baseUrl}/api/objects/${bodyId}`, { method: 'DELETE' });
    return await res.json();
  },

  /** 3. Applying Gravity */
  async getGravity() {
    const res = await fetch(`${this.baseUrl}/api/gravity`);
    return await res.json();
  },

  async setGravity(x, y) {
    const res = await fetch(`${this.baseUrl}/api/gravity`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ x, y })
    });
    return await res.json();
  },

  /** 4. Collision Detection */
  async getCollisions() {
    const res = await fetch(`${this.baseUrl}/api/collisions`);
    return await res.json();
  },

  /** 5. Controlling Movement (Speed, Direction, Position, Angle) */
  async updateMovement(bodyId, updateData) {
    const res = await fetch(`${this.baseUrl}/api/objects/${bodyId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updateData)
    });
    return await res.json();
  },

  /** 6. Applying Forces (Push, Pull, Throw / Impulses) */
  async applyForce(bodyId, fx, fy) {
    const res = await fetch(`${this.baseUrl}/api/objects/${bodyId}/force`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fx, fy })
    });
    return await res.json();
  },

  async applyImpulse(bodyId, ix, iy) {
    const res = await fetch(`${this.baseUrl}/api/objects/${bodyId}/impulse`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ix, iy })
    });
    return await res.json();
  },

  /** 7. Constraints & Joints */
  async createJoint(jointData) {
    const res = await fetch(`${this.baseUrl}/api/joints`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(jointData)
    });
    return await res.json();
  },

  async deleteJoint(jointId) {
    const res = await fetch(`${this.baseUrl}/api/joints/${jointId}`, { method: 'DELETE' });
    return await res.json();
  },

  /** 8. Presets */
  async getPresets() {
    const res = await fetch(`${this.baseUrl}/api/presets`);
    return await res.json();
  },

  async loadPreset(presetName) {
    const res = await fetch(`${this.baseUrl}/api/presets/${presetName}`, { method: 'POST' });
    return await res.json();
  }
};
