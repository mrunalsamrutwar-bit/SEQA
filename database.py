import json
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def utc_now():
    return datetime.now(timezone.utc)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(50), default='Software Architect')
    preferences_json = db.Column(db.Text, default='{}')
    created_at = db.Column(db.DateTime, default=utc_now)

    projects = db.relationship('Project', backref='owner', lazy=True, cascade='all, delete-orphan')
    activities = db.relationship('ActivityLog', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_preferences(self):
        try:
            return json.loads(self.preferences_json or '{}')
        except Exception:
            return {}

    def set_preferences(self, prefs_dict):
        self.preferences_json = json.dumps(prefs_dict)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name or self.username,
            'role': self.role,
            'preferences': self.get_preferences(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, default='')
    system_name = db.Column(db.String(200), default='System')
    dfd_level = db.Column(db.String(50), default='Level 0 (Context)')
    author = db.Column(db.String(120), default='Software Architect')
    version = db.Column(db.String(50), default='1.0.0')
    tags = db.Column(db.String(255), default='DFD, System Architecture')
    status = db.Column(db.String(50), default='In Progress')
    is_demo = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    levels = db.relationship('DfdLevel', backref='project', lazy=True, cascade='all, delete-orphan', order_by='DfdLevel.level_number')
    components = db.relationship('Component', backref='project', lazy=True, cascade='all, delete-orphan')
    data_flows = db.relationship('DataFlow', backref='project', lazy=True, cascade='all, delete-orphan')
    activities = db.relationship('ActivityLog', backref='project', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_details=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'system_name': self.system_name,
            'dfd_level': self.dfd_level,
            'author': self.author,
            'version': self.version,
            'tags': [t.strip() for t in (self.tags or '').split(',') if t.strip()],
            'status': self.status,
            'is_demo': self.is_demo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'component_counts': {
                'total': len(self.components),
                'processes': len([c for c in self.components if c.component_type == 'process']),
                'datastores': len([c for c in self.components if c.component_type == 'datastore']),
                'entities': len([c for c in self.components if c.component_type == 'entity']),
                'flows': len(self.data_flows)
            },
            'levels_count': len(self.levels)
        }

        if include_details:
            data['levels'] = [lvl.to_dict() for lvl in self.levels]
            data['components'] = [comp.to_dict() for comp in self.components]
            data['data_flows'] = [flow.to_dict() for flow in self.data_flows]

        return data


class DfdLevel(db.Model):
    __tablename__ = 'dfd_levels'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    level_number = db.Column(db.Integer, default=0)  # 0, 1, 2, 3
    level_name = db.Column(db.String(100), default='Context Diagram (Level 0)')
    parent_process_id = db.Column(db.String(50), nullable=True) # e.g., '1.0' or '2.0'
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=utc_now)

    components = db.relationship('Component', backref='level', lazy=True, cascade='all, delete-orphan')
    data_flows = db.relationship('DataFlow', backref='level', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'level_number': self.level_number,
            'level_name': self.level_name,
            'parent_process_id': self.parent_process_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'components_count': len(self.components),
            'flows_count': len(self.data_flows)
        }


class Component(db.Model):
    __tablename__ = 'components'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('dfd_levels.id', ondelete='CASCADE'), nullable=True)
    
    # Types: 'entity', 'process', 'datastore'
    component_type = db.Column(db.String(50), nullable=False)
    component_identifier = db.Column(db.String(50), nullable=False) # e.g. '1.0', 'E1', 'D1'
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    
    pos_x = db.Column(db.Float, default=100.0)
    pos_y = db.Column(db.Float, default=100.0)
    width = db.Column(db.Float, default=160.0)
    height = db.Column(db.Float, default=80.0)
    
    # Metadata for custom properties like entity_type, storage_type, fields, etc.
    metadata_json = db.Column(db.Text, default='{}')
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    def get_metadata(self):
        try:
            return json.loads(self.metadata_json or '{}')
        except Exception:
            return {}

    def set_metadata(self, meta_dict):
        self.metadata_json = json.dumps(meta_dict)

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'level_id': self.level_id,
            'component_type': self.component_type,
            'component_identifier': self.component_identifier,
            'name': self.name,
            'description': self.description,
            'pos_x': self.pos_x,
            'pos_y': self.pos_y,
            'width': self.width,
            'height': self.height,
            'metadata': self.get_metadata(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DataFlow(db.Model):
    __tablename__ = 'data_flows'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('dfd_levels.id', ondelete='CASCADE'), nullable=True)
    
    flow_identifier = db.Column(db.String(50), default='F1') # e.g. 'F1', 'F2'
    flow_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    
    # Foreign keys pointing to component IDs
    source_id = db.Column(db.Integer, db.ForeignKey('components.id', ondelete='CASCADE'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('components.id', ondelete='CASCADE'), nullable=False)
    
    data_type = db.Column(db.String(100), default='JSON / Structured Payload')
    is_bidirectional = db.Column(db.Boolean, default=False)
    
    source_component = db.relationship('Component', foreign_keys=[source_id], backref='outgoing_flows')
    dest_component = db.relationship('Component', foreign_keys=[destination_id], backref='incoming_flows')

    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'level_id': self.level_id,
            'flow_identifier': self.flow_identifier,
            'flow_name': self.flow_name,
            'description': self.description,
            'source_id': self.source_id,
            'destination_id': self.destination_id,
            'source_name': self.source_component.name if self.source_component else 'Unknown',
            'source_identifier': self.source_component.component_identifier if self.source_component else '?',
            'source_type': self.source_component.component_type if self.source_component else 'unknown',
            'destination_name': self.dest_component.name if self.dest_component else 'Unknown',
            'destination_identifier': self.dest_component.component_identifier if self.dest_component else '?',
            'destination_type': self.dest_component.component_type if self.dest_component else 'unknown',
            'data_type': self.data_type,
            'is_bidirectional': self.is_bidirectional,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, default='')
    timestamp = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'action': self.action,
            'details': self.details,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else ''
        }
