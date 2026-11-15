"""
Seed script to initialize and populate CareerForge AI database with exact reference jobs and users.
Compatible with both MySQL and SQLite engines.
"""
import os

from werkzeug.security import generate_password_hash
from app import db
from app.models import User, Job, Application

def seed(app=None, force=False):
    if app:
        with app.app_context():
            _do_seed(force=force)
    else:
        from app import create_app
        app = create_app()
        with app.app_context():
            _do_seed(force=force)

def _do_seed(force=False):
    if force:
        print("Dropping existing tables for clean re-seed...")
        db.drop_all()

    db.create_all()

    # Check if already seeded when not forced
    if not force and User.query.filter_by(username='elena').first():
        print("Database already seeded with default personas.")
        return

    print("Creating personas...")
    # 1. Admin
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        initial_admin_password = os.environ.get('INITIAL_ADMIN_PASSWORD')
        if initial_admin_password:
            admin = User(
                username='admin',
                email='admin@careerforge.ai',
                role='admin',
                full_name='System Administrator',
                headline='CareerForge Platform Admin',
                avatar_url='https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=160&auto=format&fit=crop&q=80',
                password_hash=generate_password_hash(initial_admin_password)
            )
            db.session.add(admin)
        else:
            print("Skipping admin account creation; set INITIAL_ADMIN_PASSWORD to create it.")

    # 2. Elena Vance (The Candidate featured in the UI)
    elena = User(
        username='elena',
        email='elena@careerforge.ai',
        role='seeker',
        full_name='Elena Vance',
        headline='Lead AI Systems & Solutions Architect',
        avatar_url='https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=160&auto=format&fit=crop&q=80',
        skills='Python, Transformers, Agentic UX, WBO, PyTorch, FastAPI, Three.js',
        ats_score=82,
        matches_pct=94,
        target_salary_min=160000,
        target_salary_max=220000,
        preferred_model='Remote',
        password_hash=generate_password_hash('demo123')
    )
    db.session.add(elena)

    # 3. Employers
    neuralvibe_emp = User(
        username='neuralvibe',
        email='hiring@neuralvibe.ai',
        role='employer',
        full_name='NeuralVibe Talent Team',
        headline='Next-Gen Autonomous Agent Orchestration',
        avatar_url='https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=160&auto=format&fit=crop&q=80',
        password_hash=generate_password_hash('demo123')
    )
    db.session.add(neuralvibe_emp)

    synthetix_emp = User(
        username='synthetix',
        email='careers@synthetix.design',
        role='employer',
        full_name='Synthetix Labs',
        headline='Real-Time Generative Interfaces & Spatial Compute',
        avatar_url='https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=160&auto=format&fit=crop&q=80',
        password_hash=generate_password_hash('demo123')
    )
    db.session.add(synthetix_emp)

    quantumflow_emp = User(
        username='quantumflow',
        email='recruiting@quantumflow.ai',
        role='employer',
        full_name='QuantumFlow AI Labs',
        headline='Distributed Multi-Agent Cognitive Architectures',
        avatar_url='https://images.unsplash.com/photo-1634017839464-5c339ebe3cb4?w=160&auto=format&fit=crop&q=80',
        password_hash=generate_password_hash('demo123')
    )
    db.session.add(quantumflow_emp)

    db.session.commit()

    print("Seeding openings...")
    # Exact Reference Job 1: Lead AI Solutions Architect @ NeuralVibe
    job1 = Job(
        title='Lead AI Solutions Architect',
        company='NeuralVibe',
        location='Remote',
        category='AI & Engineering',
        description='Architect and scale production enterprise multi-agent workflows, fine-tune transformer foundations, and engineer deterministic reasoning pipelines for Fortune 500 AI rollouts.',
        salary_min=160000,
        salary_max=210000,
        salary_display='$160k - $210k',
        job_type='Full-time',
        working_model='Remote',
        match_score=98,
        match_badge_text='AI Fit Badge',
        match_segments=5,
        adaptive_screening='Open',
        skills='Python, Transformers, Agentic UX',
        featured=True,
        employer_id=neuralvibe_emp.id
    )
    db.session.add(job1)

    # Exact Reference Job 2: Senior Interactive Designer @ Synthetix
    job2 = Job(
        title='Senior Interactive Designer',
        company='Synthetix',
        location='Hybrid, NYC',
        category='Product & Design',
        description='Design spatial, generative UI interfaces that adapt in real time to cognitive user intent. Bridge 3D WebGL interactions with high-fidelity design systems for next-generation AI workflows.',
        salary_min=140000,
        salary_max=185000,
        salary_display='$140k - $185k',
        job_type='Full-time',
        working_model='Hybrid',
        match_score=91,
        match_badge_text='Match Score',
        match_segments=4,
        adaptive_screening='Open',
        skills='Three.js, Design Systems, Generative UI',
        featured=True,
        employer_id=synthetix_emp.id
    )
    db.session.add(job2)

    # Rich AI Job 3: Autonomous Agent Engineer @ QuantumFlow AI
    job3 = Job(
        title='Autonomous Agent Engineer',
        company='QuantumFlow AI',
        location='Remote',
        category='AI & Engineering',
        description='Build self-healing, stateful autonomous agents leveraging hierarchical planning, vector memory retrieval, and tool-augmented execution loops.',
        salary_min=175000,
        salary_max=230000,
        salary_display='$175k - $230k',
        job_type='Full-time',
        working_model='Remote',
        match_score=95,
        match_badge_text='AI Fit Badge',
        match_segments=5,
        adaptive_screening='Fast-Track',
        skills='Python, LangGraph, Multi-Agent, VectorDB',
        featured=True,
        employer_id=quantumflow_emp.id
    )
    db.session.add(job3)

    # Rich AI Job 4: Generative AI Research Scientist @ CortexLabs
    job4 = Job(
        title='Generative AI Research Scientist',
        company='CortexLabs',
        location='San Francisco (Hybrid)',
        category='Research & Science',
        description='Pioneer next-generation multimodal latent diffusion models, explore inference acceleration techniques, and co-author high-impact research papers.',
        salary_min=190000,
        salary_max=260000,
        salary_display='$190k - $260k',
        job_type='Full-time',
        working_model='Hybrid',
        match_score=94,
        match_badge_text='AI Fit Badge',
        match_segments=5,
        adaptive_screening='Verified',
        skills='PyTorch, Diffusion Models, CUDA, Python',
        featured=True,
        employer_id=quantumflow_emp.id
    )
    db.session.add(job4)

    # Rich AI Job 5: Staff Agentic UX Architect @ AetherDynamics
    job5 = Job(
        title='Staff Agentic UX Architect',
        company='AetherDynamics',
        location='Seattle (Hybrid)',
        category='Product & Design',
        description='Formulate mental models for human-agent collaboration. Create design patterns that communicate uncertainty, latency, and autonomous intent seamlessly.',
        salary_min=165000,
        salary_max=215000,
        salary_display='$165k - $215k',
        job_type='Full-time',
        working_model='Hybrid',
        match_score=90,
        match_badge_text='Match Score',
        match_segments=4,
        adaptive_screening='Open',
        skills='Agentic UX, Prototyping, Design Systems',
        featured=True,
        employer_id=synthetix_emp.id
    )
    db.session.add(job5)

    # Rich AI Job 6: Distributed AI Infrastructure Lead @ HyperScale Core
    job6 = Job(
        title='Distributed AI Infrastructure Lead',
        company='HyperScale Core',
        location='Remote',
        category='Infrastructure & Cloud',
        description='Engineer fault-tolerant GPU orchestration clusters for continuous pre-training and ultra-low-latency speculative decoding inference at petabyte scale.',
        salary_min=180000,
        salary_max=245000,
        salary_display='$180k - $245k',
        job_type='Full-time',
        working_model='Remote',
        match_score=88,
        match_badge_text='Match Score',
        match_segments=4,
        adaptive_screening='Open',
        skills='Kubernetes, Rust, Python, vLLM, Ray',
        featured=True,
        employer_id=neuralvibe_emp.id
    )
    db.session.add(job6)

    db.session.commit()
    print("Database ready with CareerForge AI foundation data!")

if __name__ == '__main__':
    seed()
