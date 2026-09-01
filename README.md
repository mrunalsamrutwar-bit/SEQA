# DFD Architect & Documentation Studio
An interactive, web-based Data Flow Diagram (DFD) design and automated software engineering documentation platform. Build, validate, and generate complete project documentation with Level 0 (Context), Level 1, and Level 2 diagrams.
---
## 🚀 Features
- **Interactive Canvas**: Drag-and-drop elements (Processes, Data Stores, External Entities, Data Flows) with real-time SVG connection rendering.
- **Hierarchical DFD Levels**: Full support for Level 0 (Context Diagram), Level 1, and Level 2 breakdowns.
- **Automated Validation**: Real-time rule checking for DFD best practices (isolated entities, missing labels, unbalanced data stores, etc.).
- **Automated Documentation Generator**:
  - System Overview & Objectives
  - Data Dictionary & Schema Definitions
  - Process Specifications (P-Specs)
  - Traceability Matrix & Activity Logs
- **Export Options**:
  - Native PDF Export (with embedded styling and tables)
  - Native Microsoft Word (.docx) Export
  - JSON / SVG / PNG Export
- **User Authentication & Session Management**: Secure user accounts with individual project workspaces.
- **Pre-built Project Templates**: E-Commerce, Hospital Management, Banking System, Library Management, and more.
--- 
## 🛠️ Tech Stack
---
- **Backend**: Python 3.10+, Flask, Flask-SQLAlchemy, Werkzeug, Gunicorn
- **Database**: SQLite (Default) / PostgreSQL-ready via SQLAlchemy
- **Frontend**: HTML5, CSS3 (Modern Glassmorphic Dark UI), Vanilla JavaScript (Modular Canvas Engine)
- **Document Generators**: Custom PDF and DOCX streams
---
## 📦 Local Installation & Setup
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mrunalsamrutwar-bit/SEQA.git
   cd SEQA
   ```
2. **Create & Activate Virtual Environment**:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Application**:
   ```bash
   python app.py
   ```
5. **Open in Browser**:
   Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000)
---
## 🌐 Free Cloud Deployment Guide
### Option 1: Render (Recommended - 100% Free)
1. Push this repository to your GitHub account.
2. Sign up / Log in to [Render](https://render.com/).
3. Click **New +** -> **Web Service**.
4. Connect your GitHub repository.
5. Configure:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
6. Click **Deploy Web Service**.

### Option 2: Railway
1. Go to [Railway](https://railway.app/).
2. Click **New Project** -> **Deploy from GitHub Repo**.
3. Select this repository.
4. Railway will automatically detect Flask and deploy it.

### Option 3: PythonAnywhere
1. Create a free account on [PythonAnywhere](https://www.pythonanywhere.com/).
2. Open a Bash console and clone your repo:
   ```bash
   git clone https://github.com/mrunalsamrutwar-bit/SEQA.git
   ```
3. Create a virtual environment and install `requirements.txt`.
4. Configure the Web Tab with Flask pointing to `app.py`.

---
## 📁 Project Structure

```
├── app.py                     # Main Flask Application & API Routes
├── config.py                  # Application Configuration
├── database.py                # Database Models & Schema
├── seed_data.py               # Sample Projects & Templates
├── requirements.txt           # Python Dependencies
├── utils/
│   ├── doc_generator.py       # Documentation Engine
│   ├── docx_export.py         # Word (.docx) Exporter
│   ├── pdf_export.py          # PDF Exporter
│   └── validation.py          # DFD Rule Validator
├── templates/                 # HTML Views (Jinja2)
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   └── register.html
└── static/                    # Frontend Assets
    ├── css/                   # Stylesheets
    └── js/                    # Canvas & DFD Logic
```
---
## 📄 License
This project is open source and available under the [MIT License](LICENSE).