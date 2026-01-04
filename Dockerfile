# Usa una imagen base de Python
FROM python:3.10-slim

# Crea una carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requerimientos y los instala
# (Ajustamos la ruta porque tu archivo está en src/)
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el contenido de tu carpeta src al contenedor
COPY src/ .

# Comando que se ejecuta al iniciar el contenedor
CMD ["python", "main.py"]