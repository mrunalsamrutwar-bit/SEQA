/**
 * DFD Architect — Automatic Documentation View Controller
 */
const DocsView = {
  currentDocData: null,

  async init() {
    await this.loadDocumentation();
  },

  async loadDocumentation() {
    if (!State.project) {
      document.getElementById('docs-content-container').innerHTML = `
        <div style="text-align: center; padding: 4rem; color: var(--text-muted);">
          <i class="fa-solid fa-file-circle-question" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
          <h3>No Active Project</h3>
          <p>Please select a project to compile documentation.</p>
        </div>
      `;
      return;
    }

    try {
      const data = await API.get(`/api/projects/${State.project.id}/documentation`);
      this.currentDocData = data;
      this.renderDocumentation(data);
    } catch (err) {
      console.error('Failed to load documentation:', err);
      App.showToast('Error', 'Failed to generate documentation.', 'error');
    }
  },

  renderDocumentation(doc) {
    const container = document.getElementById('docs-content-container');
    if (!container) return;

    const meta = doc.project_meta;
    const metrics = doc.summary_metrics;
    const entities = doc.entities || [];
    const processes = doc.processes || [];
    const datastores = doc.datastores || [];
    const flows = doc.data_flows || [];
    const validation = doc.validation || {};

    container.innerHTML = `
      <!-- Header Document Card -->
      <div class="doc-header-card">
        <h1 class="doc-title">${meta.name}</h1>
        <p class="doc-subtitle">System Data Flow Diagram (DFD) Specification — ${meta.dfd_level}</p>

        <table class="doc-meta-table">
          <tr>
            <td class="doc-meta-label">System Name</td>
            <td><strong>${meta.system_name}</strong></td>
            <td class="doc-meta-label">DFD Level</td>
            <td><span class="badge badge-primary">${meta.dfd_level}</span></td>
          </tr>
          <tr>
            <td class="doc-meta-label">Author / Architect</td>
            <td>${meta.author}</td>
            <td class="doc-meta-label">Version</td>
            <td>${meta.version}</td>
          </tr>
          <tr>
            <td class="doc-meta-label">Last Updated</td>
            <td>${meta.updated_at}</td>
            <td class="doc-meta-label">Validation Score</td>
            <td><strong>${metrics.compliance_score}% Compliant</strong></td>
          </tr>
        </table>
      </div>

      <!-- Section 1: System Overview -->
      <div class="doc-section">
        <h3 class="doc-section-title"><i class="fa-solid fa-circle-info" style="color: var(--primary-600);"></i> 1. System Overview & Scope</h3>
        <p class="doc-section-desc">${meta.description || `This document provides the formal software engineering Data Flow architecture specification for ${meta.system_name}.`}</p>
        
        <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
          <span class="badge badge-neutral"><i class="fa-solid fa-gears" style="color: #2563EB;"></i> ${metrics.processes_count} Processes</span>
          <span class="badge badge-neutral"><i class="fa-solid fa-database" style="color: #059669;"></i> ${metrics.datastores_count} Data Stores</span>
          <span class="badge badge-neutral"><i class="fa-solid fa-users" style="color: #D97706;"></i> ${metrics.entities_count} External Entities</span>
          <span class="badge badge-neutral"><i class="fa-solid fa-arrow-right-arrow-left" style="color: #7C3AED;"></i> ${metrics.flows_count} Data Flows</span>
        </div>
      </div>

      <!-- Section 2: External Entities Catalog -->
      <div class="doc-section">
        <h3 class="doc-section-title"><i class="fa-solid fa-users" style="color: var(--accent-amber);"></i> 2. External Entities Catalog</h3>
        <p class="doc-section-desc">External entities define the boundary actors that feed information into or consume information from the system.</p>

        <div class="projects-table-wrapper">
          <table class="custom-table">
            <thead>
              <tr>
                <th style="width: 70px;">ID</th>
                <th>Entity Name</th>
                <th>Category / Type</th>
                <th>Associated Data Flows</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              ${entities.length > 0 ? entities.map(e => `
                <tr>
                  <td><strong>${e.id}</strong></td>
                  <td><strong>${e.name}</strong></td>
                  <td><span class="badge badge-neutral">${e.type}</span></td>
                  <td>
                    <div style="font-size: 0.75rem;"><strong>In:</strong> ${e.inbound_flows.join(', ') || 'None'}</div>
                    <div style="font-size: 0.75rem; margin-top: 2px;"><strong>Out:</strong> ${e.outbound_flows.join(', ') || 'None'}</div>
                  </td>
                  <td style="font-size: 0.8rem; color: var(--text-secondary);">${e.description}</td>
                </tr>
              `).join('') : '<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">No external entities defined.</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Section 3: Processes & Functional Transformations -->
      <div class="doc-section">
        <h3 class="doc-section-title"><i class="fa-solid fa-gears" style="color: var(--primary-600);"></i> 3. Processes & Functional Transformations</h3>
        <p class="doc-section-desc">Processes perform operational logic, algorithms, and transformations on incoming data streams.</p>

        <div class="projects-table-wrapper">
          <table class="custom-table">
            <thead>
              <tr>
                <th style="width: 70px;">ID</th>
                <th>Process Name</th>
                <th>Inbound Inputs</th>
                <th>Outbound Outputs</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              ${processes.length > 0 ? processes.map(p => `
                <tr>
                  <td><strong>${p.id}</strong></td>
                  <td><strong>${p.name}</strong></td>
                  <td style="font-size: 0.78rem;">${p.inputs.join('<br>') || 'None'}</td>
                  <td style="font-size: 0.78rem;">${p.outputs.join('<br>') || 'None'}</td>
                  <td style="font-size: 0.8rem; color: var(--text-secondary);">${p.description}</td>
                </tr>
              `).join('') : '<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">No processes defined.</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Section 4: Data Stores & Repositories -->
      <div class="doc-section">
        <h3 class="doc-section-title"><i class="fa-solid fa-database" style="color: var(--accent-emerald);"></i> 4. Data Stores & Repositories</h3>
        <p class="doc-section-desc">Data Stores represent resting state repositories (databases, file systems, tables) referenced by processes.</p>

        <div class="projects-table-wrapper">
          <table class="custom-table">
            <thead>
              <tr>
                <th style="width: 70px;">Store ID</th>
                <th>Data Store Name</th>
                <th>Storage Tech</th>
                <th>Connected Processes</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              ${datastores.length > 0 ? datastores.map(d => `
                <tr>
                  <td><strong>${d.id}</strong></td>
                  <td><strong>${d.name}</strong></td>
                  <td><span class="badge badge-neutral">${d.storage_type}</span></td>
                  <td>
                    <div style="font-size: 0.75rem;"><strong>Read by:</strong> ${d.readers.join(', ') || 'None'}</div>
                    <div style="font-size: 0.75rem; margin-top: 2px;"><strong>Written by:</strong> ${d.writers.join(', ') || 'None'}</div>
                  </td>
                  <td style="font-size: 0.8rem; color: var(--text-secondary);">${d.description}</td>
                </tr>
              `).join('') : '<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">No data stores defined.</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Section 5: Data Flow Matrix & Data Dictionary -->
      <div class="doc-section">
        <h3 class="doc-section-title"><i class="fa-solid fa-arrow-right-arrow-left" style="color: var(--accent-purple);"></i> 5. Data Flow Matrix & Data Dictionary</h3>
        <p class="doc-section-desc">Detailed matrix of all data items transferred across boundaries and functional components.</p>

        <div class="projects-table-wrapper">
          <table class="custom-table">
            <thead>
              <tr>
                <th style="width: 70px;">Flow ID</th>
                <th>Data Item / Flow Label</th>
                <th>Origin Source</th>
                <th>Target Destination</th>
                <th>Payload Data Type & Description</th>
              </tr>
            </thead>
            <tbody>
              ${flows.length > 0 ? flows.map(f => `
                <tr>
                  <td><strong>${f.id}</strong></td>
                  <td><strong>${f.name}</strong></td>
                  <td style="font-size: 0.8rem;">${f.source}</td>
                  <td style="font-size: 0.8rem;">${f.destination}</td>
                  <td style="font-size: 0.8rem; color: var(--text-secondary);">
                    <div><strong>Type:</strong> ${f.data_type}</div>
                    <div style="margin-top: 2px;">${f.description}</div>
                  </td>
                </tr>
              `).join('') : '<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">No data flows defined.</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Section 6: Process Narrative Specifications -->
      <div class="doc-section">
        <h3 class="doc-section-title"><i class="fa-solid fa-book-open" style="color: var(--accent-cyan);"></i> 6. Process Narrative Specifications</h3>
        
        <div style="display: flex; flex-direction: column; gap: 1rem;">
          ${processes.map(p => `
            <div class="card" style="padding: 1rem; background: var(--bg-subtle);">
              <h4 style="font-family: var(--font-display); font-size: 0.95rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.35rem;">
                Process ${p.id}: ${p.name}
              </h4>
              <p style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.4; font-style: italic;">
                "${p.detailed_narrative}"
              </p>
              <div style="display: flex; gap: 1.5rem; margin-top: 0.6rem; font-size: 0.78rem;">
                <div><strong>Inbound:</strong> ${p.inputs.join(', ') || 'None'}</div>
                <div><strong>Outbound:</strong> ${p.outputs.join(', ') || 'None'}</div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- Section 7: Validation & Verification Audit -->
      <div class="doc-section">
        <h3 class="doc-section-title"><i class="fa-solid fa-shield-halved" style="color: var(--accent-emerald);"></i> 7. DFD Validation & Compliance Audit</h3>
        <p class="doc-section-desc">Compliance score: <strong>${metrics.compliance_score}%</strong> (Errors: ${metrics.errors_count}, Warnings: ${metrics.warnings_count})</p>

        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
          ${validation.issues && validation.issues.length > 0 ? validation.issues.map(iss => `
            <div style="padding: 0.6rem 0.85rem; border-radius: var(--radius-sm); font-size: 0.8rem; background: ${iss.type === 'error' ? 'rgba(244, 63, 94, 0.08)' : 'rgba(245, 158, 11, 0.08)'}; border-left: 3px solid ${iss.type === 'error' ? 'var(--accent-rose)' : 'var(--accent-amber)'};">
              <strong>${iss.title}:</strong> ${iss.message} <em>(Suggestion: ${iss.suggestion})</em>
            </div>
          `).join('') : '<div style="padding: 0.75rem; background: rgba(16, 185, 129, 0.08); border-left: 3px solid var(--accent-emerald); font-size: 0.82rem; font-weight: 600; color: var(--accent-emerald);">✓ Perfect DFD Architecture: All syntax and semantic validation rules passed.</div>'}
        </div>
      </div>
    `;
  },

  async copyMarkdown() {
    if (!this.currentDocData || !this.currentDocData.markdown_text) return;
    try {
      await navigator.clipboard.writeText(this.currentDocData.markdown_text);
      App.showToast('Copied to Clipboard', 'Structured Markdown documentation copied.', 'success');
    } catch (err) {
      App.showToast('Error', 'Failed to copy to clipboard.', 'error');
    }
  },

  exportDocx() {
    if (!State.project) return;
    window.location.href = `/api/projects/${State.project.id}/export/docx`;
    App.showToast('Generating Word Document', 'Your .docx specification will begin downloading shortly.', 'info');
  },

  exportPdf() {
    if (!State.project) return;
    window.location.href = `/api/projects/${State.project.id}/export/pdf`;
    App.showToast('Generating PDF Document', 'Your formatted PDF report will begin downloading shortly.', 'info');
  }
};
