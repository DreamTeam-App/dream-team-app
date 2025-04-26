from flask import Blueprint, Flask, json, render_template, redirect, url_for, request, jsonify, flash, session

from routes.authentication import auth_required, role_required
from firebase_client import db  # Importa el cliente de Firestore centralizado
from firebase_admin import firestore
import datetime

student_bp = Blueprint("student", __name__)

@student_bp.before_request
@auth_required
@role_required("student")
def before_request():
    """Se ejecuta antes de cualquier ruta en este Blueprint."""
    pass

@student_bp.route('/')
def home():
    uid = session.get("user", {}).get("uid")
    pending_forms = []
    
    if uid:
        # Get user document reference
        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get()
        user_data = user_doc.to_dict() if user_doc.exists else {}
        
        # Check if forms_summary already exists
        forms_summary_exists = 'forms_summary' in user_data
        
        # Fetch incomplete forms
        forms_docs = user_ref.collection("forms").where("completed", "==", False).get()
        for doc in forms_docs:
            form_data = doc.to_dict()
            pending_forms.append(form_data)
        
        # Check if both personality and team_roles forms are completed
        if not forms_summary_exists:
            # Get completed personality form
            personality_form_docs = user_ref.collection("forms").where("form_type", "==", "personality").where("completed", "==", True).limit(1).get()
            personality_form = next((doc.to_dict() for doc in personality_form_docs), None)
            
            # Get completed team_roles form
            team_roles_form_docs = user_ref.collection("forms").where("form_type", "==", "team_roles").where("completed", "==", True).limit(1).get()
            team_roles_form = next((doc.to_dict() for doc in team_roles_form_docs), None)
            
            # If both forms are completed, generate forms_summary
            if personality_form and team_roles_form:
                # Get form IDs to fetch the actual form data
                personality_form_id = personality_form.get("form_id")
                team_roles_form_id = team_roles_form.get("form_id")
                
                # Fetch the actual form data with answers
                personality_data = db.collection("forms").document(personality_form_id).get().to_dict() if personality_form_id else None
                team_roles_data = db.collection("forms").document(team_roles_form_id).get().to_dict() if team_roles_form_id else None
                
                if personality_data and team_roles_data:
                    # Create forms_summary
                    forms_summary = {}
                    
                    # Get MBTI from personality form (response with id 1)
                    personality_answers = personality_data.get("answers", {})
                    forms_summary["MBTI"] = personality_answers.get("1", "")
                    
                    # Calculate team role scores
                    team_roles_answers = team_roles_data.get("answers", {})
                    
                    # Organizer: average of questions 1-8
                    organizer_sum = sum(int(team_roles_answers.get(str(i), 0)) for i in range(1, 9))
                    forms_summary["Organizer"] = round(organizer_sum / 8, 2)
                    
                    # Doer: average of questions 9-16
                    doer_sum = sum(int(team_roles_answers.get(str(i), 0)) for i in range(9, 17))
                    forms_summary["Doer"] = round(doer_sum / 8, 2)
                    
                    # Challenger: average of questions 17-24
                    challenger_sum = sum(int(team_roles_answers.get(str(i), 0)) for i in range(17, 25))
                    forms_summary["Challenger"] = round(challenger_sum / 8, 2)
                    
                    # Innovator: average of questions 25-32
                    innovator_sum = sum(int(team_roles_answers.get(str(i), 0)) for i in range(25, 33))
                    forms_summary["Innovator"] = round(innovator_sum / 8, 2)
                    
                    # TeamBuilder: average of questions 33-40
                    team_builder_sum = sum(int(team_roles_answers.get(str(i), 0)) for i in range(33, 41))
                    forms_summary["TeamBuilder"] = round(team_builder_sum / 8, 2)
                    
                    # Connector: average of questions 41-48
                    connector_sum = sum(int(team_roles_answers.get(str(i), 0)) for i in range(41, 49))
                    forms_summary["Connector"] = round(connector_sum / 8, 2)
                    
                    # Update user document with forms_summary
                    user_ref.update({"forms_summary": forms_summary})
                    
                    print(f"Forms summary generated for user {uid}: {forms_summary}")
    
    return render_template('student/index.html', pending_forms=pending_forms)

@student_bp.route('/clases')
def classes():
    try:
        # Obtener el UID del estudiante, ya sea desde 'user' o 'temp_user'
        uid = None
        if "user" in session and session["user"].get("uid"):
            uid = session["user"]["uid"]
        elif "temp_user" in session and session["temp_user"].get("uid"):
            uid = session["temp_user"]["uid"]

        if not uid:
            flash("No se encontró el UID del usuario en la sesión.", "error")
            return redirect(url_for('student.home'))

        # Consultar el documento del usuario en la colección 'users'
        user_doc = db.collection("users").document(uid).get()
        if not user_doc.exists:
            flash("Perfil del estudiante no encontrado.", "error")
            return redirect(url_for('student.home'))

        user_data = user_doc.to_dict()
        # Ahora enrolled_classes puede ser una lista de strings o de objetos con "class_id"
        enrolled_classes_raw = user_data.get("enrolled_classes", [])
        
        enrolled_classes = []
        for item in enrolled_classes_raw:
            # Si es un objeto, extraer el class_id y team_id; si es string, tomarlo como class_id
            if isinstance(item, dict):
                class_id = item.get("class_id")
                team_id = item.get("team_id", "")
            else:
                class_id = item
                team_id = ""
            
            if class_id:
                class_doc = db.collection("classes").document(class_id).get()
                if class_doc.exists:
                    class_data = class_doc.to_dict()
                    class_data['id'] = class_id  # Añadir el ID del documento para usarlo en enlaces
                    # Agregar el team_id obtenido, si existe, para poder mostrarlo en la vista si es necesario
                    class_data['team_id'] = team_id
                    enrolled_classes.append(class_data)
        
    except Exception as e:
        flash(f"Error fetching enrolled classes: {e}", "error")
        enrolled_classes = []
    
    return render_template('student/clases.html', enrolled_classes=enrolled_classes)

@student_bp.route('/perfil')
def profile():
    # Intentar obtener el UID del usuario desde la sesión registrada o temporal
    uid = None
    if "user" in session and session["user"].get("uid"):
        uid = session["user"]["uid"]
    elif "temp_user" in session and session["temp_user"].get("uid"):
        uid = session["temp_user"]["uid"]

    if not uid:
        flash("No se encontró el UID del usuario en la sesión.", "error")
        return redirect(url_for('home'))  # Redirige al login o home, según corresponda

    # Consultar el documento del usuario en la colección "users"
    user_doc = db.collection('users').document(uid).get()
    if user_doc.exists:
        user_profile = user_doc.to_dict()
    else:
        flash("Perfil del usuario no encontrado.", "error")
        user_profile = {}

    return render_template('student/perfil.html', user_profile=user_profile)

@student_bp.route('/join-class', methods=['POST'])
def join_class():
    try:
        # 1. Obtener el código de la clase desde el formulario
        class_code = request.form.get('class_code')
        if not class_code:
            flash("Por favor, ingresa un código de clase.", "error")
            return redirect(url_for('student.home'))

        # 2. Obtener el UID del usuario desde la sesión
        uid = None
        if "user" in session and session["user"].get("uid"):
            uid = session["user"]["uid"]
        elif "temp_user" in session and session["temp_user"].get("uid"):
            uid = session["temp_user"]["uid"]

        if not uid:
            flash("No se encontró el UID del usuario en la sesión.", "error")
            return redirect(url_for('student.home'))

        # 3. Buscar la clase con el join_code
        classes_ref = db.collection('classes')
        query = classes_ref.where('join_code', '==', class_code).limit(1)
        docs = query.get()
        if not docs:
            flash(f'No se encontró una clase con el código: {class_code}', 'error')
            return redirect(url_for('student.home'))

        # 4. Tomar el primer documento (se asume que el join_code es único)
        class_doc = docs[0]
        class_id = class_doc.id  # ID del documento de la clase

        # 4.1 Obtener los datos del usuario desde la colección "users"
        user_doc = db.collection('users').document(uid).get()
        if not user_doc.exists:
            flash("No se encontró el perfil del usuario en Firestore.", "error")
            return redirect(url_for('student.home'))
        user_data = user_doc.to_dict()

        # 5. Agregar el estudiante a la subcolección "enrollments" de esa clase,
        #    incluyendo datos adicionales del usuario para evitar hacer lookups después.
        enrollment_data = {
            "student_id": uid,
            "enrollment_date": firestore.SERVER_TIMESTAMP,
            "status": "Active",
            "name": user_data.get("name"),
            "avatar": user_data.get("avatar", "/static/images/placeholder.png"),
            "email": user_data.get("email")
        }
        class_ref = db.collection('classes').document(class_id)
        class_ref.collection('enrollments').document(uid).set(enrollment_data)

        # 6. Actualizar el documento del usuario en "users" para agregar la clase
        #    en "enrolled_classes" como objeto {class_id, team_id: ""}
        user_ref = db.collection('users').document(uid)
        user_data = user_ref.get().to_dict() if user_ref.get().exists else {}
        enrolled_classes = user_data.get("enrolled_classes", [])

        # Convertir posibles strings a objetos (si se usó antes el formato antiguo)
        converted = []
        for item in enrolled_classes:
            if isinstance(item, str):
                converted.append({"class_id": item})
            elif isinstance(item, dict):
                converted.append(item)
        
        # Buscar si ya existe un objeto para esta clase
        found = False
        for c in converted:
            if c.get("class_id") == class_id:
                # Si ya existe, si tiene team_id, se deja; sino, se agrega como vacío
                if "team_id" not in c:
                    c["team_id"] = ""
                found = True
                break
        
        if not found:
            converted.append({
                "class_id": class_id,
                "team_id": ""  # Aún no asignado
            })

        # Actualizar el documento del usuario usando set con merge=True para no sobrescribir otros campos
        user_ref.set({"enrolled_classes": converted}, merge=True)

        flash(f'Te has unido a la clase con código: {class_code}', 'success')
    except Exception as e:
        flash(f"Error al unirse a la clase: {e}", "error")

    # 7. Redirigir al home 
    return redirect(url_for('student.home'))

@student_bp.route('/clases/<string:class_id>')
def class_details(class_id):
    try:
        # 1. Obtener el UID del estudiante
        uid = None
        if "user" in session and session["user"].get("uid"):
            uid = session["user"]["uid"]
        elif "temp_user" in session and session["temp_user"].get("uid"):
            uid = session["temp_user"]["uid"]

        if not uid:
            flash("No se encontró el UID del usuario en la sesión.", "error")
            return redirect(url_for('student.classes'))

        # 2. Obtener los datos de la clase
        class_ref = db.collection("classes").document(class_id)
        class_doc = class_ref.get()
        if not class_doc.exists:
            flash('Clase no encontrada', 'error')
            return redirect(url_for('student.classes'))
        
        class_data = class_doc.to_dict()
        class_data['id'] = class_id  # Añadir el ID para usarlo en la plantilla

        # 3. Verificar que el estudiante esté inscrito en esta clase (subcolección enrollments)
        enrollment_doc = class_ref.collection("enrollments").document(uid).get()
        if not enrollment_doc.exists:
            flash('No estás inscrito en esta clase', 'error')
            return redirect(url_for('student.classes'))

        # 4. Obtener el team_id desde el documento del usuario (colección "users")
        team_id = None
        user_doc = db.collection("users").document(uid).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            enrolled_classes = user_data.get("enrolled_classes", [])
            # Buscar el objeto que coincida con esta class_id
            for c in enrolled_classes:
                # c debe ser un dict con { "class_id": "...", "team_id": "..." }
                if isinstance(c, dict) and c.get("class_id") == class_id:
                    team_id = c.get("team_id")  # Este es el ID del equipo
                    break

        # 5. Construir el objeto "team"
        team = {"name": "Sin equipo asignado", "members": []}
        if team_id:
            team_ref = class_ref.collection("teams").document(team_id)
            team_doc = team_ref.get()
            if team_doc.exists:
                team_data = team_doc.to_dict()
                team["name"] = team_data.get("name", "Equipo sin nombre")
                # Recorrer la lista "members" con la info detallada
                for member in team_data.get("members", []):
                    member_id = member.get("student_id")
                    # Buscar el documento del usuario para obtener nombre, etc.
                    member_user_doc = db.collection("users").document(member_id).get()
                    if member_user_doc.exists:
                        member_user_data = member_user_doc.to_dict()
                        team["members"].append({
                            "name": member_user_data.get("name", "Usuario sin nombre"),
                            "role": member.get("role", "Estudiante"),
                            "student_id": member_id  # Añadir el ID del estudiante para la coevaluación
                        })

        # 6. Obtener las actividades de la clase
        activities = []
        activities_ref = class_ref.collection("activities").get()
        
        for activity_doc in activities_ref:
            activity_data = activity_doc.to_dict()
            activity_id = activity_doc.id
            
            # Determinar el estado de la actividad
            due_date = activity_data.get("due_date")
            if isinstance(due_date, str):
                due_date_str = due_date
                try:
                    due_date_obj = datetime.datetime.strptime(due_date, "%Y-%m-%d")
                    now = datetime.datetime.now()
                    is_past_due = now > due_date_obj
                except ValueError:
                    is_past_due = False
            else:
                due_date_str = "Fecha no especificada"
                is_past_due = False
            
            # Verificar si el equipo del estudiante tiene una entrega
            status = "pending"
            if team_id:
                # Buscar el equipo en team_grades
                team_grades = activity_data.get("team_grades", [])
                team_grade_data = None
                for tg in team_grades:
                    if tg.get("team_id") == team_id:
                        team_grade_data = tg
                        break
                
                if team_grade_data:
                    if team_grade_data.get("submitted"):
                        submission_date = team_grade_data.get("submission_date")
                        if submission_date and isinstance(submission_date, datetime.datetime):
                            if due_date_obj and submission_date > due_date_obj:
                                status = "late"
                            else:
                                status = "completed"
                        else:
                            status = "completed"
                    elif is_past_due:
                        status = "late"
            elif is_past_due:
                status = "late"
            
            # Nota del profesor (si el equipo tiene una calificación)
            teacher_grade = "-"
            if team_id:
                team_grades = activity_data.get("team_grades", [])
                for tg in team_grades:
                    if tg.get("team_id") == team_id:
                        grade = tg.get("grade")
                        if grade:
                            teacher_grade = f"{grade}/{activity_data.get('max_grade', 100)}"
                        break
            
            # Verificar si la coevaluación está habilitada
            coevaluation_enabled = activity_data.get("enable_coevaluation", False)
            coevaluation_submitted = False
            
            # Obtener coevaluaciones (si están habilitadas y el estudiante tiene equipo)
            peer_grade = "-"
            evaluations = []
            evaluation_items = ["Contribution", "Communication", "Problem Solving", "Technical Skills", "Teamwork"]
            
            if team_id and coevaluation_enabled:
                # Buscar la coevaluación del estudiante
                coevaluation_ref = activity_doc.reference.collection("coevaluations").document(uid).get()
                if coevaluation_ref.exists:
                    coevaluation_data = coevaluation_ref.to_dict()
                    coevaluation_submitted = coevaluation_data.get("submitted", False)
                    
                    # Calcular promedio de autoevaluación
                    self_evaluation = coevaluation_data.get("self_evaluation", {})
                    self_criteria = self_evaluation.get("criteria", [])
                    self_total = 0
                    self_count = 0
                    
                    for criterion in self_criteria:
                        self_total += criterion.get("score", 0)
                        self_count += 1
                    
                    self_avg = self_total / self_count if self_count > 0 else 0
                    
                    # Obtener evaluaciones de compañeros
                    team_members = []
                    if team_doc.exists:
                        team_data = team_doc.to_dict()
                        team_members = team_data.get("members", [])
                    
                     # Almacenar en sesión
                    if "team_members" not in session:
                        session["team_members"] = {}
                    session["team_members"][class_id] = team_members

                    # Para cada miembro del equipo, buscar su coevaluación
                    for member in team_members:
                        member_id = member.get("student_id")
                        if member_id == uid:  # Saltar al propio estudiante
                            continue
                        
                        member_eval_ref = activity_doc.reference.collection("coevaluations").document(member_id).get()
                        if member_eval_ref.exists:
                            member_eval_data = member_eval_ref.to_dict()
                            
                            # Buscar la evaluación que este miembro hizo del estudiante actual
                            for eval_criteria in member_eval_data.get("evaluation_criteria", []):
                                if eval_criteria.get("student_id") == uid:
                                    criteria_scores = eval_criteria.get("criteria", [])
                                    scores = []
                                    total = 0
                                    count = 0
                                    
                                    for criterion in criteria_scores:
                                        score = criterion.get("score", 0)
                                        scores.append(f"{score}")
                                        total += score
                                        count += 1
                                    
                                    avg = total / count if count > 0 else 0
                                    
                                    evaluations.append({
                                        "student": member.get("name", "Compañero"),
                                        "scores": scores,
                                        "average": f"{avg:.1f}"
                                    })
                    
                    # Añadir la autoevaluación
                    self_scores = []
                    for criterion in self_criteria:
                        self_scores.append(f"{criterion.get('score', 0)}")
                    
                    evaluations.append({
                        "student": "Autoevaluación",
                        "scores": self_scores,
                        "average": f"{self_avg:.1f}"
                    })
                    
                    # Calcular promedio general de coevaluación
                    total_peer_score = 0
                    peer_count = 0
                    
                    for evaluation in evaluations:
                        if evaluation["student"] != "Autoevaluación":
                            total_peer_score += float(evaluation["average"])
                            peer_count += 1
                    
                    if peer_count > 0:
                        peer_grade = f"{total_peer_score / peer_count:.1f}"
            
            activity = {
                "id": activity_id,
                "title": activity_data.get("name", "Actividad sin título"),
                "description": activity_data.get("description", "Sin descripción"),
                "due_date": due_date_str,
                "status": status,
                "teacher_grade": teacher_grade,
                "peer_grade": peer_grade,
                "evaluation_items": evaluation_items,
                "evaluations": evaluations,
                "coevaluation_enabled": coevaluation_enabled,
                "coevaluation_submitted": coevaluation_submitted,
                "coevaluation_criteria": evaluation_items
            }
            
            activities.append(activity)
        
        # Ordenar actividades por fecha de entrega (más recientes primero)
        activities.sort(key=lambda x: x["due_date"], reverse=True)
        
        return render_template(
            'student/class_details.html', 
            class_data=class_data, 
            team=team, 
            activities=activities
        )
    
    except Exception as e:
        flash(f"Error al cargar los detalles de la clase: {e}", "error")
        return redirect(url_for('student.classes'))

def calculate_and_update_evaluation_scores(class_id, activity_id, student_id):
    try:
        # Referencias a la base de datos
        class_ref = db.collection('classes').document(class_id)
        activity_ref = class_ref.collection('activities').document(activity_id)
        
        # Obtener el equipo del estudiante
        user_doc = db.collection('users').document(student_id).get()
        user_data = user_doc.to_dict()
        
        team_id = None
        for enrolled_class in user_data.get('enrolled_classes', []):
            if isinstance(enrolled_class, dict) and enrolled_class.get('class_id') == class_id:
                team_id = enrolled_class.get('team_id')
                break
        
        if not team_id:
            return
        
        # Obtener los miembros del equipo
        team_ref = class_ref.collection('teams').document(team_id)
        team_doc = team_ref.get()
        
        if not team_doc.exists:
            return
        
        team_data = team_doc.to_dict()
        team_members = team_data.get('members', [])
        
        # Obtener todas las coevaluaciones del equipo
        coevaluations = []
        for member in team_members:
            member_id = member.get('student_id')
            coevaluation_ref = activity_ref.collection('coevaluations').document(member_id)
            coevaluation_doc = coevaluation_ref.get()
            
            if coevaluation_doc.exists and coevaluation_doc.to_dict().get('submitted', False):
                coevaluations.append({
                    'student_id': member_id,
                    'answers': coevaluation_doc.to_dict().get('answers', {})
                })
        
        # Calcular las calificaciones promedio para cada estudiante
        evaluation_results = {}
        
        # Preguntas de tipo matriz (2-19)
        matrix_questions = list(range(2, 20))
        
        for member in team_members:
            member_id = member.get('student_id')
            member_name = member.get('name')
            
            # Inicializar los resultados para este estudiante
            evaluation_results[member_id] = {
                'student': member_name,
                'scores': [],
                'average': 0
            }
            
            # Recopilar todas las calificaciones para este estudiante
            all_scores = []
            
            for question_id in matrix_questions:
                question_scores = []
                
                # Recopilar calificaciones de todos los evaluadores para esta pregunta
                for evaluation in coevaluations:
                    evaluator_id = evaluation['student_id']
                    answers = evaluation['answers']
                    
                    # Obtener la calificación que el evaluador dio a este estudiante para esta pregunta
                    if str(question_id) in answers and member_id in answers[str(question_id)]:
                        score = int(answers[str(question_id)][member_id])
                        question_scores.append(score)
                
                # Calcular el promedio para esta pregunta
                if question_scores:
                    question_avg = sum(question_scores) / len(question_scores)
                    evaluation_results[member_id]['scores'].append(round(question_avg, 1))
                    all_scores.extend(question_scores)
                else:
                    evaluation_results[member_id]['scores'].append(0)
            
            # Calcular el promedio general para este estudiante
            if all_scores:
                overall_avg = sum(all_scores) / len(all_scores)
                evaluation_results[member_id]['average'] = round(overall_avg, 1)
        
        # Actualizar la actividad con los resultados de la evaluación
        activity_ref.update({
            'evaluation_items': [f"P{i}" for i in matrix_questions],
            'evaluations': [evaluation_results[member_id] for member_id in evaluation_results]
        })
        
        # Actualizar la calificación de pares para cada estudiante
        for member_id, evaluation in evaluation_results.items():
            # Actualizar el documento de coevaluación del estudiante
            coevaluation_ref = activity_ref.collection('coevaluations').document(member_id)
            coevaluation_ref.update({
                'peer_grade': evaluation['average']
            })
    
    except Exception as e:
        print(f"Error al calcular las calificaciones: {e}")

@student_bp.route('/submit-coevaluation/<string:class_id>/<string:activity_id>', methods=['POST'])
def submit_coevaluation(class_id, activity_id):
    try:
        # Obtener el ID del estudiante actual
        uid = None
        if "user" in session and session["user"].get("uid"):
            uid = session["user"]["uid"]
        elif "temp_user" in session and session["temp_user"].get("uid"):
            uid = session["temp_user"]["uid"]
            
        if not uid:
            return jsonify({"success": False, "message": "No se encontró el ID del usuario en la sesión"})
        
        # Verificar que la clase y la actividad existan
        class_ref = db.collection('classes').document(class_id)
        activity_ref = class_ref.collection('activities').document(activity_id)
        
        class_doc = class_ref.get()
        activity_doc = activity_ref.get()
        
        if not class_doc.exists or not activity_doc.exists:
            return jsonify({"success": False, "message": "Clase o actividad no encontrada"})
        
        # Verificar si la coevaluación está habilitada
        activity_data = activity_doc.to_dict()
        if not activity_data.get('enable_coevaluation'):
            return jsonify({"success": False, "message": "La coevaluación no está habilitada para esta actividad"})
        
        # Verificar si el estudiante ya completó la coevaluación
        coevaluation_ref = activity_ref.collection('coevaluations').document(uid)
        coevaluation_doc = coevaluation_ref.get()
        
        if coevaluation_doc.exists and coevaluation_doc.to_dict().get('submitted', False):
            return jsonify({"success": False, "message": "Ya has completado la coevaluación para esta actividad"})
        
        # Obtener los datos del formulario
        data = request.json
        
        # Guardar las respuestas en la base de datos
        coevaluation_ref.update({
            'answers': data,
            'submitted': True,
            'submission_date': firestore.SERVER_TIMESTAMP
        })
        
        # Actualizar el estado del formulario en la subcolección "forms" del estudiante
        user_ref = db.collection('users').document(uid)
        forms_ref = user_ref.collection('forms')
        
        # Buscar el formulario correspondiente a esta actividad
        form_query = forms_ref.where('activity_id', '==', activity_id).where('class_id', '==', class_id).limit(1).get()
        
        for form_doc in form_query:
            form_ref = forms_ref.document(form_doc.id)
            form_ref.update({
                'completed': True,
                'completed_at': firestore.SERVER_TIMESTAMP
            })
        
        # Calcular y actualizar las calificaciones promedio
        calculate_and_update_evaluation_scores(class_id, activity_id, uid)
        
        return jsonify({"success": True, "message": "Coevaluación enviada correctamente"})
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al enviar la coevaluación: {str(e)}"})
    
@student_bp.route('/coevaluation/<string:class_id>/<string:activity_id>')
def coevaluation_form(class_id, activity_id):
    try:
        # Obtener el ID del estudiante actual
        uid = None
        if "user" in session and session["user"].get("uid"):
            uid = session["user"]["uid"]
        elif "temp_user" in session and session["temp_user"].get("uid"):
            uid = session["temp_user"]["uid"]
            
        if not uid:
            flash("No se encontró el ID del usuario en la sesión", "error")
            return redirect(url_for('student.classes'))
        
        # Verificar que la clase y la actividad existan
        class_ref = db.collection('classes').document(class_id)
        activity_ref = class_ref.collection('activities').document(activity_id)
        
        class_doc = class_ref.get()
        activity_doc = activity_ref.get()
        
        if not class_doc.exists or not activity_doc.exists:
            flash("Clase o actividad no encontrada", "error")
            return redirect(url_for('student.class_details', class_id=class_id))
        
        class_data = class_doc.to_dict()
        activity_data = activity_doc.to_dict()
        
        # Verificar si la coevaluación está habilitada
        if not activity_data.get('enable_coevaluation'):
            flash("La coevaluación no está habilitada para esta actividad", "error")
            return redirect(url_for('student.class_details', class_id=class_id))
        
        # Verificar si el estudiante ya completó la coevaluación
        coevaluation_ref = activity_ref.collection('coevaluations').document(uid)
        coevaluation_doc = coevaluation_ref.get()
        
        if coevaluation_doc.exists and coevaluation_doc.to_dict().get('submitted', False):
            flash("Ya has completado la coevaluación para esta actividad", "info")
            return redirect(url_for('student.class_details', class_id=class_id))
        
        # Obtener el equipo del estudiante
        user_doc = db.collection('users').document(uid).get()
        user_data = user_doc.to_dict()
        
        team_id = None
        for enrolled_class in user_data.get('enrolled_classes', []):
            if isinstance(enrolled_class, dict) and enrolled_class.get('class_id') == class_id:
                team_id = enrolled_class.get('team_id')
                break
        
        if not team_id:
            flash("No estás asignado a un equipo en esta clase", "error")
            return redirect(url_for('student.class_details', class_id=class_id))
        
        # Obtener los miembros del equipo
        team_ref = class_ref.collection('teams').document(team_id)
        team_doc = team_ref.get()
        
        if not team_doc.exists:
            flash("Equipo no encontrado", "error")
            return redirect(url_for('student.class_details', class_id=class_id))
        
        team_data = team_doc.to_dict()
        
        # Crear la lista de miembros del equipo en el formato esperado por form3.js
        team_members = []
        for member in team_data.get('members', []):
            member_id = member.get('student_id')
            member_name = member.get('name')
            if member_id and member_name:
                team_members.append({
                    'id': member_id,
                    'name': member_name
                })
        
        # Renderizar el formulario de coevaluación
        return render_template(
            'student/form3.html',
            class_id=class_id,
            activity_id=activity_id,
            class_data=class_data,
            activity_data=activity_data,
            team_data=team_data,
            team_members=json.dumps(team_members),  # Convertir a JSON para pasar al JavaScript
            current_user_id=uid
        )
    
    except Exception as e:
        flash(f"Error al cargar el formulario de coevaluación: {e}", "error")
        return redirect(url_for('student.class_details', class_id=class_id))
    
@student_bp.route('/form1')
def form1():
    uid = session.get("user", {}).get("uid")
    if uid:
        # Consulta el formulario de personalidad (asumiendo que su form_type es "personality")
        docs = db.collection("users").document(uid).collection("forms") \
                .where("form_type", "==", "personality").limit(1).get()
        if docs and len(docs) > 0:
            form = docs[0].to_dict()
            if form.get("completed"):
                flash("Ya completaste el formulario de personalidad. No es necesario volver a llenarlo.", "info")
                return redirect(url_for("student.home"))
    return render_template("student/form1.html")

@student_bp.route('/form2')
def form2():
    uid = session.get("user", {}).get("uid")
    if uid:
        # Consulta el formulario de roles de equipo (asumiendo que su form_type es "team_roles")
        docs = db.collection("users").document(uid).collection("forms") \
                .where("form_type", "==", "team_roles").limit(1).get()
        if docs and len(docs) > 0:
            form = docs[0].to_dict()
            if form.get("completed"):
                flash("Ya completaste el formulario de roles de equipo. No es necesario volver a llenarlo.", "info")
                return redirect(url_for("student.home"))
    return render_template("student/form2.html")

# Ruta para procesar el formulario de personalidad
@student_bp.route('/submit_form1', methods=['POST'])
def submit_form1():
    try:
        # Obtener el UID del estudiante
        uid = None
        if "user" in session and session["user"].get("uid"):
            uid = session["user"]["uid"]
        elif "temp_user" in session and session["temp_user"].get("uid"):
            uid = session["temp_user"]["uid"]

        if not uid:
            return jsonify({"success": False, "message": "No se encontró el UID del usuario en la sesión."})

        # Obtener los datos del formulario
        form_data = request.json
        if not form_data:
            return jsonify({"success": False, "message": "No se recibieron datos del formulario."})

        # 1. Guardar las respuestas en la colección "forms"
        form_doc = {
            "user_id": uid,
            "form_type": "personality",
            "answers": form_data,
            "submitted_at": firestore.SERVER_TIMESTAMP
        }
        
        # Crear explícitamente un nuevo documento en la colección "forms"
        new_form_ref = db.collection("forms").document()
        new_form_ref.set(form_doc)
        form_id = new_form_ref.id
        
        print(f"Formulario guardado en la colección 'forms' con ID: {form_id}")
        
        # 2. Actualizar el estado del formulario en la subcolección del usuario
        forms_ref = db.collection("users").document(uid).collection("forms")
        form_query = forms_ref.where("form_type", "==", "personality").limit(1).get()
        
        if form_query:
            # Actualizar el formulario existente
            form_doc = form_query[0]
            forms_ref.document(form_doc.id).update({
                "completed": True,
                "completed_at": firestore.SERVER_TIMESTAMP,
                "form_id": form_id  # Guardar el ID del formulario
            })
            print(f"Formulario marcado como completado en la subcolección del usuario")
        else:
            # Si no existe, crear un nuevo documento
            new_user_form_ref = forms_ref.document()
            new_user_form_ref.set({
                "form_type": "personality",
                "title": "Test de Personalidad",
                "description": "Formulario para determinar tu tipo de personalidad",
                "completed": True,
                "completed_at": firestore.SERVER_TIMESTAMP,
                "form_id": form_id  # Guardar el ID del formulario
            })
            print(f"Nuevo formulario creado y marcado como completado en la subcolección del usuario")
        
        return jsonify({
            "success": True, 
            "message": "Formulario enviado correctamente. Redirigiendo..."
        })
        
    except Exception as e:
        print(f"Error al procesar el formulario: {e}")
        return jsonify({"success": False, "message": f"Error al procesar el formulario: {str(e)}"})

# Ruta para procesar el formulario de roles de equipo
@student_bp.route('/submit_form2', methods=['POST'])
def submit_form2():
    try:
        # Obtener el UID del estudiante
        uid = None
        if "user" in session and session["user"].get("uid"):
            uid = session["user"]["uid"]
        elif "temp_user" in session and session["temp_user"].get("uid"):
            uid = session["temp_user"]["uid"]

        if not uid:
            return jsonify({"success": False, "message": "No se encontró el UID del usuario en la sesión."})

        # Obtener los datos del formulario
        form_data = request.json
        if not form_data:
            return jsonify({"success": False, "message": "No se recibieron datos del formulario."})

        # 1. Guardar las respuestas en la colección "forms"
        form_doc = {
            "user_id": uid,
            "form_type": "team_roles",
            "answers": form_data,
            "submitted_at": firestore.SERVER_TIMESTAMP
        }
        
        # Crear explícitamente un nuevo documento en la colección "forms"
        new_form_ref = db.collection("forms").document()
        new_form_ref.set(form_doc)
        form_id = new_form_ref.id
        
        print(f"Formulario de roles de equipo guardado en la colección 'forms' con ID: {form_id}")
        
        # 2. Actualizar el estado del formulario en la subcolección del usuario
        forms_ref = db.collection("users").document(uid).collection("forms")
        form_query = forms_ref.where("form_type", "==", "team_roles").limit(1).get()
        
        if form_query:
            # Actualizar el formulario existente
            form_doc = form_query[0]
            forms_ref.document(form_doc.id).update({
                "completed": True,
                "completed_at": firestore.SERVER_TIMESTAMP,
                "form_id": form_id  # Guardar el ID del formulario
            })
            print(f"Formulario de roles de equipo marcado como completado en la subcolección del usuario")
        else:
            # Si no existe, crear un nuevo documento
            new_user_form_ref = forms_ref.document()
            new_user_form_ref.set({
                "form_type": "team_roles",
                "title": "Team Role Experience and Orientation",
                "description": "Formulario para determinar tus roles en equipos de trabajo",
                "completed": True,
                "completed_at": firestore.SERVER_TIMESTAMP,
                "form_id": form_id  # Guardar el ID del formulario
            })
            print(f"Nuevo formulario de roles de equipo creado y marcado como completado en la subcolección del usuario")
        
        return jsonify({
            "success": True, 
            "message": "Formulario enviado correctamente. Redirigiendo..."
        })
        
    except Exception as e:
        print(f"Error al procesar el formulario de roles de equipo: {e}")
        return jsonify({"success": False, "message": f"Error al procesar el formulario: {str(e)}"})

# Función para asignar formularios a un estudiante
def assign_form_to_student(uid, form_type, title, description, url=None):
    """
    Asigna un formulario a un estudiante.
    
    Args:
        uid (str): ID del usuario
        form_type (str): Tipo de formulario (ej: 'personality', 'team_roles')
        title (str): Título del formulario
        description (str): Descripción del formulario
        url (str, optional): URL del formulario. Por defecto es None.
    
    Returns:
        bool: True si se asignó correctamente, False en caso contrario
    """
    try:
        # Verificar si el formulario ya está asignado
        forms_ref = db.collection("users").document(uid).collection("forms")
        form_query = forms_ref.where("form_type", "==", form_type).limit(1).get()
        
        if not form_query:
            # Si no existe, crear un nuevo documento
            form_data = {
                "form_type": form_type,
                "title": title,
                "description": description,
                "url": url if url else f"/student/{form_type}",
                "assigned_at": firestore.SERVER_TIMESTAMP,
                "completed": False
            }
            
            forms_ref.add(form_data)
            return True
        
        return False
    except Exception as e:
        print(f"Error al asignar formulario: {e}")
        return False