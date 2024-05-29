# Use a base image for Python
FROM python:3.11

# Define o diretório de trabalho
WORKDIR /app

# Install dependencies required for OpenCV
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx && \
    apt-get install -y libgl1-mesa-glx libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Copia o arquivo de requisitos para o diretório de trabalho
COPY requirements.txt requirements.txt

# Instale gdown e qualquer outra dependência necessária
RUN pip install gdown

# Defina as variáveis de ambiente
ENV BERTIMBAU_PATH=app/bertimbau-finetuned
ENV BERTIMBAU_URL=https://drive.google.com/drive/folders/1gE6JdtHgSw9GOqtS-u8xs0x9hjxZwwWA?usp=sharing

# Execute o comando para verificar se a pasta existe e fazer o download se necessário
RUN if [ ! -d "$BERTIMBAU_PATH" ]; then \
    gdown --folder $BERTIMBAU_URL -O $BERTIMBAU_PATH; \
    fi
    
# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o conteúdo da aplicação para o diretório de trabalho
COPY . .

ENV PYTHONPATH=/app

# Comando para rodar o servidor Gunicorn
CMD ["gunicorn", "-c", "gunicorn_config.py", "app:create_app('prod')"]