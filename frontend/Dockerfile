# Use a imagem oficial do Nginx
FROM nginx:stable-alpine

# Copie os arquivos estáticos do seu app para o diretório padrão do Nginx
COPY index.html /usr/share/nginx/html
COPY style.css /usr/share/nginx/html
COPY script.js /usr/share/nginx/html
COPY assets/ /usr/share/nginx/html/assets/

# Copie a configuração customizada do Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf