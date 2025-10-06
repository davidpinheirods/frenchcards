from app import create_app, db
from app.models import Flashcard, Avaliacao
import sys

app = create_app()

def clear_data():
    """Apaga todos os registros das tabelas Flashcard e Avaliacao."""
    try:
        # Apaga primeiro as avaliações por causa da chave estrangeira
        num_avaliacoes = db.session.query(Avaliacao).delete()
        # Apaga os flashcards
        num_flashcards = db.session.query(Flashcard).delete()
        
        db.session.commit()
        
        print(f"Sucesso! {num_avaliacoes} registro(s) apagado(s) de 'avaliacao'.")
        print(f"Sucesso! {num_flashcards} registro(s) apagado(s) de 'flashcards'.")
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao limpar as tabelas: {e}")

if __name__ == '__main__':
    # Adiciona uma confirmação de segurança
    confirm = input("ATENÇÃO: Isso apagará TODOS os dados das tabelas 'flashcards' e 'avaliacao'.\nDigite 'sim' para continuar: ")
    if confirm.lower() == 'sim':
        with app.app_context():
            clear_data()
    else:
        print("Operação cancelada.")
        sys.exit()