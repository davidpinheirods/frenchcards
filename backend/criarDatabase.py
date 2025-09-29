from processaCsv import lerCelulaCsv
from apiGemini import apiGemini
import mysql.connector
from config.db import db_connector
import json


def limpar_dividir_json(json_sujo_str: str) -> tuple[str, str]:
    try:
        start_index = json_sujo_str.find('{')
        end_index = json_sujo_str.rfind('}')

        if start_index == -1 or end_index == -1:
            raise json.JSONDecodeError("Não foi possível encontrar um objeto JSON válido na string.", json_sujo_str, 0)

        json_limpo_str = json_sujo_str[start_index : end_index + 1]

        # Decodifica a string JSON limpa para um dicionário Python
        dados_json = json.loads(json_limpo_str)

        # Verifica se o JSON tem as chaves esperadas e se contém exatamente duas partes
        if not isinstance(dados_json, dict):
            raise ValueError("O JSON limpo não é um objeto (dicionário).")
        
        if "frase" not in dados_json or "traducao" not in dados_json:
             raise KeyError("O JSON deve conter as chaves 'frase' e 'traducao'.")
        
        if len(dados_json) != 2:
            # Isso é uma suposição baseada no seu exemplo. Se o JSON puder ter mais chaves
            # e você ainda quiser apenas 'frase' e 'traducao', esta verificação pode ser removida.
            print(f"Atenção: O JSON contém mais de duas chaves, mas apenas 'frase' e 'traducao' serão retornadas. Chaves encontradas: {list(dados_json.keys())}")


        # Divide o JSON em duas partes
        parte1 = dados_json["frase"]
        parte2 = dados_json["traducao"]

        return parte1, parte2

    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
        raise
    except KeyError as e:
        print(f"Erro: Chave ausente no JSON: {e}")
        raise
    except ValueError as e:
        print(f"Erro de validação do JSON: {e}")
        raise
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        raise 

def salvar_na_db(frase: str, traducao: str):
    conn = None
    cursor = None
    try:
        # Obtém a conexão com o banco de dados usando sua função importada
        conn = db_connector()
        if conn is None:
            print("Não foi possível estabelecer conexão com o banco de dados.")
            return

        cursor = conn.cursor()

        sql = "INSERT INTO flashcards (frase, traducao) VALUES (%s, %s)"
        
        # Os valores a serem inseridos
        valores = (frase, traducao)

        # Executa a query
        cursor.execute(sql, valores)

        # Confirma a transação
        conn.commit()
        print("Dados salvos com sucesso no banco de dados!")

    except mysql.connector.Error as err:
        print(f"Erro ao salvar no MySQL: {err}")
        # Reverte a transação em caso de erro
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        # Garante que o cursor e a conexão sejam fechados
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def main():
    """
    Função principal para orquestrar o processamento.
    """
    indice_atual = 2
    while True:
        # 1. Obter a string de processarCsv.py
        saida_csv = lerCelulaCsv("docs/palavrasFrances.csv",indice_atual)

        # 2. Verificar se ainda há dados para processar
        if not saida_csv: # Se a string for vazia, significa que não há mais dados
            print("Fim do arquivo CSV. Todas as linhas processadas.")
            break

        # 3. Incrementar o índice para a próxima iteração
        indice_atual += 1

        # 4. Dividindo json e salvando no banco de dados a saida
        #print(dividir_e_limpar_json(apiGemini(saida_csv)))
        #print(limpar_dividir_json(apiGemini(saida_csv)))

        frase_result, traducao_result = limpar_dividir_json(apiGemini(saida_csv))
        print(f"{frase_result} \n {traducao_result}")

        salvar_na_db(frase_result, traducao_result)
        


if __name__ == "__main__":
    main()