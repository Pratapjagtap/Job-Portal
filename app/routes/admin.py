from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app import db, role_required
from app.models import User, Job, Application

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    users = User.query.order_by(User.created_at.desc()).all()
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    applications = Application.query.order_by(
        Application.created_at.desc()
    ).all()
    stats = {
        'users': User.query.count(),
        'jobs': Job.query.count(),
        'applications': Application.query.count(),
        'active_jobs': Job.query.filter_by(is_active=True).count(),
    }
    return render_template(
        'admin/dashboard.html',
        users=users, jobs=jobs, applications=applications, stats=stats,
    )


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@role_required('admin')
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot modify your own account.', 'warning')
        return redirect(url_for('admin.dashboard'))
    if user.role == 'admin':
        flash('Cannot modify another admin account.', 'warning')
        return redirect(url_for('admin.dashboard'))
    new_role = 'employer' if user.role == 'seeker' else 'seeker'
    user.role = new_role
    db.session.commit()
    flash(f'{user.username} is now a {new_role}.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/jobs/<int:job_id>/toggle', methods=['POST'])
@login_required
@role_required('admin')
def toggle_job(job_id):
    job = Job.query.get_or_404(job_id)
    job.is_active = not job.is_active
    db.session.commit()
    state = 'activated' if job.is_active else 'deactivated'
    flash(f'Job "{job.title}" {state}.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/applications/<int:app_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_application(app_id):
    application = Application.query.get_or_404(app_id)
    db.session.delete(application)
    db.session.commit()
    flash('Application deleted.', 'info')
    return redirect(url_for('admin.dashboard'))
