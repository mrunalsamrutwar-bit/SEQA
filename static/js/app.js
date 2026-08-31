/**
 * DFD Architect — Main Application Router & Controller
 */
const App = {
  activeView: 'dashboard',
  confirmCallback: null,
  searchTimer: null,

  async init() {
    console.log('🚀 Initializing DFD Architect Workspace...');

    // 1. Setup Theme
    this.initTheme();

    // 2. Setup Global Keybindings
    this.initKeybindings();

    // 3. Setup Global Search Input
    this.initGlobalSearch();

    // 4. Load initial project list & active project
    try {
      const res = await API.get('/api/projects');
      const projects = res.projects || [];
      
      if (projects.length > 0) {
        // Load first project (demo or user's project)
        await this.openProject(projects[0].id, false);
      }

      // Initialize Dashboard
      await DashboardView.init();
    } catch (err) {
      console.error('App init error:', err);
    }
  },

  // -------------------------------------------------------------
  // View Navigation
  // -------------------------------------------------------------
  switchView(viewName) {
    this.activeView = viewName;

    // Update views visibility
    document.querySelectorAll('.app-view').forEach(el => el.classList.remove('active'));
    const targetView = document.getElementById(`view-${viewName}`);
    if (targetView) targetView.classList.add('active');

    // Update Sidebar Navigation
    document.querySelectorAll('.sidebar-nav .nav-item').forEach(el => {
      if (el.getAttribute('data-view') === viewName) {
        el.classList.add('active');
      } else {
        el.classList.remove('active');
      }
    });

    // Update Breadcrumb
    const bcCurrent = document.getElementById('breadcrumb-current-view');
    if (bcCurrent) {
      const titles = {
        'dashboard': 'Dashboard',
        'projects': 'My Projects',
        'designer': 'DFD Designer',
        'docs': 'Documentation',
        'templates': 'Templates Library',
        'analytics': 'Analytics',
        'settings': 'Settings',
        'help': 'Help & Guide'
      };
      bcCurrent.textContent = titles[viewName] || viewName;
    }

    // Toggle save status pill in header
    const savePill = document.getElementById('save-status-pill');
    if (savePill) {
      savePill.style.display = viewName === 'designer' ? 'flex' : 'none';
    }

    // Trigger View Initializers
    if (viewName === 'dashboard') {
      DashboardView.init();
    } else if (viewName === 'projects') {
      ProjectsView.init();
    } else if (viewName === 'designer') {
      Designer.init();
      CanvasEngine.render();
      setTimeout(() => CanvasEngine.zoomFit(), 50);
    } else if (viewName === 'docs') {
      DocsView.init();
    } else if (viewName === 'templates') {
      TemplatesView.init();
    } else if (viewName === 'analytics') {
      AnalyticsView.init();
    }
  },

  // -------------------------------------------------------------
  // Project Loading
  // -------------------------------------------------------------
  async openProject(projectId, switchToDesignerView = true) {
    try {
      const res = await API.get(`/api/projects/${projectId}`);
      if (res.project) {
        State.setProject(res.project);
        
        // Update header project name
        const headerName = document.getElementById('header-active-project-name');
        if (headerName) headerName.textContent = res.project.name;

        if (switchToDesignerView) {
          this.switchView('designer');
        }
      }
    } catch (err) {
      console.error('Failed to open project:', err);
      this.showToast('Error', 'Could not open project.', 'error');
    }
  },

  // -------------------------------------------------------------
  // Global Search Modal (Ctrl + K)
  // -------------------------------------------------------------
  initGlobalSearch() {
    const input = document.getElementById('global-search-input');
    if (!input) return;

    input.addEventListener('input', (e) => {
      clearTimeout(this.searchTimer);
      const query = e.target.value.trim();
      if (!query) {
        document.getElementById('global-search-results').innerHTML = `
          <div style="padding: 2rem; text-align: center; color: var(--text-muted); font-size: 0.85rem;">
            Type keywords to search across your system architecture models.
          </div>
        `;
        return;
      }

      this.searchTimer = setTimeout(async () => {
        try {
          const res = await API.get('/api/search', { q: query });
          this.renderSearchResults(res.results || []);
        } catch (err) {
          console.error('Search error:', err);
        }
      }, 250);
    });
  },

  renderSearchResults(results) {
    const container = document.getElementById('global-search-results');
    if (!container) return;

    if (results.length === 0) {
      container.innerHTML = `
        <div style="padding: 2rem; text-align: center; color: var(--text-muted); font-size: 0.85rem;">
          No matching components or projects found.
        </div>
      `;
      return;
    }

    container.innerHTML = results.map(r => `
      <div class="search-result-item" onclick="App.handleSearchResultClick(${JSON.stringify(r).replace(/"/g, '&quot;')})">
        <div style="width: 32px; height: 32px; border-radius: var(--radius-sm); background: var(--bg-subtle); display: flex; align-items: center; justify-content: center; color: var(--primary-600);">
          <i class="fa-solid fa-${r.icon || 'circle-dot'}"></i>
        </div>
        <div style="flex: 1;">
          <div style="font-weight: 700; font-size: 0.85rem; color: var(--text-primary);">${r.title}</div>
          <div style="font-size: 0.75rem; color: var(--text-muted);">${r.subtitle}</div>
        </div>
        <span class="badge badge-neutral" style="font-size: 0.68rem; text-transform: uppercase;">${r.type}</span>
      </div>
    `).join('');
  },

  async handleSearchResultClick(result) {
    this.closeModal('modal-search');
    if (result.project_id) {
      await this.openProject(result.project_id, true);
      if (result.level_id) {
        Designer.switchLevel(result.level_id);
      }
      if (result.component_id) {
        ValidationView.jumpToComponent(result.component_id);
      } else if (result.flow_id) {
        ValidationView.jumpToFlow(result.flow_id);
      }
    }
  },

  openSearchModal() {
    this.openModal('modal-search');
    const input = document.getElementById('global-search-input');
    if (input) {
      input.value = '';
      setTimeout(() => input.focus(), 100);
    }
  },

  // -------------------------------------------------------------
  // Keyboard Shortcuts Listener
  // -------------------------------------------------------------
  initKeybindings() {
    window.addEventListener('keydown', (e) => {
      // Ignore key shortcuts if focused on input/textarea
      const isInput = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName);

      // Ctrl + K -> Open Global Search
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        this.openSearchModal();
        return;
      }

      // Escape -> Close Modals / Validation Drawer / Deselect
      if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.open').forEach(m => m.classList.remove('open'));
        ValidationView.closeDrawer();
        if (!isInput && this.activeView === 'designer') {
          Designer.deselectAll();
        }
        return;
      }

      if (isInput) return;

      // Ctrl + S -> Manual Save
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
        e.preventDefault();
        if (this.activeView === 'designer') {
          Designer.manualSave();
          this.showToast('Saved', 'Diagram changes persisted.', 'success');
        }
        return;
      }

      // Ctrl + Z -> Undo
      if ((e.ctrlKey || e.metaKey) && !e.shiftKey && e.key.toLowerCase() === 'z') {
        e.preventDefault();
        if (this.activeView === 'designer') {
          CanvasEngine.undo();
        }
        return;
      }

      // Ctrl + Y (or Ctrl+Shift+Z) -> Redo
      if (((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'y') || ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'z')) {
        e.preventDefault();
        if (this.activeView === 'designer') {
          CanvasEngine.redo();
        }
        return;
      }

      // Alt + L -> Auto-Layout
      if (e.altKey && e.key.toLowerCase() === 'l') {
        e.preventDefault();
        if (this.activeView === 'designer') {
          CanvasEngine.autoLayout();
        }
        return;
      }

      // Delete or Backspace -> Delete selected Node or Flow
      if (e.key === 'Delete' || e.key === 'Backspace') {
        if (this.activeView === 'designer') {
          if (State.selectedNodeId) {
            e.preventDefault();
            Designer.deleteActiveComponent();
          } else if (State.selectedFlowId) {
            e.preventDefault();
            Designer.deleteActiveFlow();
          }
        }
      }
    });
  },

  // -------------------------------------------------------------
  // Theme Toggle (Dark / Light Mode)
  // -------------------------------------------------------------
  initTheme() {
    const savedTheme = localStorage.getItem('dfd_theme') || 'light';
    if (savedTheme === 'dark') {
      document.body.classList.add('dark-mode');
      this.updateThemeToggleIcon(true);
    }
  },

  toggleTheme() {
    const isDark = document.body.classList.toggle('dark-mode');
    localStorage.setItem('dfd_theme', isDark ? 'dark' : 'light');
    this.updateThemeToggleIcon(isDark);
    CanvasEngine.render();
    if (this.activeView === 'dashboard') DashboardView.init();
    if (this.activeView === 'analytics') AnalyticsView.init();
    this.showToast('Theme Changed', `Switched to ${isDark ? 'Dark' : 'Light'} theme.`, 'info');
  },

  updateThemeToggleIcon(isDark) {
    const btn = document.getElementById('theme-toggle-btn');
    if (btn) {
      btn.innerHTML = `<i class="fa-solid fa-${isDark ? 'sun' : 'moon'}"></i>`;
    }
  },

  // -------------------------------------------------------------
  // Global Modals & Dialogs
  // -------------------------------------------------------------
  openModal(modalId) {
    document.getElementById(modalId)?.classList.add('open');
  },

  closeModal(modalId) {
    document.getElementById(modalId)?.classList.remove('open');
  },

  openCreateProjectModal() {
    this.openModal('modal-create-project');
    setTimeout(() => {
      document.getElementById('new-proj-name')?.focus();
    }, 100);
  },

  openExportModal() {
    this.openModal('modal-export');
  },

  openConfirmModal(title, message, onConfirm) {
    document.getElementById('confirm-title').textContent = title;
    document.getElementById('confirm-message').innerHTML = message;
    this.confirmCallback = onConfirm;

    const btn = document.getElementById('confirm-action-btn');
    btn.onclick = () => {
      this.closeModal('modal-confirm');
      if (this.confirmCallback) this.confirmCallback();
    };

    this.openModal('modal-confirm');
  },

  // -------------------------------------------------------------
  // Export Handlers
  // -------------------------------------------------------------
  triggerExportForProject(projectId) {
    this.openProject(projectId, false).then(() => {
      this.openExportModal();
    });
  },

  async triggerExportForProject(projectId) {
    if (!State.project || State.project.id !== projectId) {
      await this.openProject(projectId, false);
    }
    this.openExportModal();
  },

  buildCompleteDiagramSvg() {
    const components = State.getCurrentComponents();
    const flows = State.getCurrentFlows();
    const isDark = document.body.classList.contains('dark-mode');

    // Calculate diagram bounding box
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    if (components.length === 0) {
      minX = 0; minY = 0; maxX = 800; maxY = 600;
    } else {
      components.forEach(c => {
        const w = c.width || 160;
        const h = c.height || 80;
        minX = Math.min(minX, c.pos_x);
        minY = Math.min(minY, c.pos_y);
        maxX = Math.max(maxX, c.pos_x + w);
        maxY = Math.max(maxY, c.pos_y + h);
      });
    }

    const padding = 60;
    const viewX = Math.max(0, minX - padding);
    const viewY = Math.max(0, minY - padding);
    const viewW = Math.max(800, (maxX - minX) + padding * 2);
    const viewH = Math.max(600, (maxY - minY) + padding * 2);

    const bgColor = isDark ? '#0B0F19' : '#F8FAFC';
    const textColor = isDark ? '#F1F5F9' : '#0F172A';
    const subtextColor = isDark ? '#94A3B8' : '#64748B';
    const arrowColor = isDark ? '#818CF8' : '#4F46E5';

    let svgXml = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${viewX} ${viewY} ${viewW} ${viewH}" width="${viewW}" height="${viewH}" style="background-color: ${bgColor}; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;">
      <defs>
        <marker id="export-arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill="${arrowColor}" />
        </marker>
        <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%" filterUnits="userSpaceOnUse">
          <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="${isDark ? '0.35' : '0.08'}"/>
        </filter>
      </defs>

      <!-- Background -->
      <rect x="${viewX}" y="${viewY}" width="${viewW}" height="${viewH}" fill="${bgColor}" />
      
      <!-- Diagram Title & Metadata Watermark -->
      <g transform="translate(${viewX + 24}, ${viewY + 34})">
        <text x="0" y="0" font-size="16" font-weight="800" fill="${textColor}">${State.project ? State.project.name : 'System Architecture'} — ${State.getActiveLevel() ? State.getActiveLevel().level_name : 'DFD'}</text>
        <text x="0" y="18" font-size="11" font-weight="500" fill="${subtextColor}">Generated with DFD Architect • ${new Date().toLocaleDateString()}</text>
      </g>

      <!-- Data Flows Layer -->
      <g id="export-flows">`;

    // Render Flows
    flows.forEach(flow => {
      const src = State.getComponentById(flow.source_id);
      const dst = State.getComponentById(flow.destination_id);
      if (!src || !dst) return;

      const { srcPort, dstPort } = Connections.getPortPositions(src, dst);
      const { path, midpoint } = Connections.calculateBezierPath(srcPort, dstPort);
      const labelText = flow.flow_name || flow.flow_identifier || 'Flow';
      const labelW = Math.max(50, labelText.length * 6.5 + 14);
      const labelH = 20;

      svgXml += `
        <path d="${path}" fill="none" stroke="${arrowColor}" stroke-width="2" marker-end="url(#export-arrow)" ${flow.is_bidirectional ? 'marker-start="url(#export-arrow)"' : ''} />
        <g transform="translate(${midpoint.x - labelW / 2}, ${midpoint.y - labelH / 2})">
          <rect width="${labelW}" height="${labelH}" rx="4" fill="${isDark ? '#1E293B' : '#FFFFFF'}" stroke="${isDark ? '#334155' : '#CBD5E1'}" stroke-width="1" />
          <text x="${labelW / 2}" y="${labelH / 2 + 3.5}" text-anchor="middle" font-size="9.5" font-weight="600" fill="${textColor}">${labelText}</text>
        </g>
      `;
    });

    svgXml += `</g>
      <!-- Components Layer -->
      <g id="export-nodes">`;

    // Render Component Nodes
    components.forEach(c => {
      const x = c.pos_x;
      const y = c.pos_y;
      const w = c.width || 160;
      const h = c.height || 80;

      if (c.component_type === 'process') {
        const fill = isDark ? '#1E293B' : '#FFFFFF';
        const stroke = '#2563EB';
        const headerBg = isDark ? '#1E3A8A' : '#EFF6FF';
        svgXml += `
          <g transform="translate(${x}, ${y})" filter="url(#shadow)">
            <rect width="${w}" height="${h}" rx="12" fill="${fill}" stroke="${stroke}" stroke-width="2"/>
            <path d="M 0 24 L ${w} 24" stroke="${isDark ? '#3B82F6' : '#BFDBFE'}" stroke-width="1.5"/>
            <rect width="${w}" height="24" rx="12" fill="${headerBg}" />
            <rect y="12" width="${w}" height="12" fill="${headerBg}" />
            <text x="10" y="16" font-size="10.5" font-weight="800" fill="#2563EB">${c.component_identifier || '1.0'}</text>
            <text x="${w - 10}" y="16" font-size="9.5" font-weight="600" fill="${subtextColor}" text-anchor="end">PROCESS</text>
            <text x="${w / 2}" y="${24 + (h - 24) / 2 + 4}" text-anchor="middle" font-size="11.5" font-weight="700" fill="${textColor}">${c.name}</text>
          </g>
        `;
      } else if (c.component_type === 'entity') {
        const fill = isDark ? '#1E293B' : '#FFFFFF';
        const stroke = '#D97706';
        svgXml += `
          <g transform="translate(${x}, ${y})" filter="url(#shadow)">
            <rect width="${w}" height="${h}" rx="4" fill="${fill}" stroke="${stroke}" stroke-width="2"/>
            <rect x="3" y="3" width="${w - 6}" height="${h - 6}" rx="2" fill="none" stroke="${isDark ? '#78350F' : '#FDE68A'}" stroke-width="1"/>
            <text x="8" y="16" font-size="9.5" font-weight="800" fill="#D97706">${c.component_identifier || 'E1'}</text>
            <text x="${w / 2}" y="${h / 2 + 4}" text-anchor="middle" font-size="11.5" font-weight="700" fill="${textColor}">${c.name}</text>
          </g>
        `;
      } else if (c.component_type === 'datastore') {
        const fill = isDark ? '#1E293B' : '#FFFFFF';
        const stroke = '#059669';
        svgXml += `
          <g transform="translate(${x}, ${y})" filter="url(#shadow)">
            <rect width="${w}" height="${h}" rx="4" fill="${fill}" stroke="${stroke}" stroke-width="2"/>
            <line x1="36" y1="0" x2="36" y2="${h}" stroke="${isDark ? '#064E3B' : '#A7F3D0'}" stroke-width="1.5"/>
            <text x="18" y="${h / 2 + 4}" text-anchor="middle" font-size="10.5" font-weight="800" fill="#059669">${c.component_identifier || 'D1'}</text>
            <text x="${36 + (w - 36) / 2}" y="${h / 2 + 4}" text-anchor="middle" font-size="11.5" font-weight="700" fill="${textColor}">${c.name}</text>
          </g>
        `;
      }
    });

    svgXml += `</g>
    </svg>`;
    return svgXml;
  },

  exportSvgImage() {
    const svgData = this.buildCompleteDiagramSvg();
    const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `${State.project ? State.project.name.replace(/\s+/g, '_') : 'Diagram'}_DFD.svg`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    this.showToast('Vector SVG Exported', 'Complete vector diagram downloaded.', 'success');
  },

  exportPngImage() {
    this.showToast('Rendering PNG', 'Generating high-resolution diagram image...', 'info');
    const svgData = this.buildCompleteDiagramSvg();
    const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const img = new Image();

    img.onload = () => {
      const canvas = document.createElement('canvas');
      const scale = 2; // High-DPI 2x supersampling
      canvas.width = img.width * scale || 2400;
      canvas.height = img.height * scale || 1600;
      const ctx = canvas.getContext('2d');
      ctx.scale(scale, scale);
      ctx.drawImage(img, 0, 0);

      const pngUrl = canvas.toDataURL('image/png');
      const a = document.createElement('a');
      a.href = pngUrl;
      a.download = `${State.project ? State.project.name.replace(/\s+/g, '_') : 'Diagram'}_DFD.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      this.showToast('PNG Exported', 'High-resolution diagram downloaded.', 'success');
    };
    img.src = url;
  },

  runValidation() {
    ValidationView.runValidation();
  },

  async logout() {
    try {
      await API.post('/api/auth/logout');
      window.location.href = '/login';
    } catch (err) {
      window.location.href = '/login';
    }
  },

  // -------------------------------------------------------------
  // Toast Notifications
  // -------------------------------------------------------------
  showToast(title, message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const iconMap = {
      'success': 'fa-circle-check',
      'error': 'fa-circle-xmark',
      'warning': 'fa-triangle-exclamation',
      'info': 'fa-circle-info'
    };

    toast.innerHTML = `
      <div style="font-size: 1.1rem; color: ${type === 'success' ? 'var(--accent-emerald)' : (type === 'error' ? 'var(--accent-rose)' : (type === 'warning' ? 'var(--accent-amber)' : 'var(--accent-blue)'))};">
        <i class="fa-solid ${iconMap[type] || 'fa-circle-info'}"></i>
      </div>
      <div class="toast-content">
        <div class="toast-title">${title}</div>
        <div class="toast-message">${message}</div>
      </div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      setTimeout(() => toast.remove(), 250);
    }, 3500);
  }
};

// Bootstrap application on page load if app workspace container exists
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('app-container')) {
    App.init();
  }
});
