import os
from typing import cast
from dotenv import load_dotenv
from mysql import connector

def db_connector() -> connector.MySQLConnection | None:
    load_dotenv()

    try:
        # Conectar ao db
        conn = connector.connect(
            host=os.getenv("DATABASE_URL"),  # URL do banco de dados
            user=os.getenv("DATABASE_USER"),  # Usuário do banco de dados
            password=os.getenv("DATABASE_PASSWORD"),  # Senha do banco de dados
            database=os.getenv("DATABASE_NAME"),  # Nome do banco de dados
            port=os.getenv("DATABASE_PORT"),
        )
        return cast(connector.MySQLConnection, conn)
    except connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        return None
