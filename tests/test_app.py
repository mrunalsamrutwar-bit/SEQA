import unittest
import json
import os
import tempfile
from app import app
from database import db, User, Project, DfdLevel, Component, DataFlow
from utils.validation import validate_dfd
from utils.doc_generator import generate_project_documentation
from utils.pdf_export import generate_pdf_stream
from utils.docx_export import generate_docx_stream

class TestSEQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_fd, cls.db_path = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{cls.db_path}'
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.config['WTF_CSRF_ENABLED'] = False
        with app.app_context():
            db.drop_all()
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        os.close(cls.db_fd)
        try:
            os.unlink(cls.db_path)
        except OSError:
            pass

    def setUp(self):
        self.client = app.test_client()

    def test_01_public_pages(self):
        res = self.client.get('/login')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/register')
        self.assertEqual(res.status_code, 200)

    def test_02_auth_workflow(self):
        with app.app_context():
            # Register user
            reg_res = self.client.post('/api/auth/register', json={
                'username': 'tester',
                'email': 'tester@example.com',
                'password': 'password123',
                'full_name': 'Test Engineer'
            })
            self.assertEqual(reg_res.status_code, 200)
            data = json.loads(reg_res.data)
            self.assertTrue(data.get('success'))

            # Login
            login_res = self.client.post('/api/auth/login', json={
                'username': 'tester',
                'password': 'password123'
            })
            self.assertEqual(login_res.status_code, 200)

    def test_03_project_and_diagram_flow(self):
        with app.app_context():
            # Login as tester
            self.client.post('/api/auth/login', json={
                'username': 'tester',
                'password': 'password123'
            })

            # Create project
            proj_res = self.client.post('/api/projects', json={
                'name': 'Automated Hospital System',
                'description': 'Healthcare information and patient records management.',
                'system_name': 'Hospital System',
                'version': '1.0.0'
            })
            self.assertEqual(proj_res.status_code, 200)
            proj_data = json.loads(proj_res.data)
            project_id = proj_data['project']['id']

            # Get projects list
            list_res = self.client.get('/api/projects')
            self.assertEqual(list_res.status_code, 200)
            projects = json.loads(list_res.data).get('projects', [])
            self.assertTrue(any(p['id'] == project_id for p in projects))

    def test_04_validation_and_exports(self):
        with app.app_context():
            user = User.query.filter_by(username='tester').first()
            if not user:
                user = User(username='tester2', email='tester2@test.com', full_name='Tester 2')
                user.set_password('pass123')
                db.session.add(user)
                db.session.commit()

            project = Project(
                user_id=user.id,
                name='E-Commerce Platform',
                description='Online shopping and checkout system',
                system_name='E-Commerce Platform',
                version='1.0.0'
            )
            db.session.add(project)
            db.session.commit()

            level0 = DfdLevel(project_id=project.id, level_number=0, level_name='Context Diagram')
            db.session.add(level0)
            db.session.commit()

            c1 = Component(project_id=project.id, level_id=level0.id, component_identifier='E1', name='Customer', component_type='entity')
            c2 = Component(project_id=project.id, level_id=level0.id, component_identifier='0.0', name='Order Processing', component_type='process')
            db.session.add_all([c1, c2])
            db.session.commit()

            flow = DataFlow(project_id=project.id, level_id=level0.id, flow_identifier='F1', source_id=c1.id, destination_id=c2.id, flow_name='Order Request')
            db.session.add(flow)
            db.session.commit()

            # Validate DFD
            val_result = validate_dfd(project, level_id=level0.id)
            self.assertIn('is_valid', val_result)
            self.assertIn('summary', val_result)

            # Generate documentation
            doc = generate_project_documentation(project)
            self.assertIn('project_meta', doc)
            self.assertIn('markdown_text', doc)
            self.assertIn('entities', doc)
            self.assertIn('processes', doc)

            # PDF export
            pdf_stream = generate_pdf_stream(doc)
            self.assertTrue(len(pdf_stream.getvalue()) > 0)

            # DOCX export
            docx_stream = generate_docx_stream(doc)
            self.assertTrue(len(docx_stream.getvalue()) > 0)

if __name__ == '__main__':
    unittest.main()
