
# Dream Team App

## 🧠 Tecnologías Utilizadas

> Esta aplicación web integra múltiples tecnologías modernas para lograr una arquitectura escalable, segura y mantenible.

| Tecnología              | Descripción                                                                                             | Badge |
|------------------------|---------------------------------------------------------------------------------------------------------|--------|
| **Python 3.10+**        | Lenguaje principal para la lógica del backend                                                           | ![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white) |
| **Flask**              | Framework web ligero utilizado para definir rutas, vistas y lógica del servidor                        | ![Flask](https://img.shields.io/badge/Flask-Web_Framework-black?logo=flask) |
| **Firebase Admin SDK** | Autenticación de usuarios, conexión a Firestore, y servicios de nube de Google Cloud                    | ![Firebase](https://img.shields.io/badge/Firebase-Admin_SDK-yellow?logo=firebase) |
| **Google Firestore**    | Base de datos NoSQL escalable usada para almacenar información dinámica del sistema                    | ![Firestore](https://img.shields.io/badge/Google_Firestore-NoSQL_Database-orange?logo=google-cloud) |
| **Jinja2 + HTML5**      | Sistema de plantillas para generar contenido dinámico en vistas HTML                                    | ![HTML](https://img.shields.io/badge/HTML-Jinja2-blue?logo=html5) |
| **CSS + JavaScript**    | Estilos personalizados y lógica del frontend para la experiencia del usuario                            | ![CSS](https://img.shields.io/badge/CSS-JS-yellow?logo=css3) |
| **dotenv**              | Gestión de credenciales y variables de entorno sensibles con archivo `.env`                            | ![dotenv](https://img.shields.io/badge/dotenv-Env_Variables-brightgreen) |
| **Machine Learning**    | Modelo incluido en `ml.zip`, presumiblemente para predicción o clasificación                           | ![ML](https://img.shields.io/badge/Machine_Learning-Model_Zip-lightgrey) |
| **Docker / Containerfile** | Despliegue automatizado y aislado en entornos de contenedores                                    | ![Docker](https://img.shields.io/badge/Docker-Containerfile-2496ED?logo=docker&logoColor=white) |


---

## 📁 Estructura del Proyecto

> Organización del código y recursos principales del sistema.

| Tipo / Nombre                       | Descripción                                                                 |
|------------------------------------|-----------------------------------------------------------------------------|
| ![json](https://img.shields.io/badge/firebase-auth.json-lightgrey)  | Archivo principal de ejecución de la aplicación Flask                        |
| `firebase-auth.json` | Clave privada de Firebase *(⚠️ No esta en el repositorio por cuestiones de seguridad)* |
| ![py](https://img.shields.io/badge/firebase_client.py-%20-blue?logo=python&logoColor=white)  | Inicialización del SDK de Firebase                                          |
| ![py](https://img.shields.io/badge/firebase_config.py-%20-blue?logo=python&logoColor=white)  | Configuraciones de entorno de Firebase                                      |
| ![txt](https://img.shields.io/badge/firestore_rules_example.txt-%20-lightgrey) | Reglas de seguridad de ejemplo para Firestore                              |
| ![txt](https://img.shields.io/badge/requirements.txt-%20-critical)  | Dependencias requeridas por la aplicación                                   |
| ![docker](https://img.shields.io/badge/Containerfile-%20-blue?logo=docker)  | Archivo para crear contenedores (Docker/Podman)                             |
| ![env](https://img.shields.io/badge/.env-%20-green) | Variables de entorno para ejecución segura                                  |
| ![gitignore](https://img.shields.io/badge/.gitignore-%20-lightgrey)  | Exclusiones del repositorio                                                 |
| ![md](https://img.shields.io/badge/README.md-%20-blue?logo=markdown&logoColor=white)  | Documentación principal del proyecto                                        |
| 📁 `routes/`                        | Módulos de rutas (blueprints) para Flask                                    |
| 📁 `templates/`                     | Archivos HTML/Jinja2 para renderizado dinámico                              |
| 📁 `static/`                        | Archivos estáticos (CSS, JS, imágenes)                                      |
| 📁 `ml/` / `ml.zip`                 | Archivos del modelo de machine learning                                     |
| 📁 `__pycache__/`                  | Archivos temporales generados por Python *(ignorar en producción)*         |


---

## 🚀 Instalación y Ejecución Local

1. Clona este repositorio:

```bash
git clone https://github.com/usuario/flask-website.git
cd flask-website
```

2. Crea un entorno virtual y activa:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala dependencias:

```bash
pip install -r requirements.txt
```

4. Configura tu entorno:
   - Crea un archivo `.env` con tus variables de entorno si no existe.
   - Asegúrate de tener `firebase-auth.json` válido para tu proyecto.

5. Ejecuta la aplicación:

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

---

## 🧪 Despliegue con Contenedor (opcional)

Si deseas desplegar usando Docker o Podman:

```bash
docker build -t flask-app -f Containerfile .
docker run -p 5000:5000 flask-app
```

---










