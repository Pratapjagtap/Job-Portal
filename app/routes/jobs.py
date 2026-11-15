import os
import sqlite3
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request,
    abort, jsonify, current_app
)
from flask_login import login_required, current_user, login_user

from app import db, role_required, csrf
from app.models import Job, Application, User
from app.forms import JobForm, ApplicationForm, ProfileForm

jobs_bp = Blueprint('jobs', __name__)


@jobs_bp.route('/')
def index():
    tab = request.args.get('tab', 'discover').lower()
    q = request.args.get('q', '').strip()
    role = request.args.get('role', '').strip()
    skill = request.args.get('skills', '').strip()
    compensation = request.args.get('compensation', '').strip()
    working_model = request.args.get('working_model', '').strip()

    query = Job.query.filter_by(is_active=True)

    if q:
        query = query.filter(
            db.or_(
                Job.title.ilike(f'%{q}%'),
                Job.description.ilike(f'%{q}%'),
                Job.skills.ilike(f'%{q}%'),
                Job.company.ilike(f'%{q}%')
            )
        )
    if working_model and working_model.lower() not in ('all', 'all models', ''):
        query = query.filter(Job.working_model.ilike(f'%{working_model}%'))

    if role and role.lower() not in ('all', 'all roles', ''):
        query = query.filter(
            db.or_(
                Job.title.ilike(f'%{role}%'),
                Job.category.ilike(f'%{role}%')
            )
        )

    jobs = query.order_by(Job.match_score.desc()).all()

    # Use the demo candidate for unauthenticated previews.
    profile_user = current_user if current_user.is_authenticated else User.query.filter_by(username='elena').first()
    if not profile_user:
        profile_user = User.query.first()

    # Pre-calculated stats for the Agent Hub and Talent views
    all_users = User.query.all()
    all_applications = Application.query.order_by(Application.created_at.desc()).all()

    return render_template(
        'jobs/index.html',
        jobs=jobs,
        profile_user=profile_user,
        active_tab=tab,
        q=q,
        role=role,
        skills=skill,
        compensation=compensation,
        working_model=working_model,
        all_users=all_users,
        all_applications=all_applications
    )


# ==============================================================================
# PROFILE & CUSTOM PROFILE BUILDER
# ==============================================================================
@jobs_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    """
    Candidate & Custom Profile Manager.
    Allows viewing the profile and editing all custom fields (Name, Headline,
    Skills, Avatar, Salary, Working Model, and Bio).
    """
    user = current_user if current_user.is_authenticated else User.query.filter_by(username='elena').first()
    if not user:
        user = User.query.first()

    form = ProfileForm(obj=user)

    if form.validate_on_submit():
        user.full_name = form.full_name.data.strip()
        user.headline = form.headline.data.strip()
        user.skills = form.skills.data.strip()
        if form.avatar_url.data:
            user.avatar_url = form.avatar_url.data.strip()
        user.target_salary_min = form.target_salary_min.data or user.target_salary_min
        user.target_salary_max = form.target_salary_max.data or user.target_salary_max
        user.preferred_model = form.preferred_model.data
        user.resume_summary = form.resume_summary.data.strip()

        # Dynamic ATS & Match Score Recalculation
        skill_count = len(user.get_skills_list())
        new_ats = min(99, max(75, 76 + (skill_count * 2)))
        new_matches = min(99, max(80, 84 + (skill_count * 2)))
        user.ats_score = new_ats
        user.matches_pct = new_matches

        db.session.commit()
        flash(f'Profile updated successfully! Recalculated ATS Score: {new_ats}% | Match Potential: {new_matches}%.', 'success')
        return redirect(url_for('jobs.profile'))

    user_applications = user.applications.order_by(Application.created_at.desc()).all()

    return render_template(
        'jobs/profile.html',
        user=user,
        form=form,
        applications=user_applications
    )


# ==============================================================================
# DATABASE EXPLORER & LIVE VIEWER (MySQL & SQLite)
# ==============================================================================
@jobs_bp.route('/database')
def database_explorer():
    """
    Live Database Explorer supporting both MySQL and SQLite engines dynamically.
    """
    from sqlalchemy import text
    engine_name = db.engine.name
    url = db.engine.url

    if engine_name == 'mysql':
        try:
            version_str = db.session.execute(text('SELECT VERSION();')).scalar()
        except Exception:
            version_str = '8.0'
        db_engine_display = f"MySQL {version_str} (InnoDB)"
        db_target = f"{url.host}:{url.port or 3306} / {url.database}"
        driver_display = f"PyMySQL ({url.drivername})"
    else:
        db_path = os.path.join(current_app.instance_path, 'portal.db')
        file_size_kb = round(os.path.getsize(db_path) / 1024, 2) if os.path.exists(db_path) else 0
        db_engine_display = "SQLite 3.x"
        db_target = f"instance/portal.db ({file_size_kb} KB)"
        driver_display = "sqlite3"

    users = User.query.order_by(User.id.asc()).all()
    jobs = Job.query.order_by(Job.id.asc()).all()
    applications = Application.query.order_by(Application.id.asc()).all()

    stats = {
        'db_engine': db_engine_display,
        'db_target': db_target,
        'driver': driver_display,
        'users_count': len(users),
        'jobs_count': len(jobs),
        'applications_count': len(applications),
        'status': 'Online & Connected'
    }

    active_table = request.args.get('table', 'users')

    return render_template(
        'jobs/database.html',
        stats=stats,
        users=users,
        jobs=jobs,
        applications=applications,
        active_table=active_table
    )


@jobs_bp.route('/database/query', methods=['POST'])
@csrf.exempt
def database_query():
    """Execute safe read-only SQL queries on the live active database (MySQL/SQLite)."""
    from sqlalchemy import text
    query_text = request.form.get('sql_query', '').strip()
    if not query_text:
        flash('Please enter a SQL query.', 'warning')
        return redirect(url_for('jobs.database_explorer', table='query'))

    # Security check: Read-only statements
    cleaned_lower = query_text.lower()
    allowed_prefixes = ('select', 'show', 'describe', 'explain')
    if not any(cleaned_lower.startswith(prefix) for prefix in allowed_prefixes):
        flash('Only read-only SELECT, SHOW, DESCRIBE, and EXPLAIN queries are permitted.', 'danger')
        return redirect(url_for('jobs.database_explorer', table='query'))

    columns = []
    rows = []
    error = None

    try:
        res = db.session.execute(text(query_text))
        if res.returns_rows:
            columns = list(res.keys())
            rows = [dict(zip(columns, row)) for row in res.fetchall()]
    except Exception as e:
        error = str(e)

    # Return back with query result
    engine_name = db.engine.name
    url = db.engine.url
    if engine_name == 'mysql':
        try:
            version_str = db.session.execute(text('SELECT VERSION();')).scalar()
        except Exception:
            version_str = '8.0'
        db_engine_display = f"MySQL {version_str} (InnoDB)"
        db_target = f"{url.host}:{url.port or 3306} / {url.database}"
        driver_display = f"PyMySQL ({url.drivername})"
    else:
        db_path = os.path.join(current_app.instance_path, 'portal.db')
        file_size_kb = round(os.path.getsize(db_path) / 1024, 2) if os.path.exists(db_path) else 0
        db_engine_display = "SQLite 3.x"
        db_target = f"instance/portal.db ({file_size_kb} KB)"
        driver_display = "sqlite3"

    users = User.query.order_by(User.id.asc()).all()
    jobs = Job.query.order_by(Job.id.asc()).all()
    applications = Application.query.order_by(Application.id.asc()).all()

    stats = {
        'db_engine': db_engine_display,
        'db_target': db_target,
        'driver': driver_display,
        'users_count': len(users),
        'jobs_count': len(jobs),
        'applications_count': len(applications),
        'status': 'Online & Connected'
    }

    return render_template(
        'jobs/database.html',
        stats=stats,
        users=users,
        jobs=jobs,
        applications=applications,
        active_table='query',
        query_text=query_text,
        query_columns=columns,
        query_rows=rows,
        query_error=error
    )


@jobs_bp.route('/database/reseed', methods=['POST'])
@csrf.exempt
def database_reseed():
    """Reseeds the database to default reference state."""
    try:
        from seed_data import seed
        seed(current_app, force=True)
        flash('Database re-seeded successfully with reference jobs and demo accounts.', 'success')
    except Exception as e:
        flash(f'Error re-seeding: {e}', 'danger')
    return redirect(url_for('jobs.database_explorer'))


# ==============================================================================
# DEMO PERSONA SWITCHER
# ==============================================================================
@jobs_bp.route('/switch-demo/<username>')
def switch_demo(username):
    """Convenience helper to switch between the demo seeker, employer, and admin."""
    user = User.query.filter_by(username=username).first()
    if user:
        login_user(user)
        flash(f'Switched active profile to {user.full_name or user.username} ({user.role})', 'success')
    return redirect(url_for('jobs.index'))


@jobs_bp.route('/jobs/<int:job_id>')
def detail(job_id):
    job = Job.query.get_or_404(job_id)
    if not job.is_active and not (
        current_user.is_authenticated and
        (current_user.id == job.employer_id or current_user.role == 'admin')
    ):
        abort(404)
    form = ApplicationForm()
    has_applied = False
    profile_user = current_user if current_user.is_authenticated else User.query.filter_by(username='elena').first()

    if profile_user:
        has_applied = Application.query.filter_by(
            job_id=job.id, user_id=profile_user.id
        ).first() is not None

    return render_template(
        'jobs/detail.html',
        job=job,
        form=form,
        has_applied=has_applied,
        profile_user=profile_user
    )


@jobs_bp.route('/jobs/<int:job_id>/apply', methods=['POST'])
def apply(job_id):
    job = Job.query.get_or_404(job_id)
    user = current_user if current_user.is_authenticated else User.query.filter_by(role='seeker').first()
    if not user:
        flash('Please login or switch to a candidate profile to apply.', 'warning')
        return redirect(url_for('jobs.detail', job_id=job.id))

    existing = Application.query.filter_by(job_id=job.id, user_id=user.id).first()
    if existing:
        flash('You have already applied for this job.', 'info')
        return redirect(url_for('jobs.detail', job_id=job.id))

    form = ApplicationForm()
    cover_letter = form.cover_letter.data if form.validate_on_submit() else request.form.get('cover_letter')
    if not cover_letter:
        cover_letter = f"AI Tailored Application from {user.full_name or user.username} with matched skills in {job.skills}."

    application = Application(
        job_id=job.id,
        user_id=user.id,
        cover_letter=cover_letter,
        match_score_at_apply=job.match_score
    )
    db.session.add(application)
    db.session.commit()
    flash(f'AI Application submitted for "{job.title}" at {job.company}!', 'success')
    return redirect(url_for('jobs.detail', job_id=job.id))


@jobs_bp.route('/post', methods=['GET', 'POST'])
@login_required
@role_required('employer', 'admin')
def post():
    form = JobForm()
    if form.validate_on_submit():
        job = Job(
            title=form.title.data,
            company=form.company.data,
            location=form.location.data,
            category=form.category.data,
            description=form.description.data,
            salary_min=form.salary_min.data,
            salary_max=form.salary_max.data,
            salary_display=(
                f"${form.salary_min.data // 1000}k - ${form.salary_max.data // 1000}k"
                if form.salary_min.data and form.salary_max.data else "Competitive"
            ),
            job_type=form.job_type.data,
            working_model=form.working_model.data,
            employer_id=current_user.id,
            match_score=92,
            match_badge_text='AI Fit Badge',
            skills=form.skills.data or 'Python, Transformers, Agentic UX'
        )
        db.session.add(job)
        db.session.commit()
        flash(f'Job "{job.title}" posted successfully!', 'success')
        return redirect(url_for('jobs.detail', job_id=job.id))
    return render_template('jobs/post.html', form=form)


@jobs_bp.route('/my-jobs')
@login_required
@role_required('employer', 'admin')
def my_jobs():
    if current_user.role == 'admin':
        jobs = Job.query.order_by(Job.created_at.desc()).all()
    else:
        jobs = current_user.jobs.order_by(Job.created_at.desc()).all()
    return render_template('jobs/my_jobs.html', jobs=jobs)


@jobs_bp.route('/my-applications')
def my_applications():
    user = current_user if current_user.is_authenticated else User.query.filter_by(role='seeker').first()
    if not user:
        user = User.query.first()
    applications = user.applications.order_by(
        Application.created_at.desc()
    ).all()
    return render_template('jobs/applications.html', applications=applications)


@jobs_bp.route('/jobs/<int:job_id>/applications')
@login_required
@role_required('employer', 'admin')
def job_applications(job_id):
    job = Job.query.get_or_404(job_id)
    if current_user.role != 'admin' and job.employer_id != current_user.id:
        abort(403)
    applications = job.applications.order_by(
        Application.created_at.desc()
    ).all()
    return render_template(
        'jobs/job_applications.html', job=job, applications=applications
    )
