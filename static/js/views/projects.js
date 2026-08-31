/**
 * DFD Architect — My Projects View Controller
 */
const ProjectsView = {
  allProjects: [],

  async init() {
    await this.loadProjects();
  },

  async loadProjects() {
    try {
      const res = await API.get('/api/projects');
      this.allProjects = res.projects || [];
      this.renderProjects(this.allProjects);
    } catch (err) {
      console.error('Failed to load projects:', err);
      App.showToast('Error', 'Failed to retrieve projects list.', 'error');
    }
  },

  filterProjects() {
    const searchVal = (document.getElementById('projects-search-input')?.value || '').toLowerCase().trim();
    const levelVal = document.getElementById('projects-level-filter')?.value || 'all';
    const sortVal = document.getElementById('projects-sort-select')?.value || 'updated_at';

    let filtered = this.allProjects.filter(p => {
      const matchesSearch = !searchVal || 
        p.name.toLowerCase().includes(searchVal) || 
        (p.description || '').toLowerCase().includes(searchVal) ||
        (p.system_name || '').toLowerCase().includes(searchVal);
      
      const matchesLevel = levelVal === 'all' || (p.dfd_level || '').includes(levelVal);
      return matchesSearch && matchesLevel;
    });

    if (sortVal === 'name') {
      filtered.sort((a, b) => a.name.localeCompare(b.name));
    } else if (sortVal === 'created_at') {
      filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    } else {
      filtered.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
    }

    this.renderProjects(filtered);
  },

  renderProjects(projects) {
    const container = document.getElementById('projects-list-container');
    if (!container) return;

    if (projects.length === 0) {
      container.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 4rem 2rem; background: var(--bg-surface); border-radius: var(--radius-xl); border: 1px dashed var(--border-default);">
          <i class="fa-solid fa-folder-open" style="font-size: 3rem; color: var(--text-muted); margin-bottom: 1rem; opacity: 0.5;"></i>
          <h3 style="font-family: var(--font-display); font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem;">No Projects Found</h3>
          <p style="font-size: 0.85rem; color: var(--text-muted); max-width: 420px; margin: 0 auto 1.5rem;">
            Create a new Data Flow Diagram project from scratch or clone one of the pre-built industry templates.
          </p>
          <button class="btn btn-primary" onclick="App.openCreateProjectModal()">
            <i class="fa-solid fa-plus"></i> Create New DFD
          </button>
        </div>
      `;
      return;
    }

    container.innerHTML = projects.map(p => {
      const counts = p.component_counts || {};
      const updatedDate = p.updated_at ? new Date(p.updated_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) : 'Recently';

      return `
        <div class="project-card" onclick="App.openProject(${p.id})">
          <div>
            <div class="project-card-header">
              <span class="badge ${p.is_demo ? 'badge-warning' : 'badge-primary'}">${p.is_demo ? 'Demo Project' : p.dfd_level}</span>
              <span style="font-size: 0.75rem; color: var(--text-muted);">${updatedDate}</span>
            </div>
            
            <h3 class="project-card-title" style="margin-top: 0.6rem;">${p.name}</h3>
            <div style="font-size: 0.78rem; font-weight: 600; color: var(--text-muted); margin-top: 0.15rem;">${p.system_name || 'System'}</div>
            <p class="project-card-desc">${p.description || 'System Data Flow Diagram architecture specification.'}</p>
          </div>

          <div>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.75rem;">
              <span class="badge badge-neutral" style="font-size: 0.7rem;"><i class="fa-solid fa-gears" style="color: #2563EB;"></i> ${counts.processes || 0} Processes</span>
              <span class="badge badge-neutral" style="font-size: 0.7rem;"><i class="fa-solid fa-database" style="color: #059669;"></i> ${counts.datastores || 0} Stores</span>
              <span class="badge badge-neutral" style="font-size: 0.7rem;"><i class="fa-solid fa-users" style="color: #D97706;"></i> ${counts.entities || 0} Entities</span>
              <span class="badge badge-neutral" style="font-size: 0.7rem;"><i class="fa-solid fa-arrow-right-arrow-left" style="color: #7C3AED;"></i> ${counts.flows || 0} Flows</span>
            </div>

            <div class="project-card-footer" onclick="event.stopPropagation()">
              <button class="btn btn-primary btn-sm" onclick="App.openProject(${p.id})">
                <i class="fa-solid fa-pen-ruler"></i> Open Designer
              </button>
              
              <div style="display: flex; gap: 0.35rem;">
                <button class="btn btn-secondary btn-sm" onclick="ProjectsView.duplicateProject(${p.id})" title="Duplicate Project">
                  <i class="fa-solid fa-copy"></i>
                </button>
                <button class="btn btn-secondary btn-sm" onclick="App.triggerExportForProject(${p.id})" title="Export">
                  <i class="fa-solid fa-file-export"></i>
                </button>
                ${!p.is_demo ? `
                  <button class="btn btn-secondary btn-sm" onclick="ProjectsView.confirmDeleteProject(${p.id}, '${p.name.replace(/'/g, "\\'")}')" title="Delete Project" style="color: var(--accent-rose);">
                    <i class="fa-solid fa-trash"></i>
                  </button>
                ` : ''}
              </div>
            </div>
          </div>
        </div>
      `;
    }).join('');
  },

  async handleCreateProject(e) {
    e.preventDefault();
    const name = document.getElementById('new-proj-name').value.trim();
    const systemName = document.getElementById('new-system-name').value.trim();
    const dfdLevel = document.getElementById('new-dfd-level').value;
    const author = document.getElementById('new-author').value.trim();
    const desc = document.getElementById('new-proj-desc').value.trim();

    if (!name) return;

    try {
      const res = await API.post('/api/projects', {
        name: name,
        system_name: systemName || name,
        dfd_level: dfdLevel,
        author: author,
        description: desc
      });

      if (res.success) {
        App.closeModal('modal-create-project');
        App.showToast('Project Created', `Project '${name}' is ready in workspace.`, 'success');
        document.getElementById('create-project-form').reset();
        await this.loadProjects();
        App.openProject(res.project.id);
      }
    } catch (err) {
      App.showToast('Error', err.message || 'Failed to create project.', 'error');
    }
  },

  async duplicateProject(projectId) {
    try {
      const res = await API.post(`/api/projects/${projectId}/duplicate`);
      if (res.success) {
        App.showToast('Project Duplicated', 'Cloned project created successfully.', 'success');
        await this.loadProjects();
        await DashboardView.init();
      }
    } catch (err) {
      App.showToast('Error', err.message || 'Failed to duplicate project.', 'error');
    }
  },

  confirmDeleteProject(projectId, projectName) {
    App.openConfirmModal(
      'Delete Project',
      `Are you sure you want to permanently delete <strong>'${projectName}'</strong> and all associated levels, diagrams, and components? This action cannot be undone.`,
      async () => {
        try {
          const res = await API.delete(`/api/projects/${projectId}`);
          if (res.success) {
            App.showToast('Deleted', `Project '${projectName}' removed.`, 'info');
            await this.loadProjects();
            await DashboardView.init();
            
            // If active project was deleted, switch to first available
            if (State.project && State.project.id === projectId) {
              const remaining = this.allProjects.filter(p => p.id !== projectId);
              if (remaining.length > 0) {
                App.openProject(remaining[0].id);
              }
            }
          }
        } catch (err) {
          App.showToast('Error', err.message || 'Failed to delete project.', 'error');
        }
      }
    );
  }
};
