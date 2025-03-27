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

        # Si el usuario ya está en sesión, devolver los datos sin consultar Firestore
        if "user" in session:
            return jsonify({
                "new_user": False,
                "name": session["user"]["name"],
                "role": session["user"]["role"]
            })

        # Consultar Firestore solo si el usuario no está en sesión
        user_ref = db.collection("users").document(uid).get()
        if user_ref.exists:
            user_data = user_ref.to_dict()
            session["user"] = user_data  # Guardar en sesión
            
            return jsonify({
                "new_user": False,
                "name": user_data["name"],
                "role": user_data["role"]
            })

        # Si el usuario no existe, guardarlo en sesión temporal
        session["temp_user"] = {"uid": uid, "email": email}
        return jsonify({"new_user": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 401


orders = [
    {"id": "#20462", "product": "Hat", "productImage": "/static/images/placeholder.svg", "customer": "Matt Dickerson", "date": "13/05/2022", "amount": "$4.95", "paymentMode": "Transfer Bank", "status": "Delivered"},
    {"id": "#18933", "product": "Laptop", "productImage": "/static/images/placeholder.svg", "customer": "Wiktoria", "date": "22/05/2022", "amount": "$8.95", "paymentMode": "Cash on Delivery", "status": "Delivered"},
    {"id": "#45169", "product": "Phone", "productImage": "/static/images/placeholder.svg", "customer": "Trixie Byrd", "date": "15/06/2022", "amount": "$1,149.95", "paymentMode": "Cash on Delivery", "status": "Process"},
]

#####################
""" Public Routes """

@app.route('/')
def home():
    return render_template('public/home2.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    uid = session.get("temp_user", {}).get("uid")
    email = session.get("temp_user", {}).get("email")
    name = request.form.get("name")
    institution_id = request.form.get("institution_id")

    if not uid or not email or not name or not institution_id:
        return "Faltan datos", 400

    # Guardar en Firestore solo si no existe
    user_ref = db.collection("users").document(uid)
    if not user_ref.get().exists:
        user_ref.set({
            "email": email,
            "name": name,
            "role": "student",  
            "institution_id": institution_id
        })

    # Limpiar sesión temporal y guardar usuario en sesión normal
    session.pop("temp_user", None)
    session["user"] = {"email": email, "name": name, "role": "student"}

    return redirect(url_for('dashboard'))

@app.route('/home')
def home2():
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
    app.run(host='0.0.0.0', port=5000)
