# Importando as bibliotecas necessárias
from flask import Flask, jsonify, abort, request
from flask_cors import CORS # NOVO: Importar o CORS
from config.db import db_connector
import mysql.connector

app = Flask(__name__)
CORS(app) # NOVO: Habilitar o CORS para toda a aplicação. Isso resolve o erro "Failed to fetch".

# --- ROTA PRINCIPAL (ÍNDICE) ---
# NOVA ROTA: Adicionada para responder à raiz do servidor.
@app.route('/')
def index():
    """
    Rota de boas-vindas para confirmar que a API está no ar.
    """
    return jsonify({"message": "API de Flashcards no ar! Use as rotas /estudar ou /flashcards/revisao para começar."})


# --- Rota para buscar todos os flashcards ---
# (Sem alterações aqui)
@app.route('/flashcards', methods=['GET'])
def get_flashcards():
    conn = None
    cursor = None
    try:
        conn = db_connector()
        if conn is None:
            abort(500, description="Não foi possível conectar ao banco de dados.")
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, frase, traducao FROM flashcards")
        flashcards = cursor.fetchall()
        return jsonify(flashcards)
    except mysql.connector.Error as err:
        print(f"Erro de MySQL: {err}")
        abort(500, description="Erro ao buscar dados no banco de dados.")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# --- ROTA INTELIGENTE: Fila de Estudo Principal ---
# (Sem alterações aqui)
@app.route('/estudar', methods=['GET'])
def get_study_session():
    conn = None
    cursor = None
    try:
        conn = db_connector()
        if conn is None:
            abort(500, description="Não foi possível conectar ao banco de dados.")
        cursor = conn.cursor(dictionary=True)
        query_nao_avaliados = """
            SELECT f.id, f.frase, f.traducao
            FROM flashcards f
            LEFT JOIN avaliacao a ON f.id = a.flashcard_id
            WHERE a.flashcard_id IS NULL;
        """
        cursor.execute(query_nao_avaliados)
        cards_para_aprender = cursor.fetchall()

        if cards_para_aprender:
            return jsonify(cards_para_aprender)
        else:
            query_revisao = """
                SELECT f.id, f.frase, f.traducao
                FROM flashcards f
                JOIN avaliacao a ON f.id = a.flashcard_id
                WHERE a.avaliacao_id > 1 
                ORDER BY a.avaliacao_id DESC, a.data_avaliacao ASC;
            """
            cursor.execute(query_revisao)
            cards_para_revisar = cursor.fetchall()

            if cards_para_revisar:
                return jsonify(cards_para_revisar)
            else:
                return jsonify({
                    "status": "concluido",
                    "message": "Parabéns! Você não tem novos cards para aprender e nenhuma revisão pendente."
                })
    except mysql.connector.Error as err:
        print(f"Erro de MySQL: {err}")
        abort(500, description="Erro ao montar a fila de estudos.")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --- Rota para a fila de revisão ---
# (Sem alterações aqui)
@app.route('/flashcards/revisao', methods=['GET'])
def get_review_queue():
    conn = None
    cursor = None
    try:
        conn = db_connector()
        if conn is None:
            abort(500, description="Não foi possível conectar ao banco de dados.")
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                f.id, 
                f.frase, 
                f.traducao
            FROM 
                flashcards f
            JOIN 
                avaliacao a ON f.id = a.flashcard_id
            WHERE 
                a.avaliacao_id > 1
            ORDER BY 
                a.avaliacao_id DESC, a.data_avaliacao ASC;
        """
        cursor.execute(query)
        review_flashcards = cursor.fetchall()
        return jsonify(review_flashcards)
    except mysql.connector.Error as err:
        print(f"Erro de MySQL: {err}")
        abort(500, description="Erro ao buscar dados para revisão.")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --- Rota para salvar a avaliação de um flashcard ---
# (Sem alterações aqui)
@app.route('/avaliar', methods=['POST'])
def save_evaluation():
    data = request.get_json()
    if not data or 'flashcard_id' not in data or 'avaliacao_id' not in data:
        abort(400, description="Requisição inválida. Faltando 'flashcard_id' ou 'avaliacao_id'.")

    flashcard_id = data['flashcard_id']
    avaliacao_id = data['avaliacao_id']

    conn = None
    cursor = None
    try:
        conn = db_connector()
        if conn is None:
            abort(500, description="Não foi possível conectar ao banco de dados.")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM avaliacao WHERE flashcard_id = %s", (flashcard_id,))
        existing_evaluation = cursor.fetchone()
        
        if existing_evaluation:
            sql = "UPDATE avaliacao SET avaliacao_id = %s WHERE flashcard_id = %s"
            values = (avaliacao_id, flashcard_id)
        else:
            sql = "INSERT INTO avaliacao (flashcard_id, avaliacao_id) VALUES (%s, %s)"
            values = (flashcard_id, avaliacao_id)
        
        cursor.execute(sql, values)
        conn.commit()
        return jsonify({"message": "Avaliação salva com sucesso!"}), 200
    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        print(f"Erro de MySQL: {err}")
        abort(500, description="Erro ao salvar a avaliação.")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)