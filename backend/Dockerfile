
FROM python:3.11-slim

# Defina o diretório de trabalho dentro do container
WORKDIR /app

# Copie o arquivo de dependências primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copie todo o resto do código do backend para o container
COPY . .

# Exponha a porta que o Flask usa
EXPOSE 5000

# O comando para iniciar a aplicação
# Usamos "flask run" que é mais adequado para desenvolvimento/produção do que app.run()
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "run:app"]