/**
 * DFD Architect — Dashboard View Controller
 */
const DashboardView = {
  chartInstance: null,

  async init() {
    await this.loadStats();
    await this.loadRecentProjects();
  },

  async loadStats() {
    try {
      const data = await API.get('/api/analytics');
      const stats = data.stats || {};

      document.getElementById('stat-total-projects').textContent = stats.total_projects || 0;
      document.getElementById('stat-total-levels').textContent = stats.total_levels || 0;
      document.getElementById('stat-total-processes').textContent = stats.processes_count || 0;
      document.getElementById('stat-total-datastores').textContent = stats.datastores_count || 0;
      document.getElementById('stat-total-entities').textContent = stats.entities_count || 0;
      document.getElementById('stat-total-flows').textContent = stats.total_flows || 0;

      const sidebarBadge = document.getElementById('sidebar-projects-count');
      if (sidebarBadge) sidebarBadge.textContent = stats.total_projects || 0;

      this.renderBreakdownChart(data.component_distribution || []);
    } catch (err) {
      console.error('Failed to load dashboard stats:', err);
    }
  },

  async loadRecentProjects() {
    try {
      const res = await API.get('/api/projects', { sort: 'updated_at' });
      const tbody = document.getElementById('dashboard-recent-projects-tbody');
      if (!tbody) return;

      const projects = res.projects || [];
      if (projects.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="5" style="text-align: center; padding: 2rem; color: var(--text-muted);">
              No projects found. Click <strong>+ Create New DFD</strong> or explore the Template Library.
            </td>
          </tr>
        `;
        return;
      }

      tbody.innerHTML = projects.slice(0, 5).map(p => {
        const counts = p.component_counts || {};
        const compSummary = `${counts.processes || 0} Procs, ${counts.datastores || 0} Stores, ${counts.entities || 0} Entities, ${counts.flows || 0} Flows`;
        const updatedDate = p.updated_at ? new Date(p.updated_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) : '-';

        return `
          <tr>
            <td>
              <div class="project-name-cell" onclick="App.openProject(${p.id})">
                <i class="fa-solid fa-diagram-project" style="color: var(--primary-600); margin-right: 6px;"></i>
                ${p.name}
              </div>
              <div style="font-size: 0.75rem; color: var(--text-muted);">${p.system_name || 'System'}</div>
            </td>
            <td><span class="badge badge-primary">${p.dfd_level}</span></td>
            <td><span style="font-size: 0.78rem; color: var(--text-secondary);">${compSummary}</span></td>
            <td><span style="font-size: 0.78rem; color: var(--text-muted);">${updatedDate}</span></td>
            <td style="text-align: right;">
              <button class="btn btn-primary btn-sm" onclick="App.openProject(${p.id})" title="Open in Designer">
                <i class="fa-solid fa-arrow-up-right-from-square"></i> Open
              </button>
              <button class="btn btn-secondary btn-sm" onclick="ProjectsView.duplicateProject(${p.id})" title="Duplicate">
                <i class="fa-solid fa-copy"></i>
              </button>
              ${!p.is_demo ? `
                <button class="btn btn-secondary btn-sm" onclick="ProjectsView.confirmDeleteProject(${p.id}, '${p.name}')" title="Delete" style="color: var(--accent-rose);">
                  <i class="fa-solid fa-trash"></i>
                </button>
              ` : ''}
            </td>
          </tr>
        `;
      }).join('');
    } catch (err) {
      console.error('Failed to load recent projects:', err);
    }
  },

  renderBreakdownChart(distribution) {
    const canvas = document.getElementById('dashboardComponentChart');
    if (!canvas) return;

    if (this.chartInstance) {
      this.chartInstance.destroy();
    }

    const labels = distribution.map(d => d.type);
    const data = distribution.map(d => d.count);
    const colors = distribution.map(d => d.color);

    const total = data.reduce((a, b) => a + b, 0);
    if (total === 0) {
      // Dummy visual placeholder if brand new
      data.push(1);
      colors.push('#E2E8F0');
      labels.push('No Components Yet');
    }

    const isDark = document.body.classList.contains('dark-mode');

    this.chartInstance = new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: colors,
          borderWidth: 2,
          borderColor: isDark ? '#1E293B' : '#FFFFFF'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 12,
              font: { size: 11, family: 'Inter' },
              color: isDark ? '#94A3B8' : '#475569'
            }
          }
        }
      }
    });
  }
};
