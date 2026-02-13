"""
Decoradores personalizados para rutas
"""
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """
    Decorador que requiere que el usuario sea administrador
    
    Usage:
        @app.route('/admin')
        @login_required
        @admin_required
        def admin_panel():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'Admin':
            flash('Acceso denegado. Se requieren privilegios de administrador.', 'error')
            return redirect(url_for('caja.index'))
        return f(*args, **kwargs)
    return decorated_function
