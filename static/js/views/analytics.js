/**
 * DFD Architect — Analytics View Controller
 */
const AnalyticsView = {
  doughnutChart: null,

  async init() {
    await this.loadAnalytics();
  },

  async loadAnalytics() {
    try {
      const data = await API.get('/api/analytics');
      this.renderDoughnut(data.component_distribution || []);
      this.renderActivities(data.recent_activities || []);
    } catch (err) {
      console.error('Failed to load analytics:', err);
    }
  },

  renderDoughnut(distribution) {
    const canvas = document.getElementById('analyticsDoughnutChart');
    if (!canvas) return;

    if (this.doughnutChart) {
      this.doughnutChart.destroy();
    }

    const labels = distribution.map(d => d.type);
    const data = distribution.map(d => d.count);
    const colors = distribution.map(d => d.color);

    const isDark = document.body.classList.contains('dark-mode');

    this.doughnutChart = new Chart(canvas, {
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
        cutout: '65%',
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
  },

  renderActivities(activities) {
    const container = document.getElementById('analytics-activity-timeline');
    if (!container) return;

    if (activities.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; color: var(--text-muted); font-size: 0.82rem; padding: 2rem;">
          No recent activity logs recorded yet.
        </div>
      `;
      return;
    }

    container.innerHTML = activities.map(a => `
      <div style="display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.6rem 0.75rem; background: var(--bg-subtle); border-radius: var(--radius-md);">
        <div style="width: 28px; height: 28px; border-radius: 50%; background: var(--primary-100); color: var(--primary-700); display: flex; align-items: center; justify-content: center; font-size: 0.75rem;">
          <i class="fa-solid fa-clock-rotate-left"></i>
        </div>
        <div style="flex: 1;">
          <div style="font-weight: 700; font-size: 0.82rem; color: var(--text-primary);">${a.action}</div>
          <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 2px;">${a.details}</div>
          <div style="font-size: 0.68rem; color: var(--text-muted); margin-top: 4px;">${a.timestamp}</div>
        </div>
      </div>
    `).join('');
  }
};
