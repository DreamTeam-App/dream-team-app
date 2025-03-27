# firebase_client.py
import firebase_admin
from firebase_admin import credentials, firestore

# Inicializar Firebase Admin con tus credenciales
cred = credentials.Certificate("firebase-auth.json")
firebase_admin.initialize_app(cred)

# Crear y exportar el cliente de Firestore
db = firestore.client()
