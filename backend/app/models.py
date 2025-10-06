# backend/app/models.py

from app import db
from sqlalchemy.sql import func

class Flashcard(db.Model):
    """
    Representa a tabela 'flashcards'.
    Cada instância desta classe é uma linha na tabela (um flashcard).
    """
    __tablename__ = 'flashcards'
    id = db.Column(db.Integer, primary_key=True)
    frase = db.Column(db.String(255), nullable=False, unique=True)
    traducao = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        """
        Retorna uma representação do modelo em formato de dicionário,
        útil para a serialização em JSON.
        """
        return {
            'id': self.id,
            'frase': self.frase,
            'traducao': self.traducao
        }

class AvaliacaoTipo(db.Model):
    """
    Representa a tabela 'avaliacaotipo'.
    Armazena os tipos de avaliação possíveis (ex: 'Fácil', 'Médio').
    """
    __tablename__ = 'avaliacaotipo'
    id = db.Column(db.Integer, primary_key=True)
    avaliacao = db.Column(db.String(11), nullable=False, unique=True)

class Avaliacao(db.Model):
    """
    Representa a tabela 'avaliacao'.
    Registra a avaliação que um usuário deu para um flashcard específico.
    """
    __tablename__ = 'avaliacao'
    id = db.Column(db.Integer, primary_key=True)
    data_avaliacao = db.Column(db.TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Definição das Chaves Estrangeiras
    flashcard_id = db.Column(db.Integer, db.ForeignKey('flashcards.id'), nullable=False, unique=True)
    avaliacao_id = db.Column(db.Integer, db.ForeignKey('avaliacaotipo.id'), nullable=False)

    # Relacionamentos ORM (a "mágica" do SQLAlchemy)
    # Permitem acessar os objetos Python relacionados diretamente.
    # Ex: uma_avaliacao.flashcard retornará o objeto Flashcard correspondente.
    flashcard = db.relationship('Flashcard', backref=db.backref('avaliacao', lazy=True, uselist=False, cascade="all, delete-orphan"))
    tipo = db.relationship('AvaliacaoTipo', backref=db.backref('avaliacoes', lazy=True))