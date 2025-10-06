# backend/config.py
import os

class Config:
    """Configurações base da aplicação."""
    # Desativa o rastreamento de modificações do SQLAlchemy para economizar recursos
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Constrói a URI de conexão a partir das variáveis de ambiente
    DB_USER = os.environ.get('DB_USER')
    DB_PASS = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST')
    DB_NAME = os.environ.get('DB_NAME')
    
    # A URI precisa do formato: mysql+pymysql://user:password@host/dbname
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'