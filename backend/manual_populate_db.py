import json
import time
from app.utils.processaCsv import lerCelulaCsv
from app.utils.apiGemini import apiGemini
from app.models import Flashcard
from app import create_app, db

app = create_app()

def parse_gemini_response(json_str: str) -> dict:
    """Converte a string JSON (já limpa) em um dicionário Python."""
    try:
        # Não precisamos mais extrair, apenas carregar o JSON
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"    -> Erro ao converter JSON para dicionário: {e}")
        raise

# ... (A função salvar_flashcard_na_db e main permanecem as mesmas de antes) ...
def salvar_flashcard_na_db(dados_card: dict):
    try:
        card_existente = Flashcard.query.filter_by(
            palavra_chave=dados_card['palavra_chave'],
            tempo_verbal=dados_card['tempo_verbal']
        ).first()

        if card_existente:
            print(f"   -> Combinação '{dados_card['palavra_chave']}' + '{dados_card['tempo_verbal']}' já existe. Pulando.")
            return

        novo_card = Flashcard(
            frase=dados_card['frase'],
            traducao=dados_card['traducao'],
            palavra_chave=dados_card['palavra_chave'],
            tempo_verbal=dados_card['tempo_verbal']
        )
        db.session.add(novo_card)
        db.session.commit()
        print(f"   -> Card salvo com sucesso para: '{dados_card['palavra_chave']}'")
    except Exception as e:
        print(f"   -> Ocorreu um erro ao salvar o card no banco: {e}")
        db.session.rollback()

def main():
    tempos_verbais_para_praticar = [
        "Présent de l'indicatif",
        "Passé composé",
        "Imparfait",
        "Futur simple",
        "Futur proche",
        "Conditionnel présent"
    ]
    
    with app.app_context():
        print("\n--- INICIANDO PROCESSO DE POPULAÇÃO MANUAL DE FLASHCARDS ---")
        
        for tempo_verbal in tempos_verbais_para_praticar:
            print(f"\n--- Processando para o tempo verbal: [{tempo_verbal}] ---")
            
            indice_atual = 2
            while True:
                palavra_frances = lerCelulaCsv("docs/palavrasFrances.csv", indice_atual)
                
                if not palavra_frances:
                    print(f"--- Fim do CSV para o tempo verbal: [{tempo_verbal}] ---")
                    break

                print(f"Lendo palavra-chave: '{palavra_frances}' (linha {indice_atual})")
                
                resposta_gemini = apiGemini(palavra_frances, tempo_verbal)
                
                if resposta_gemini:
                    try:
                        dados_completos = parse_gemini_response(resposta_gemini)
                        salvar_flashcard_na_db(dados_completos)
                    except Exception as e:
                        print(f"   -> Falha ao processar a resposta para '{palavra_frances}'. Erro: {e}")
                else:
                    print(f"   -> Falha geral ao obter resposta para '{palavra_frances}' após múltiplas tentativas.")

                indice_atual += 1
        
        print("\n--- PROCESSO DE POPULAÇÃO CONCLUÍDO ---")

if __name__ == "__main__":
    main()