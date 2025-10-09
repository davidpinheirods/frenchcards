# backend/app/services.py
from datetime import datetime, timedelta
from sqlalchemy import or_
from app.models import db, Flashcard, Avaliacao


def get_all_flashcards_service():
    """Retorna todos os flashcards."""
    cards = Flashcard.query.all()
    return [card.to_dict() for card in cards]

def get_study_session_service():
    """Monta a fila de estudos."""
    # Encontra flashcards que não estão na tabela de avaliação
    cards_para_aprender = db.session.query(Flashcard).outerjoin(Avaliacao).filter(Avaliacao.flashcard_id == None).all()

    if cards_para_aprender:
        return [card.to_dict() for card in cards_para_aprender]

    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    cards_para_revisar = Flashcard.query.join(Avaliacao).filter(
        or_(
            Avaliacao.avaliacao_id > 1,
            db.and_(
                Avaliacao.avaliacao_id == 1,
                Avaliacao.data_avaliacao <= seven_days_ago
            )
        )
    ).order_by(Avaliacao.avaliacao_id.desc(), Avaliacao.data_avaliacao.asc()).all()

    if cards_para_revisar:
        return [card.to_dict() for card in cards_para_revisar]

    # Se não há nem novos nem para revisar
    return {
        "status": "concluido",
        "message": "Parabéns! Você não tem novos cards para aprender e nenhuma revisão pendente."
    }

def save_evaluation_service(flashcard_id, avaliacao_id):
    """Salva ou atualiza a avaliação de um flashcard."""
    avaliacao_existente = Avaliacao.query.filter_by(flashcard_id=flashcard_id).first()
    
    if avaliacao_existente:
        avaliacao_existente.avaliacao_id = avaliacao_id
    else:
        nova_avaliacao = Avaliacao(flashcard_id=flashcard_id, avaliacao_id=avaliacao_id)
        db.session.add(nova_avaliacao)
    
    db.session.commit()

def get_review_queue_service():
    """
    Busca todos os flashcards marcados para revisão (não são 'Fácil').
    A ordem é por dificuldade (mais difíceis primeiro) e depois por data (mais antigos primeiro).
    """
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    cards_para_revisar = Flashcard.query.join(Avaliacao).filter(
        or_(
            Avaliacao.avaliacao_id > 1,
            db.and_(
                Avaliacao.avaliacao_id == 1,
                Avaliacao.data_avaliacao <= seven_days_ago
            )
        )
    ).order_by(Avaliacao.avaliacao_id.desc(), Avaliacao.data_avaliacao.asc()).all()
    
    return [card.to_dict() for card in cards_para_revisar]