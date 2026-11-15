from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required

from app.models import db, User
from app.forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip(),
            role=form.role.data,
            full_name=form.username.data.replace('_', ' ').title(),
            headline='AI Software Engineer & Systems Architect' if form.role.data == 'seeker' else 'Hiring Manager & Talent Lead',
            avatar_url='https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=160&auto=format&fit=crop&q=80' if form.role.data == 'seeker' else 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=160&auto=format&fit=crop&q=80',
            skills='Python, PyTorch, Transformers, FastAPI, Docker, SQL' if form.role.data == 'seeker' else 'Talent Acquisition, Technical Screening, Engineering Leadership',
            ats_score=84 if form.role.data == 'seeker' else 90,
            matches_pct=92
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        # Log in newly registered user immediately for quick access!
        login_user(user)
        flash(f'Account created successfully! Welcome, {user.full_name}. You can now customize your profile.', 'success')
        return redirect(url_for('jobs.profile'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Welcome back, {user.full_name or user.username}!', 'success')
            return redirect(url_for('jobs.index'))
        flash('Invalid email or password. Please verify credentials or use the 1-click persona buttons below.', 'danger')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('jobs.index'))
