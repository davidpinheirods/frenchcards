import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging
import time
import json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def configure_gemini_api() -> bool:
    # ... (esta função permanece a mesma) ...
    try:
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key is None:
            raise ValueError("A variável de ambiente GOOGLE_API_KEY não está definida.")
        genai.configure(api_key=api_key) # type: ignore
        return True
    except Exception as e:
        logger.error(f"Erro de configuração da API: {e}")
        return False

def get_gemini_response(prompt_text, model_name='gemini-flash-latest'):
    # ... (esta função permanece a mesma) ...
    try:
        model = genai.GenerativeModel(model_name) # type: ignore
        logger.info(f"Enviando prompt para o {model_name}...")
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        logger.error(f"Ocorreu um erro ao gerar a resposta do Gemini: {e}")
        return ""

def _extract_json_string(text: str) -> str | None:
    # ... (esta função permanece a mesma) ...
    try:
        start_index = text.find('{')
        end_index = text.rfind('}')
        if start_index == -1 or end_index == -1: return None
        return text[start_index : end_index + 1]
    except (TypeError, AttributeError):
        return None

def apiGemini(palavraInput: str, tempoVerbal: str) -> str:
    if not configure_gemini_api():
        return ""

    # --- PROMPT REFINADO COM MAIS REGRAS ---
    user_prompt = f"""
    Sua tarefa é criar um flashcard de aprendizado de idiomas. Siga estas regras estritamente:

    1.  Use a palavra em francês "{palavraInput}" em uma frase natural.
    2.  A frase deve usar o tempo verbal "{tempoVerbal}".
    3.  A frase gerada não deve destacar a palavra-chave com asteriscos, negrito ou qualquer outra formatação.
    4.  A tradução deve ser para o português do Brasil.
    5.  Não inclua inglês ou qualquer outro idioma na resposta.

    Retorne a resposta EXCLUSIVAMENTE no seguinte formato JSON:
    {{
      "palavra_chave": "{palavraInput}",
      "frase": "Sua frase gerada em francês aqui.",
      "traducao": "Sua tradução em português do Brasil aqui.",
      "tempo_verbal": "{tempoVerbal}"
    }}
    """
    
    max_retries = 3
    # --- TEMPO DE ESPERA AUMENTADO ---
    retry_delay = 15 # segundos

    for attempt in range(max_retries):
        logger.info(f"Tentativa {attempt + 1} de {max_retries} para '{palavraInput}' ({tempoVerbal})...")
        raw_response = get_gemini_response(user_prompt)
        
        clean_json_str = _extract_json_string(raw_response)

        if clean_json_str:
            try:
                json.loads(clean_json_str)
                logger.info("JSON extraído e validado com sucesso!")
                return clean_json_str
            except json.JSONDecodeError:
                logger.warning("String extraída não é um JSON válido.")
        
        logger.warning(f"Tentativa {attempt + 1} falhou. A resposta não continha um JSON válido.")
        if attempt < max_retries - 1:
            logger.info(f"Aguardando {retry_delay} segundos...")
            time.sleep(retry_delay)

    logger.error(f"Todas as {max_retries} tentativas falharam para '{palavraInput}'. Desistindo.")
    return ""