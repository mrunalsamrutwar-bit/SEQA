/**
 * DFD Architect — Core Canvas Engine (Zoom, Pan, Interaction, Minimap)
 */
const CanvasEngine = {
  isPanning: false,
  isDraggingNode: false,
  isConnecting: false,

  panStart: { x: 0, y: 0 },
  draggedNodeId: null,
  nodeDragOffset: { x: 0, y: 0 },
  connectingSource: { id: null, side: null, x: 0, y: 0 },

  init() {
    const viewport = document.getElementById('canvas-viewport');
    if (!viewport) return;

    // Viewport Panning & Zooming Listeners
    viewport.addEventListener('mousedown', (e) => this.handleMouseDown(e));
    window.addEventListener('mousemove', (e) => this.handleMouseMove(e));
    window.addEventListener('mouseup', (e) => this.handleMouseUp(e));
    viewport.addEventListener('wheel', (e) => this.handleWheel(e), { passive: false });

    // Deselect on empty canvas click
    viewport.addEventListener('click', (e) => {
      if (e.target.id === 'canvas-viewport' || e.target.id === 'canvas-grid' || e.target.id === 'canvas-transform-layer') {
        Designer.deselectAll();
      }
    });

    this.applyTransform();
  },

  render() {
    Nodes.renderNodes();
    Connections.renderFlows();
    this.updateMinimap();
  },

  // Coordinate Conversion: Screen to Canvas World Coordinates
  screenToWorld(clientX, clientY) {
    const viewport = document.getElementById('canvas-viewport');
    const rect = viewport.getBoundingClientRect();
    const x = (clientX - rect.left - State.viewport.panX) / State.viewport.zoom;
    const y = (clientY - rect.top - State.viewport.panY) / State.viewport.zoom;
    return { x, y };
  },

  applyTransform() {
    const layer = document.getElementById('canvas-transform-layer');
    if (!layer) return;
    layer.style.transform = `translate(${State.viewport.panX}px, ${State.viewport.panY}px) scale(${State.viewport.zoom})`;
    
    // Also move grid background
    const grid = document.getElementById('canvas-grid');
    if (grid) {
      grid.style.transform = `translate(${State.viewport.panX % 20}px, ${State.viewport.panY % 20}px)`;
    }

    this.updateMinimap();
  },

  handleWheel(e) {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
    const newZoom = Math.min(State.viewport.maxZoom, Math.max(State.viewport.minZoom, State.viewport.zoom * zoomFactor));
    
    if (newZoom !== State.viewport.zoom) {
      const mouseWorld = this.screenToWorld(e.clientX, e.clientY);
      State.viewport.panX = e.clientX - mouseWorld.x * newZoom;
      State.viewport.panY = e.clientY - mouseWorld.y * newZoom;
      State.viewport.zoom = newZoom;
      this.applyTransform();
    }
  },

  handleMouseDown(e) {
    // Start Panning if middle click, spacebar down, or clicking empty viewport
    if (e.button === 1 || e.spaceKey || (e.target.id === 'canvas-viewport' || e.target.id === 'canvas-grid')) {
      this.isPanning = true;
      this.panStart = { x: e.clientX - State.viewport.panX, y: e.clientY - State.viewport.panY };
      document.body.style.cursor = 'grabbing';
    }
  },

  startDraggingNode(nodeId, e) {
    this.isDraggingNode = true;
    this.draggedNodeId = nodeId;
    Designer.selectNode(nodeId);

    const comp = State.getComponentById(nodeId);
    const mouseWorld = this.screenToWorld(e.clientX, e.clientY);
    this.nodeDragOffset = {
      x: mouseWorld.x - comp.pos_x,
      y: mouseWorld.y - comp.pos_y
    };

    HistoryManager.pushState(`Move ${comp.name}`);
  },

  startConnecting(nodeId, side, e) {
    this.isConnecting = true;
    const comp = State.getComponentById(nodeId);
    const compW = comp.width || 160;
    const compH = comp.height || 80;

    let portX = comp.pos_x;
    let portY = comp.pos_y;

    if (side === 'top') { portX += compW / 2; }
    else if (side === 'right') { portX += compW; portY += compH / 2; }
    else if (side === 'bottom') { portX += compW / 2; portY += compH; }
    else if (side === 'left') { portY += compH / 2; }

    this.connectingSource = { id: nodeId, side, x: portX, y: portY };
  },

  handleMouseMove(e) {
    if (this.isPanning) {
      State.viewport.panX = e.clientX - this.panStart.x;
      State.viewport.panY = e.clientY - this.panStart.y;
      this.applyTransform();
    } else if (this.isDraggingNode && this.draggedNodeId) {
      const mouseWorld = this.screenToWorld(e.clientX, e.clientY);
      let newX = mouseWorld.x - this.nodeDragOffset.x;
      let newY = mouseWorld.y - this.nodeDragOffset.y;

      // Snap to Grid (20px) if enabled
      if (State.preferences.snap_to_grid) {
        const gridSize = State.preferences.grid_size || 20;
        newX = Math.round(newX / gridSize) * gridSize;
        newY = Math.round(newY / gridSize) * gridSize;
      }

      const comp = State.getComponentById(this.draggedNodeId);
      if (comp) {
        comp.pos_x = newX;
        comp.pos_y = newY;
        
        // Fast DOM update for smooth 60fps dragging
        const el = document.getElementById(`node-${comp.id}`);
        if (el) {
          el.style.left = `${newX}px`;
          el.style.top = `${newY}px`;
        }

        // Live reroute connected data flow arrows
        Connections.renderFlows();
      }
    } else if (this.isConnecting) {
      const mouseWorld = this.screenToWorld(e.clientX, e.clientY);
      Connections.updatePreviewLine(this.connectingSource.x, this.connectingSource.y, mouseWorld.x, mouseWorld.y);
    }
  },

  handleMouseUp(e) {
    if (this.isPanning) {
      this.isPanning = false;
      document.body.style.cursor = 'default';
    }

    if (this.isDraggingNode) {
      this.isDraggingNode = false;
      this.draggedNodeId = null;
      Designer.scheduleAutoSave();
      this.updateMinimap();
    }

    if (this.isConnecting) {
      this.isConnecting = false;
      Connections.hidePreviewLine();

      // Check if dropped on a target node
      const targetElement = document.elementFromPoint(e.clientX, e.clientY);
      const targetNodeEl = targetElement ? targetElement.closest('.dfd-node') : null;

      if (targetNodeEl) {
        const targetNodeId = parseInt(targetNodeEl.getAttribute('data-node-id'));
        if (targetNodeId && targetNodeId !== this.connectingSource.id) {
          Designer.createNewFlow(this.connectingSource.id, targetNodeId);
        }
      }
    }
  },

  zoomIn() {
    State.viewport.zoom = Math.min(State.viewport.maxZoom, State.viewport.zoom + 0.15);
    this.applyTransform();
  },

  zoomOut() {
    State.viewport.zoom = Math.max(State.viewport.minZoom, State.viewport.zoom - 0.15);
    this.applyTransform();
  },

  zoomFit() {
    const components = State.getCurrentComponents();
    if (components.length === 0) {
      State.viewport.zoom = 1.0;
      State.viewport.panX = 40;
      State.viewport.panY = 40;
      this.applyTransform();
      return;
    }

    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    components.forEach(c => {
      minX = Math.min(minX, c.pos_x);
      minY = Math.min(minY, c.pos_y);
      maxX = Math.max(maxX, c.pos_x + (c.width || 160));
      maxY = Math.max(maxY, c.pos_y + (c.height || 80));
    });

    const viewport = document.getElementById('canvas-viewport');
    const vw = viewport.clientWidth;
    const vh = viewport.clientHeight;

    const width = maxX - minX + 120;
    const height = maxY - minY + 120;

    const scaleX = vw / width;
    const scaleY = vh / height;
    const fitZoom = Math.min(1.2, Math.max(0.4, Math.min(scaleX, scaleY)));

    State.viewport.zoom = fitZoom;
    State.viewport.panX = (vw - width * fitZoom) / 2 - (minX - 60) * fitZoom;
    State.viewport.panY = (vh - height * fitZoom) / 2 - (minY - 60) * fitZoom;

    this.applyTransform();
  },

  undo() {
    HistoryManager.undo();
  },

  redo() {
    HistoryManager.redo();
  },

  autoLayout() {
    AutoLayout.apply();
  },

  // Minimap Real-time Synchronization
  updateMinimap() {
    const box = document.getElementById('minimap-box');
    if (!box) return;

    const components = State.getCurrentComponents();
    if (components.length === 0) return;

    let maxX = 1200, maxY = 800;
    components.forEach(c => {
      maxX = Math.max(maxX, c.pos_x + 300);
      maxY = Math.max(maxY, c.pos_y + 200);
    });

    const mmW = 180;
    const mmH = 98;

    const scaleX = mmW / maxX;
    const scaleY = mmH / maxY;

    const viewport = document.getElementById('canvas-viewport');
    if (!viewport) return;

    const vpW = viewport.clientWidth;
    const vpH = viewport.clientHeight;

    const boxX = Math.max(0, (-State.viewport.panX / State.viewport.zoom) * scaleX);
    const boxY = Math.max(0, (-State.viewport.panY / State.viewport.zoom) * scaleY);
    const boxW = Math.min(mmW, (vpW / State.viewport.zoom) * scaleX);
    const boxH = Math.min(mmH, (vpH / State.viewport.zoom) * scaleY);

    box.style.left = `${boxX}px`;
    box.style.top = `${boxY}px`;
    box.style.width = `${boxW}px`;
    box.style.height = `${boxH}px`;
  }
};
