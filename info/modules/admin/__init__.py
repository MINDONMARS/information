from flask import Blueprint

admin_blue = Blueprint('admin', __name__, url_prefix='/admin')

from .views import *


@admin_blue.before_request
def admin_authentication():
    if not request.url.endswith('/admin/login'):
        user_id = session['user_id']
        is_admin = session['is_admin']
        if not user_id or not is_admin:
            return redirect(url_for('index.index'))