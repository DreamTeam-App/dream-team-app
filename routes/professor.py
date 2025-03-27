import random
import string
from flask import Blueprint, flash, render_template, request, redirect, url_for, jsonify, session
from routes.authentication import *
from firebase_client import db  # Importa el cliente de Firestore centralizado

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
        class_ref = db.collection('classes').document(class_id)
        class_doc = class_ref.get()
        if not class_doc.exists:
            flash("Class not found", "error")
            return redirect(url_for('professor.index'))
        class_data = class_doc.to_dict()
        
        # Consultar las primeras 5 inscripciones y 3 equipos para mostrar un resumen
        enrollments_ref = class_ref.collection('enrollments').limit(5)
        enrollments_docs = enrollments_ref.get()
        enrollments = [doc.to_dict() for doc in enrollments_docs]
        
        teams_ref = class_ref.collection('teams').limit(3)
        teams_docs = teams_ref.get()
        teams = [doc.to_dict() for doc in teams_docs]
        
        return render_template('professor/class_details.html',
                               selected_class=class_data,
                               enrollments_summary=enrollments,
                               teams_summary=teams,
                               student_count=len(enrollments),
                               team_count=len(teams),
                               classes=[])  # Puedes pasar la lista completa de clases si es necesario
    except Exception as e:
        flash(f"Error fetching class details: {e}", "error")
        return redirect(url_for('professor.index'))

# Ruta para mostrar todos los estudiantes (inscripciones) de una clase
@professor_bp.route('/class/<class_id>/students')
def students(class_id):
    try:
        class_ref = db.collection('classes').document(class_id)
        enrollments_ref = class_ref.collection('enrollments')
        docs = enrollments_ref.get()
        students = [doc.to_dict() for doc in docs]
        return render_template('professor/students.html',
                               selected_class=class_ref.get().to_dict(),
                               students=students,
                               total_students=len(students),
                               classes=[]) 
    except Exception as e:
        flash(f"Error fetching students: {e}", "error")
        return redirect(url_for('professor.index'))

# Ruta para mostrar todos los equipos de una clase
@professor_bp.route('/class/<class_id>/teams')
def teams(class_id):
    try:
        class_ref = db.collection('classes').document(class_id)
        teams_ref = class_ref.collection('teams')
        docs = teams_ref.get()
        teams = [doc.to_dict() for doc in docs]
        
        # Para la formación de equipos, también se consultan los estudiantes inscritos
        enrollments_docs = class_ref.collection('enrollments').get()
        students = [doc.to_dict() for doc in enrollments_docs]
        
        return render_template('professor/teams.html',
                               selected_class=class_ref.get().to_dict(),
                               teams=teams,
                               total_teams=len(teams),
                               students=students,
                               classes=[])
    except Exception as e:
        flash(f"Error fetching teams: {e}", "error")
        return redirect(url_for('professor.index'))

# Ruta API: Obtener los detalles de un equipo (usando collection group query)
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
            # Se busca el estudiante correspondiente (asumiendo que se almacena "student_id")
            student = next((s for s in students if s.get('id') == member.get('student_id')), None)
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
        # Se espera recibir una lista de IDs de estudiantes seleccionados
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

