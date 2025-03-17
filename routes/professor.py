import random
import string
from flask import Blueprint, flash, render_template, request, redirect, url_for, jsonify
from routes.authentication import *

professor_bp = Blueprint("professor", __name__)

@professor_bp.before_request
@auth_required
@role_required("professor")
def before_request():
    """Se ejecuta antes de cualquier ruta en este Blueprint."""
    pass

# Mock data for classes
mock_classes = [
    {
        "id": "CS101",
        "name": "Introduction to Computer Science",
        "instructor": "Dr. Jane Smith",
        "schedule": "Mon, Wed, Fri 10:00 AM - 11:30 AM",
        "location": "Building A, Room 203",
        "start_date": "01/09/2022",
        "end_date": "15/12/2022",
        "description": "An introductory course covering the fundamentals of computer science, including programming basics, algorithms, and data structures."
    },
    {
        "id": "CS201",
        "name": "Data Structures and Algorithms",
        "instructor": "Prof. John Davis",
        "schedule": "Tue, Thu 2:00 PM - 3:30 PM",
        "location": "Building B, Room 105",
        "start_date": "01/09/2022",
        "end_date": "15/12/2022",
        "description": "A comprehensive study of data structures and algorithms, focusing on efficiency, implementation, and application."
    },
    {
        "id": "CS301",
        "name": "Database Systems",
        "instructor": "Dr. Maria Rodriguez",
        "schedule": "Mon, Wed 1:00 PM - 2:30 PM",
        "location": "Building C, Room 302",
        "start_date": "01/09/2022",
        "end_date": "15/12/2022",
        "description": "An exploration of database design, implementation, and management, covering relational models, SQL, and NoSQL systems."
    }
]

# Mock data for students by class
mock_students_by_class = {
    "CS101": [
        {
            "id": "#ST001",
            "name": "Matt Dickerson",
            "avatar": "/static/images/placeholder.png",
            "email": "matt.d@example.com",
            "enrollment_date": "13/05/2022",
            "grade": "A",
            "attendance": "95%",
            "status": "Active"
        },
        {
            "id": "#ST002",
            "name": "Wiktoria Johnson",
            "avatar": "/static/images/placeholder.png",
            "email": "wiktoria.j@example.com",
            "enrollment_date": "22/05/2022",
            "grade": "B+",
            "attendance": "88%",
            "status": "Active"
        },
        {
            "id": "#ST003",
            "name": "Trixie Byrd",
            "avatar": "/static/images/placeholder.png",
            "email": "trixie.b@example.com",
            "enrollment_date": "15/06/2022",
            "grade": "A-",
            "attendance": "92%",
            "status": "Active"
        },
        {
            "id": "#ST004",
            "name": "Brad Mason",
            "avatar": "/static/images/placeholder.png",
            "email": "brad.m@example.com",
            "enrollment_date": "06/09/2022",
            "grade": "C+",
            "attendance": "78%",
            "status": "Warning"
        },
        {
            "id": "#ST005",
            "name": "Lita Lestrange",
            "avatar": "/static/images/placeholder.png",
            "email": "lita.m@example.com",
            "enrollment_date": "06/09/2022",
            "grade": "C+",
            "attendance": "78%",
            "status": "Active"
        },
        {
            "id": "#ST005",
            "name": "Newt Scamander",
            "avatar": "/static/images/placeholder.png",
            "email": "scamanderNewt.m@example.com",
            "enrollment_date": "06/09/2022",
            "grade": "C+",
            "attendance": "78%",
            "status": "Active"
        }
    ],
    "CS201": [
        {
            "id": "#ST005",
            "name": "Sanderson Miller",
            "avatar": "/static/images/placeholder.png",
            "email": "sanderson.m@example.com",
            "enrollment_date": "25/09/2022",
            "grade": "B",
            "attendance": "85%",
            "status": "Active"
        },
        {
            "id": "#ST006",
            "name": "Jun Redfern",
            "avatar": "/static/images/placeholder.png",
            "email": "jun.r@example.com",
            "enrollment_date": "04/10/2022",
            "grade": "A+",
            "attendance": "98%",
            "status": "Active"
        }
    ],
    "CS301": [
        {
            "id": "#ST007",
            "name": "Miriam Kidd",
            "avatar": "/static/images/placeholder.png",
            "email": "miriam.k@example.com",
            "enrollment_date": "17/10/2022",
            "grade": "B-",
            "attendance": "82%",
            "status": "Active"
        },
        {
            "id": "#ST008",
            "name": "Dominic Wilson",
            "avatar": "/static/images/placeholder.png",
            "email": "dominic.w@example.com",
            "enrollment_date": "24/10/2022",
            "grade": "C",
            "attendance": "75%",
            "status": "Warning"
        }
    ]
}

# Mock data for teams by class with member roles
mock_teams_by_class = {
    "CS101": [
        {
            "id": "#TM001",
            "name": "Alpha Team",
            "project": "E-commerce Platform",
            "members": [
                {"name": "Matt Dickerson", "role": "Team Lead"},
                {"name": "Trixie Byrd", "role": "Frontend Developer"}
            ],
            "progress": "75%",
            "grade": "A-",
            "status": "On Track"
        },
        {
            "id": "#TM002",
            "name": "Beta Team",
            "project": "Mobile App Development",
            "members": [
                {"name": "Wiktoria Johnson", "role": "UI/UX Designer"},
                {"name": "Brad Mason", "role": "Backend Developer"}
            ],
            "progress": "60%",
            "grade": "B+",
            "status": "On Track"
        }
    ],
    "CS201": [
        {
            "id": "#TM003",
            "name": "Gamma Team",
            "project": "Data Visualization Tool",
            "members": [
                {"name": "Sanderson Miller", "role": "Data Analyst"},
                {"name": "Jun Redfern", "role": "Project Manager"}
            ],
            "progress": "45%",
            "grade": "B",
            "status": "Behind Schedule"
        }
    ],
    "CS301": [
        {
            "id": "#TM004",
            "name": "Delta Team",
            "project": "Database Migration System",
            "members": [
                {"name": "Miriam Kidd", "role": "Database Administrator"},
                {"name": "Dominic Wilson", "role": "Quality Assurance"}
            ],
            "progress": "30%",
            "grade": "B-",
            "status": "Behind Schedule"
        }
    ]
}

# Available team roles
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
# Helper function to generate a random class code
def generate_class_code(length=6):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Helper function to check if a student is already in a team
def is_student_in_team(student_name, class_id):
    teams = mock_teams_by_class.get(class_id, [])
    for team in teams:
        if any(member['name'] == student_name for member in team['members']):
            return True
    return False

# Helper function to get students with team status
def get_students_with_team_status(class_id):
    students = mock_students_by_class.get(class_id, [])
    for student in students:
        student['in_team'] = is_student_in_team(student['name'], class_id)
    return students

@professor_bp.route('/index')
@auth_required
def index():
    return render_template('professor/index.html', classes=mock_classes)

@professor_bp.route('/create_class', methods=['POST'])
def create_class():
    # Get form data
    class_name = request.form.get('class_name')
    instructor = request.form.get('instructor')
    schedule = request.form.get('schedule')
    location = request.form.get('location')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    description = request.form.get('description')
    
    # Generate a unique class ID and join code
    class_id = f"CS{len(mock_classes) + 101}"
    join_code = generate_class_code()
    
    # Create new class
    new_class = {
        "id": class_id,
        "name": class_name,
        "instructor": instructor,
        "schedule": schedule,
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
        "description": description,
        "join_code": join_code
    }
    
    # Add to mock data
    mock_classes.append(new_class)
    mock_students_by_class[class_id] = []
    mock_teams_by_class[class_id] = []
    
    flash(f'Class "{class_name}" created successfully! Join code: {join_code}', 'success')
    return redirect(url_for('professor.index'))


@professor_bp.route('/class/<class_id>')
def class_details(class_id):
    # Find the class by ID
    selected_class = next((c for c in mock_classes if c["id"] == class_id), None)
    
    if not selected_class:
        return redirect(url_for('professor.index'))
    
    # Get students and teams for this class
    students = mock_students_by_class.get(class_id, [])
    teams = mock_teams_by_class.get(class_id, [])
    
    return render_template(
        'professor/class_details.html', 
        selected_class=selected_class, 
        students=students[:5],  # Just show first 5 for summary
        teams=teams[:3],        # Just show first 3 for summary
        student_count=len(students),
        team_count=len(teams),
        classes=mock_classes
    )

@professor_bp.route('/class/<class_id>/students')
def students(class_id):
    # Find the class by ID
    selected_class = next((c for c in mock_classes if c["id"] == class_id), None)
    
    if not selected_class:
        return redirect(url_for('professor.index'))
    
    # Get students for this class with team status
    students = get_students_with_team_status(class_id)
    
    # Get existing teams for this class
    teams = mock_teams_by_class.get(class_id, [])
    
    # Handle search
    search_term = request.args.get('search', '').lower()
    if search_term:
        students = [s for s in students if 
                   search_term in s['id'].lower() or 
                   search_term in s['name'].lower() or 
                   search_term in s['email'].lower() or 
                   search_term in s['status'].lower()]
    
    # Handle pagination
    rows_per_page = int(request.args.get('rows', 10))
    page = int(request.args.get('page', 1))
    start_idx = (page - 1) * rows_per_page
    end_idx = start_idx + rows_per_page
    paginated_students = students[start_idx:end_idx]
    total_pages = (len(students) + rows_per_page - 1) // rows_per_page
    
    return render_template(
        'professor/students.html', 
        selected_class=selected_class, 
        students=paginated_students,
        all_students=students,  # For team formation
        total_students=len(students),
        page=page,
        total_pages=total_pages,
        rows_per_page=rows_per_page,
        search_term=search_term,
        classes=mock_classes,
        team_roles=team_roles,
        existing_teams=teams
    )

@professor_bp.route('/class/<class_id>/teams')
def teams(class_id):
    # Find the class by ID
    selected_class = next((c for c in mock_classes if c["id"] == class_id), None)
    
    if not selected_class:
        return redirect(url_for('professor.index'))
    
    # Get teams for this class
    teams = mock_teams_by_class.get(class_id, [])
    students = mock_students_by_class.get(class_id, [])
    
    # Handle search
    search_term = request.args.get('search', '').lower()
    if search_term:
        teams = [t for t in teams if 
                search_term in t['id'].lower() or 
                search_term in t['name'].lower() or 
                search_term in t['project'].lower() or 
                search_term in t['status'].lower() or
                any(search_term in member['name'].lower() for member in t['members'])]
    
    # Handle pagination
    rows_per_page = int(request.args.get('rows', 10))
    page = int(request.args.get('page', 1))
    start_idx = (page - 1) * rows_per_page
    end_idx = start_idx + rows_per_page
    paginated_teams = teams[start_idx:end_idx]
    total_pages = (len(teams) + rows_per_page - 1) // rows_per_page
    
    return render_template(
        'professor/teams.html', 
        selected_class=selected_class, 
        teams=paginated_teams,
        students=students,
        total_teams=len(teams),
        page=page,
        total_pages=total_pages,
        rows_per_page=rows_per_page,
        search_term=search_term,
        classes=mock_classes
    )

@professor_bp.route('/api/team/<team_id>/details')
def team_details(team_id):
    # Find the team by ID across all classes
    for class_id, teams in mock_teams_by_class.items():
        for team in teams:
            if team['id'] == team_id:
                # Get student details for team members
                students = mock_students_by_class.get(class_id, [])
                member_details = []
                for member in team['members']:
                    student = next((s for s in students if s['name'] == member['name']), None)
                    if student:
                        member_details.append({
                            'name': student['name'],
                            'avatar': student['avatar'],
                            'email': student['email'],
                            'role': member['role']
                        })
                    else:
                        member_details.append({
                            'name': member['name'],
                            'avatar': '/static/images/placeholder.png',
                            'email': 'No email available',
                            'role': member['role']
                        })
                
                return jsonify({
                    'team': team,
                    'members': member_details
                })
    
    return jsonify({'error': 'Team not found'}), 404

@professor_bp.route('/delete_student/<student_id>')
def delete_student(student_id):
    # In a real app, this would delete from the database
    # For this demo, we'll just redirect back
    class_id = request.args.get('class_id')
    return redirect(url_for('students', class_id=class_id))

@professor_bp.route('/delete_team/<team_id>')
def delete_team(team_id):
    # In a real app, this would delete from the database
    # For this demo, we'll just redirect back
    class_id = request.args.get('class_id')
    return redirect(url_for('teams', class_id=class_id))

@professor_bp.route('/create_team/<class_id>', methods=['POST'])
def create_team(class_id):
    # In a real app, this would save to the database
    # For this demo, we'll just add to our mock data
    
    team_name = request.form.get('team_name')
    team_project = request.form.get('team_project')
    selected_students = request.form.getlist('selected_students')
    
    # Create a new team ID
    existing_teams = mock_teams_by_class.get(class_id, [])
    new_team_id = f"#TM{len(existing_teams) + 1:03d}"
    
    # Create member list with roles
    members = []
    for student_id in selected_students:
        student_name = request.form.get(f'student_name_{student_id}')
        student_role = request.form.get(f'student_role_{student_id}')
        members.append({
            "name": student_name,
            "role": student_role
        })
    
    # Create new team
    new_team = {
        "id": new_team_id,
        "name": team_name,
        "project": team_project,
        "members": members,
        "progress": "0%",
        "grade": "N/A",
        "status": "Not Started"
    }
    
    # Add to mock data
    if class_id not in mock_teams_by_class:
        mock_teams_by_class[class_id] = []
    
    mock_teams_by_class[class_id].append(new_team)
    
    flash(f'Team "{team_name}" created successfully!', 'success')
    return redirect(url_for('teams', class_id=class_id))

@professor_bp.route('/update_team_member_role/<class_id>/<team_id>', methods=['POST'])
def update_team_member_role(class_id, team_id):
    # In a real app, this would update the database
    # For this demo, we'll update our mock data
    
    member_name = request.form.get('member_name')
    new_role = request.form.get('new_role')
    
    teams = mock_teams_by_class.get(class_id, [])
    for team in teams:
        if team['id'] == team_id:
            for member in team['members']:
                if member['name'] == member_name:
                    member['role'] = new_role
                    flash(f'Role updated for {member_name}', 'success')
                    break
    
    return redirect(url_for('teams', class_id=class_id))

@professor_bp.route('/logout')
def logout():
    # In a real app, this would clear the session
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('home'))

@professor_bp.route('/edit_profile')
def edit_profile():
    # In a real app, this would show a profile edit form
    flash('Profile editing is not implemented in this demo', 'info')
    return redirect(url_for('professor.index'))
