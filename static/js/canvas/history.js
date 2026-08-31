/**
 * DFD Architect — Undo / Redo Command History Stack
 */
const HistoryManager = {
  undoStack: [],
  redoStack: [],
  maxStackSize: 40,

  pushState(snapshotDescription = 'Action') {
    const snapshot = {
      description: snapshotDescription,
      components: JSON.parse(JSON.stringify(State.components)),
      dataFlows: JSON.parse(JSON.stringify(State.dataFlows))
    };

    this.undoStack.push(snapshot);
    if (this.undoStack.length > this.maxStackSize) {
      this.undoStack.shift();
    }
    this.redoStack = []; // clear redo on new action
  },

  undo() {
    if (this.undoStack.length === 0) {
      App.showToast('Undo', 'No more actions to undo.', 'info');
      return;
    }

    // Save current state to redo stack
    const currentSnapshot = {
      description: 'Current State',
      components: JSON.parse(JSON.stringify(State.components)),
      dataFlows: JSON.parse(JSON.stringify(State.dataFlows))
    };
    this.redoStack.push(currentSnapshot);

    const prevSnapshot = this.undoStack.pop();
    State.components = prevSnapshot.components;
    State.dataFlows = prevSnapshot.dataFlows;

    CanvasEngine.render();
    Designer.scheduleAutoSave();
    App.showToast('Undo', `Reverted ${prevSnapshot.description}`, 'info');
  },

  redo() {
    if (this.redoStack.length === 0) {
      App.showToast('Redo', 'No actions to redo.', 'info');
      return;
    }

    const currentSnapshot = {
      description: 'Current State',
      components: JSON.parse(JSON.stringify(State.components)),
      dataFlows: JSON.parse(JSON.stringify(State.dataFlows))
    };
    this.undoStack.push(currentSnapshot);

    const nextSnapshot = this.redoStack.pop();
    State.components = nextSnapshot.components;
    State.dataFlows = nextSnapshot.dataFlows;

    CanvasEngine.render();
    Designer.scheduleAutoSave();
    App.showToast('Redo', `Applied ${nextSnapshot.description}`, 'info');
  }
};
