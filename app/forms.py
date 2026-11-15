from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, TextAreaField, SelectField,
    IntegerField, BooleanField, SubmitField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, Optional, ValidationError
)
from app.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=3, max=64)
    ])
    email = StringField('Email', validators=[
        DataRequired(), Email(), Length(max=120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=6)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match.')
    ])
    role = SelectField('I am a', choices=[
        ('seeker', 'Job Seeker (Candidate)'),
        ('employer', 'Employer (Hiring Manager)'),
    ], validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log In')


class ProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[
        DataRequired(), Length(max=100)
    ])
    headline = StringField('Professional Headline', validators=[
        DataRequired(), Length(max=150)
    ])
    skills = StringField('Skills (comma-separated)', validators=[
        DataRequired(), Length(max=300)
    ])
    avatar_url = StringField('Avatar Image URL', validators=[
        Optional(), Length(max=300)
    ])
    target_salary_min = IntegerField('Target Min Salary ($/yr)', validators=[Optional()])
    target_salary_max = IntegerField('Target Max Salary ($/yr)', validators=[Optional()])
    preferred_model = SelectField('Preferred Working Model', choices=[
        ('Remote', 'Remote'),
        ('Hybrid', 'Hybrid'),
        ('Onsite', 'On-site'),
    ], default='Remote')
    resume_summary = TextAreaField('Executive Bio & Resume Summary', validators=[
        Optional(), Length(max=2000)
    ])
    submit = SubmitField('Save & Update Custom Profile')


class JobForm(FlaskForm):
    title = StringField('Job Title', validators=[
        DataRequired(), Length(max=120)
    ])
    company = StringField('Company', validators=[
        DataRequired(), Length(max=120)
    ])
    location = StringField('Location', validators=[
        DataRequired(), Length(max=120)
    ])
    category = SelectField('Category', choices=[
        ('AI & Engineering', 'AI & Machine Learning'),
        ('Product & Design', 'Product & Design'),
        ('Research & Science', 'Research & Science'),
        ('Infrastructure & Cloud', 'Infrastructure & Cloud'),
        ('Full-Stack', 'Full-Stack Software'),
        ('IT', 'IT & General Software'),
        ('Other', 'Other'),
    ], validators=[DataRequired()])
    job_type = SelectField('Job Type', choices=[
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Internship', 'Internship'),
    ], validators=[DataRequired()])
    working_model = SelectField('Working Model', choices=[
        ('Remote', 'Remote'),
        ('Hybrid', 'Hybrid'),
        ('Onsite', 'On-site'),
    ], default='Remote')
    salary_min = IntegerField('Min Salary (USD/year)', validators=[Optional()])
    salary_max = IntegerField('Max Salary (USD/year)', validators=[Optional()])
    skills = StringField('Required Skills (comma-separated)', validators=[Optional()])
    description = TextAreaField('Description', validators=[
        DataRequired(), Length(min=20)
    ])
    submit = SubmitField('Post Job')


class ApplicationForm(FlaskForm):
    cover_letter = TextAreaField('Cover Letter (optional)', validators=[
        Optional(), Length(max=2000)
    ])
    submit = SubmitField('Apply for this Job')
