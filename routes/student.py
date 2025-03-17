from flask import Blueprint, Flask, render_template, redirect, url_for, request, jsonify, flash, session

from routes.authentication import auth_required, role_required

student_bp = Blueprint("student", __name__)

@student_bp.before_request
@auth_required
@role_required("student")
def before_request():
    """Se ejecuta antes de cualquier ruta en este Blueprint."""
    pass

# Datos de ejemplo - en una aplicación real, esto vendría de una base de datos
mock_forms = [
    {"id": 1, "title": "Formulario de Intereses", "description": "Completa tus intereses académicos y profesionales"},
    {"id": 2, "title": "Test de Personalidad", "description": "Descubre tu tipo de personalidad"}
]

enrolled_classes = [
    {"id": 1, "name": "Introducción a la Programación", "instructor": "Prof. García", "schedule": "Lunes y Miércoles, 10:00 - 12:00"},
    {"id": 2, "name": "Diseño UX/UI", "instructor": "Prof. Martínez", "schedule": "Martes y Jueves, 14:00 - 16:00"},
]

user_profile = {
    "name": "Juan Pérez",
    "email": "juan.perez@ejemplo.com",
    "studentId": "ST12345",
    "program": "Ingeniería de Software",
    "semester": "3er Semestre"
}

# Rutas
@student_bp.route('/')
def home():
    return render_template('student/index.html', pending_forms=mock_forms)

@student_bp.route('/clases')
def classes():
    return render_template('student/clases.html', enrolled_classes=enrolled_classes)

@student_bp.route('/perfil')
def profile():
    return render_template('student/perfil.html', user_profile=user_profile)

@student_bp.route('/join-class', methods=['POST'])
def join_class():
    class_code = request.form.get('class_code')
    # Aquí iría la lógica para unirse a la clase con el código
    flash(f'Te has unido a la clase con código: {class_code}', 'success')
    return redirect(url_for('home'))
