import os
from dotenv import load_dotenv

# Local testing ke liye .env se variables load karta hai
# Production/Deployment par ye silently bypass ho jayega
load_dotenv()

class Config:
    """
    👑 DAKASH ENGINE - GUARDED MASTER CONFIGURATION
    Optimized for Groq AI Integration & Secure Cloud Deployment.
    """
    
    # 🔐 FLASK SECURITY (Neural Link Encryption)
    # .env mein SECRET_KEY nahi mila toh default use karega
    SECRET_KEY = os.environ.get('SECRET_KEY', 'DAKASH_DIVINE_KEY_777_X')
    
    # 🧠 AI CORE: GEMINI API KEY (Guarded)
    # Ye line sabse important hai deployment ke liye
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # 📂 DATABASE ARCHITECTURE
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Deployment par DATABASE_URL milta hai (Postgres), local par SQLite chalega
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'samarth_v2.db').replace('\\', '/')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 🚀 GLOBAL APP SETTINGS
    # Deployment par DEBUG hamesha False rehna chahiye (Security check)
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    PROJECT_NAME = "SAMARTH"
    VERSION = "2.5.0"
    
    # 📁 ASSET MANAGEMENT
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB Buffer

    # 🛡️ SESSION SECURITY (PC/Mobile Protection)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_SECURE', 'False') == 'True'
    PERMANENT_SESSION_LIFETIME = 604800 # 7 Days

    @staticmethod
    def init_app(app):
        """
        Engine Guard: Initialization checks before launch.
        """
        # Ensure 'instance' folder exists for SQLite
        instance_path = os.path.join(Config.BASE_DIR, 'instance')
        os.makedirs(instance_path, exist_ok=True)

        # Ensure 'uploads' folder exists
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

        # 🛡️ API KEY GUARD: Deployment par ye error log karega agar key missing ho
        if not Config.GEMINI_API_KEY:
            print(">> [CRITICAL ERROR]: GEMINI_API_KEY is not set in Environment Variables!")
        else:
            print(f">> [DAKASH-ENGINE]: Neural Link Established (Gemini V{Config.VERSION}). 🚀")

        print(f">> [SYSTEM]: Environment: {'Development' if Config.DEBUG else 'Production'}")