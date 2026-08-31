/**
 * DFD Architect — Help & Guide Controller
 */
const HelpView = {
  init() {
    // Setup help interactions and smooth scrolling if needed
  },

  scrollToSection(sectionId) {
    const el = document.getElementById(sectionId);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
};
