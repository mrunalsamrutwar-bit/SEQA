/**
 * DFD Architect — Central State Store
 */
const State = {
  // Active Project & Model Data
  project: null,
  activeLevelId: null,
  components: [],     // All components in current project
  dataFlows: [],      // All data flows in current project
  levels: [],         // All levels in current project

  // Canvas Viewport State
  viewport: {
    zoom: 1.0,
    panX: 40,
    panY: 40,
    minZoom: 0.25,
    maxZoom: 2.5
  },

  // Selection & Interaction
  selectedNodeId: null,
  selectedFlowId: null,
  activeTool: 'select', // 'select', 'connect'
  connectingSourceId: null,
  connectingSourcePort: null,

  // User Preferences
  preferences: {
    theme: 'light',
    grid_visible: true,
    snap_to_grid: true,
    grid_size: 20,
    auto_save: true,
    notation_style: 'gane_sarson' // 'gane_sarson' or 'yourdon_demarcos'
  },

  // Event Listeners
  listeners: {},

  on(event, callback) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(callback);
  },

  emit(event, payload) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(cb => {
        try { cb(payload); } catch(e) { console.error(`Event error [${event}]:`, e); }
      });
    }
  },

  // State Mutators
  setProject(projectData) {
    this.project = projectData;
    this.levels = projectData.levels || [];
    this.components = projectData.components || [];
    this.dataFlows = projectData.data_flows || [];

    if (this.levels.length > 0 && !this.activeLevelId) {
      this.activeLevelId = this.levels[0].id;
    }

    this.emit('project:loaded', this.project);
    this.emit('level:changed', this.activeLevelId);
  },

  setActiveLevel(levelId) {
    this.activeLevelId = levelId;
    this.selectedNodeId = null;
    this.selectedFlowId = null;
    this.emit('level:changed', levelId);
  },

  getCurrentComponents() {
    if (!this.activeLevelId) return this.components;
    return this.components.filter(c => c.level_id === this.activeLevelId);
  },

  getCurrentFlows() {
    if (!this.activeLevelId) return this.dataFlows;
    return this.dataFlows.filter(f => f.level_id === this.activeLevelId);
  },

  getComponentById(id) {
    return this.components.find(c => c.id === id);
  },

  getFlowById(id) {
    return this.dataFlows.find(f => f.id === id);
  },

  updateComponentLocal(id, updates) {
    const comp = this.getComponentById(id);
    if (comp) {
      Object.assign(comp, updates);
      this.emit('component:updated', comp);
    }
  },

  updateFlowLocal(id, updates) {
    const flow = this.getFlowById(id);
    if (flow) {
      Object.assign(flow, updates);
      this.emit('flow:updated', flow);
    }
  }
};
