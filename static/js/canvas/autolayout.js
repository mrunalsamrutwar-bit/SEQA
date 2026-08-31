/**
 * DFD Architect — Hierarchical Auto-Layout Algorithm
 */
const AutoLayout = {
  apply() {
    const components = State.getCurrentComponents();
    if (!components || components.length === 0) return;

    HistoryManager.pushState('Auto-Layout');

    const entities = components.filter(c => c.component_type === 'entity');
    const processes = components.filter(c => c.component_type === 'process');
    const datastores = components.filter(c => c.component_type === 'datastore');

    const startX = 80;
    const startY = 80;
    const colSpacing = 300;
    const rowSpacing = 160;

    // Arrange External Entities (Left column or top)
    entities.forEach((entity, index) => {
      entity.pos_x = startX;
      entity.pos_y = startY + index * rowSpacing;
    });

    // Arrange Processes in center column(s)
    const procColX = startX + colSpacing;
    processes.forEach((proc, index) => {
      // Split into 2 columns if more than 3 processes
      const colOffset = Math.floor(index / 3) * 260;
      const rowOffset = (index % 3) * rowSpacing;
      proc.pos_x = procColX + colOffset;
      proc.pos_y = startY + rowOffset;
    });

    // Arrange Data Stores on right or bottom
    const storeColX = procColX + (processes.length > 3 ? 520 : 280);
    datastores.forEach((store, index) => {
      store.pos_x = storeColX;
      store.pos_y = startY + index * rowSpacing;
    });

    CanvasEngine.render();
    Designer.scheduleAutoSave();
    CanvasEngine.zoomFit();
    App.showToast('Auto-Layout', 'Diagram nodes arranged in hierarchical layers.', 'success');
  }
};
