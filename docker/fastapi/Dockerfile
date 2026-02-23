# Imagen base oficial de Python (Debian Bookworm Slim)
FROM python:3.12-slim-bookworm

# Variables de entorno para optimizar Python en Docker
# Evita que Python genere archivos .pyc y fuerza el log en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalación de dependencias necesarias del sistema
# para compilar librerías de Python y el editor de texto vim
# Finalmente se elimina la caché de los índices de paquetes 
# para reducir el tamaño de la imagen
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    vim \ 
    && rm -rf /var/lib/apt/lists/*

# Se define el directorio de trabajo
WORKDIR /home/python

# Se define el PYTHONPATH para que Python pueda encontrar 
# los módulos de la aplicación
ENV PYTHONPATH=/home/python

# Se copia el archivo de dependencias y 
# luego se instalan las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r /home/python/requirements.txt

