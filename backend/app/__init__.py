# backend/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config

# Inicializa as extensões sem estarem atreladas a um app específico
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    """
    Cria e configura uma instância da aplicação Flask.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Conecta as extensões com a instância da aplicação
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Importa e registra o Blueprint com as rotas
    from app.routes import api_bp
    app.register_blueprint(api_bp)

    return app