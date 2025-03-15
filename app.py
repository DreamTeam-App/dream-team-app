from flask import Flask, redirect, render_template, request, make_response, session, abort, jsonify, url_for
import secrets
from functools import wraps
import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import timedelta
import os
from dotenv import load_dotenv
from routes.professor import professor_bp
from routes.authentication import *
load_dotenv()



app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Configure session cookie settings
app.config['SESSION_COOKIE_SECURE'] = True  # Ensure cookies are sent over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Adjust session expiration as needed
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Can be 'Strict', 'Lax', or 'None'


# Firebase Admin SDK setup
cred = credentials.Certificate("firebase-auth.json")
firebase_admin.initialize_app(cred)
db = firestore.client()



########################################
""" Authentication and Authorization """

# Decorator for routes that require authentication



@app.route('/auth', methods=['POST'])
def authorize():
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return "Unauthorized", 401

    token = token[7:]  # Strip off 'Bearer ' to get the actual token

    try:
        decoded_token = auth.verify_id_token(token, check_revoked=True, clock_skew_seconds=60) # Validate token here
        session['user'] = decoded_token # Add user to session
        return redirect(url_for('dashboard'))
    
    except:
        return "Unauthorized", 401

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
        return redirect(url_for('dashboard'))
    else:
        return render_template('public/login.html')

@app.route('/signup')
def signup():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('public/signup.html')


@app.route('/reset-password')
def reset_password():
    if 'user' in session:
        return redirect(url_for('dashboard'))
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





if __name__ == '__main__':
    app.run(debug=True)