import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

def _get_db_uri():
    """
    Smart DB URI resolver:
    1. DATABASE_URL env var (Neon PostgreSQL) — highest priority
    2. Vercel serverless: /tmp folder SQLite
    3. Local dev: instance/ folder SQLite
    """
    if os.environ.get('DATABASE_URL'):
        url = os.environ.get('DATABASE_URL')
        # Fix for older postgres:// URLs -> postgresql://
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql://', 1)
        # Neon requires SSL — add if not already present
        if 'sslmode' not in url and 'neon.tech' in url:
            url += '?sslmode=require'
        print(f">> [DATABASE]: Using PostgreSQL (Neon) ✅")
        return url

    if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
        db_path = '/tmp/samarth_v2.db'
        print(f">> [VERCEL MODE]: Using /tmp SQLite DB at {db_path}")
        return f'sqlite:///{db_path}'

    base_dir = os.path.abspath(os.path.dirname(__file__))
    instance_dir = os.path.join(base_dir, 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    return 'sqlite:///' + os.path.join(instance_dir, 'samarth_v2.db').replace('\\', '/')



class Config:
    """
    👑 DAKASH ENGINE - GUARDED MASTER CONFIGURATION
    Optimized for Vercel Serverless & Secure Cloud Deployment.
    """

    # 🔐 FLASK SECURITY — MUST be set in Vercel env vars for session persistence!
    SECRET_KEY = os.environ.get('SECRET_KEY', 'DAKASH_DIVINE_KEY_777_STATIC_FIXED')

    # 🧠 AI CORE
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    # 📂 DATABASE
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = _get_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # ✅ Neon PostgreSQL + Vercel serverless optimized pool settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,       # Test connection before use
        "pool_recycle": 280,         # Recycle before Neon's 300s timeout
        "pool_size": 1,              # Serverless: keep pool tiny
        "max_overflow": 2,
        "connect_args": {
            "connect_timeout": 10,
            "sslmode": "require"     # Neon requires SSL
        } if os.environ.get('DATABASE_URL') and 'neon.tech' in os.environ.get('DATABASE_URL', '') else {}
    }


    # 🚀 APP SETTINGS
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    PROJECT_NAME = "SAMARTH"
    VERSION = "2.5.0"

    # 📁 ASSET MANAGEMENT
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # 🛡️ SESSION SETTINGS — Critical for Vercel login persistence
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'          # ✅ Fixes cross-request session loss
    SESSION_COOKIE_NAME = 'samarth_session'  # ✅ Fixed name prevents conflicts
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # ✅ timedelta not int

    # Only force Secure cookies on HTTPS (Vercel is HTTPS, local is HTTP)
    SESSION_COOKIE_SECURE = os.environ.get('VERCEL_ENV') is not None

    # ✅ REMEMBER ME COOKIE — stays even after browser close
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = os.environ.get('VERCEL_ENV') is not None
    REMEMBER_COOKIE_SAMESITE = 'Lax'

    @staticmethod
    def init_app(app):
        try:
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        except OSError:
            pass

        if not Config.GEMINI_API_KEY:
            print(">> [CRITICAL ERROR]: GEMINI_API_KEY is not set!")
        else:
            print(f">> [DAKASH-ENGINE]: Neural Link Established (Gemini V{Config.VERSION}). 🚀")

        print(f">> [SYSTEM]: Environment: {'Development' if Config.DEBUG else 'Production'}")
        print(f">> [DATABASE]: {Config.SQLALCHEMY_DATABASE_URI[:50]}...")
        print(f">> [SESSION]: Cookie Secure={Config.SESSION_COOKIE_SECURE}, SameSite={Config.SESSION_COOKIE_SAMESITE}")