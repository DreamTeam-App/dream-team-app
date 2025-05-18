from flask import Flask, redirect, render_template, request, make_response, session, abort, jsonify, url_for
import secrets
from functools import wraps
import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import timedelta
import os
from dotenv import load_dotenv
from routes.professor import professor_bp
from routes.student import student_bp
from routes.authentication import *
from firebase_client import *

load_dotenv()



app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Configure session cookie settings
app.config['SESSION_COOKIE_SECURE'] = True  # Ensure cookies are sent over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Adjust session expiration as needed
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Can be 'Strict', 'Lax', or 'None'




########################################
""" Authentication and Authorization """

# Decorator for routes that require authentication


@app.route('/new_user', methods=['POST'])
def new_user():
    data = request.get_json()
    uid = data.get('uid')
    email = data.get('email')
    name = data.get('name', '')

    return jsonify({"success": True})
@app.route('/auth', methods=['POST'])
def authorize():
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401

    token = token[7:]  # Elimina "Bearer "

    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token["uid"]
        email = decoded_token["email"]

        # Si ya existe un usuario en sesión, nos aseguramos de que incluya el UID
        if "user" in session:
            session["user"]["uid"] = uid  # Agregamos el uid si no está presente
            return jsonify({
                "new_user": False,
                "name": session["user"]["name"],
                "role": session["user"]["role"]
            })

        # Consultar Firestore solo si el usuario no está en sesión
        user_ref = db.collection("users").document(uid).get()
        if user_ref.exists:
            user_data = user_ref.to_dict()
            user_data["uid"] = uid  # Aseguramos que el uid esté en los datos
            session["user"] = user_data  # Guardamos el usuario en sesión
            return jsonify({
                "new_user": False,
                "name": user_data["name"],
                "role": user_data["role"]
            })

        # Si el usuario no existe, se guarda en sesión temporal junto con el uid y email
        session["temp_user"] = {"uid": uid, "email": email}
        return jsonify({"new_user": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 401



#####################
""" Public Routes """

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('student.home'))
    else:
        return render_template('public/home2.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        # Mostrar el formulario de registro
        return render_template('register.html')

    # Procesar el formulario (método POST)
    uid = session.get("temp_user", {}).get("uid")
    email = session.get("temp_user", {}).get("email")
    name = request.form.get("name")

    if not uid or not email or not name:
        flash("Por favor complete su nombre para continuar.", "error")
        return redirect(url_for('register'))

    # Generar un ID institucional aleatorio para anonimizar al usuario
    import uuid
    anonymous_id = str(uuid.uuid4())[:8].upper()  # Genera un ID alfanumérico de 8 caracteres

    # Guardar en Firestore solo si no existe
    user_ref = db.collection("users").document(uid)
    user_doc = user_ref.get()

    if not user_doc.exists:
        # Crea el documento del usuario
        user_ref.set({
            "email": email,
            "name": name,
            "role": "student",
            "anonymous_id": anonymous_id,  # Guardamos el ID anónimo
            "consent_given": True  # Asumimos que el usuario dio su consentimiento al hacer clic en "Guardar"
        })

        # Aquí asignamos los formularios pendientes al nuevo estudiante
        forms_to_assign = [
            {
                "form_type": "personality",
                "title": "Test de Personalidad",
                "description": "Formulario para determinar tu tipo de personalidad",
                "url": "/student/form1"
            },
            {
                "form_type": "team_roles",
                "title": "Team Role Experience and Orientation",
                "description": "Completa este test para determinar tus roles en equipos de trabajo",
                "url": "/student/form2"
            }
            # Agrega más formularios si lo requieres
        ]

        for f in forms_to_assign:
            # Creamos un nuevo documento en la subcolección "forms"
            form_doc_ref = user_ref.collection("forms").document()
            form_data = {
                "form_id": form_doc_ref.id,
                "form_type": f["form_type"],
                "title": f["title"],
                "description": f["description"],
                "url": f["url"],
                "completed": False,     # Se inicia en falso
                "completed_at": None    # Se asigna None o un timestamp vacío
            }
            form_doc_ref.set(form_data)

    # Limpiar sesión temporal y guardar usuario en sesión normal
    session.pop("temp_user", None)
    session["user"] = {"uid": uid, "email": email, "name": name, "role": "student"}

    flash("Registro completado con éxito. Bienvenido/a a Dream Team.", "success")
    return redirect(url_for('login'))

@app.route('/home')
def home2():
    if 'user' in session:
        return redirect(url_for('student.home'))
    else:
        team_members = [
            {"name": "Sara Suarez", "role": "DEVELOPER", "image": "/static/images/home/woman1.svg"},
            {"name": "Felipe Bolivar", "role": "DEVELOPER", "image": "/static/images/home/man1.svg"},
            {"name": "María José Gómez", "role": "DEVELOPER", "image": "/static/images/home/woman2.svg"},
            {"name": "José Torres", "role": "DEVELOPER", "image": "/static/images/home/man2.svg"}
        ]
        
        partners = [
            {"name": "Google", "image": "/static/images/placeholder.svg"},
            {"name": "Microsoft", "image": "/static/images/placeholder.svg"},
            {"name": "Airbnb", "image": "/static/images/placeholder.svg"},
            {"name": "Facebook", "image": "/static/images/placeholder.svg"},
            {"name": "Spotify", "image": "/static/images/placeholder.svg"}
        ]
        
        return render_template('public/home2.html', team_members=team_members, partners=partners)


@app.route('/login')
def login():
    if 'user' in session:
        return redirect(url_for('student.home'))
    else:
        return render_template('public/login.html')

@app.route('/signup')
def signup():
    if 'user' in session:
        return redirect(url_for('student.home'))
    else:
        return render_template('public/signup.html')


@app.route('/reset-password')
def reset_password():
    if 'user' in session:
        return redirect(url_for('student.home'))
    else:
        return render_template('public/forgot_password.html')

@app.route('/terms')
def terms():
    return render_template('public/terms.html')

@app.route('/privacy')
def privacy():
    return render_template('public/privacy.html')

@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove the user from session
    response = make_response(redirect(url_for('login')))
    response.set_cookie('session', '', expires=0)  # Optionally clear the session cookie
    return response


##############################################
""" Private Routes (Require authorization) """

@app.route('/dashboard')
@auth_required
def dashboard():

    return render_template('public/dashboard.html')

app.register_blueprint(professor_bp, url_prefix="/professor")
app.register_blueprint(student_bp, url_prefix="/student")




if __name__ == '__main__':
    app.run(debug=True)
