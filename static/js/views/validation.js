/**
 * DFD Architect — Validation View & Rule Audit Controller
 */
const ValidationView = {
  async runValidation(levelId = null) {
    if (!State.project) {
      App.showToast('No Project', 'Please open a project to validate.', 'info');
      return;
    }

    const lvlId = levelId || State.activeLevelId;
    try {
      const result = await API.get(`/api/projects/${State.project.id}/validate`, { level_id: lvlId });
      this.renderValidationDrawer(result);
      this.openDrawer();
    } catch (err) {
      console.error('Validation error:', err);
      App.showToast('Validation Error', 'Failed to complete DFD validation analysis.', 'error');
    }
  },

  renderValidationDrawer(result) {
    const body = document.getElementById('validation-body');
    const scoreBadge = document.getElementById('validation-score-badge');
    if (!body || !scoreBadge) return;

    const summary = result.summary || {};
    const score = summary.compliance_score || 0;
    const errors = summary.errors_count || 0;
    const warnings = summary.warnings_count || 0;

    // Update Score Badge
    scoreBadge.className = `validation-score-badge ${errors > 0 ? 'badge-danger' : (warnings > 0 ? 'badge-warning' : 'badge-success')}`;
    scoreBadge.innerHTML = `
      <i class="fa-solid ${errors > 0 ? 'fa-triangle-exclamation' : (warnings > 0 ? 'fa-circle-exclamation' : 'fa-circle-check')}"></i>
      <span>${score}% Compliant (${errors} Errors, ${warnings} Warnings)</span>
    `;

    const rules = result.rules || [];
    body.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 0.75rem; margin-bottom: 1rem;">
        <div class="card" style="padding: 0.75rem; background: var(--bg-subtle);">
          <div style="font-size: 0.7rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700;">Compliance Score</div>
          <div style="font-size: 1.3rem; font-weight: 800; color: ${score >= 90 ? 'var(--accent-emerald)' : (score >= 70 ? 'var(--accent-amber)' : 'var(--accent-rose)')};">${score}%</div>
        </div>
        <div class="card" style="padding: 0.75rem; background: var(--bg-subtle);">
          <div style="font-size: 0.7rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700;">Rules Passed</div>
          <div style="font-size: 1.3rem; font-weight: 800; color: var(--accent-emerald);">${summary.passed_count}/${summary.total_rules}</div>
        </div>
        <div class="card" style="padding: 0.75rem; background: var(--bg-subtle);">
          <div style="font-size: 0.7rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700;">Errors</div>
          <div style="font-size: 1.3rem; font-weight: 800; color: var(--accent-rose);">${errors}</div>
        </div>
        <div class="card" style="padding: 0.75rem; background: var(--bg-subtle);">
          <div style="font-size: 0.7rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700;">Warnings</div>
          <div style="font-size: 1.3rem; font-weight: 800; color: var(--accent-amber);">${warnings}</div>
        </div>
      </div>

      <div style="display: flex; flex-direction: column; gap: 0.75rem;">
        ${rules.map(rule => {
          const isPassed = rule.status === 'passed';
          const isError = rule.status === 'error';
          const badgeClass = isPassed ? 'badge-success' : (isError ? 'badge-danger' : 'badge-warning');
          const statusText = isPassed ? 'PASSED' : (isError ? 'ERROR' : 'WARNING');

          return `
            <div class="validation-rule-item ${isPassed ? 'rule-passed' : (isError ? 'rule-error' : 'rule-warning')}">
              <div style="margin-top: 2px;">
                <i class="fa-solid ${isPassed ? 'fa-check-circle' : (isError ? 'fa-times-circle' : 'fa-exclamation-triangle')}" 
                   style="color: ${isPassed ? 'var(--accent-emerald)' : (isError ? 'var(--accent-rose)' : 'var(--accent-amber)')}; font-size: 1.1rem;"></i>
              </div>
              <div style="flex: 1;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                  <div style="font-weight: 700; font-size: 0.88rem; color: var(--text-primary);">${rule.title}</div>
                  <span class="badge ${badgeClass}">${statusText}</span>
                </div>
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.15rem;">${rule.description}</div>

                ${rule.items && rule.items.length > 0 ? `
                  <div style="margin-top: 0.6rem; display: flex; flex-direction: column; gap: 0.4rem;">
                    ${rule.items.map(item => `
                      <div style="padding: 0.5rem 0.75rem; background: var(--bg-subtle); border-radius: var(--radius-sm); font-size: 0.78rem; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                          <div style="font-weight: 600; color: var(--text-primary);">${item.message}</div>
                          <div style="color: var(--text-muted); margin-top: 2px;">→ <em>Suggestion: ${item.suggestion}</em></div>
                        </div>
                        ${item.component_id ? `
                          <button class="btn btn-secondary btn-sm" style="padding: 0.2rem 0.5rem; font-size: 0.7rem;" onclick="ValidationView.jumpToComponent(${item.component_id})">
                            <i class="fa-solid fa-crosshairs"></i> Locate
                          </button>
                        ` : (item.flow_id ? `
                          <button class="btn btn-secondary btn-sm" style="padding: 0.2rem 0.5rem; font-size: 0.7rem;" onclick="ValidationView.jumpToFlow(${item.flow_id})">
                            <i class="fa-solid fa-crosshairs"></i> Locate
                          </button>
                        ` : '')}
                      </div>
                    `).join('')}
                  </div>
                ` : ''}
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;
  },

  jumpToComponent(compId) {
    App.switchView('designer');
    Designer.selectNode(compId);
    const comp = State.getComponentById(compId);
    if (comp) {
      const viewport = document.getElementById('canvas-viewport');
      if (viewport) {
        State.viewport.panX = viewport.clientWidth / 2 - (comp.pos_x + (comp.width || 160) / 2) * State.viewport.zoom;
        State.viewport.panY = viewport.clientHeight / 2 - (comp.pos_y + (comp.height || 80) / 2) * State.viewport.zoom;
        CanvasEngine.applyTransform();
      }
    }
  },

  jumpToFlow(flowId) {
    App.switchView('designer');
    Designer.selectFlow(flowId);
  },

  openDrawer() {
    document.getElementById('validation-drawer')?.classList.add('open');
  },

  closeDrawer() {
    document.getElementById('validation-drawer')?.classList.remove('open');
  }
};
