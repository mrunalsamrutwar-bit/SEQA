import os
import sys

# Add project root directory to Python module search path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class VercelPathFix:
    """
    Ensures Flask receives the exact client requested route path (e.g. /login, /register, /api/projects)
    when running inside Vercel Serverless Functions.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        if path.startswith('/api/index') or path == '/api' or path == '':
            real_path = environ.get('HTTP_X_MATCHED_PATH') or environ.get('HTTP_X_FORWARDED_PATH')
            if real_path and not real_path.startswith('/api/index'):
                environ['PATH_INFO'] = real_path
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathFix(app.wsgi_app)
