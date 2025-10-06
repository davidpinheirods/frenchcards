import csv
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def lerCelulaCsv(nome_arquivo: str, numero_linha: int):
    """
    Lê o conteúdo da primeira coluna (coluna A) de uma linha específica de um arquivo CSV.

    Args:
        nome_arquivo (str): O caminho para o arquivo CSV.
        numero_linha (int): O número da linha que você deseja ler (começando de 1).

    Returns:
        str or None: O valor da célula na linha e coluna especificadas,
                     ou None se a linha não existir ou houver um erro.
    """
    if numero_linha < 2:
        logger.error("Erro: O número da linha deve ser 2 ou maior.")
        return None

    try:
        with open(nome_arquivo, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            
            # Pula as linhas até chegar na linha desejada
            for i, row in enumerate(reader, start=1):
                if i == numero_linha:
                    if row:  # Garante que a linha não está vazia
                        return row[0]  # Retorna o valor da primeira coluna (índice 0)
                    else:
                        logger.warning(f"A linha {numero_linha} está vazia no arquivo.")
                        return None
            
            logger.error(f"A linha {numero_linha} não foi encontrada no arquivo '{nome_arquivo}'.")
            return None # Retorna None se a linha não for encontrada
            
    except FileNotFoundError:
        logger.error(f"O arquivo '{nome_arquivo}' não foi encontrado.")
        return None
    except IndexError:
        logger.error(f"A coluna A (primeira coluna) não existe na linha {numero_linha} do arquivo.")
        return None
    except Exception as e:
        logger.error(f"Ocorreu um erro ao ler o arquivo CSV: {e}")
        return None

if __name__ == "__main__":
    arquivoCsv = "palavrasFrances.csv" 
    
    # --- Solicitar a linha ao usuário ---
    while True:
        try:
            linha_desejada_str = input("Digite o número da linha que você deseja ler (ex: 2 para a segunda palavra): ")
            linha_desejada = int(linha_desejada_str)
            break # Sai do loop se o input for um número válido
        except ValueError:
            logger.error("Entrada inválida. Por favor, digite um número inteiro.")

    # --- Realizar a leitura da célula específica ---
    palavra_do_csv = lerCelulaCsv(arquivoCsv, linha_desejada)

    if palavra_do_csv is not None:
        logger.info(f"\nPalavra da linha {linha_desejada}: '{palavra_do_csv}'")
    else:
        logger.error(False)
