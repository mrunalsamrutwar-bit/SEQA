import os
import shutil

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Vercel / AWS Lambda serverless read-only filesystem support
is_serverless = bool(os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))
if is_serverless:
    db_path = '/tmp/dfd_architect.db'
    source_db = os.path.join(BASE_DIR, 'dfd_architect.db')
    if os.path.exists(source_db) and not os.path.exists(db_path):
        try:
            shutil.copy2(source_db, db_path)
        except Exception:
            pass
else:
    db_path = os.path.join(BASE_DIR, 'dfd_architect.db')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dfd-architect-ultra-secure-key-2026-xyz')
    
    # Support postgres:// URL format for Supabase / Neon / Render
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
        
    SQLALCHEMY_DATABASE_URI = db_url or f"sqlite:///{db_path}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
