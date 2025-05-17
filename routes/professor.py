import random
import string
from flask import Blueprint, flash, render_template, request, redirect, url_for, jsonify, session
from routes.authentication import *
from firebase_client import db  # Importa el cliente de Firestore centralizado
from firebase_admin import firestore
from ml.pipeline_utils import predecir_desempeno_equipo
from flask import request
import pandas as pd
from datetime import datetime


professor_bp = Blueprint("professor", __name__)

@professor_bp.before_request
@auth_required
@role_required("professor")
def before_request():
    """Se ejecuta antes de cualquier ruta en este Blueprint."""
    pass

# =====================================================
# Rutas de Vistas (render_template) y API combinadas
# =====================================================

# Ruta de índice: Muestra la lista de clases
@professor_bp.route('/index')
def index():
    try:
        # Obtener UID desde sesión
        if "user" in session and session["user"].get("uid"):
            uid = session["user"]["uid"]
        elif "temp_user" in session and session["temp_user"].get("uid"):
            uid = session["temp_user"]["uid"]
        else:
            flash("No se encontró el UID del usuario en la sesión.", "error")
            return redirect(url_for('home'))

        # Obtener perfil del usuario
        user_doc = db.collection('users').document(uid).get()
        if user_doc.exists:
            user = user_doc.to_dict()
            user["uid"] = uid
        else:
            flash("Perfil del profesor no encontrado.", "error")
            return redirect(url_for('home'))

        # Obtener solo las clases del profesor
        classes_ref = db.collection('classes').where('instructor_id', '==', uid)
        docs = classes_ref.get()
        classes = [doc.to_dict() for doc in docs]

    except Exception as e:
        flash(f"Error al obtener las clases: {e}", "error")
        classes = []
        user = {}

    return render_template('professor/index.html', classes=classes, user=user)



@professor_bp.route('/perfil')
def profile():
    # Intentar obtener el UID del usuario desde la sesión registrada o temporal
    uid = None
    if "user" in session and session["user"].get("uid"):
        uid = session["user"]["uid"]
    elif "temp_user" in session and session["temp_user"].get("uid"):
        uid = session["temp_user"]["uid"]

    if not uid:
        flash("No se encontró el UID del profesor en la sesión.", "error")
        return redirect(url_for('home'))  # Redirige al login o home, según corresponda

    # Consultar el documento del usuario en la colección "users"
    user_doc = db.collection('users').document(uid).get()
    if user_doc.exists:
        user_profile = user_doc.to_dict()
        user_profile["uid"] = uid  
    else:
        flash("Perfil del profesor no encontrado.", "error")
        user_profile = {}

    return render_template('professor/perfil.html', user_profile=user_profile)

# Ruta para crear una clase (usa formulario enviado vía POST)
@professor_bp.route('/create_class', methods=['POST'])
def create_class():
    try:
        if "user" in session and session["user"].get("uid"):
            uid = session["user"]["uid"]
        # Se obtienen los datos del formulario
        class_name = request.form.get('class_name')
        instructor = request.form.get('instructor')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        location = request.form.get('location')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        description = request.form.get('description')
        
        schedule = f"{start_time} - {end_time}"
        # Generar un join code aleatorio
        join_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        
        new_class = {
            "name": class_name,
            "instructor": instructor,
            "instructor_id" : uid,
            "schedule": schedule,
            "location": location,
            "start_date": start_date,
            "end_date": end_date,
            "description": description,
            "join_code": join_code
        }
        
        # Crear el documento en Firestore; se genera un ID automáticamente
        class_ref = db.collection('classes').document()
        new_class["id"] = class_ref.id
        class_ref.set(new_class)
        
        flash(f'Class "{class_name}" created successfully! Join code: {join_code}', 'success')
    except Exception as e:
        flash(f"Error creating class: {e}", "error")
    return redirect(url_for('professor.index'))

# Ruta para ver los detalles de una clase (incluye resumen de inscripciones y equipos)
@professor_bp.route('/class/<class_id>')
def class_details(class_id):
    try:
        # Obtener la referencia y documento de la clase
        class_ref = db.collection('classes').document(class_id)
        class_doc = class_ref.get()
        if not class_doc.exists:
            flash("La clase no se encontró en la base de datos.", "error")
            return redirect(url_for('professor.index'))
        class_data = class_doc.to_dict()

        # Consultar las primeras 5 inscripciones (estudiantes) para el resumen
        
        enrollments_ref = class_ref.collection('enrollments')
        enrollment_docs = enrollments_ref.get()
        enrollments = [doc.to_dict() for doc in enrollment_docs]

        # Consultar los primeros 3 equipos para el resumen
        teams_ref = class_ref.collection('teams')
        teams_docs = teams_ref.get()
        teams = [doc.to_dict() for doc in teams_docs]

        # Renderizar la plantilla y pasar "students" para que el template lo use
        return render_template('professor/class_details.html',
                               selected_class=class_data,
                               students=enrollments[:5],  # Aquí se pasa la lista de inscripciones como "students"
                               teams=teams[:5],
                               student_count=len(enrollments),
                               team_count=len(teams),
                               classes=[])  # Puedes pasar la lista completa de clases si es necesaria
    except Exception as e:
        flash(f"Error fetching class details: {e}", "error")
        return redirect(url_for('professor.index'))



# Ruta para mostrar todos los estudiantes (inscripciones) de una clase
@professor_bp.route('/class/<class_id>/students')
def students(class_id):
    try:
        # 1. Verificar que la clase exista
        class_ref = db.collection('classes').document(class_id)
        class_doc = class_ref.get()
        if not class_doc.exists:
            flash("La clase no se encontró en la base de datos.", "error")
            return redirect(url_for('professor.index'))

        selected_class = class_doc.to_dict()

        # 2. Obtener todos los documentos en la subcolección "enrollments"
        enrollments_ref = class_ref.collection('enrollments')
        enrollment_docs = enrollments_ref.get()

        # 2.1. Obtener todos los equipos de la clase y compilar un conjunto (set) de student_ids que ya tienen equipo
        teams_ref = class_ref.collection('teams')
        team_docs = teams_ref.get()
        students_in_team = set()
        for team_doc in team_docs:
            team_data = team_doc.to_dict()
            for member in team_data.get("members", []):
                # Se asume que en cada miembro se almacena "student_id"
                if "student_id" in member:
                    students_in_team.add(member["student_id"])

        # 3. Para cada inscripción, hacer un lookup en "users" para obtener más info del estudiante
        students = []
        for enroll_doc in enrollment_docs:
            enrollment_data = enroll_doc.to_dict()  # ej: { student_id: uid, status: "Active", ... }

            # Extraer el UID del estudiante
            student_id = enrollment_data.get("student_id")
            if not student_id:
                continue  # Omitir si no hay student_id

            # Agregar la propiedad in_team según si el estudiante ya pertenece a un equipo
            enrollment_data["in_team"] = (student_id in students_in_team)

            # 4. Buscar el documento del usuario en "users" con ese UID
            user_doc = db.collection('users').document(student_id).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                # Fusionar la información de la inscripción con la del usuario
                enrollment_data["id"] = student_id
                enrollment_data["name"] = user_data.get("name", "N/A")
                enrollment_data["avatar"] = user_data.get("avatar", "/static/images/placeholder.png")
                enrollment_data["email"] = user_data.get("email", "")
            else:
                # Valores por defecto si el usuario no existe en "users"
                enrollment_data["id"] = student_id
                enrollment_data["name"] = "Unknown User"
                enrollment_data["avatar"] = "/static/images/placeholder.png"
                enrollment_data["email"] = ""

            students.append(enrollment_data)

        # Definir valores predeterminados para paginación y búsqueda
        page = 1
        rows_per_page = 10
        search_term = ""
        total_pages = 1

        # Definir la lista de roles para la formación de equipos
        team_roles = [
            "Team Lead",
            "Project Manager",
            "Frontend Developer",
            "Backend Developer",
            "Full Stack Developer",
            "UI/UX Designer",
            "Database Administrator",
            "DevOps Engineer",
            "Quality Assurance",
            "Data Analyst",
            "Documentation Specialist",
            "Content Creator"
        ]

        return render_template(
            'professor/students.html',
            selected_class=selected_class,
            students=students,
            total_students=len(students),
            classes=[],             # Si tienes una lista completa de clases, pásala aquí
            page=page,
            rows_per_page=rows_per_page,
            search_term=search_term,
            total_pages=total_pages,
            team_roles=team_roles
        )

    except Exception as e:
        print("Error fetching students:", e)
        flash(f"Error fetching students: {e}", "error")
        return redirect(url_for('professor.index'))


# Ruta para eliminar un estudiante (acción dummy; en un caso real se eliminaría de Firestore)
@professor_bp.route('/delete_student/<student_id>')
def delete_student(student_id):
    class_id = request.args.get('class_id')
    flash(f"Student {student_id} deleted (dummy action)", "success")
    return redirect(url_for('professor.students', class_id=class_id))

# Ruta para eliminar un equipo (acción dummy)
@professor_bp.route('/delete_team/<team_id>')
def delete_team(team_id):
    class_id = request.args.get('class_id')
    flash(f"Team {team_id} deleted (dummy action)", "success")
    return redirect(url_for('professor.teams', class_id=class_id))

# Ruta para crear un equipo en una clase (usando datos del formulario)
@professor_bp.route('/create_team/<class_id>', methods=['POST'])
def create_team(class_id):
    try:
        team_name = request.form.get('team_name')
        team_project = request.form.get('team_project')
        selected_students = request.form.getlist('selected_students')
        
        members = []
        for student_id in selected_students:
            student_name = request.form.get(f'student_name_{student_id}')
            student_role = request.form.get(f'student_role_{student_id}')
            members.append({
                "student_id": student_id,
                "name": student_name,
                "role": student_role
            })

        # Crear el documento del equipo
        class_ref = db.collection('classes').document(class_id)
        team_ref = class_ref.collection('teams').document()
        new_team = {
            "name": team_name,
            "project": team_project,
            "members": members,
            "progress": 0,
            "grade": "N/A",
            "status": "Not Started",
            "id": team_ref.id
        }
        team_ref.set(new_team)

        # Actualizar la inscripción y el documento del usuario para cada estudiante
        for student_id in selected_students:
            # 1. Subcolección "enrollments"
            enrollment_ref = class_ref.collection('enrollments').document(student_id)
            enrollment_ref.update({"team_id": team_ref.id})

            # 2. Colección "users"
            user_ref = db.collection("users").document(student_id)
            user_doc = user_ref.get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                enrolled_classes = user_data.get("enrolled_classes", [])

                # Convertir strings en objetos {class_id: "xxx"}
                converted = []
                for item in enrolled_classes:
                    if isinstance(item, str):
                        # Convertir el string en un dict con la clave "class_id"
                        converted.append({"class_id": item})
                    elif isinstance(item, dict):
                        converted.append(item)
                    else:
                        # Por si acaso, ignorar o manejar tipos desconocidos
                        continue

                # Ahora 'converted' es una lista de objetos con al menos "class_id"
                found = False
                for c in converted:
                    if c.get("class_id") == class_id:
                        c["team_id"] = team_ref.id
                        found = True
                        break
                if not found:
                    converted.append({
                        "class_id": class_id,
                        "team_id": team_ref.id
                    })

                # Guardar la lista de vuelta en el doc del usuario
                user_ref.update({"enrolled_classes": converted})

        flash(f'Team "{team_name}" created successfully!', 'success')
        return redirect(url_for('professor.teams', class_id=class_id))
    except Exception as e:
        flash(f"Error creating team: {e}", "error")
        return redirect(url_for('professor.teams', class_id=class_id))




# Ruta para actualizar el rol de un miembro del equipo (vía formulario)
@professor_bp.route('/update_team_member_role/<class_id>/<team_id>', methods=['POST'])
def update_team_member_role(class_id, team_id):
    try:
        member_name = request.form.get('member_name')
        new_role = request.form.get('new_role')
        class_ref = db.collection('classes').document(class_id)
        team_ref = class_ref.collection('teams').document(team_id)
        team_doc = team_ref.get()
        if not team_doc.exists:
            flash("Team not found", "error")
            return redirect(url_for('professor.teams', class_id=class_id))
        team_data = team_doc.to_dict()
        updated = False
        for member in team_data.get('members', []):
            if member.get('name') == member_name:
                member['role'] = new_role
                updated = True
                break
        if updated:
            team_ref.update({'members': team_data.get('members')})
            flash(f"Role updated for {member_name}", "success")
        else:
            flash("Member not found", "error")
    except Exception as e:
        flash(f"Error updating team member role: {e}", "error")
    return redirect(url_for('professor.teams', class_id=class_id))

# Rutas adicionales: Logout y Edit Profile
@professor_bp.route('/logout')
def logout():
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('home'))

@professor_bp.route('/edit_profile')
def edit_profile():
    flash('Profile editing is not implemented in this demo', 'info')
    return redirect(url_for('professor.index'))


# Add this function to check if all students have teams
def all_students_have_teams(class_id):
    """Check if all students in a class have been assigned to a team"""
    try:
        class_ref = db.collection('classes').document(class_id)
        
        # Get all enrollments
        enrollments_ref = class_ref.collection('enrollments')
        enrollment_docs = enrollments_ref.get()
        
        # If there are no enrollments, return True (edge case)
        if not enrollment_docs:
            return True
            
        # Check each enrollment to see if they have a team_id
        for doc in enrollment_docs:
            enrollment_data = doc.to_dict()
            if not enrollment_data.get('team_id'):
                return False
                
        return True
    except Exception as e:
        print(f"Error checking if all students have teams: {e}")
        return False


# Función para verificar si todos los miembros del equipo han completado un formulario específico
def check_team_forms_completion(team_members, form_type):
    """
    Verifica si todos los miembros del equipo han completado un formulario específico
    
    Args:
        team_members: Lista de miembros del equipo con sus student_id
        form_type: Tipo de formulario a verificar ('personality' o 'team_roles')
        
    Returns:
        tuple: (todos_completados, lista_de_pendientes)
    """
    try:
        all_completed = True
        pending_members = []
        
        for member in team_members:
            student_id = member.get('student_id')
            student_name = member.get('name')
            
            # Buscar en la colección de formularios del usuario
            user_ref = db.collection('users').document(student_id)
            forms_ref = user_ref.collection('forms')
            
            # Consultar si existe un formulario del tipo especificado y si está completado
            form_query = forms_ref.where('form_type', '==', form_type).limit(1).get()
            
            form_completed = False
            if form_query:
                form_doc = form_query[0]
                form_data = form_doc.to_dict()
                form_completed = form_data.get('completed', False)
            
            if not form_completed:
                all_completed = False
                pending_members.append(student_name)
        
        return all_completed, pending_members
    
    except Exception as e:
        print(f"Error checking team forms completion: {e}")
        return False, []

@professor_bp.route('/team/<team_id>/details')
def team_details(team_id):
    try:
        # Se usa una query de grupo para buscar en todas las subcolecciones "teams"
        teams_query = db.collection_group('teams').where('id', '==', team_id)
        docs = teams_query.get()
        if not docs:
            return jsonify({'error': 'Team not found'}), 404
        
        team_doc = docs[0]  # Se asume que el ID de equipo es único
        team_data = team_doc.to_dict()
        
        # Se obtiene la referencia a la clase (padre del documento del equipo)
        class_ref = team_doc.reference.parent.parent
        enrollments_docs = class_ref.collection('enrollments').get()
        students = [doc.to_dict() for doc in enrollments_docs]
        
        # Buscar actividades que tienen este equipo en su array team_grades
        activities_ref = class_ref.collection('activities')
        activities_docs = activities_ref.get()
        
        team_activities = []
        for activity_doc in activities_docs:
            activity_data = activity_doc.to_dict()
            
            # Verificar si este equipo está en el array team_grades
            team_grades = activity_data.get('team_grades', [])
            team_grade_entry = next((grade for grade in team_grades if grade.get('team_id') == team_id), None)
            
            if team_grade_entry:
                # Esta actividad está asignada a este equipo
                activity_data['id'] = activity_doc.id
                activity_data['team_grade'] = team_grade_entry
                team_activities.append(activity_data)
        
        # Obtener información de coevaluaciones para cada actividad
        for activity in team_activities:
            activity_id = activity.get('id')
            
            # Verificar si la coevaluación está habilitada para esta actividad
            if activity.get('enable_coevaluation'):
                # Buscar coevaluaciones para esta actividad
                coevaluations_ref = class_ref.collection('activities').document(activity_id).collection('coevaluations')
                coevaluations = coevaluations_ref.get()
                
                # Identificar miembros que han completado la coevaluación
                completed_evaluators = []
                pending_evaluators = []
                
                for member in team_data.get('members', []):
                    student_id = member.get('student_id')
                    coevaluation_doc = coevaluations_ref.document(student_id).get()
                    
                    if coevaluation_doc.exists and coevaluation_doc.to_dict().get('submitted', False):
                        completed_evaluators.append(student_id)
                    else:
                        pending_evaluators.append(student_id)
                
                # Calcular estado de coevaluación
                total_members = len(team_data.get('members', []))
                coevaluation_percentage = 0
                if total_members > 0:
                    coevaluation_percentage = int((len(completed_evaluators) / total_members) * 100)
                
                activity['coevaluation_status'] = {
                    'completed': completed_evaluators,
                    'pending': pending_evaluators,
                    'percentage': coevaluation_percentage,
                    'all_completed': len(completed_evaluators) == total_members
                }
        
        member_details = []
        for member in team_data.get('members', []):
            # Se busca el estudiante correspondiente usando 'student_id'
            student = next((s for s in students if s.get('student_id') == member.get('student_id')), None)
            
            # Verificar si el miembro ha completado las coevaluaciones
            coevaluation_completed = {}
            for activity in team_activities:
                if activity.get('enable_coevaluation'):
                    activity_id = activity.get('id')
                    coevaluation_completed[activity_id] = member.get('student_id') in activity.get('coevaluation_status', {}).get('completed', [])
            
            if student:
                member_details.append({
                    'name': student.get('name'),
                    'avatar': student.get('avatar'),
                    'email': student.get('email'),
                    'role': member.get('role'),
                    'student_id': member.get('student_id'),
                    'coevaluation_completed': coevaluation_completed
                })
            else:
                member_details.append({
                    'name': member.get('name'),
                    'avatar': '/static/images/placeholder.png',
                    'email': 'No email available',
                    'role': member.get('role'),
                    'student_id': member.get('student_id'),
                    'coevaluation_completed': coevaluation_completed
                })
        
        return jsonify({
            'team': team_data, 
            'members': member_details,
            'activities': team_activities
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@professor_bp.route('/class/<class_id>/teams')
def teams(class_id):
    try:
        class_ref = db.collection('classes').document(class_id)
        teams_ref = class_ref.collection('teams')
        docs = teams_ref.get()
        teams = []
        
        # Obtener actividades para esta clase
        activities_ref = class_ref.collection('activities')
        activities_docs = activities_ref.get()
        activities = []
        
        for doc in activities_docs:
            activity_data = doc.to_dict()
            activity_data['id'] = doc.id
            activities.append(activity_data)
        
        # Para la formación de equipos, también se consultan los estudiantes inscritos
        enrollments_docs = class_ref.collection('enrollments').get()
        students = []
        for doc in enrollments_docs:
            data = doc.to_dict()
            # Aseguramos que la inscripción tenga el campo 'student_id'
            if "student_id" in data and "id" not in data:
                data["id"] = data["student_id"]
            students.append(data)
        
        # Procesar cada equipo
        for doc in docs:
            team_data = doc.to_dict()
            team_data['id'] = doc.id
            
            # Buscar actividades asignadas a este equipo
            team_activities = []
            for activity in activities:
                # Verificar si este equipo está en el array team_grades
                team_grades = activity.get('team_grades', [])
                team_grade_entry = next((grade for grade in team_grades if grade.get('team_id') == team_data['id']), None)
                
                if team_grade_entry:
                    # Esta actividad está asignada a este equipo
                    activity_copy = activity.copy()
                    activity_copy['team_grade'] = team_grade_entry
                    
                    # Verificar si la coevaluación está habilitada para esta actividad
                    if activity_copy.get('enable_coevaluation'):
                        activity_id = activity_copy.get('id')
                        
                        # Buscar coevaluaciones para esta actividad
                        coevaluations_ref = class_ref.collection('activities').document(activity_id).collection('coevaluations')
                        
                        # Identificar miembros que han completado la coevaluación
                        completed_evaluators = []
                        pending_evaluators = []
                        
                        for member in team_data.get('members', []):
                            student_id = member.get('student_id')
                            student_name = member.get('name')
                            coevaluation_doc = coevaluations_ref.document(student_id).get()
                            
                            if coevaluation_doc.exists and coevaluation_doc.to_dict().get('submitted', False):
                                completed_evaluators.append(student_id)
                            else:
                                pending_evaluators.append(student_name)
                        
                        # Calcular estado de coevaluación
                        total_members = len(team_data.get('members', []))
                        coevaluation_percentage = 0
                        if total_members > 0:
                            coevaluation_percentage = int((len(completed_evaluators) / total_members) * 100)
                        
                        activity_copy['coevaluation_status'] = {
                            'completed_count': len(completed_evaluators),
                            'total_count': total_members,
                            'percentage': coevaluation_percentage,
                            'all_completed': len(completed_evaluators) == total_members,
                            'pending_members': pending_evaluators
                        }
                    
                    # Verificar si todos los miembros han completado los formularios de personalidad y roles
                    personality_completed, personality_pending = check_team_forms_completion(
                        team_data.get('members', []), 'personality')
                    activity_copy['personality_forms_completed'] = personality_completed
                    activity_copy['personality_pending_members'] = personality_pending
                    
                    team_roles_completed, team_roles_pending = check_team_forms_completion(
                        team_data.get('members', []), 'team_roles')
                    activity_copy['team_roles_forms_completed'] = team_roles_completed
                    activity_copy['team_roles_pending_members'] = team_roles_pending
                    
                    team_activities.append(activity_copy)
            
            team_data['activities'] = team_activities
            teams.append(team_data)
        
        # Check if all students have teams
        all_students_in_team = all_students_have_teams(class_id)
        
        # Definir valores predeterminados para paginación y búsqueda
        page = 1
        rows_per_page = 10
        search_term = ""
        total_pages = 1

        return render_template('professor/teams.html',
                               selected_class=class_ref.get().to_dict(),
                               teams=teams,
                               total_teams=len(teams),
                               students=students,
                               classes=[],  # Si tienes una lista completa de clases, pásala aquí
                               page=page,
                               rows_per_page=rows_per_page,
                               search_term=search_term,
                               total_pages=total_pages,
                               all_students_in_team=all_students_in_team,
                               activities=activities)
    except Exception as e:
        flash(f"Error fetching teams: {e}", "error")
        return redirect(url_for('professor.index'))

@professor_bp.route('/team/<team_id>/predict-performance', methods=['POST'])
def predict_team_performance(team_id):
    try:
        # Obtener el class_id del request
        class_id = request.json.get('class_id')
        
        if not class_id:
            # Intentar obtener el class_id del referrer
            referrer = request.referrer
            if referrer and '/class/' in referrer:
                # Extract class_id from URL pattern like /professor/class/{class_id}/...
                parts = referrer.split('/')
                for i, part in enumerate(parts):
                    if part == 'class' and i+1 < len(parts):
                        class_id = parts[i+1].split('?')[0]
                        break
        
        if not class_id:
            return jsonify({'success': False, 'message': 'Se requiere el ID de la clase'}), 400
        
        # Obtener la referencia a la clase
        class_ref = db.collection('classes').document(class_id)
        class_doc = class_ref.get()
        
        if not class_doc.exists:
            return jsonify({'success': False, 'message': 'Clase no encontrada'}), 404
        
        # Verificar si el profesor es el dueño de la clase
        class_data = class_doc.to_dict()
        if not class_data or class_data.get('professor_id') != session.get('user_id'):
            return jsonify({'success': False, 'message': 'No tienes permiso para realizar esta acción'})
        
        # Obtener el equipo específico de la colección de equipos de la clase
        team_ref = class_ref.collection('teams').document(team_id)
        team_doc = team_ref.get()
        
        if not team_doc.exists:
            return jsonify({'success': False, 'message': 'Equipo no encontrado'}), 404
        
        team_data = team_doc.to_dict()
        
        # Obtener la actividad especificada en la solicitud
        activity_id = request.json.get('activity_id')
        if not activity_id:
            return jsonify({'success': False, 'message': 'Debe especificar una actividad para predecir el desempeño'})
        
        # Verificar que la actividad existe
        activity_ref = class_ref.collection('activities').document(activity_id)
        activity_doc = activity_ref.get()
        if not activity_doc.exists:
            return jsonify({'success': False, 'message': 'La actividad especificada no existe'})
        
        activity_data = activity_doc.to_dict()
        
        # Verificar si la coevaluación está habilitada para esta actividad
        if not activity_data.get('enable_coevaluation'):
            return jsonify({'success': False, 'message': 'Esta actividad no tiene evaluaciones del clima del equipo habilitadas'})
        
        # Verificar si este equipo está en el array team_grades de la actividad
        team_grades = activity_data.get('team_grades', [])
        team_grade_entry = next((grade for grade in team_grades if grade.get('team_id') == team_id), None)
        
        if not team_grade_entry:
            return jsonify({'success': False, 'message': 'Este equipo no está asignado a la actividad especificada'})
        
        # Verificar si la actividad ha sido calificada
        if not team_grade_entry.get('submitted', False):
            return jsonify({'success': False, 'message': 'La actividad debe ser calificada antes de predecir el desempeño'})
        
        # Obtener coevaluaciones para esta actividad y equipo
        coevaluations_ref = activity_ref.collection('coevaluations')
        
        # Obtener los miembros del equipo
        team_members = team_data.get('members', [])
        member_ids = [member.get('student_id') for member in team_members]
        
        # Verificar si todos los miembros han completado la coevaluación
        all_coevaluations = []
        completed_evaluators = []
        
        for member_id in member_ids:
            coevaluation_doc = coevaluations_ref.document(member_id).get()
            
            if coevaluation_doc.exists and coevaluation_doc.to_dict().get('submitted', False):
                completed_evaluators.append(member_id)
                coevaluation_data = coevaluation_doc.to_dict()
                coevaluation_data['student_id'] = member_id  # Aseguramos que el ID del estudiante esté en los datos
                all_coevaluations.append(coevaluation_data)
        
        if len(completed_evaluators) < len(member_ids):
            return jsonify({'success': False, 'message': 'No todos los miembros han completado la evaluación del clima del equipo'})
        
        # Verificar si todos los miembros han completado los formularios de personalidad y roles
        personality_completed, _ = check_team_forms_completion(team_members, 'personality')
        if not personality_completed:
            return jsonify({'success': False, 'message': 'No todos los miembros han completado el test de personalidad'})
        
        team_roles_completed, _ = check_team_forms_completion(team_members, 'team_roles')
        if not team_roles_completed:
            return jsonify({'success': False, 'message': 'No todos los miembros han completado el test de roles de equipo'})
        
        # Definir las características y sus rangos de ítems
        characteristics = {
            'Commitment': [2, 3],          # items 2-3
            'Communication': [4, 5],       # items 4-5
            'Motivation': [6, 7],          # items 6-7
            'GoalSetting': [8, 9],        # items 8-9
            'DiversityPerception': [10, 11], # items 10-11
            'EmotionalIntelligence': [12, 13], # items 12-13
            'Trust': [14, 15],             # items 14-15
            'WorkSatisfaction': [16, 17],  # items 16-17
            'Autonomy': [18, 19],          # items 18-19
            'ProcessIndicator': list(range(20, 27))   # items 20-26
        }
        
        # Estructura para almacenar el primer promedio (dentro de la misma respuesta)
        first_avg = {}  # (evaluador_id, evaluado_id, caracteristica) -> promedio
        individual_prom_scores = {}

        # Procesar cada coevaluación
        for coevaluation in all_coevaluations:
            evaluator_id = coevaluation.get('student_id')
            answers = coevaluation.get('answers', {})
            individual_prom_scores[evaluator_id] = answers.get("1", {})

            

            # Para cada característica, calcular el promedio de sus ítems
            for char_name, item_ids in characteristics.items():
                # Para cada miembro evaluado
                for evaluated_id in member_ids:
                    # Calcular el promedio de los ítems para esta característica
                    total_score = 0
                    count = 0
                    
                    for item_id in item_ids:
                        item_id_str = str(item_id)
                        if item_id_str in answers and evaluated_id in answers[item_id_str] and (item_id <= 19):
                            try:
                                score = float(answers[item_id_str][evaluated_id])
                                total_score += score
                                count += 1
                            except (ValueError, TypeError):
                                # Ignorar valores no numéricos
                                pass
                        if item_id > 19:
                            score = float(answers.get(item_id_str, {}))
                            total_score += score
                            count += 1

                    # Si hay al menos un ítem válido, calcular el promedio
                    if count > 0:
                        avg_score = total_score / count
                        first_avg[(evaluator_id, evaluated_id, char_name)] = avg_score
        
        # Estructura para almacenar el segundo promedio (entre todas las respuestas recibidas)
        second_avg = {}  # (evaluado_id, caracteristica) -> promedio
        
        # Para cada miembro evaluado y cada característica
        for evaluated_id in member_ids:
            for char_name in characteristics.keys():
                # Recopilar todos los promedios de primera etapa para este evaluado y característica
                scores = []
                for key, score in first_avg.items():
                    if key[1] == evaluated_id and key[2] == char_name:
                        scores.append(score)
                
                # Calcular el promedio de segunda etapa
                if scores:
                    second_avg[(evaluated_id, char_name)] = sum(scores) / len(scores)
                else:
                    second_avg[(evaluated_id, char_name)] = 0
        
        # Calcular el promedio de equipo para cada característica
        team_metrics = {}
        for char_name in characteristics.keys():
            char_scores = []
            for evaluated_id in member_ids:
                char_scores.append(second_avg.get((evaluated_id, char_name), 0))
            
            if char_scores:
                team_metrics[char_name] = sum(char_scores) / len(char_scores)
            else:
                team_metrics[char_name] = 0
        
        # Calcular el promedio ponderado del equipo
        prom_ponderado = sum(team_metrics.values()) / len(team_metrics) if team_metrics else 0
        
        # Crear factores para la respuesta
        factors = [
            {'name': 'Prom. Ponderado', 'value': f'{prom_ponderado:.2f}'},
        ]
        
        for characteristic, value in team_metrics.items():
            factors.append({'name': characteristic, 'value': f'{value:.2f}'})
        
        # Obtener forms_summary para cada miembro del equipo
        member_data = []
        for member in team_members:
            member_id = member.get('student_id')
            user_ref = db.collection('users').document(member_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                forms_summary = user_data.get('forms_summary', {})
                
                # Obtener las métricas individuales para este miembro
                member_metrics = {
                    char_name: second_avg.get((member_id, char_name), 0)
                    for char_name in characteristics.keys()
                }
                
                # Crear un diccionario con los datos del miembro en el orden especificado
                member_info = {
                    'student_id': member_id,
                    'prom_ponderado': individual_prom_scores.get(member_id, 0),
                    'team_id': team_id,
                    'MBTI': forms_summary.get('MBTI', ''),
                    'Organizer': forms_summary.get('Organizer', 0),
                    'Doer': forms_summary.get('Doer', 0),
                    'Challenger': forms_summary.get('Challenger', 0),
                    'Innovator': forms_summary.get('Innovator', 0),
                    'TeamBuilder': forms_summary.get('TeamBuilder', 0),
                    'Connector': forms_summary.get('Connector', 0),
                    'Equipo ID': team_data.get('name', 'Unknown Team'),
                    'Commitment': member_metrics.get('Commitment', 0),
                    'Communication': member_metrics.get('Communication', 0),
                    'Motivation': member_metrics.get('Motivation', 0),
                    'GoalSetting': member_metrics.get('GoalSetting', 0),
                    'DiversityPerception': member_metrics.get('DiversityPerception', 0),
                    'EmotionalIntelligence': member_metrics.get('EmotionalIntelligence', 0),
                    'Trust': member_metrics.get('Trust', 0),
                    'WorkSatisfaction': member_metrics.get('WorkSatisfaction', 0),
                    'Autonomy': member_metrics.get('Autonomy', 0),
                    'ProcessIndicator': member_metrics.get('ProcessIndicator', 0)
                }
                
                member_data.append(member_info)
        
        # Generar CSV
        import csv
        import io
        import os
        from datetime import datetime
        
        # Crear un buffer en memoria para el CSV
        csv_buffer = io.StringIO()
        
        # Definir el orden exacto de las columnas
        fieldnames = [
            'student_id',
            'prom_ponderado',
            'team_id',
            'MBTI',
            'Organizer',
            'Doer',
            'Challenger',
            'Innovator',
            'TeamBuilder',
            'Connector',
            'Equipo ID',
            'Commitment',
            'Communication',
            'Motivation',
            'GoalSetting',
            'DiversityPerception',
            'EmotionalIntelligence',
            'Trust',
            'WorkSatisfaction',
            'Autonomy',
            'ProcessIndicator'
        ]
        
        # Crear el escritor CSV con el orden específico de columnas
        csv_writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
        
        # Escribir la cabecera y las filas
        csv_writer.writeheader()
        for member in member_data:
            csv_writer.writerow(member)
        
        # Obtener el contenido del CSV
        csv_content = csv_buffer.getvalue()
        
        # Crear un nombre de archivo para el CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"team_{team_id}_performance_{timestamp}.csv"
        
        # Guardar el CSV en el sistema de archivos (opcional)
        # Asegúrate de que la carpeta exista
        csv_dir = os.path.join(os.getcwd(), 'static', 'reports')
        os.makedirs(csv_dir, exist_ok=True)
        
        csv_path = os.path.join(csv_dir, csv_filename)
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            f.write(csv_content)
        
        # Guardar la referencia al CSV en la base de datos
        csv_data = {
            'team_id': team_id,
            'team_name': team_data.get('name', 'Unknown Team'),
            'activity_id': activity_id,
            'class_id': class_id,
            'filename': csv_filename,
            'path': csv_path,
            'created_at': firestore.SERVER_TIMESTAMP,
            'member_count': len(member_data)
        }
        
        # Guardar en Firestore
        report_ref = class_ref.collection('performance_reports').document()
        report_ref.set(csv_data)
        
        # Actualizar el progreso del equipo en la base de datos
        # Usamos el promedio ponderado como progreso (escala 0-5 convertida a 0-100)
        df_equipo = pd.read_csv(csv_path)
        new_progress = -1
        try:
            pred = predecir_desempeno_equipo(df_equipo)
            new_progress = round(pred*100,2)
        except Exception as e:
            # Aquí capturas cualquier error de transformación o del modelo
            print(f" Error al predecir modelo: {e}")
        team_ref.update({
            'progress': new_progress,
            'last_prediction': firestore.SERVER_TIMESTAMP,
            'performance_metrics': team_metrics,
            'prom_ponderado': prom_ponderado,
            'last_report_id': report_ref.id
        })
        
        # También actualizar el progreso en la actividad
        updated_team_grades = []
        for grade in team_grades:
            if grade.get('team_id') == team_id:
                grade['predicted_performance'] = new_progress
                grade['performance_metrics'] = team_metrics
                grade['prom_ponderado'] = prom_ponderado
            updated_team_grades.append(grade)
        
        activity_ref.update({
            'team_grades': updated_team_grades
        })
        
        # Crear URL para descargar el CSV
        csv_url = f"/static/reports/{csv_filename}"
        
        return jsonify({
            'success': True,
            'new_progress': new_progress,
            'factors': factors,
            'prom_ponderado': prom_ponderado,
            'message': 'Reporte CSV generado con éxito. Se ha guardado el análisis completo incluyendo datos de personalidad y roles de equipo.',
            'report_id': report_ref.id,
            'csv_url': csv_url,
            'filename': csv_filename
        })
    except Exception as e:
        print(f"Error en predict_team_performance: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    
@professor_bp.route('/class/<class_id>/activities')
def activities(class_id):
    try:
        class_ref = db.collection('classes').document(class_id)
        class_doc = class_ref.get()

        if not class_doc.exists:
            flash("Class not found", "error")
            return redirect(url_for('professor.index'))

        #  Obtener estudiantes desde la colección enrollments
        enrollments_docs = class_ref.collection('enrollments').get()
        students = []
        for doc in enrollments_docs:
            data = doc.to_dict()
            if "student_id" in data and "id" not in data:
                data["id"] = data["student_id"]
            students.append(data)

        student_count = len(students)

        #  Obtener actividades
        activities_ref = class_ref.collection('activities')
        activities_docs = activities_ref.get()
        activities = [doc.to_dict() for doc in activities_docs]

        #  Verificar si todos los estudiantes tienen equipo
        all_students_in_team = all_students_have_teams(class_id)

        return render_template('professor/activities.html',
                               selected_class=class_doc.to_dict(),
                               activities=activities,
                               student_count=student_count,
                               all_students_in_team=all_students_in_team,
                               classes=[])  # Si tienes otras clases, pásalas aquí

    except Exception as e:
        flash(f"Error fetching activities: {e}", "error")
        return redirect(url_for('professor.index'))



# Add routes for activities
@professor_bp.route('/create_activity/<class_id>', methods=['POST'])
def create_activity(class_id):
    try:
        # Check if all students have teams
        if not all_students_have_teams(class_id):
            flash("All students must be assigned to a team before creating an activity.", "error")
            return redirect(url_for('professor.teams', class_id=class_id))
        
        # Get form data
        activity_name = request.form.get('activity_name')
        activity_description = request.form.get('activity_description')
        due_date = request.form.get('due_date')
        max_grade = request.form.get('max_grade', 100)
        enable_coevaluation = 'enable_coevaluation' in request.form
        
        # Create activity document
        class_ref = db.collection('classes').document(class_id)
        activity_ref = class_ref.collection('activities').document()
        
        # Get all teams for this class
        teams_ref = class_ref.collection('teams')
        team_docs = teams_ref.get()
        
        # Create team_grades array with an entry for each team
        team_grades = []
        for team_doc in team_docs:
            team_data = team_doc.to_dict()
            team_grades.append({
                'team_id': team_data.get('id'),
                'team_name': team_data.get('name'),
                'grade': 0,
                'feedback': '',
                'submitted': False,
                'submission_date': None
            })
        
        # Create activity document
        activity_data = {
            'id': activity_ref.id,
            'name': activity_name,
            'description': activity_description,
            'due_date': due_date,
            'max_grade': int(max_grade),
            'enable_coevaluation': enable_coevaluation,
            'status': 'Open',
            'created_at': firestore.SERVER_TIMESTAMP,
            'team_grades': team_grades
        }
        
        activity_ref.set(activity_data)
        
        # If co-evaluation is enabled, create co-evaluation documents for each team member
        if enable_coevaluation:
            for team_doc in team_docs:
                team_data = team_doc.to_dict()
                team_id = team_data.get('id')
                
                # Create co-evaluation subcollection for this activity
                coevaluation_ref = activity_ref.collection('coevaluations')
                
                # For each team member, create a co-evaluation document
                for member in team_data.get('members', []):
                    student_id = member.get('student_id')
                    
                    # Create evaluation criteria for each team member
                    evaluation_criteria = []
                    for other_member in team_data.get('members', []):
                        other_student_id = other_member.get('student_id')
                        if student_id != other_student_id:
                            evaluation_criteria.append({
                                'student_id': other_student_id,
                                'student_name': other_member.get('name'),
                                'criteria': [
                                    {'name': 'Contribution', 'score': 0, 'max_score': 5},
                                    {'name': 'Communication', 'score': 0, 'max_score': 5},
                                    {'name': 'Problem Solving', 'score': 0, 'max_score': 5},
                                    {'name': 'Technical Skills', 'score': 0, 'max_score': 5},
                                    {'name': 'Teamwork', 'score': 0, 'max_score': 5}
                                ],
                                'comments': ''
                            })
                    
                    # Add self-evaluation
                    self_evaluation = {
                        'criteria': [
                            {'name': 'Contribution', 'score': 0, 'max_score': 5},
                            {'name': 'Communication', 'score': 0, 'max_score': 5},
                            {'name': 'Problem Solving', 'score': 0, 'max_score': 5},
                            {'name': 'Technical Skills', 'score': 0, 'max_score': 5},
                            {'name': 'Teamwork', 'score': 0, 'max_score': 5}
                        ],
                        'comments': ''
                    }
                    
                    # Create co-evaluation document
                    coevaluation_data = {
                        'student_id': student_id,
                        'student_name': member.get('name'),
                        'team_id': team_id,
                        'team_name': team_data.get('name'),
                        'submitted': False,
                        'submission_date': None,
                        'evaluation_criteria': evaluation_criteria,
                        'self_evaluation': self_evaluation
                    }
                    
                    coevaluation_ref.document(student_id).set(coevaluation_data)
        
        flash(f'Activity "{activity_name}" created successfully!', 'success')
        return redirect(url_for('professor.activities', class_id=class_id))
    except Exception as e:
        flash(f"Error creating activity: {e}", "error")
        return redirect(url_for('professor.activities', class_id=class_id))

@professor_bp.route('/activity/<class_id>/<activity_id>')
def activity_details(class_id, activity_id):
    try:
        class_ref = db.collection('classes').document(class_id)
        activity_ref = class_ref.collection('activities').document(activity_id)
        activity_doc = activity_ref.get()
        
        if not activity_doc.exists:
            flash("Activity not found", "error")
            return redirect(url_for('professor.teams', class_id=class_id))
            
        activity_data = activity_doc.to_dict()
        
        # Get co-evaluation data if enabled
        coevaluation_summary = None
        if activity_data.get('enable_coevaluation'):
            coevaluation_ref = activity_ref.collection('coevaluations')
            coevaluation_docs = coevaluation_ref.get()
            coevaluations = [doc.to_dict() for doc in coevaluation_docs]
            
            # Calculate summary statistics for co-evaluations
            coevaluation_summary = calculate_coevaluation_summary(coevaluations)
        
        return render_template('professor/activity_details.html',
                              selected_class=class_ref.get().to_dict(),
                              activity=activity_data,
                              coevaluation_summary=coevaluation_summary)
    except Exception as e:
        flash(f"Error fetching activity details: {e}", "error")
        return redirect(url_for('professor.teams', class_id=class_id))

@professor_bp.route('/enable_coevaluation/<class_id>/<activity_id>')
def enable_coevaluation(class_id, activity_id):
    try:
        # Verificar que la clase y la actividad existan
        class_ref = db.collection('classes').document(class_id)
        activity_ref = class_ref.collection('activities').document(activity_id)
        
        class_doc = class_ref.get()
        activity_doc = activity_ref.get()
        
        if not class_doc.exists or not activity_doc.exists:
            flash("Clase o actividad no encontrada", "error")
            return redirect(url_for('professor.activities', class_id=class_id))
        
        activity_data = activity_doc.to_dict()
        
        # Verificar si la coevaluación ya está habilitada
        if activity_data.get('enable_coevaluation'):
            flash("La evaluación del clima del equipo ya está habilitada para esta actividad", "info")
            return redirect(url_for('professor.activities', class_id=class_id))
        
        # Obtener todos los equipos de la clase
        teams_ref = class_ref.collection('teams')
        teams = teams_ref.get()
        
        # Para cada equipo, crear registros de coevaluación para cada miembro
        for team_doc in teams:
            team_data = team_doc.to_dict()
            team_id = team_doc.id
            
            # Obtener los miembros del equipo
            team_members = team_data.get('members', [])
            
            # Para cada miembro del equipo, crear un registro en su subcolección "forms"
            for member in team_members:
                student_id = member.get('student_id')
                student_name = member.get('name')
                
                user_ref = db.collection('users').document(student_id)
                forms_ref = user_ref.collection('forms')
                
                form_doc_ref = forms_ref.document()
                form_data = {
                    "form_id": form_doc_ref.id,
                    "form_type": "coevaluation",
                    "title": f"Evaluación del clima del equipo: {activity_data.get('name')}",
                    "description": f"Evaluación cruzada del clima del equipo para la actividad {activity_data.get('name')}",
                    "url": f"/student/coevaluation/{class_id}/{activity_id}",
                    "activity_id": activity_id,
                    "class_id": class_id,
                    "team_id": team_id,
                    "team_members": team_members,  # Incluye los datos de los miembros del equipo
                    "completed": False,
                    "completed_at": None,
                    "assigned_at": firestore.SERVER_TIMESTAMP
                }
                form_doc_ref.set(form_data)
                
                # También crear un documento en la colección de coevaluaciones de la actividad
                coevaluation_ref = activity_ref.collection('coevaluations').document(student_id)
                coevaluation_data = {
                    "student_id": student_id,
                    "student_name": student_name,
                    "team_id": team_id,
                    "team_name": team_data.get('name'),
                    "submitted": False,
                    "submission_date": None,
                    "answers": {}
                }
                coevaluation_ref.set(coevaluation_data)
        
        # Actualizar la actividad para habilitar la coevaluación
        activity_ref.update({
            'enable_coevaluation': True,
            'coevaluation_enabled_at': firestore.SERVER_TIMESTAMP
        })
        
        flash("Evaluación del clima del equipo habilitada correctamente para esta actividad", "success")
        return redirect(url_for('professor.activities', class_id=class_id))
    
    except Exception as e:
        flash(f"Error al habilitar la evaluación del clima del equipo: {e}", "error")
        return redirect(url_for('professor.activities', class_id=class_id))

@professor_bp.route('/delete_activity/<class_id>/<activity_id>')
def delete_activity(class_id, activity_id):
    try:
        class_ref = db.collection('classes').document(class_id)
        activity_ref = class_ref.collection('activities').document(activity_id)
        
        # Delete co-evaluations subcollection if it exists
        coevaluation_ref = activity_ref.collection('coevaluations')
        coevaluation_docs = coevaluation_ref.get()
        for doc in coevaluation_docs:
            doc.reference.delete()
        
        # Delete activity document
        activity_ref.delete()
        
        flash("Activity deleted successfully", "success")
        return redirect(url_for('professor.teams', class_id=class_id))
    except Exception as e:
        flash(f"Error deleting activity: {e}", "error")
        return redirect(url_for('professor.teams', class_id=class_id))

@professor_bp.route('/grade_team/<class_id>/<activity_id>', methods=['POST'])
def grade_team(class_id, activity_id):
    try:
        # Obtener datos del formulario
        team_id = request.form.get('team_id')
        grade = request.form.get('grade')
        feedback = request.form.get('feedback', '')

        if not team_id or not grade:
            flash("Faltan campos requeridos", "error")
            return redirect(url_for('professor.activity_details', class_id=class_id, activity_id=activity_id))

        grade = int(grade)

        # Obtener referencias
        class_ref = db.collection('classes').document(class_id)
        activity_ref = class_ref.collection('activities').document(activity_id)
        activity_doc = activity_ref.get()

        if not activity_doc.exists:
            flash("Actividad no encontrada", "error")
            return redirect(url_for('professor.teams', class_id=class_id))

        activity_data = activity_doc.to_dict()
        team_grades = activity_data.get('team_grades', [])

        # Buscar o insertar calificación del equipo
        updated = False
        for team_grade in team_grades:
            if str(team_grade.get('team_id')) == str(team_id):
                team_grade['grade'] = grade
                team_grade['feedback'] = feedback
                team_grade['submitted'] = True
                team_grade['submission_date'] = datetime.utcnow()
                updated = True
                break

        if not updated:
            team_grades.append({
                'team_id': team_id,
                'grade': grade,
                'feedback': feedback,
                'submitted': True,
                'submission_date': datetime.utcnow(),
                'team_name': ''  # opcional
            })

        # Guardar cambios en la actividad
        activity_ref.update({'team_grades': team_grades})

        # Actualizar documento del equipo (opcional)
        teams_ref = class_ref.collection('teams')
        team_docs = teams_ref.where('id', '==', team_id).limit(1).get()
        if team_docs:
            team_docs[0].reference.update({
                'grade': f"{grade}/{activity_data.get('max_grade')}"
            })

        flash("¡Calificación guardada correctamente!", "success")
        return redirect(url_for('professor.activity_details', class_id=class_id, activity_id=activity_id))

    except Exception as e:
        flash(f"Error al guardar la calificación: {e}", "error")
        return redirect(url_for('professor.activity_details', class_id=class_id, activity_id=activity_id))


# Nueva ruta para calificar una actividad desde la vista de equipos
@professor_bp.route('/team/<team_id>/activity/<activity_id>/grade', methods=['POST'])
def grade_activity(team_id, activity_id):
    try:
        # Get form data
        grade = request.form.get('grade')
        feedback = request.form.get('feedback', '')
        
        if not grade:
            return jsonify({'success': False, 'message': 'La calificación es obligatoria'}), 400
        
        # Convert grade to float
        try:
            grade = float(grade)
        except ValueError:
            return jsonify({'success': False, 'message': 'La calificación debe ser un número válido'}), 400
        
        # Extract class_id from the referrer URL
        referrer = request.referrer
        class_id = None
        
        if referrer and '/class/' in referrer:
            # Extract class_id from URL pattern like /professor/class/{class_id}/...
            parts = referrer.split('/')
            for i, part in enumerate(parts):
                if part == 'class' and i+1 < len(parts):
                    class_id = parts[i+1].split('?')[0]
                    break
        
        # If we couldn't get class_id from referrer, try to find the activity
        if not class_id:
            # Find the activity document using a collection group query
            activities_query = db.collection_group('activities').where(firestore.field_path.FieldPath.document_id(), '==', activity_id)
            activity_docs = activities_query.get()
            
            if not activity_docs:
                return jsonify({'success': False, 'message': 'Actividad no encontrada'}), 404
            
            # Get the class_id from the activity's reference path
            activity_doc = activity_docs[0]
            class_id = activity_doc.reference.parent.parent.id
        
        # Now we have the class_id, we can directly access the activity document
        class_ref = db.collection('classes').document(class_id)
        activity_ref = class_ref.collection('activities').document(activity_id)
        activity_doc = activity_ref.get()
        
        if not activity_doc.exists:
            return jsonify({'success': False, 'message': 'Actividad no encontrada'}), 404
        
        activity_data = activity_doc.to_dict()
        max_grade = activity_data.get('max_grade', 100)
        
        # Get the team_grades array
        team_grades = activity_data.get('team_grades', [])
        
        # Find and update the specific team's grade in the array
        updated = False
        for i, team_grade in enumerate(team_grades):
            if team_grade.get('team_id') == team_id:
                # Update the existing team grade entry
                team_grades[i] = {
                    'team_id': team_id,
                    'team_name': team_grade.get('team_name', 'Unknown Team'),
                    'grade': grade,
                    'feedback': feedback,
                    'submitted': True,
                    'submission_date': firestore.SERVER_TIMESTAMP
                }
                updated = True
                break
        
        if not updated:
            # If the team wasn't found in the array, get the team name and add a new entry
            team_ref = class_ref.collection('teams').document(team_id)
            team_doc = team_ref.get()
            
            team_name = "Unknown Team"
            if team_doc.exists:
                team_data = team_doc.to_dict()
                team_name = team_data.get('name', 'Unknown Team')
            
            # Add new entry to team_grades array
            team_grades.append({
                'team_id': team_id,
                'team_name': team_name,
                'grade': grade,
                'feedback': feedback,
                'submitted': True,
                'submission_date': firestore.SERVER_TIMESTAMP
            })
        
        # Update the activity document with the modified team_grades array
        activity_ref.update({'team_grades': team_grades})
        
        # Also update the team document with the latest grade
        team_ref = class_ref.collection('teams').document(team_id)
        team_doc = team_ref.get()
        
        if team_doc.exists:
            team_ref.update({'grade': f"{grade}/{max_grade}"})
        
        return jsonify({
            'success': True,
            'message': 'Calificación guardada correctamente',
            'grade': grade,
            'max_grade': max_grade,
            'feedback': feedback
        })
    
    except Exception as e:
        print(f"Error saving grade: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# Helper function to calculate co-evaluation summary
def calculate_coevaluation_summary(coevaluations):
    """Calculate summary statistics for co-evaluations"""
    if not coevaluations:
        return None
        
    summary = {
        'total_students': len(coevaluations),
        'submitted_count': 0,
        'submission_rate': 0,
        'average_scores': {},
        'student_summaries': []
    }
    
    # Count submitted evaluations
    for evaluation in coevaluations:
        if evaluation.get('submitted'):
            summary['submitted_count'] += 1
    
    # Calculate submission rate
    if summary['total_students'] > 0:
        summary['submission_rate'] = (summary['submitted_count'] / summary['total_students']) * 100
    
    # Calculate average scores for each student
    for evaluation in coevaluations:
        student_id = evaluation.get('student_id')
        student_name = evaluation.get('student_name')
        
        # Skip if not submitted
        if not evaluation.get('submitted'):
            continue
        
        # Calculate average scores from peer evaluations
        peer_scores = {}
        peer_count = 0
        
        for peer_eval in evaluation.get('evaluation_criteria', []):
            peer_count += 1
            for criterion in peer_eval.get('criteria', []):
                criterion_name = criterion.get('name')
                criterion_score = criterion.get('score', 0)
                
                if criterion_name not in peer_scores:
                    peer_scores[criterion_name] = 0
                
                peer_scores[criterion_name] += criterion_score
        
        # Calculate self-evaluation scores
        self_scores = {}
        for criterion in evaluation.get('self_evaluation', {}).get('criteria', []):
            criterion_name = criterion.get('name')
            criterion_score = criterion.get('score', 0)
            self_scores[criterion_name] = criterion_score
        
        # Calculate averages
        avg_peer_scores = {}
        if peer_count > 0:
            for criterion_name, total_score in peer_scores.items():
                avg_peer_scores[criterion_name] = total_score / peer_count
        
        # Add to student summaries
        student_summary = {
            'student_id': student_id,
            'student_name': student_name,
            'peer_scores': avg_peer_scores,
            'self_scores': self_scores
        }
        
        summary['student_summaries'].append(student_summary)
        
        # Update global averages
        for criterion_name, avg_score in avg_peer_scores.items():
            if criterion_name not in summary['average_scores']:
                summary['average_scores'][criterion_name] = {
                    'total': 0,
                    'count': 0,
                    'average': 0
                }
            
            summary['average_scores'][criterion_name]['total'] += avg_score
            summary['average_scores'][criterion_name]['count'] += 1
    
    # Calculate final averages
    for criterion_name, data in summary['average_scores'].items():
        if data['count'] > 0:
            data['average'] = data['total'] / data['count']
    
    return summary

@professor_bp.route('/evaluar_equipo', methods=["POST"])
def evaluar_equipo():
    try:
        datos_equipo = request.get_json()
        df_equipo = pd.DataFrame(datos_equipo)

        resultado = predecir_desempeno_equipo(df_equipo)
        return {"success": True, "prediccion": round(resultado, 2)}

    except Exception as e:
        return {"success": False, "error": str(e)}, 500