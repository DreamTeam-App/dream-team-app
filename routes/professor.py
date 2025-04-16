import random
import string
from flask import Blueprint, flash, render_template, request, redirect, url_for, jsonify, session
from routes.authentication import *
from firebase_client import db  # Importa el cliente de Firestore centralizado
from firebase_admin import firestore

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
        classes_ref = db.collection('classes')
        docs = classes_ref.get()
        classes = [doc.to_dict() for doc in docs]
    except Exception as e:
        flash(f"Error fetching classes: {e}", "error")
        classes = []
    return render_template('professor/index.html', classes=classes)

# Ruta para crear una clase (usa formulario enviado vía POST)
@professor_bp.route('/create_class', methods=['POST'])
def create_class():
    try:
        # Se obtienen los datos del formulario
        class_name = request.form.get('class_name')
        instructor = request.form.get('instructor')
        schedule = request.form.get('schedule')
        location = request.form.get('location')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        description = request.form.get('description')
        
        # Generar un join code aleatorio
        join_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        
        new_class = {
            "name": class_name,
            "instructor": instructor,
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
        enrollments_ref = class_ref.collection('enrollments').limit(5)
        enrollment_docs = enrollments_ref.get()
        enrollments = [doc.to_dict() for doc in enrollment_docs]

        # Consultar los primeros 3 equipos para el resumen
        teams_ref = class_ref.collection('teams').limit(3)
        teams_docs = teams_ref.get()
        teams = [doc.to_dict() for doc in teams_docs]

        # Renderizar la plantilla y pasar "students" para que el template lo use
        return render_template('professor/class_details.html',
                               selected_class=class_data,
                               students=enrollments,  # Aquí se pasa la lista de inscripciones como "students"
                               teams_summary=teams,
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
        
        member_details = []
        for member in team_data.get('members', []):
            # Se busca el estudiante correspondiente usando 'student_id'
            student = next((s for s in students if s.get('student_id') == member.get('student_id')), None)
            if student:
                member_details.append({
                    'name': student.get('name'),
                    'avatar': student.get('avatar'),
                    'email': student.get('email'),
                    'role': member.get('role')
                })
            else:
                member_details.append({
                    'name': member.get('name'),
                    'avatar': '/static/images/placeholder.png',
                    'email': 'No email available',
                    'role': member.get('role')
                })
        return jsonify({'team': team_data, 'members': member_details})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
            "progress": "0%",
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

# Modify the teams route to check if all students have teams
@professor_bp.route('/class/<class_id>/teams')
def teams(class_id):
    try:
        class_ref = db.collection('classes').document(class_id)
        teams_ref = class_ref.collection('teams')
        docs = teams_ref.get()
        teams = [doc.to_dict() for doc in docs]
        
        # Para la formación de equipos, también se consultan los estudiantes inscritos
        enrollments_docs = class_ref.collection('enrollments').get()
        students = []
        for doc in enrollments_docs:
            data = doc.to_dict()
            # Aseguramos que la inscripción tenga el campo 'student_id'
            if "student_id" in data and "id" not in data:
                data["id"] = data["student_id"]
            students.append(data)
        
        # Check if all students have teams
        all_students_in_team = all_students_have_teams(class_id)
        
        # Get activities for this class
        activities_ref = class_ref.collection('activities')
        activities_docs = activities_ref.get()
        activities = [doc.to_dict() for doc in activities_docs]
        
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

@professor_bp.route('/class/<class_id>/activities')
def activities(class_id):
    try:
        class_ref = db.collection('classes').document(class_id)
        class_doc = class_ref.get()
        
        if not class_doc.exists:
            flash("Class not found", "error")
            return redirect(url_for('professor.index'))
            
        # Get activities for this class
        activities_ref = class_ref.collection('activities')
        activities_docs = activities_ref.get()
        activities = [doc.to_dict() for doc in activities_docs]
        
        # Check if all students have teams
        all_students_in_team = all_students_have_teams(class_id)
        
        return render_template('professor/activities.html',
                              selected_class=class_doc.to_dict(),
                              activities=activities,
                              all_students_in_team=all_students_in_team,
                              classes=[])  # If you have a list of classes, pass it here
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
            flash("La coevaluación ya está habilitada para esta actividad", "info")
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
                    "title": f"Coevaluación: {activity_data.get('name')}",
                    "description": f"Evaluación cruzada de trabajo en equipo para la actividad {activity_data.get('name')}",
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
        
        flash("Coevaluación habilitada correctamente para esta actividad", "success")
        return redirect(url_for('professor.activities', class_id=class_id))
    
    except Exception as e:
        flash(f"Error al habilitar la coevaluación: {e}", "error")
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
        team_id = request.form.get('team_id')
        grade = request.form.get('grade')
        feedback = request.form.get('feedback')
        
        if not team_id or not grade:
            flash("Missing required fields", "error")
            return redirect(url_for('professor.activity_details', class_id=class_id, activity_id=activity_id))
        
        # Convert grade to integer
        grade = int(grade)
        
        # Get activity document
        class_ref = db.collection('classes').document(class_id)
        activity_ref = class_ref.collection('activities').document(activity_id)
        activity_doc = activity_ref.get()
        
        if not activity_doc.exists:
            flash("Activity not found", "error")
            return redirect(url_for('professor.teams', class_id=class_id))
            
        activity_data = activity_doc.to_dict()
        
        # Update the team grade in the team_grades array
        team_grades = activity_data.get('team_grades', [])
        for team_grade in team_grades:
            if team_grade.get('team_id') == team_id:
                team_grade['grade'] = grade
                team_grade['feedback'] = feedback
                break
        
        # Update the activity document
        activity_ref.update({'team_grades': team_grades})
        
        # Update the team document with the latest grade
        teams_ref = class_ref.collection('teams')
        team_query = teams_ref.where('id', '==', team_id).limit(1)
        team_docs = team_query.get()
        
        if team_docs:
            team_doc = team_docs[0]
            team_ref = team_doc.reference
            team_ref.update({'grade': f"{grade}/{activity_data.get('max_grade')}"})
        
        flash("Team grade saved successfully", "success")
        return redirect(url_for('professor.activity_details', class_id=class_id, activity_id=activity_id))
    except Exception as e:
        flash(f"Error saving team grade: {e}", "error")
        return redirect(url_for('professor.activity_details', class_id=class_id, activity_id=activity_id))

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