import google.generativeai as genai
import os
import textwrap
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# 1. Função de Configuração da API
def configure_gemini_api() -> bool:
    """Configura a API do Gemini com a chave de API."""
    try:
        load_dotenv() # Carrega as variáveis do arquivo .env
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key is None:
            raise ValueError("A variável de ambiente GOOGLE_API_KEY não está definida.")
        genai.configure(api_key=api_key) # type: ignore
        logger.info("API do Gemini configurada com sucesso!")
        return True
    except ValueError as e:
        logger.error(f"Erro de configuração da API: {e}")
        logger.error("Por favor, defina a variável de ambiente GOOGLE_API_KEY com sua chave de API.")
        logger.error("Certifique-se de que sua chave está no arquivo .env ou como uma variável de ambiente do sistema.")
        return False

# 2. Função para Listar Modelos (DEVE VIR ANTES DE main() se for chamada lá)
def list_available_models():
    """
    Lista todos os modelos de IA generativa disponíveis para a sua API Key.
    """
    logger.debug("\nVerificando modelos disponíveis...")
    try:
        for m in genai.list_models(): # type: ignore
            if 'generateContent' in m.supported_generation_methods:
                logger.info(f"- {m.name} (Suporta generateContent)")
            else:
                logger.info(f"- {m.name} (Não suporta generateContent para texto)")
        logger.info("\n^ Verifique a lista acima para o modelo que você deseja usar.")
    except Exception as e:
        logger.error(f"Erro ao listar modelos: {e}")

# 3. Função para Obter Resposta do Gemini
def get_gemini_response(prompt_text, model_name='gemini-2.5-flash-preview-05-20'): 
    """
    Envia um prompt para o modelo Gemini e retorna a resposta.
    """
    try:
        model = genai.GenerativeModel(model_name) # type: ignore
        logger.info(f"\nEnviando prompt para o {model_name}... Por favor, aguarde.")
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        logger.error(f"Ocorreu um erro ao gerar a resposta do Gemini com o modelo '{model_name}': {e}")
        return ""

# 4. Função para Exibir Resposta Formatada
def display_formatted_response(response_text):
    if response_text:
        #logger.info("\n" + "="*50)
        #logger.info("RESPOSTA DO GEMINI:")
        #logger.info("="*50)
        wrapped_text = textwrap.fill(response_text, width=80)
        print(wrapped_text)
        #logger.info("="*50)
    else:
        logger.error("\nNão foi possível obter uma resposta do Gemini.")

# 5. Função Principal
def apiGemini(palavraInput) -> str:
    if not configure_gemini_api():
        return ""

    #list_available_models()

    #logger.info("\n--- Conectado ao Gemini ---")
    #logger.info("Digite 'sair' a qualquer momento para encerrar.")
    #logger.info("Modelo padrão: gemini-2.5-flash-preview-05-20")
    # palavraInput = "avoir"
    user_prompt = f'Gere uma frase em francês contendo a palavra "{palavraInput}" e a sua tradução e retorne a resposta em formato JSON como no exemplo a seguir: {{"frase": "frase gerada", "traducao": "traducao da frase"}}'
    
    gemini_response = get_gemini_response(user_prompt)
    #display_formatted_response(gemini_response)

    return gemini_response

if __name__ == "__main__":
    print(apiGemini("David"))