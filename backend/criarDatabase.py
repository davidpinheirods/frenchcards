import json
from app.utils.processaCsv import lerCelulaCsv
from app.utils.apiGemini import apiGemini
from app import create_app, db
from app.models import Flashcard, AvaliacaoTipo

# Cria uma instância da aplicação para estabelecer o contexto
app = create_app()

def limpar_dividir_json(json_sujo_str: str) -> tuple[str, str]:
    """
    Extrai o objeto JSON de uma string que pode conter texto adicional
    e retorna os valores das chaves 'frase' e 'traducao'.
    """
    try:
        start_index = json_sujo_str.find('{')
        end_index = json_sujo_str.rfind('}')
        if start_index == -1 or end_index == -1:
            raise json.JSONDecodeError("Não foi possível encontrar um objeto JSON válido.", json_sujo_str, 0)
        
        json_limpo_str = json_sujo_str[start_index : end_index + 1]
        dados_json = json.loads(json_limpo_str)
        
        return dados_json["frase"], dados_json["traducao"]
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Erro ao processar JSON: {e}")
        # Lança a exceção para que a função chamadora saiba que falhou
        raise

def popular_tipos_avaliacao():
    """
    Garante que a tabela avaliacaotipo contenha os valores padrão.
    Só insere os tipos se eles ainda não existirem.
    """
    print("Verificando e populando tipos de avaliação...")
    tipos = {1: 'Fácil', 2: 'Médio', 3: 'Difícil', 4: 'Não Lembro'}
    
    for tipo_id, tipo_str in tipos.items():
        # Verifica se um tipo com este ID já existe
        existe = AvaliacaoTipo.query.get(tipo_id)
        if not existe:
            novo_tipo = AvaliacaoTipo(id=tipo_id, avaliacao=tipo_str)
            db.session.add(novo_tipo)
            print(f"Adicionado tipo: '{tipo_str}'")
            
    db.session.commit()
    print("Tipos de avaliação finalizados.")

def salvar_flashcard_na_db(frase: str, traducao: str):
    """Salva um novo flashcard no banco de dados usando o ORM."""
    try:
        # Verifica se já existe um card com esta frase
        card_existente = Flashcard.query.filter_by(frase=frase).first()
        if card_existente:
            print(f"Card já existe no banco: '{frase}'. Pulando.")
            return

        novo_card = Flashcard(frase=frase, traducao=traducao)
        db.session.add(novo_card)
        db.session.commit()
        print(f"Card salvo com sucesso: '{frase}'")
    except Exception as e:
        print(f"Ocorreu um erro ao salvar o card: {e}")
        db.session.rollback()

def main():
    """
    Função principal que orquestra a leitura do CSV, chamada da API
    e gravação dos dados no banco de dados.
    """
    # Executa toda a lógica dentro do contexto da aplicação Flask
    with app.app_context():
        # 1. Garante que os tipos de avaliação existam
        popular_tipos_avaliacao()

        # 2. Processa o arquivo CSV para criar novos flashcards
        indice_atual = 2
        print("\nIniciando processamento do arquivo CSV...")
        while True:
            palavra_frances = lerCelulaCsv("docs/palavrasFrances.csv", indice_atual)
            
            if not palavra_frances:
                print("\nFim do arquivo CSV. Processamento concluído.")
                break

            print(f"\nProcessando linha {indice_atual}: '{palavra_frances}'")
            
            try:
                resposta_gemini = apiGemini(palavra_frances)
                frase_gerada, traducao_gerada = limpar_dividir_json(resposta_gemini)
                salvar_flashcard_na_db(frase_gerada, traducao_gerada)
            except Exception as e:
                print(f"Falha ao processar a palavra '{palavra_frances}'. Erro: {e}. Passando para a próxima.")

            indice_atual += 1

if __name__ == "__main__":
    main()