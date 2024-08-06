from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Allow requests from specific origins
    CORS(app, origins=[
        "https://chess-main.vercel.app",
        "https://chessdemo-alpha.vercel.app",
        "https://chessdemo-l3qrzgj5q-ramyas-projects-4cb2348e.vercel.app",
        "https://chess-main-git-main-ramyas-projects-4cb2348e.vercel.app",
        "http://localhost:3000"
    ])

    from app.database import init_db
    init_db(app)

    # Register Blueprints
    from app.routes.main import main_bp
    from app.routes.images import images_bp
    from app.routes.students import students_bp
    from app.routes.sessions import sessions_bp
    from app.routes.email import email_bp
    from app.routes.tournaments import tournaments_bp
    from app.routes.users import users_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(images_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(email_bp)
    app.register_blueprint(tournaments_bp)
    app.register_blueprint(users_bp)

    return app