FROM python:3.11-slim

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiar el código fuente dentro del contenedor
COPY . /app

# Instalar dependencias
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exponer el puerto de Flask
EXPOSE 5000

# Comando para iniciar la aplicación Flask
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
