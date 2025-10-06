# backend/app/routes.py
from flask import Blueprint, jsonify, request, abort
from app import services
from sqlalchemy.exc import SQLAlchemyError

# Cria um Blueprint chamado 'api'
api_bp = Blueprint('api', __name__)

@api_bp.route('/flashcards', methods=['GET'])
def get_flashcards():
    try:
        flashcards = services.get_all_flashcards_service()
        return jsonify(flashcards)
    except SQLAlchemyError as e:
        print(f"Erro de banco de dados: {e}")
        abort(500, description="Erro ao buscar dados no banco de dados.")

@api_bp.route('/estudar', methods=['GET'])
def get_study_session():
    try:
        session_data = services.get_study_session_service()
        return jsonify(session_data)
    except SQLAlchemyError as e:
        print(f"Erro de banco de dados: {e}")
        abort(500, description="Erro ao montar a fila de estudos.")

@api_bp.route('/avaliar', methods=['POST'])
def save_evaluation():
    data = request.get_json()
    if not data or 'flashcard_id' not in data or 'avaliacao_id' not in data:
        abort(400, description="Requisição inválida. Faltando 'flashcard_id' ou 'avaliacao_id'.")

    try:
        services.save_evaluation_service(data['flashcard_id'], data['avaliacao_id'])
        return jsonify({"message": "Avaliação salva com sucesso!"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Erro de banco de dados: {e}")
        abort(500, description="Erro ao salvar a avaliação.")

@api_bp.route('/flashcards/revisao', methods=['GET'])
def get_review_queue():
    """
    Endpoint para buscar apenas a fila de cards para revisão.
    """
    try:
        review_cards = services.get_review_queue_service()
        return jsonify(review_cards)
    except SQLAlchemyError as e:
        print(f"Erro de banco de dados ao buscar fila de revisão: {e}")
        abort(500, description="Erro ao buscar dados para revisão.")