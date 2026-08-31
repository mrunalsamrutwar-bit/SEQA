/**
 * DFD Architect — Templates Gallery Controller
 */
const TemplatesView = {
  templates: [],

  async init() {
    await this.loadTemplates();
  },

  async loadTemplates() {
    try {
      const res = await API.get('/api/templates');
      this.templates = res.templates || [];
      this.renderTemplates(this.templates);
    } catch (err) {
      console.error('Failed to load templates:', err);
    }
  },

  renderTemplates(templates) {
    const container = document.getElementById('templates-container');
    if (!container) return;

    container.innerHTML = templates.map(t => {
      // Calculate components across levels
      let procCount = 0, storeCount = 0, entityCount = 0, flowCount = 0;
      (t.levels || []).forEach(lvl => {
        (lvl.components || []).forEach(c => {
          if (c.type === 'process') procCount++;
          else if (c.type === 'datastore') storeCount++;
          else if (c.type === 'entity') entityCount++;
        });
        flowCount += (lvl.flows || []).length;
      });

      return `
        <div class="template-card">
          <div class="template-card-header">
            <span class="template-badge">${t.category}</span>
            <h3 class="template-title">${t.name}</h3>
          </div>
          
          <div class="template-card-body">
            <p class="template-desc">${t.description}</p>

            <div>
              <div class="template-metrics" style="margin-bottom: 1rem;">
                <span><i class="fa-solid fa-gears" style="color: #2563EB;"></i> ${procCount} Processes</span>
                <span><i class="fa-solid fa-database" style="color: #059669;"></i> ${storeCount} Stores</span>
                <span><i class="fa-solid fa-users" style="color: #D97706;"></i> ${entityCount} Entities</span>
                <span><i class="fa-solid fa-arrow-right-arrow-left" style="color: #7C3AED;"></i> ${flowCount} Flows</span>
              </div>

              <button class="btn btn-primary" style="width: 100%;" onclick="TemplatesView.useTemplate('${t.id}', '${t.name.replace(/'/g, "\\'")}')">
                <i class="fa-solid fa-wand-magic-sparkles"></i> Use This Template
              </button>
            </div>
          </div>
        </div>
      `;
    }).join('');
  },

  async useTemplate(templateId, templateName) {
    try {
      const res = await API.post(`/api/templates/${templateId}/instantiate`, {
        name: `My ${templateName}`
      });

      if (res.success) {
        App.showToast('Template Instantiated', `Created project from '${templateName}'.`, 'success');
        await ProjectsView.loadProjects();
        await DashboardView.init();
        App.openProject(res.project.id);
      }
    } catch (err) {
      App.showToast('Error', err.message || 'Failed to instantiate template.', 'error');
    }
  }
};
