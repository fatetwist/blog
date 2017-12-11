from . import admin
from ..decorators import admin_required
from ..models import Log_schcard
from flask import render_template


@admin.route('/log_schcard')

def log_schcard():
    logs = Log_schcard.query.order_by(Log_schcard.time.desc()).all()
    print(logs)
    return render_template('admin/log_schcard.html', logs=logs)
