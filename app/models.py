from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='seeker')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # CareerForge AI profile enhancements
    full_name = db.Column(db.String(100), default='')
    headline = db.Column(db.String(150), default='Lead AI Solutions Architect & Systems Strategist')
    avatar_url = db.Column(
        db.String(300),
        default='https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=160&auto=format&fit=crop&q=80'
    )
    skills = db.Column(
        db.Text,
        default='Python, Transformers, Agentic UX, WBO, PyTorch, FastAPI, Three.js'
    )
    ats_score = db.Column(db.Integer, default=82)
    matches_pct = db.Column(db.Integer, default=94)
    target_salary_min = db.Column(db.Integer, default=150000)
    target_salary_max = db.Column(db.Integer, default=220000)
    preferred_model = db.Column(db.String(30), default='Remote')
    resume_summary = db.Column(
        db.Text,
        default='Accomplished AI Solutions Architect with 8+ years designing agentic workflows, transformer model fine-tuning, high-throughput Python microservices, and interactive generative AI user experiences.'
    )

    jobs = db.relationship('Job', backref='employer', lazy='dynamic')
    applications = db.relationship('Application', backref='applicant', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_skills_list(self):
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name or self.username,
            'headline': self.headline,
            'email': self.email,
            'role': self.role,
            'avatar_url': self.avatar_url,
            'skills': self.get_skills_list(),
            'ats_score': self.ats_score,
            'matches_pct': self.matches_pct,
            'target_salary_min': self.target_salary_min,
            'target_salary_max': self.target_salary_max,
            'preferred_model': self.preferred_model,
        }

    def __repr__(self):
        return f'<User {self.username}>'


class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(60), nullable=False, default='AI & Engineering')
    description = db.Column(db.Text, nullable=False)
    salary_min = db.Column(db.Integer, nullable=True)
    salary_max = db.Column(db.Integer, nullable=True)
    salary_display = db.Column(db.String(50), default='$160k - $210k')
    job_type = db.Column(db.String(30), default='Full-time')
    working_model = db.Column(db.String(30), default='Remote')  # Remote, Hybrid, Onsite
    match_score = db.Column(db.Integer, default=95)
    match_badge_text = db.Column(db.String(50), default='AI Fit Badge')
    match_segments = db.Column(db.Integer, default=5)
    adaptive_screening = db.Column(db.String(50), default='Open')
    skills = db.Column(db.String(250), default='Python, Transformers, Agentic UX')
    featured = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    employer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    applications = db.relationship('Application', backref='job', lazy='dynamic')

    def get_skills_list(self):
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'category': self.category,
            'description': self.description,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'salary_display': self.salary_display or (
                f"${self.salary_min // 1000}k - ${self.salary_max // 1000}k"
                if self.salary_min and self.salary_max else "Competitive"
            ),
            'job_type': self.job_type,
            'working_model': self.working_model,
            'match_score': self.match_score,
            'match_badge_text': self.match_badge_text,
            'match_segments': self.match_segments,
            'adaptive_screening': self.adaptive_screening,
            'skills': self.get_skills_list(),
            'featured': self.featured,
            'created_at': self.created_at.strftime('%Y-%m-%d'),
            'applications_count': self.applications.count(),
        }

    def __repr__(self):
        return f'<Job {self.title}>'


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default='pending')
    cover_letter = db.Column(db.Text, nullable=True)
    tailored_resume_summary = db.Column(db.Text, nullable=True)
    match_score_at_apply = db.Column(db.Integer, default=98)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('job_id', 'user_id', name='unique_application'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'cover_letter': self.cover_letter,
            'match_score_at_apply': self.match_score_at_apply,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
            'job': self.job.to_dict() if self.job else None,
            'applicant': self.applicant.to_dict() if self.applicant else None,
        }

    def __repr__(self):
        return f'<Application {self.id}>'
