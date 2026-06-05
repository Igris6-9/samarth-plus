import os
from dotenv import load_dotenv

# Local testing ke liye .env se variables load karta hai
# Production/Deployment par ye silently bypass ho jayega
load_dotenv()

def _get_db_uri():
    """
    Smart DB URI resolver:
    1. DATABASE_URL env var (Postgres/MySQL for production) — highest priority
    2. Vercel serverless: /tmp folder (only writable dir on Vercel)
    3. Local dev: instance/ folder (SQLite)
    """
    # Production database (Postgres etc.)
    if os.environ.get('DATABASE_URL'):
        url = os.environ.get('DATABASE_URL')
        # Fix for older Heroku/Render postgres URLs (postgres:// -> postgresql://)
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql://', 1)
        return url

    # Vercel serverless: only /tmp is writable
    if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
        db_path = '/tmp/samarth_v2.db'
        print(f">> [VERCEL MODE]: Using /tmp SQLite DB at {db_path}")
        return f'sqlite:///{db_path}'

    # Local development: use instance/ folder
    base_dir = os.path.abspath(os.path.dirname(__file__))
    instance_dir = os.path.join(base_dir, 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    return 'sqlite:///' + os.path.join(instance_dir, 'samarth_v2.db').replace('\\', '/')


class Config:
    """
    👑 DAKASH ENGINE - GUARDED MASTER CONFIGURATION
    Optimized for Vercel Serverless & Secure Cloud Deployment.
    """

    # 🔐 FLASK SECURITY (Neural Link Encryption)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'DAKASH_DIVINE_KEY_777_X')

    # 🧠 AI CORE: GEMINI API KEY (Guarded)
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    # 📂 DATABASE ARCHITECTURE — Smart resolver above handles all environments
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = _get_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 🚀 GLOBAL APP SETTINGS
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    PROJECT_NAME = "SAMARTH"
    VERSION = "2.5.0"

    # 📁 ASSET MANAGEMENT
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB Buffer

    # 🛡️ SESSION SECURITY (PC/Mobile Protection)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_SECURE', 'False') == 'True'
    PERMANENT_SESSION_LIFETIME = 604800  # 7 Days

    @staticmethod
    def init_app(app):
        """
        Engine Guard: Initialization checks before launch.
        """
        # Ensure 'uploads' folder exists (only on non-serverless)
        try:
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        except OSError:
            pass  # Vercel read-only filesystem - skip silently

        # 🛡️ API KEY GUARD
        if not Config.GEMINI_API_KEY:
            print(">> [CRITICAL ERROR]: GEMINI_API_KEY is not set in Environment Variables!")
        else:
            print(f">> [DAKASH-ENGINE]: Neural Link Established (Gemini V{Config.VERSION}). 🚀")

        print(f">> [SYSTEM]: Environment: {'Development' if Config.DEBUG else 'Production'}")
        print(f">> [DATABASE]: Using URI: {Config.SQLALCHEMY_DATABASE_URI[:40]}...")