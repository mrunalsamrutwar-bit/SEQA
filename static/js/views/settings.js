/**
 * DFD Architect — Settings & Profile Controller
 */
const SettingsView = {
  async saveProfile(e) {
    e.preventDefault();
    const fullName = document.getElementById('set-fullname')?.value.trim();
    const email = document.getElementById('set-email')?.value.trim();
    const role = document.getElementById('set-role')?.value.trim();

    try {
      const res = await API.put('/api/auth/profile', {
        full_name: fullName,
        email: email,
        role: role
      });

      if (res.success) {
        App.showToast('Profile Updated', 'User profile details saved.', 'success');
        document.getElementById('user-display-name').textContent = res.user.full_name || res.user.username;
      }
    } catch (err) {
      App.showToast('Error', err.message || 'Failed to update profile.', 'error');
    }
  },

  async savePreferences() {
    const notationStyle = document.getElementById('pref-notation-style')?.value || 'gane_sarson';
    const snapGrid = document.getElementById('pref-snap-grid')?.checked;
    const autoSave = document.getElementById('pref-auto-save')?.checked;

    State.preferences.notation_style = notationStyle;
    State.preferences.snap_to_grid = snapGrid;
    State.preferences.auto_save = autoSave;

    try {
      await API.put('/api/auth/preferences', State.preferences);
      CanvasEngine.render();
      App.showToast('Preferences Saved', 'Canvas settings updated.', 'info');
    } catch (err) {
      console.error('Failed to save preferences:', err);
    }
  }
};
