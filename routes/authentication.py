from functools import wraps
from flask import redirect, session, url_for, flash

def auth_required(f):
    """Decorador para restringir el acceso a usuarios autenticados."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            flash("Debes iniciar sesión para acceder a esta página.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    """Decorador para restringir el acceso a rutas según el rol del usuario."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = session.get("user")

            # Si no hay usuario autenticado o el rol no coincide, redirigir
            if not user or user.get("role") != required_role:
                flash("No tienes permiso para acceder a esta página.", "danger")

                # Redirigir según el rol del usuario
                if user and user.get("role") == "professor":
                    return redirect(url_for("professor.index"))
                elif user and user.get("role") == "student":
                    return redirect(url_for("student.home"))
                else:
                    return redirect(url_for("login"))  # Si no tiene sesión, redirigir a login

            return f(*args, **kwargs)
        return decorated_function
    return decorator
