/**
 * DFD Architect — DFD Designer View & Properties Inspector Controller
 */
const Designer = {
  saveTimer: null,
  draggedType: null,

  init() {
    CanvasEngine.init();
    this.populateLevelSelector();
    this.renderInspector();
  },

  setMode(mode) {
    State.activeTool = mode;
    document.querySelectorAll('.canvas-floating-toolbar .toolbar-btn').forEach(btn => btn.classList.remove('active'));
    if (mode === 'select') {
      document.getElementById('tool-select-btn')?.classList.add('active');
    } else if (mode === 'connect') {
      document.getElementById('tool-connect-btn')?.classList.add('active');
      App.showToast('Connection Mode', 'Drag from any node port to another node to create a Data Flow.', 'info');
    }
  },

  // -------------------------------------------------------------
  // Drag & Drop from Left Component Palette
  // -------------------------------------------------------------
  handlePaletteDragStart(e, compType) {
    this.draggedType = compType;
    e.dataTransfer.setData('text/plain', compType);
    e.dataTransfer.effectAllowed = 'copy';
  },

  handleCanvasDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
  },

  async handleCanvasDrop(e) {
    e.preventDefault();
    const compType = e.dataTransfer.getData('text/plain') || this.draggedType;
    if (!compType || !State.project) return;

    const mouseWorld = CanvasEngine.screenToWorld(e.clientX, e.clientY);
    let posX = mouseWorld.x;
    let posY = mouseWorld.y;

    if (State.preferences.snap_to_grid) {
      const gridSize = State.preferences.grid_size || 20;
      posX = Math.round(posX / gridSize) * gridSize;
      posY = Math.round(posY / gridSize) * gridSize;
    }

    HistoryManager.pushState(`Add ${compType}`);

    try {
      const res = await API.post(`/api/projects/${State.project.id}/components`, {
        component_type: compType,
        level_id: State.activeLevelId,
        pos_x: posX,
        pos_y: posY
      });

      if (res.success) {
        State.components.push(res.component);
        CanvasEngine.render();
        this.selectNode(res.component.id);
        this.scheduleAutoSave();
        App.showToast('Component Added', `Added new ${compType} to diagram.`, 'success');
      }
    } catch (err) {
      App.showToast('Error', err.message || 'Failed to add component.', 'error');
    }
  },

  // -------------------------------------------------------------
  // Node & Flow Selection Management
  // -------------------------------------------------------------
  selectNode(nodeId) {
    State.selectedNodeId = nodeId;
    State.selectedFlowId = null;

    document.querySelectorAll('.dfd-node').forEach(el => el.classList.remove('selected'));
    document.querySelectorAll('.dfd-flow-path').forEach(el => el.classList.remove('selected'));

    const el = document.getElementById(`node-${nodeId}`);
    if (el) el.classList.add('selected');

    this.renderInspector();
  },

  selectFlow(flowId) {
    State.selectedFlowId = flowId;
    State.selectedNodeId = null;

    document.querySelectorAll('.dfd-node').forEach(el => el.classList.remove('selected'));
    Connections.renderFlows();

    this.renderInspector();
  },

  deselectAll() {
    State.selectedNodeId = null;
    State.selectedFlowId = null;
    document.querySelectorAll('.dfd-node').forEach(el => el.classList.remove('selected'));
    Connections.renderFlows();
    this.renderInspector();
  },

  // -------------------------------------------------------------
  // Data Flow Creation
  // -------------------------------------------------------------
  async createNewFlow(sourceId, destId) {
    if (!State.project) return;

    const src = State.getComponentById(sourceId);
    const dst = State.getComponentById(destId);
    if (!src || !dst) return;

    // Check for existing identical flow
    const existing = State.getCurrentFlows().find(f => f.source_id === sourceId && f.destination_id === destId);
    if (existing) {
      App.showToast('Flow Exists', `Data flow between '${src.name}' and '${dst.name}' already exists.`, 'info');
      this.selectFlow(existing.id);
      return;
    }

    HistoryManager.pushState('Add Data Flow');

    try {
      const defaultName = `${src.name.split(' ')[0]} Data`;
      const res = await API.post(`/api/projects/${State.project.id}/flows`, {
        source_id: sourceId,
        destination_id: destId,
        level_id: State.activeLevelId,
        flow_name: defaultName,
        data_type: 'JSON / Structured Payload'
      });

      if (res.success) {
        State.dataFlows.push(res.flow);
        CanvasEngine.render();
        this.selectFlow(res.flow.id);
        this.scheduleAutoSave();
        App.showToast('Data Flow Connected', `Connected '${src.name}' → '${dst.name}'`, 'success');
      }
    } catch (err) {
      App.showToast('Error', err.message || 'Failed to create data flow.', 'error');
    }
  },

  // -------------------------------------------------------------
  // Properties Inspector Panel Rendering & Real-time Two-Way Binding
  // -------------------------------------------------------------
  renderInspector() {
    const body = document.getElementById('inspector-body');
    const title = document.getElementById('inspector-title');
    if (!body || !title) return;

    if (State.selectedNodeId) {
      const comp = State.getComponentById(State.selectedNodeId);
      if (!comp) { this.renderEmptyInspector(); return; }

      title.innerHTML = `<i class="fa-solid fa-sliders" style="color: var(--primary-600); margin-right: 6px;"></i> ${comp.component_type.toUpperCase()} PROPERTIES`;
      const meta = comp.metadata || {};

      let typeSpecificFields = '';
      if (comp.component_type === 'process') {
        typeSpecificFields = `
          <div class="form-group">
            <label class="form-label">Process ID / Number</label>
            <input type="text" id="inspector-comp-ident" class="form-input" value="${comp.component_identifier || '1.0'}" oninput="Designer.updateActiveComponent('component_identifier', this.value)">
          </div>
          <div class="form-group">
            <label class="form-label">Decomposition Actions</label>
            <button class="btn btn-secondary btn-sm" style="width: 100%; justify-content: center;" onclick="Designer.openDecomposeModal('${comp.component_identifier}')">
              <i class="fa-solid fa-sitemap" style="color: var(--primary-600);"></i> Decompose into Level 2
            </button>
          </div>
        `;
      } else if (comp.component_type === 'entity') {
        typeSpecificFields = `
          <div class="form-group">
            <label class="form-label">Entity Identifier</label>
            <input type="text" id="inspector-comp-ident" class="form-input" value="${comp.component_identifier || 'E1'}" oninput="Designer.updateActiveComponent('component_identifier', this.value)">
          </div>
          <div class="form-group">
            <label class="form-label">Entity Category / Type</label>
            <select class="form-select" onchange="Designer.updateActiveComponentMeta('entity_type', this.value)">
              <option value="End User" ${meta.entity_type === 'End User' ? 'selected' : ''}>End User / Customer</option>
              <option value="Third-Party System" ${meta.entity_type === 'Third-Party System' ? 'selected' : ''}>Third-Party System / API</option>
              <option value="Internal Staff" ${meta.entity_type === 'Internal Staff' ? 'selected' : ''}>Internal Staff / Admin</option>
              <option value="External Service" ${meta.entity_type === 'External Service' ? 'selected' : ''}>External Service Provider</option>
            </select>
          </div>
        `;
      } else if (comp.component_type === 'datastore') {
        typeSpecificFields = `
          <div class="form-group">
            <label class="form-label">Store Identifier</label>
            <input type="text" id="inspector-comp-ident" class="form-input" value="${comp.component_identifier || 'D1'}" oninput="Designer.updateActiveComponent('component_identifier', this.value)">
          </div>
          <div class="form-group">
            <label class="form-label">Storage Technology</label>
            <select class="form-select" onchange="Designer.updateActiveComponentMeta('storage_type', this.value)">
              <option value="PostgreSQL" ${meta.storage_type === 'PostgreSQL' ? 'selected' : ''}>Relational DB (PostgreSQL / MySQL)</option>
              <option value="NoSQL Document Store" ${meta.storage_type === 'NoSQL Document Store' ? 'selected' : ''}>NoSQL Document Store (MongoDB)</option>
              <option value="In-Memory Cache (Redis)" ${meta.storage_type === 'In-Memory Cache (Redis)' ? 'selected' : ''}>In-Memory Cache (Redis)</option>
              <option value="File System / Blob Storage" ${meta.storage_type === 'File System / Blob Storage' ? 'selected' : ''}>File System / S3 Bucket</option>
              <option value="Immutable Ledger DB" ${meta.storage_type === 'Immutable Ledger DB' ? 'selected' : ''}>Immutable Ledger / Audit Log</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Schema Attributes / Fields</label>
            <input type="text" class="form-input" placeholder="id, created_at, payload..." value="${meta.schema_fields || ''}" oninput="Designer.updateActiveComponentMeta('schema_fields', this.value)">
          </div>
        `;
      }

      body.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 0.85rem;">
          <div class="form-group">
            <label class="form-label">Component Name *</label>
            <input type="text" id="inspector-comp-name" class="form-input" value="${comp.name}" oninput="Designer.updateActiveComponent('name', this.value)">
          </div>

          ${typeSpecificFields}

          <div class="form-group">
            <label class="form-label">Description / Purpose</label>
            <textarea class="form-textarea" rows="3" placeholder="Describe functional behavior..." oninput="Designer.updateActiveComponent('description', this.value)">${comp.description || ''}</textarea>
          </div>

          <div style="padding-top: 1rem; border-top: 1px solid var(--border-subtle); display: flex; gap: 0.5rem;">
            <button class="btn btn-danger btn-sm" style="width: 100%;" onclick="Designer.deleteActiveComponent()">
              <i class="fa-solid fa-trash"></i> Delete Node
            </button>
          </div>
        </div>
      `;
    } else if (State.selectedFlowId) {
      const flow = State.getFlowById(State.selectedFlowId);
      if (!flow) { this.renderEmptyInspector(); return; }

      const src = State.getComponentById(flow.source_id);
      const dst = State.getComponentById(flow.destination_id);

      title.innerHTML = `<i class="fa-solid fa-arrow-right-arrow-left" style="color: var(--accent-purple); margin-right: 6px;"></i> DATA FLOW`;

      body.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 0.85rem;">
          <div class="form-group">
            <label class="form-label">Flow Identifier</label>
            <input type="text" class="form-input" value="${flow.flow_identifier || 'F1'}" oninput="Designer.updateActiveFlow('flow_identifier', this.value)">
          </div>

          <div class="form-group">
            <label class="form-label">Data Item / Label *</label>
            <input type="text" class="form-input" value="${flow.flow_name}" oninput="Designer.updateActiveFlow('flow_name', this.value)">
          </div>

          <div class="card" style="padding: 0.75rem; background: var(--bg-subtle);">
            <div style="font-size: 0.75rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Origin Source</div>
            <div style="font-size: 0.85rem; font-weight: 600; color: var(--text-primary); margin-top: 0.15rem;">${src ? `${src.component_identifier} ${src.name}` : 'Unknown'}</div>
            
            <div style="font-size: 0.75rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; margin-top: 0.6rem;">Target Destination</div>
            <div style="font-size: 0.85rem; font-weight: 600; color: var(--text-primary); margin-top: 0.15rem;">${dst ? `${dst.component_identifier} ${dst.name}` : 'Unknown'}</div>
          </div>

          <div class="form-group">
            <label class="form-label">Data Payload Format</label>
            <input type="text" class="form-input" value="${flow.data_type || 'JSON / Structured Payload'}" oninput="Designer.updateActiveFlow('data_type', this.value)">
          </div>

          <div class="form-group">
            <label class="form-label">Description / Data Dictionary</label>
            <textarea class="form-textarea" rows="3" placeholder="Specify data attributes transferred..." oninput="Designer.updateActiveFlow('description', this.value)">${flow.description || ''}</textarea>
          </div>

          <div class="form-group">
            <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.82rem; font-weight: 600; cursor: pointer;">
              <input type="checkbox" ${flow.is_bidirectional ? 'checked' : ''} onchange="Designer.updateActiveFlow('is_bidirectional', this.checked)">
              <span>Bidirectional Data Flow (⇄)</span>
            </label>
          </div>

          <div style="padding-top: 1rem; border-top: 1px solid var(--border-subtle);">
            <button class="btn btn-danger btn-sm" style="width: 100%;" onclick="Designer.deleteActiveFlow()">
              <i class="fa-solid fa-trash"></i> Delete Flow
            </button>
          </div>
        </div>
      `;
    } else {
      this.renderEmptyInspector();
    }
  },

  renderEmptyInspector() {
    const title = document.getElementById('inspector-title');
    const body = document.getElementById('inspector-body');
    if (!body || !title) return;

    title.textContent = 'Properties Inspector';
    body.innerHTML = `
      <div class="inspector-empty">
        <i class="fa-solid fa-arrow-pointer"></i>
        <p>Click on any Process, Entity, Data Store, or Data Flow arrow to view and configure its properties.</p>
      </div>
    `;
  },

  // -------------------------------------------------------------
  // Live Property Updating
  // -------------------------------------------------------------
  updateActiveComponent(field, val) {
    if (!State.selectedNodeId) return;
    const comp = State.getComponentById(State.selectedNodeId);
    if (!comp) return;

    comp[field] = val;
    Nodes.renderNodes();
    this.scheduleAutoSave();
  },

  updateActiveComponentMeta(key, val) {
    if (!State.selectedNodeId) return;
    const comp = State.getComponentById(State.selectedNodeId);
    if (!comp) return;

    if (!comp.metadata) comp.metadata = {};
    comp.metadata[key] = val;
    Nodes.renderNodes();
    this.scheduleAutoSave();
  },

  updateActiveFlow(field, val) {
    if (!State.selectedFlowId) return;
    const flow = State.getFlowById(State.selectedFlowId);
    if (!flow) return;

    flow[field] = val;
    Connections.renderFlows();
    this.scheduleAutoSave();
  },

  // -------------------------------------------------------------
  // Deletion Management
  // -------------------------------------------------------------
  async deleteActiveComponent() {
    if (!State.selectedNodeId || !State.project) return;
    const comp = State.getComponentById(State.selectedNodeId);
    if (!comp) return;

    HistoryManager.pushState(`Delete ${comp.name}`);

    try {
      const res = await API.delete(`/api/projects/${State.project.id}/components/${comp.id}`);
      if (res.success) {
        State.components = State.components.filter(c => c.id !== comp.id);
        State.dataFlows = State.dataFlows.filter(f => f.source_id !== comp.id && f.destination_id !== comp.id);
        State.selectedNodeId = null;
        CanvasEngine.render();
        this.renderInspector();
        this.scheduleAutoSave();
        App.showToast('Deleted', `Component '${comp.name}' removed.`, 'info');
      }
    } catch (err) {
      App.showToast('Error', err.message || 'Failed to delete component.', 'error');
    }
  },

  async deleteActiveFlow() {
    if (!State.selectedFlowId || !State.project) return;
    const flow = State.getFlowById(State.selectedFlowId);
    if (!flow) return;

    HistoryManager.pushState('Delete Data Flow');

    try {
      const res = await API.delete(`/api/projects/${State.project.id}/flows/${flow.id}`);
      if (res.success) {
        State.dataFlows = State.dataFlows.filter(f => f.id !== flow.id);
        State.selectedFlowId = null;
        CanvasEngine.render();
        this.renderInspector();
        this.scheduleAutoSave();
        App.showToast('Deleted', 'Data flow removed.', 'info');
      }
    } catch (err) {
      App.showToast('Error', err.message || 'Failed to delete flow.', 'error');
    }
  },

  // -------------------------------------------------------------
  // Level Switching & Decomposition
  // -------------------------------------------------------------
  populateLevelSelector() {
    const sel = document.getElementById('canvas-level-selector');
    if (!sel || !State.levels) return;

    sel.innerHTML = State.levels.map(lvl => `
      <option value="${lvl.id}" ${lvl.id === State.activeLevelId ? 'selected' : ''}>
        ${lvl.level_name} ${lvl.parent_process_id ? `(Decomposed ${lvl.parent_process_id})` : ''}
      </option>
    `).join('');
  },

  switchLevel(levelId) {
    State.setActiveLevel(parseInt(levelId));
    CanvasEngine.render();
    CanvasEngine.zoomFit();
    this.renderInspector();
  },

  openCreateLevelModal(parentProcessId = '') {
    const input = document.getElementById('new-parent-proc');
    const nameInput = document.getElementById('new-level-name');
    if (input) input.value = parentProcessId;
    if (nameInput) {
      const nextNum = State.levels.length;
      nameInput.value = parentProcessId ? `Level 2 – Process ${parentProcessId} Breakdown` : `Level ${nextNum}`;
    }
    App.openModal('modal-create-level');
  },

  openDecomposeModal(processIdentifier) {
    this.openCreateLevelModal(processIdentifier);
  },

  async handleCreateLevel(e) {
    e.preventDefault();
    const name = document.getElementById('new-level-name').value.trim();
    const parentProc = document.getElementById('new-parent-proc').value.trim();
    if (!name || !State.project) return;

    try {
      const res = await API.post(`/api/projects/${State.project.id}/levels`, {
        level_name: name,
        parent_process_id: parentProc || null,
        level_number: State.levels.length
      });

      if (res.success) {
        App.closeModal('modal-create-level');
        App.showToast('Level Created', `Added ${name} to hierarchy.`, 'success');
        
        // Refresh project to load new level and scaffolded sub-processes
        await App.openProject(State.project.id);
        this.switchLevel(res.level.id);
      }
    } catch (err) {
      App.showToast('Error', err.message || 'Failed to create level.', 'error');
    }
  },

  // -------------------------------------------------------------
  // Auto-Save Management
  // -------------------------------------------------------------
  scheduleAutoSave() {
    this.setSaveStatus('unsaved');
    if (!State.preferences.auto_save) return;

    clearTimeout(this.saveTimer);
    this.saveTimer = setTimeout(() => {
      this.persistToServer();
    }, 1200); // 1.2s debounce
  },

  manualSave() {
    clearTimeout(this.saveTimer);
    this.persistToServer();
  },

  async persistToServer() {
    if (!State.project) return;
    this.setSaveStatus('saving');

    const positions = {};
    State.components.forEach(c => {
      positions[c.id] = { x: c.pos_x, y: c.pos_y };
    });

    try {
      await API.post(`/api/projects/${State.project.id}/batch-sync`, {
        positions: positions
      });
      this.setSaveStatus('saved');
    } catch (err) {
      console.error('Auto-save error:', err);
      this.setSaveStatus('unsaved');
    }
  },

  setSaveStatus(status) {
    const pill = document.getElementById('save-status-pill');
    const text = document.getElementById('save-status-text');
    if (!pill || !text) return;

    pill.style.display = 'flex';
    pill.className = `save-status-pill ${status}`;

    if (status === 'saving') {
      text.textContent = 'Saving...';
      pill.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>Saving...</span>';
    } else if (status === 'saved') {
      text.textContent = 'Saved';
      pill.innerHTML = '<i class="fa-solid fa-check"></i> <span>Saved</span>';
    } else {
      text.textContent = 'Unsaved changes';
      pill.innerHTML = '<i class="fa-solid fa-circle-dot"></i> <span>Unsaved</span>';
    }
  }
};
