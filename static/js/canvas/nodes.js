/**
 * DFD Architect — Canvas Node DOM Renderer & Interaction Manager
 */
const Nodes = {
  renderNodes() {
    const container = document.getElementById('canvas-nodes');
    if (!container) return;
    container.innerHTML = '';

    const components = State.getCurrentComponents();
    const notation = State.preferences.notation_style || 'gane_sarson';

    components.forEach(comp => {
      const isSelected = State.selectedNodeId === comp.id;
      const el = document.createElement('div');
      el.className = `dfd-node dfd-node-${comp.component_type} ${isSelected ? 'selected' : ''} notation-${notation}`;
      el.id = `node-${comp.id}`;
      el.setAttribute('data-node-id', comp.id);
      
      el.style.left = `${comp.pos_x}px`;
      el.style.top = `${comp.pos_y}px`;
      el.style.width = `${comp.width || 160}px`;
      el.style.height = `${comp.height || 80}px`;

      // Build Inner HTML based on Component Type
      if (comp.component_type === 'process') {
        el.innerHTML = `
          <div class="node-process-header">
            <span class="node-process-id">${comp.component_identifier || '1.0'}</span>
            <span class="node-process-type">Process</span>
          </div>
          <div class="node-process-body">
            <div class="node-process-name">${comp.name}</div>
          </div>
        `;
      } else if (comp.component_type === 'entity') {
        const meta = comp.metadata || {};
        el.innerHTML = `
          <div class="node-entity-id">${comp.component_identifier || 'E1'}</div>
          <div class="node-entity-name">${comp.name}</div>
          <span class="node-entity-badge">${meta.entity_type || 'External Actor'}</span>
        `;
      } else if (comp.component_type === 'datastore') {
        const meta = comp.metadata || {};
        el.innerHTML = `
          <div class="node-store-id-box">${comp.component_identifier || 'D1'}</div>
          <div class="node-store-body">
            <div class="node-store-name">${comp.name}</div>
            <div class="node-store-type">${meta.storage_type || 'Persistent Store'}</div>
          </div>
        `;
      }

      // Append 4 Interactive Connection Ports (Top, Right, Bottom, Left)
      ['top', 'right', 'bottom', 'left'].forEach(side => {
        const port = document.createElement('div');
        port.className = `node-port port-${side}`;
        port.setAttribute('data-port-side', side);
        port.setAttribute('data-node-id', comp.id);
        
        // Port mouse down starts connection drag
        port.onmousedown = (e) => {
          e.stopPropagation();
          CanvasEngine.startConnecting(comp.id, side, e);
        };
        el.appendChild(port);
      });

      // Node selection & Drag listeners
      el.onmousedown = (e) => {
        if (e.target.classList.contains('node-port')) return;
        e.stopPropagation();
        CanvasEngine.startDraggingNode(comp.id, e);
      };

      // Double click to quick edit name
      el.ondblclick = (e) => {
        e.stopPropagation();
        Designer.selectNode(comp.id);
        const nameInput = document.getElementById('inspector-comp-name');
        if (nameInput) nameInput.focus();
      };

      container.appendChild(el);
    });
  }
};
