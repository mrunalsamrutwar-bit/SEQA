import os
import json
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file, make_response
from flask_cors import CORS
from config import Config
from database import db, User, Project, DfdLevel, Component, DataFlow, ActivityLog
from seed_data import init_seed_data, TEMPLATES_DATA, instantiate_template
from utils.validation import validate_dfd
from utils.doc_generator import generate_project_documentation
from utils.docx_export import generate_docx_stream
from utils.pdf_export import generate_pdf_stream

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)

# Initialize database and seed templates / demo data
init_seed_data(app)


# -------------------------------------------------------------
# Authentication Helpers & Middleware
# -------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Check if demo mode or fallback to first user if session expired during quick use
            first_user = User.query.first()
            if first_user and app.config.get('AUTO_DEMO_LOGIN', False):
                session['user_id'] = first_user.id
                session['username'] = first_user.username
            else:
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({'error': 'Authentication required. Please login.'}), 401
                return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return db.session.get(User, user_id)


# -------------------------------------------------------------
# Frontend HTML Page Routes
# -------------------------------------------------------------
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    user = get_current_user()
    if not user:
        session.clear()
        return redirect(url_for('login_page'))
    return render_template('index.html', user=user.to_dict())

@app.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register')
def register_page():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('register.html')


# -------------------------------------------------------------
# Authentication REST API Endpoints
# -------------------------------------------------------------
@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip()
    password = data.get('password')
    full_name = (data.get('full_name') or '').strip()

    if not username or not email or not password:
        return jsonify({'error': 'Username, email, and password are required.'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': f"Username '{username}' is already taken."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': f"Email '{email}' is already registered."}), 400

    new_user = User(
        username=username,
        email=email,
        full_name=full_name or username,
        role='Software Architect'
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    # Log in immediately
    session['user_id'] = new_user.id
    session['username'] = new_user.username
    session.permanent = True

    return jsonify({'success': True, 'message': 'Account registered successfully.', 'user': new_user.to_dict()})


@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    ident = (data.get('identifier') or data.get('username') or data.get('email') or '').strip()
    password = data.get('password') or ''
    remember_me = data.get('remember_me', False)

    if not ident or not password:
        return jsonify({'error': 'Username/email and password are required.'}), 400

    user = User.query.filter((User.username == ident) | (User.email == ident)).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username/email or password.'}), 401

    session['user_id'] = user.id
    session['username'] = user.username
    if remember_me:
        session.permanent = True

    return jsonify({'success': True, 'message': f'Welcome back, {user.full_name or user.username}!', 'user': user.to_dict()})


@app.route('/api/auth/demo-login', methods=['POST'])
def api_demo_login():
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        # Create admin user if missing
        admin_user = User(
            username='admin',
            email='admin@dfdarchitect.io',
            full_name='Mrunal (Lead Systems Architect)',
            role='Principal Software Architect'
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()

    session['user_id'] = admin_user.id
    session['username'] = admin_user.username
    session.permanent = True

    return jsonify({'success': True, 'message': 'Logged in as Demo Administrator.', 'user': admin_user.to_dict()})


@app.route('/api/auth/me', methods=['GET'])
def api_me():
    user = get_current_user()
    if not user:
        return jsonify({'authenticated': False}), 401
    return jsonify({'authenticated': True, 'user': user.to_dict()})


@app.route('/api/auth/logout', methods=['POST', 'GET'])
def api_logout():
    session.clear()
    if request.is_json:
        return jsonify({'success': True, 'message': 'Logged out successfully.'})
    return redirect(url_for('login_page'))


@app.route('/api/auth/profile', methods=['PUT'])
@login_required
def api_update_profile():
    user = get_current_user()
    data = request.get_json() or {}

    if 'full_name' in data:
        user.full_name = data['full_name'].strip()
    if 'role' in data:
        user.role = data['role'].strip()
    if 'email' in data:
        new_email = data['email'].strip()
        existing = User.query.filter(User.email == new_email, User.id != user.id).first()
        if existing:
            return jsonify({'error': 'Email is already in use by another account.'}), 400
        user.email = new_email

    if data.get('new_password'):
        user.set_password(data['new_password'])

    db.session.commit()
    return jsonify({'success': True, 'message': 'Profile updated successfully.', 'user': user.to_dict()})


@app.route('/api/auth/preferences', methods=['PUT'])
@login_required
def api_update_preferences():
    user = get_current_user()
    data = request.get_json() or {}
    current_prefs = user.get_preferences()
    current_prefs.update(data)
    user.set_preferences(current_prefs)
    db.session.commit()
    return jsonify({'success': True, 'preferences': current_prefs})


# -------------------------------------------------------------
# Projects Management REST APIs
# -------------------------------------------------------------
@app.route('/api/projects', methods=['GET'])
@login_required
def api_get_projects():
    user = get_current_user()
    query = Project.query.filter((Project.user_id == user.id) | (Project.is_demo == True))

    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(Project.name.ilike(f'%{search}%') | Project.description.ilike(f'%{search}%') | Project.system_name.ilike(f'%{search}%'))

    dfd_level = request.args.get('level', '').strip()
    if dfd_level and dfd_level != 'all':
        query = query.filter(Project.dfd_level.ilike(f'%{dfd_level}%'))

    sort_by = request.args.get('sort', 'updated_at')
    if sort_by == 'name':
        query = query.order_by(Project.name.asc())
    elif sort_by == 'created_at':
        query = query.order_by(Project.created_at.desc())
    else:
        query = query.order_by(Project.updated_at.desc())

    projects = query.all()
    return jsonify({'projects': [p.to_dict() for p in projects]})


@app.route('/api/projects', methods=['POST'])
@login_required
def api_create_project():
    user = get_current_user()
    data = request.get_json() or {}

    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'Project name is required.'}), 400

    system_name = (data.get('system_name') or name).strip()
    dfd_level = data.get('dfd_level', 'Context Diagram / Level 0')
    description = (data.get('description') or '').strip()
    author = (data.get('author') or user.full_name or user.username).strip()
    version = (data.get('version') or '1.0.0').strip()
    tags = (data.get('tags') or 'DFD, Architecture').strip()

    project = Project(
        user_id=user.id,
        name=name,
        description=description,
        system_name=system_name,
        dfd_level=dfd_level,
        author=author,
        version=version,
        tags=tags,
        status='In Progress'
    )
    db.session.add(project)
    db.session.flush()

    # Create Initial Level 0
    lvl0 = DfdLevel(
        project_id=project.id,
        level_number=0,
        level_name='Context Diagram (Level 0)',
        parent_process_id=None,
        notes='System Boundary and External Entities'
    )
    db.session.add(lvl0)
    db.session.flush()

    # Create Initial Central Process if Context Diagram
    central_proc = Component(
        project_id=project.id,
        level_id=lvl0.id,
        component_type='process',
        component_identifier='0.0',
        name=system_name,
        description=f'Main system process for {system_name}',
        pos_x=400.0,
        pos_y=200.0,
        width=150.0,
        height=90.0,
        metadata_json='{}'
    )
    db.session.add(central_proc)

    # Activity log
    log = ActivityLog(
        project_id=project.id,
        user_id=user.id,
        action='Created Project',
        details=f"Created new DFD project '{name}'."
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({'success': True, 'project': project.to_dict(include_details=True)})


@app.route('/api/projects/<int:project_id>', methods=['GET'])
@login_required
def api_get_project(project_id):
    user = get_current_user()
    project = Project.query.filter(Project.id == project_id, (Project.user_id == user.id) | (Project.is_demo == True)).first()
    if not project:
        return jsonify({'error': 'Project not found.'}), 404

    return jsonify({'project': project.to_dict(include_details=True)})


@app.route('/api/projects/<int:project_id>', methods=['PUT'])
@login_required
def api_update_project(project_id):
    user = get_current_user()
    project = Project.query.filter_by(id=project_id, user_id=user.id).first()
    if not project:
        return jsonify({'error': 'Project not found or read-only.'}), 404

    data = request.get_json() or {}
    if 'name' in data and data['name'].strip():
        project.name = data['name'].strip()
    if 'system_name' in data:
        project.system_name = data['system_name'].strip()
    if 'description' in data:
        project.description = data['description'].strip()
    if 'dfd_level' in data:
        project.dfd_level = data['dfd_level'].strip()
    if 'author' in data:
        project.author = data['author'].strip()
    if 'version' in data:
        project.version = data['version'].strip()
    if 'tags' in data:
        project.tags = data['tags'] if isinstance(data['tags'], str) else ', '.join(data['tags'])
    if 'status' in data:
        project.status = data['status']

    project.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'success': True, 'project': project.to_dict()})


@app.route('/api/projects/<int:project_id>/duplicate', methods=['POST'])
@login_required
def api_duplicate_project(project_id):
    user = get_current_user()
    src_project = Project.query.filter(Project.id == project_id, (Project.user_id == user.id) | (Project.is_demo == True)).first()
    if not src_project:
        return jsonify({'error': 'Project not found.'}), 404

    # Create new cloned project
    new_project = Project(
        user_id=user.id,
        name=f"Copy of {src_project.name}",
        description=src_project.description,
        system_name=src_project.system_name,
        dfd_level=src_project.dfd_level,
        author=user.full_name or user.username,
        version=src_project.version,
        tags=src_project.tags,
        status='In Progress',
        is_demo=False
    )
    db.session.add(new_project)
    db.session.flush()

    comp_id_map = {} # old_comp_id -> new_comp_id

    # Clone levels
    for lvl in src_project.levels:
        new_lvl = DfdLevel(
            project_id=new_project.id,
            level_number=lvl.level_number,
            level_name=lvl.level_name,
            parent_process_id=lvl.parent_process_id,
            notes=lvl.notes
        )
        db.session.add(new_lvl)
        db.session.flush()

        # Clone components in this level
        level_comps = [c for c in src_project.components if c.level_id == lvl.id]
        for c in level_comps:
            new_c = Component(
                project_id=new_project.id,
                level_id=new_lvl.id,
                component_type=c.component_type,
                component_identifier=c.component_identifier,
                name=c.name,
                description=c.description,
                pos_x=c.pos_x,
                pos_y=c.pos_y,
                width=c.width,
                height=c.height,
                metadata_json=c.metadata_json
            )
            db.session.add(new_c)
            db.session.flush()
            comp_id_map[c.id] = new_c.id

        # Clone data flows in this level
        level_flows = [f for f in src_project.data_flows if f.level_id == lvl.id]
        for f in level_flows:
            new_src_id = comp_id_map.get(f.source_id)
            new_dst_id = comp_id_map.get(f.destination_id)
            if new_src_id and new_dst_id:
                new_flow = DataFlow(
                    project_id=new_project.id,
                    level_id=new_lvl.id,
                    flow_identifier=f.flow_identifier,
                    flow_name=f.flow_name,
                    description=f.description,
                    source_id=new_src_id,
                    destination_id=new_dst_id,
                    data_type=f.data_type,
                    is_bidirectional=f.is_bidirectional
                )
                db.session.add(new_flow)

    log = ActivityLog(
        project_id=new_project.id,
        user_id=user.id,
        action='Duplicated Project',
        details=f"Cloned from '{src_project.name}'."
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Project duplicated successfully.', 'project': new_project.to_dict()})


@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
@login_required
def api_delete_project(project_id):
    user = get_current_user()
    project = Project.query.filter_by(id=project_id, user_id=user.id).first()
    if not project:
        return jsonify({'error': 'Project not found.'}), 404

    db.session.delete(project)
    db.session.commit()
    return jsonify({'success': True, 'message': f"Project '{project.name}' deleted successfully."})


# -------------------------------------------------------------
# DFD Levels REST APIs
# -------------------------------------------------------------
@app.route('/api/projects/<int:project_id>/levels', methods=['GET'])
@login_required
def api_get_levels(project_id):
    project = Project.query.get_or_404(project_id)
    return jsonify({'levels': [lvl.to_dict() for lvl in project.levels]})


@app.route('/api/projects/<int:project_id>/levels', methods=['POST'])
@login_required
def api_create_level(project_id):
    project = Project.query.get_or_404(project_id)
    data = request.get_json() or {}

    level_num = int(data.get('level_number', len(project.levels)))
    level_name = data.get('level_name', f"Level {level_num}")
    parent_process_id = data.get('parent_process_id') # e.g., '2.0'
    notes = data.get('notes', '')

    new_level = DfdLevel(
        project_id=project.id,
        level_number=level_num,
        level_name=level_name,
        parent_process_id=parent_process_id,
        notes=notes
    )
    db.session.add(new_level)
    db.session.flush()

    # If decomposing a parent process (e.g. 2.0), generate initial child process skeletons (2.1, 2.2)
    if parent_process_id:
        p1 = Component(
            project_id=project.id,
            level_id=new_level.id,
            component_type='process',
            component_identifier=f"{parent_process_id}.1" if not parent_process_id.endswith('.0') else f"{parent_process_id[:-2]}.1",
            name=f"Sub-process 1 for {parent_process_id}",
            description=f"Decomposed sub-process for {parent_process_id}",
            pos_x=300.0,
            pos_y=160.0,
            width=150.0,
            height=90.0
        )
        p2 = Component(
            project_id=project.id,
            level_id=new_level.id,
            component_type='process',
            component_identifier=f"{parent_process_id}.2" if not parent_process_id.endswith('.0') else f"{parent_process_id[:-2]}.2",
            name=f"Sub-process 2 for {parent_process_id}",
            description=f"Decomposed sub-process for {parent_process_id}",
            pos_x=560.0,
            pos_y=160.0,
            width=150.0,
            height=90.0
        )
        db.session.add_all([p1, p2])

    project.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'success': True, 'level': new_level.to_dict()})


@app.route('/api/projects/<int:project_id>/levels/<int:level_id>', methods=['DELETE'])
@login_required
def api_delete_level(project_id, level_id):
    level = DfdLevel.query.filter_by(id=level_id, project_id=project_id).first_or_404()
    if level.level_number == 0:
        return jsonify({'error': 'Cannot delete Level 0 Context Diagram.'}), 400

    db.session.delete(level)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Level deleted.'})


# -------------------------------------------------------------
# Components CRUD REST APIs
# -------------------------------------------------------------
@app.route('/api/projects/<int:project_id>/components', methods=['POST'])
@login_required
def api_create_component(project_id):
    project = Project.query.get_or_404(project_id)
    data = request.get_json() or {}

    comp_type = data.get('component_type', 'process') # 'entity', 'process', 'datastore'
    name = (data.get('name') or f"New {comp_type.capitalize()}").strip()
    identifier = data.get('component_identifier')
    level_id = data.get('level_id')

    if not level_id and project.levels:
        level_id = project.levels[0].id

    # Auto-generate identifier if not supplied
    if not identifier:
        existing = [c for c in project.components if c.level_id == level_id and c.component_type == comp_type]
        if comp_type == 'process':
            identifier = f"{len(existing) + 1}.0"
        elif comp_type == 'entity':
            identifier = f"E{len(existing) + 1}"
        elif comp_type == 'datastore':
            identifier = f"D{len(existing) + 1}"
        else:
            identifier = f"C{len(existing) + 1}"

    comp = Component(
        project_id=project.id,
        level_id=level_id,
        component_type=comp_type,
        component_identifier=identifier,
        name=name,
        description=data.get('description', ''),
        pos_x=float(data.get('pos_x', 200.0)),
        pos_y=float(data.get('pos_y', 200.0)),
        width=float(data.get('width', 160.0 if comp_type != 'process' else 140.0)),
        height=float(data.get('height', 80.0 if comp_type != 'process' else 90.0)),
        metadata_json=json.dumps(data.get('metadata', {}))
    )
    db.session.add(comp)
    project.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'success': True, 'component': comp.to_dict()})


@app.route('/api/projects/<int:project_id>/components/<int:comp_id>', methods=['PUT'])
@login_required
def api_update_component(project_id, comp_id):
    comp = Component.query.filter_by(id=comp_id, project_id=project_id).first_or_404()
    data = request.get_json() or {}

    if 'name' in data:
        comp.name = data['name'].strip()
    if 'component_identifier' in data:
        comp.component_identifier = data['component_identifier'].strip()
    if 'description' in data:
        comp.description = data['description'].strip()
    if 'pos_x' in data:
        comp.pos_x = float(data['pos_x'])
    if 'pos_y' in data:
        comp.pos_y = float(data['pos_y'])
    if 'width' in data:
        comp.width = float(data['width'])
    if 'height' in data:
        comp.height = float(data['height'])
    if 'metadata' in data:
        cur_meta = comp.get_metadata()
        cur_meta.update(data['metadata'])
        comp.set_metadata(cur_meta)

    comp.project.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'success': True, 'component': comp.to_dict()})


@app.route('/api/projects/<int:project_id>/components/<int:comp_id>', methods=['DELETE'])
@login_required
def api_delete_component(project_id, comp_id):
    comp = Component.query.filter_by(id=comp_id, project_id=project_id).first_or_404()
    project = comp.project
    db.session.delete(comp)
    project.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'message': 'Component and attached flows deleted.'})


# -------------------------------------------------------------
# Data Flows CRUD REST APIs
# -------------------------------------------------------------
@app.route('/api/projects/<int:project_id>/flows', methods=['POST'])
@login_required
def api_create_flow(project_id):
    project = Project.query.get_or_404(project_id)
    data = request.get_json() or {}

    source_id = data.get('source_id')
    destination_id = data.get('destination_id')
    flow_name = (data.get('flow_name') or 'Data Packet').strip()
    level_id = data.get('level_id')

    if not source_id or not destination_id:
        return jsonify({'error': 'Source and Destination components are required.'}), 400

    if not level_id and project.levels:
        level_id = project.levels[0].id

    # Auto-generate flow identifier
    existing_flows = [f for f in project.data_flows if f.level_id == level_id]
    identifier = data.get('flow_identifier') or f"F{len(existing_flows) + 1}"

    flow = DataFlow(
        project_id=project.id,
        level_id=level_id,
        flow_identifier=identifier,
        flow_name=flow_name,
        description=data.get('description', ''),
        source_id=source_id,
        destination_id=destination_id,
        data_type=data.get('data_type', 'JSON / Structured Payload'),
        is_bidirectional=data.get('is_bidirectional', False)
    )
    db.session.add(flow)
    project.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'success': True, 'flow': flow.to_dict()})


@app.route('/api/projects/<int:project_id>/flows/<int:flow_id>', methods=['PUT'])
@login_required
def api_update_flow(project_id, flow_id):
    flow = DataFlow.query.filter_by(id=flow_id, project_id=project_id).first_or_404()
    data = request.get_json() or {}

    if 'flow_name' in data:
        flow.flow_name = data['flow_name'].strip()
    if 'flow_identifier' in data:
        flow.flow_identifier = data['flow_identifier'].strip()
    if 'description' in data:
        flow.description = data['description'].strip()
    if 'data_type' in data:
        flow.data_type = data['data_type'].strip()
    if 'is_bidirectional' in data:
        flow.is_bidirectional = bool(data['is_bidirectional'])
    if 'source_id' in data:
        flow.source_id = int(data['source_id'])
    if 'destination_id' in data:
        flow.destination_id = int(data['destination_id'])

    flow.project.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'success': True, 'flow': flow.to_dict()})


@app.route('/api/projects/<int:project_id>/flows/<int:flow_id>', methods=['DELETE'])
@login_required
def api_delete_flow(project_id, flow_id):
    flow = DataFlow.query.filter_by(id=flow_id, project_id=project_id).first_or_404()
    project = flow.project
    db.session.delete(flow)
    project.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'message': 'Data flow deleted.'})


# -------------------------------------------------------------
# Batch Synchronization (Auto-Save Canvas Positions & State)
# -------------------------------------------------------------
@app.route('/api/projects/<int:project_id>/batch-sync', methods=['POST'])
@login_required
def api_batch_sync(project_id):
    project = Project.query.get_or_404(project_id)
    data = request.get_json() or {}

    # Update components positions
    positions = data.get('positions', {}) # comp_id -> {x, y}
    for comp_id_str, pos in positions.items():
        try:
            cid = int(comp_id_str)
            comp = Component.query.filter_by(id=cid, project_id=project.id).first()
            if comp:
                comp.pos_x = float(pos.get('x', comp.pos_x))
                comp.pos_y = float(pos.get('y', comp.pos_y))
        except Exception:
            continue

    project.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'message': 'Saved successfully.'})


# -------------------------------------------------------------
# DFD Validation API
# -------------------------------------------------------------
@app.route('/api/projects/<int:project_id>/validate', methods=['GET'])
@login_required
def api_validate_project(project_id):
    project = Project.query.get_or_404(project_id)
    level_id = request.args.get('level_id', type=int)
    result = validate_dfd(project, level_id)
    return jsonify(result)


# -------------------------------------------------------------
# Automatic Documentation API
# -------------------------------------------------------------
@app.route('/api/projects/<int:project_id>/documentation', methods=['GET'])
@login_required
def api_get_documentation(project_id):
    project = Project.query.get_or_404(project_id)
    level_id = request.args.get('level_id', type=int)
    doc_data = generate_project_documentation(project, level_id)
    return jsonify(doc_data)


# -------------------------------------------------------------
# Export REST APIs (JSON, DOCX, PDF)
# -------------------------------------------------------------
@app.route('/api/projects/<int:project_id>/export/json', methods=['GET'])
@login_required
def api_export_json(project_id):
    project = Project.query.get_or_404(project_id)
    data = project.to_dict(include_details=True)
    doc = generate_project_documentation(project)
    data['documentation'] = doc

    response = make_response(json.dumps(data, indent=2))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = f'attachment; filename="{project.name.replace(" ", "_")}_DFD.json"'
    return response


@app.route('/api/projects/<int:project_id>/export/docx', methods=['GET'])
@login_required
def api_export_docx(project_id):
    project = Project.query.get_or_404(project_id)
    level_id = request.args.get('level_id', type=int)
    doc_data = generate_project_documentation(project, level_id)
    
    stream = generate_docx_stream(doc_data)
    filename = f"{project.name.replace(' ', '_')}_DFD_Specification.docx"
    return send_file(
        stream,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )


@app.route('/api/projects/<int:project_id>/export/pdf', methods=['GET'])
@login_required
def api_export_pdf(project_id):
    project = Project.query.get_or_404(project_id)
    level_id = request.args.get('level_id', type=int)
    doc_data = generate_project_documentation(project, level_id)

    stream = generate_pdf_stream(doc_data)
    filename = f"{project.name.replace(' ', '_')}_DFD_Documentation.pdf"
    return send_file(
        stream,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )


# -------------------------------------------------------------
# Template Library APIs
# -------------------------------------------------------------
@app.route('/api/templates', methods=['GET'])
@login_required
def api_get_templates():
    return jsonify({'templates': TEMPLATES_DATA})


@app.route('/api/templates/<template_id>/instantiate', methods=['POST'])
@login_required
def api_instantiate_template(template_id):
    user = get_current_user()
    data = request.get_json() or {}
    project_name = data.get('name')

    template = next((t for t in TEMPLATES_DATA if t['id'] == template_id), None)
    if not template:
        return jsonify({'error': 'Template not found.'}), 404

    project = instantiate_template(template, user.id, project_name=project_name, is_demo=False)
    return jsonify({'success': True, 'project': project.to_dict(include_details=True)})


# -------------------------------------------------------------
# Global Search API
# -------------------------------------------------------------
@app.route('/api/search', methods=['GET'])
@login_required
def api_global_search():
    user = get_current_user()
    q = (request.args.get('q') or '').strip()
    if not q:
        return jsonify({'results': []})

    results = []
    # 1. Search projects
    projects = Project.query.filter(
        (Project.user_id == user.id) | (Project.is_demo == True),
        Project.name.ilike(f'%{q}%') | Project.description.ilike(f'%{q}%')
    ).limit(5).all()

    for p in projects:
        results.append({
            'type': 'project',
            'title': p.name,
            'subtitle': f"Project • {p.dfd_level}",
            'project_id': p.id,
            'level_id': None,
            'icon': 'folder'
        })

    # 2. Search components
    user_project_ids = [p.id for p in Project.query.filter((Project.user_id == user.id) | (Project.is_demo == True)).all()]
    if user_project_ids:
        comps = Component.query.filter(
            Component.project_id.in_(user_project_ids),
            Component.name.ilike(f'%{q}%') | Component.component_identifier.ilike(f'%{q}%') | Component.description.ilike(f'%{q}%')
        ).limit(10).all()

        for c in comps:
            results.append({
                'type': c.component_type,
                'title': f"{c.component_identifier} {c.name}",
                'subtitle': f"{c.component_type.capitalize()} in '{c.project.name}'",
                'project_id': c.project_id,
                'level_id': c.level_id,
                'component_id': c.id,
                'icon': 'cpu' if c.component_type == 'process' else ('database' if c.component_type == 'datastore' else 'users')
            })

        # 3. Search data flows
        flows = DataFlow.query.filter(
            DataFlow.project_id.in_(user_project_ids),
            DataFlow.flow_name.ilike(f'%{q}%') | DataFlow.flow_identifier.ilike(f'%{q}%')
        ).limit(8).all()

        for f in flows:
            results.append({
                'type': 'flow',
                'title': f"{f.flow_identifier} {f.flow_name}",
                'subtitle': f"Data Flow in '{f.project.name}' ({f.source_component.name if f.source_component else '?'} → {f.dest_component.name if f.dest_component else '?'})",
                'project_id': f.project_id,
                'level_id': f.level_id,
                'flow_id': f.id,
                'icon': 'arrow-right'
            })

    return jsonify({'results': results})


# -------------------------------------------------------------
# Analytics Dashboard API
# -------------------------------------------------------------
@app.route('/api/analytics', methods=['GET'])
@login_required
def api_get_analytics():
    user = get_current_user()
    projects = Project.query.filter((Project.user_id == user.id) | (Project.is_demo == True)).all()
    project_ids = [p.id for p in projects]

    total_projects = len(projects)
    total_levels = DfdLevel.query.filter(DfdLevel.project_id.in_(project_ids)).count() if project_ids else 0
    total_components = Component.query.filter(Component.project_id.in_(project_ids)).count() if project_ids else 0
    total_flows = DataFlow.query.filter(DataFlow.project_id.in_(project_ids)).count() if project_ids else 0

    processes_count = Component.query.filter(Component.project_id.in_(project_ids), Component.component_type == 'process').count() if project_ids else 0
    datastores_count = Component.query.filter(Component.project_id.in_(project_ids), Component.component_type == 'datastore').count() if project_ids else 0
    entities_count = Component.query.filter(Component.project_id.in_(project_ids), Component.component_type == 'entity').count() if project_ids else 0

    recent_activities = ActivityLog.query.filter(ActivityLog.user_id == user.id).order_by(ActivityLog.timestamp.desc()).limit(8).all()

    return jsonify({
        'stats': {
            'total_projects': total_projects,
            'total_levels': total_levels,
            'total_components': total_components,
            'total_flows': total_flows,
            'processes_count': processes_count,
            'datastores_count': datastores_count,
            'entities_count': entities_count
        },
        'component_distribution': [
            {'type': 'Processes', 'count': processes_count, 'color': '#2563EB'},
            {'type': 'Data Stores', 'count': datastores_count, 'color': '#059669'},
            {'type': 'External Entities', 'count': entities_count, 'color': '#D97706'},
            {'type': 'Data Flows', 'count': total_flows, 'color': '#7C3AED'}
        ],
        'recent_activities': [a.to_dict() for a in recent_activities]
    })


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
