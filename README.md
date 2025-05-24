
# Flask Website with Firebase & Machine Learning Integration

🎓 **Proyecto de Tesis - Aplicación Web Inteligente**

Este repositorio contiene una aplicación web desarrollada en **Flask**, que integra autenticación y servicios en la nube mediante **Firebase**, y funcionalidades inteligentes a través de un modelo de **Machine Learning**. Este sistema fue desarrollado como parte de un trabajo de grado universitario.

---

## 📌 Objetivo del Proyecto

Desarrollar una plataforma web moderna y segura que permita realizar tareas específicas de análisis o predicción utilizando modelos de machine learning, almacenando resultados y usuarios en Firebase.

---

## 🧠 Tecnologías Utilizadas

- **Python 3.10+**
- **Flask**
- **Firebase (Auth, Firestore)**
- **Machine Learning (modelo empaquetado en `ml.zip`)**
- **Docker / Containerfile (opcional)**
- **HTML/CSS/JS (en templates si aplica)**

---

## 📂 Estructura del Proyecto

```plaintext
flask-website/
│
├── app.py                    # Punto de entrada de la aplicación Flask
├── firebase_client.py        # Cliente Firebase para autenticación y base de datos
├── firebase_config.py        # Configuración de claves y servicios de Firebase
├── firebase-auth.json        # Archivo de credenciales para Firebase
├── ml.zip                    # Archivo comprimido del modelo de ML (por descomprimir)
├── requirements.txt          # Dependencias necesarias del proyecto
├── Containerfile             # Configuración para despliegue en contenedor (Docker)
├── .env                      # Variables de entorno (no debe compartirse públicamente)
└── README.md                 # Documentación del proyecto
```

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

## 📄 Licencia

Este proyecto se desarrolló con fines académicos. Su uso y distribución están permitidos bajo licencia MIT si así se define en el archivo `LICENSE`.

---

## 🤝 Créditos

Desarrollado por [Tu Nombre Aquí] como parte del trabajo de grado en [Nombre del Programa o Universidad].









