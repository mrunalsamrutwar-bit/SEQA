# SEQA – DFD Architect & Documentation Studio

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat-square&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-black.svg?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57.svg?style=flat-square&logo=sqlite)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://github.com/mrunalsamrutwar-bit/SEQA/pulls)

**SEQA (DFD Architect & Documentation Studio)** is a professional, full-stack software engineering platform designed to visually model, validate, and automatically generate comprehensive engineering documentation for Data Flow Diagrams (DFDs) across multi-level hierarchies (Context Level 0, Level 1, and Level 2).

---

## 🌟 Key Highlights

- 🎨 **Interactive Visual Canvas**: Drag-and-drop elements with real-time SVG connection rendering, auto-layout algorithms, and smooth pan/zoom.
- 📐 **Hierarchical DFD Decomposition**: Seamlessly navigate between Level 0 (Context Diagram), Level 1 (Subsystems), and Level 2 (Detailed Processes).
- 🛡️ **Automated SEQA Rule Validator**: Real-time linting for structural flaws, including Black Holes, Miracles, Grey Holes, and illegal direct data store / entity connections.
- 📑 **One-Click Documentation Generator**: Instantly compile complete engineering specifications including Data Dictionaries, Process Specifications (P-Specs), and Traceability Matrices.
- 📦 **Zero-Dependency Native Exporters**: Built-in pure-Python vector PDF and Microsoft Word (`.docx`) document generation, plus high-res PNG, SVG, and JSON exports.
- 🗂️ **Pre-loaded Industry Templates**: E-Commerce, Hospital Management, Banking & ATM, Library Management, and Online Learning systems.

---

## 🚀 Features Overview

### 1. Visual Modeling & Diagramming
- **Supported Elements**: External Entities (Actors), Processes (Functions/Services), Data Stores (Databases/Files), and Directed Data Flows.
- **Dynamic Routing**: Automatic bezier and orthogonal vector paths with bidirectional flow support.
- **Smart Auto-Layout**: Integrated force-directed graph alignment to organize messy diagrams (`Alt + L`).
- **History Management**: Unlimited Undo (`Ctrl + Z`) and Redo (`Ctrl + Y`) capabilities.

### 2. Automated DFD Validation Engine
SEQA automatically analyzes your diagrams against standard Software Engineering & Quality Assurance principles:
- **Black Hole**: Processes with incoming data flows but zero outgoing flows.
- **Miracle (White Hole)**: Processes producing outputs with no incoming data.
- **Grey Hole**: Processes where output data cannot be generated from provided input data.
- **Illegal Connections**: Flagging direct Entity-to-Entity or DataStore-to-DataStore flows (which must pass through a process).
- **Orphaned Nodes**: Identifying disconnected components and unlabeled data flows.

### 3. Automated Documentation & Export Suite
- **System Overview & Objectives**: Executive summary and architectural scope.
- **Data Dictionary**: Comprehensive listing of all data flows, data structures, and types.
- **Process Specifications (P-Specs)**: Input/output tables, algorithm logic, and execution criteria.
- **Multi-Format Export**:
  - 📄 **Vector PDF**: Custom multi-page styled reports with cover page, tables, and callouts.
  - 📝 **Microsoft Word (`.docx`)**: Editable technical documentation package.
  - 🖼️ **Image & Vector (`PNG` / `SVG`)**: Crisp graphical exports for presentations.
  - 💾 **JSON**: Schema-compliant project backup and cross-environment import/export.

---

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| **Backend Framework** | Python 3.10+, Flask, Flask-SQLAlchemy, Werkzeug, Gunicorn |
| **Database** | SQLite (Default) / PostgreSQL-ready via SQLAlchemy ORM |
| **Frontend Architecture** | Modern Vanilla JavaScript (Modular Canvas Engine), HTML5, CSS3 (Glassmorphic Theme) |
| **Visuals & Charts** | Chart.js, FontAwesome 6, Google Fonts (Outfit, Inter, JetBrains Mono) |
| **Document Generation** | Custom zero-dependency pure-Python vector PDF & OpenXML DOCX builders |

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| <kbd>Ctrl</kbd> + <kbd>S</kbd> | Save diagram changes |
| <kbd>Ctrl</kbd> + <kbd>Z</kbd> | Undo last canvas action |
| <kbd>Ctrl</kbd> + <kbd>Y</kbd> | Redo canvas action |
| <kbd>Alt</kbd> + <kbd>L</kbd> | Trigger automatic canvas layout |
| <kbd>Ctrl</kbd> + <kbd>K</kbd> | Open Global Search across all projects and entities |
| <kbd>Delete</kbd> / <kbd>Backspace</kbd> | Delete selected node or connection |
| <kbd>Space</kbd> + <kbd>Drag</kbd> | Pan workspace canvas |

---

## 📦 Local Installation & Setup

### Prerequisites
- Python 3.10 or higher installed ([Download Python](https://www.python.org/downloads/))
- Git installed ([Download Git](https://git-scm.com/))

### 1. Clone the Repository
```bash
git clone https://github.com/mrunalsamrutwar-bit/SEQA.git
cd SEQA
```

### 2. Set Up a Virtual Environment
```bash
# On Windows
python -m venv venv
.\venv\Scripts\activate

# On macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch the Application
```bash
python app.py
```

### 5. Access the Web Application
Open your browser and navigate to:
```
http://127.0.0.1:5000
```
> Default demo account credentials are automatically seeded upon first launch, or you can register a new account on the login page.

---

## 🌐 Cloud Deployment Options

### Deploy to Render (Recommended - Free)
1. Push your code to your GitHub repository.
2. Sign in to [Render](https://render.com/).
3. Click **New +** → **Web Service** and connect your `SEQA` repository.
4. Set the build settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Click **Deploy Web Service**.

### Deploy to Railway
1. Go to [Railway](https://railway.app/).
2. Click **New Project** → **Deploy from GitHub Repo**.
3. Select `SEQA` — Railway will automatically detect the Python Flask application and start it using Gunicorn.

### Deploy to PythonAnywhere
1. Create a free account on [PythonAnywhere](https://www.pythonanywhere.com/).
2. Open a **Bash console** and clone the repository:
   ```bash
   git clone https://github.com/mrunalsamrutwar-bit/SEQA.git
   ```
3. Create a virtual environment and install dependencies:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 seqa-env
   pip install -r requirements.txt
   ```
4. In the **Web** tab, configure the WSGI configuration file pointing to `app.py`.

---

## 📁 Repository Structure

```
SEQA/
├── app.py                     # Main Flask Application & REST API Endpoints
├── config.py                  # Environment & App Configuration
├── database.py                # SQLAlchemy Models & Schema Definitions
├── requirements.txt           # Python Project Dependencies
├── seed_data.py               # Pre-configured Industry Templates & Initial Data
├── LICENSE                    # MIT License File
├── README.md                  # Project Documentation
├── static/                    # Frontend Static Assets
│   ├── css/
│   │   ├── canvas.css         # Canvas, Nodes, Grid, & Connector Styling
│   │   ├── components.css     # Modals, Forms, Buttons, & Toolbars
│   │   └── main.css           # Global Theme, Layout, & Typography
│   └── js/
│       ├── api.js             # Client API Service Layer
│       ├── app.js             # Main App Router & View Controller
│       ├── state.js           # Central Application State
│       ├── canvas/
│       │   ├── autolayout.js  # Force-Directed Auto-Layout Engine
│       │   ├── connections.js # SVG Bezier & Line Routing Logic
│       │   ├── engine.js      # Zoom, Pan, Drag, & Canvas Event Engine
│       │   ├── history.js     # Undo / Redo Command Stack
│       │   └── nodes.js       # Node Rendering & Interactive Handles
│       └── views/
│           ├── analytics.js   # Diagram Complexity & Metrics View
│           ├── dashboard.js   # Main Metrics & Recent Projects
│           ├── designer.js    # Visual DFD Designer Workspace
│           ├── docs.js        # Automated Documentation Viewer
│           ├── help.js        # Guide & Keyboard Shortcuts
│           ├── projects.js    # Project List & Management
│           ├── settings.js    # User & Workspace Settings
│           ├── templates.js   # Template Gallery & Instantiation
│           └── validation.js  # Validation Rule Checklist View
├── templates/                 # Jinja2 HTML Templates
│   ├── base.html              # Core App Shell & Global Modals
│   ├── index.html             # Single Page Application Container
│   ├── login.html             # User Authentication Login Page
│   └── register.html          # User Registration Page
└── utils/                     # Backend Utilities & Generators
    ├── doc_generator.py       # Documentation Synthesis Engine
    ├── docx_export.py         # Pure-Python Word (.docx) Exporter
    ├── pdf_export.py          # Pure-Python Vector PDF Exporter
    └── validation.py          # DFD Structural Rule Validator
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
1. Fork the Project (`https://github.com/mrunalsamrutwar-bit/SEQA/fork`)
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.