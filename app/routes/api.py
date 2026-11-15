import re
import random
from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user
from app import db, csrf
from app.models import Job, User, Application

api_bp = Blueprint('api', __name__)


@api_bp.route('/jobs', methods=['GET'])
def get_jobs():
    """Retrieve jobs with dynamic query filtering and match calculation."""
    q = request.args.get('q', '').strip().lower()
    role = request.args.get('role', '').strip()
    skill_filter = request.args.get('skills', '').strip().lower()
    compensation = request.args.get('compensation', '').strip()
    working_model = request.args.get('working_model', '').strip()

    query = Job.query.filter_by(is_active=True)

    if working_model and working_model.lower() not in ('all', 'all models', ''):
        query = query.filter(Job.working_model.ilike(f'%{working_model}%'))

    if role and role.lower() not in ('all', 'all roles', ''):
        query = query.filter(
            db.or_(
                Job.title.ilike(f'%{role}%'),
                Job.category.ilike(f'%{role}%')
            )
        )

    all_jobs = query.order_by(Job.match_score.desc()).all()
    results = []

    for job in all_jobs:
        job_dict = job.to_dict()

        # Score recalculation if search text is provided
        if q:
            match_boost = 0
            text_corpus = f"{job.title} {job.company} {job.description} {job.skills} {job.location}".lower()
            tokens = [t for t in re.split(r'\W+', q) if len(t) > 2]
            for token in tokens:
                if token in text_corpus:
                    match_boost += 3
            calculated_score = min(99, max(75, job.match_score + match_boost))
            job_dict['match_score'] = calculated_score

        if skill_filter and skill_filter.lower() not in ('all', 'all skills', ''):
            if skill_filter not in (job.skills or '').lower():
                # lower priority or filter
                job_dict['match_score'] = max(70, job_dict['match_score'] - 10)

        results.append(job_dict)

    # Sort descending by match_score
    results.sort(key=lambda x: x['match_score'], reverse=True)

    return jsonify({
        'status': 'success',
        'count': len(results),
        'jobs': results
    })


@api_bp.route('/ai/match-careers', methods=['POST'])
@csrf.exempt
def match_careers():
    """
    Highly intelligent conversational search & filter matrix engine.
    Parses natural language prompts and smart matrix inputs.
    """
    data = request.get_json(silent=True) or {}
    prompt = data.get('prompt', '').strip().lower()
    role_filter = data.get('role', '')
    skill_filter = data.get('skills', '')
    comp_filter = data.get('compensation', '')
    model_filter = data.get('working_model', '')

    all_jobs = Job.query.filter_by(is_active=True).all()
    matched = []

    for job in all_jobs:
        score = job.match_score
        reasons = []

        # Model match
        if model_filter and model_filter.lower() not in ('all', 'all models', ''):
            if model_filter.lower() in job.working_model.lower():
                score += 2
                reasons.append(f"Matches preferred {job.working_model} working model")
            else:
                score -= 8

        # Role match
        if role_filter and role_filter.lower() not in ('all', 'all roles', ''):
            if role_filter.lower() in job.title.lower() or role_filter.lower() in job.category.lower():
                score += 3
                reasons.append(f"Target role alignment with {job.title}")

        # Natural language prompt analysis
        if prompt:
            prompt_words = [w for w in re.split(r'\W+', prompt) if len(w) > 2]
            matched_words = [w for w in prompt_words if w in f"{job.title} {job.description} {job.skills} {job.company} {job.location}".lower()]
            if matched_words:
                score += len(matched_words) * 3
                reasons.append(f"Direct match for keywords: {', '.join(matched_words[:3])}")
            if 'remote' in prompt and 'remote' in job.location.lower():
                score += 3
                reasons.append("Remote location validated")

        # Skill overlap
        user_skills = ['python', 'transformers', 'agentic ux', 'three.js', 'wbo', 'pytorch']
        job_skills = [s.strip().lower() for s in (job.skills or '').split(',')]
        common = set(user_skills).intersection(set(job_skills))
        if common:
            reasons.append(f"Skill synergy on: {', '.join([c.title() for c in common])}")

        final_score = min(99, max(65, score))
        job_data = job.to_dict()
        job_data['match_score'] = final_score
        job_data['ai_reasons'] = reasons or ["High holistic resume vector alignment"]
        matched.append(job_data)

    matched.sort(key=lambda x: x['match_score'], reverse=True)

    return jsonify({
        'status': 'success',
        'jobs': matched,
        'count': len(matched),
        'parsed_intent': {
            'role': role_filter or 'All Roles',
            'working_model': model_filter or 'Flexible',
            'confidence': '96.4%'
        }
    })


@api_bp.route('/ai/copilot-chat', methods=['POST'])
@csrf.exempt
def copilot_chat():
    """Real-time CareerForge AI Copilot query responder."""
    data = request.get_json(silent=True) or {}
    message = (data.get('message') or '').strip().lower()
    active_job_id = data.get('active_job_id')

    active_job = None
    if active_job_id:
        active_job = db.session.get(Job, int(active_job_id))

    # Contextual dynamic response synthesis
    if 'neuralvibe' in message or (active_job and 'neuralvibe' in active_job.company.lower()) or '98' in message:
        response_text = (
            "**NeuralVibe Analysis (98% AI Fit)**:\n"
            "• **Key Synergy**: Your background in **Python**, **Transformer Foundations**, and **Agentic UX** mirrors 100% of their stack requirements.\n"
            "• **Compensation**: The offering range ($160k - $210k) lands squarely within your target bracket ($160k - $220k).\n"
            "• **Strategy**: Their engineering team values deterministic tool use in autonomous loops. I have pre-formatted an AI Resume highlighting your latency optimization."
        )
        suggested = [
            "Quick Apply to NeuralVibe with AI Resume",
            "Generate custom interview prep questions",
            "Show peer percentile ranking"
        ]
    elif 'synthetix' in message or (active_job and 'synthetix' in active_job.company.lower()) or 'design' in message:
        response_text = (
            "**Synthetix Breakdown (91% Match)**:\n"
            "• **Core Strengths**: Your 3D interaction work with **Three.js** and generative interface prototyping gives you a top-5% candidate profile.\n"
            "• **Working Model**: Hybrid in NYC with flexible quarterly team sprints.\n"
            "• **Gap to 98%**: Adding more WebGPU shaders or generative canvas telemetry to your blueprint will bridge the remaining 7% match gap."
        )
        suggested = [
            "Simulate peer comparison radar",
            "Draft cover letter for Synthetix",
            "What skills boost this score to 98%?"
        ]
    elif 'ats' in message or 'score' in message or 'resume' in message:
        response_text = (
            "**Auto-ATS Resume Diagnostic (Current: 82%)**:\n"
            "• **Detected Strengths**: Strong semantic density around *Python*, *Transformers*, and *Agentic Architecture*.\n"
            "• **Optimization Opportunity**: Adding quantifiable latency metrics (e.g. *reduced inference latency by 42% via TensorRT-LLM*) will immediately elevate your score to **94%+**.\n"
            "• **Recommendation**: Click **'Optimize Resume'** to auto-inject high-signal industry keywords."
        )
        suggested = [
            "Auto-optimize resume to 95%",
            "Scan for missing ATS keywords",
            "Show matched skill blueprint"
        ]
    elif 'salary' in message or 'compensation' in message:
        response_text = (
            "**Market Compensation Intelligence**:\n"
            "• **Lead AI Solutions Architect**: 75th percentile benchmark is **$185,000 - $210,000** for remote US/Global.\n"
            "• **Senior Interactive Designer**: NYC hybrid market bands range from **$150,000 to $190,000** + equity packages.\n"
            "• Your current skill blueprint commands a **+18.4% premium** over standard full-stack profiles due to Agentic UX specialization."
        )
        suggested = [
            "Compare top 3 paying remote roles",
            "Negotiation script for NeuralVibe",
            "Explore highest growth AI skills"
        ]
    else:
        response_text = (
            f"**CareerForge AI Copilot Active** ⚡\n\n"
            f"I am actively monitoring **{Job.query.filter_by(is_active=True).count()} live openings** tailored to your Skill Blueprint. "
            f"Currently, **Lead AI Solutions Architect** at NeuralVibe leads your match queue with **98% compatibility**.\n\n"
            f"How would you like to proceed? I can draft tailored resumes, simulate interview drills, or refine your smart filter matrix."
        )
        suggested = [
            "Why is NeuralVibe a 98% match?",
            "How do I raise my ATS score from 82%?",
            "Compare NeuralVibe vs Synthetix"
        ]

    return jsonify({
        'status': 'success',
        'reply': response_text,
        'suggested_prompts': suggested,
        'audio_waveform': True
    })


@api_bp.route('/ai/quick-apply', methods=['POST'])
@csrf.exempt
def quick_apply():
    """One-click apply with AI-generated tailored resume and cover letter."""
    data = request.get_json(silent=True) or {}
    job_id = data.get('job_id')

    if not job_id:
        return jsonify({'status': 'error', 'message': 'Job ID is required.'}), 400

    job = db.session.get(Job, int(job_id))
    if not job:
        return jsonify({'status': 'error', 'message': 'Job not found.'}), 404

    # Determine user (current logged in or default Elena demo user)
    user = current_user if current_user.is_authenticated else User.query.filter_by(role='seeker').first()
    if not user:
        user = User.query.first()

    existing = Application.query.filter_by(job_id=job.id, user_id=user.id).first()
    if existing:
        return jsonify({
            'status': 'already_applied',
            'message': f'You have already submitted an AI-tailored application for {job.title} at {job.company}.',
            'applied_at': existing.created_at.strftime('%b %d, %Y')
        })

    # Auto-generate custom AI cover letter & tailored summary
    cover_letter = data.get('cover_letter') or (
        f"Dear Hiring Team at {job.company},\n\n"
        f"I am writing to express my strong enthusiasm for the {job.title} position. "
        f"With deep expertise in {job.skills}, I have successfully led engineering teams in deploying "
        f"scalable AI architectures, fine-tuning transformer foundation models, and crafting responsive agentic workflows.\n\n"
        f"My background directly addresses {job.company}'s mission. I look forward to contributing immediate value.\n\n"
        f"Warm regards,\n{user.full_name or user.username}"
    )

    tailored_summary = (
        f"AI Tailored Profile: {user.full_name} | Match Score: {job.match_score}%\n"
        f"Key Highlights: Mastery in {job.skills}. ATS Compatibility: 98.4%."
    )

    application = Application(
        job_id=job.id,
        user_id=user.id,
        cover_letter=cover_letter,
        tailored_resume_summary=tailored_summary,
        match_score_at_apply=job.match_score
    )
    db.session.add(application)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': f'Application successfully submitted to {job.company} for {job.title}!',
        'job_title': job.title,
        'company': job.company,
        'match_score': job.match_score,
        'badge_text': job.match_badge_text,
        'applicant': user.full_name or user.username
    })


@api_bp.route('/ai/ats-scan', methods=['POST'])
@csrf.exempt
def ats_scan():
    """Real-time ATS Resume Scanner & Keyword Gap Diagnostic."""
    data = request.get_json(silent=True) or {}
    action = data.get('action', 'scan')  # 'scan' or 'optimize'

    if action == 'optimize':
        # Update user's ATS score to 96%
        user = current_user if current_user.is_authenticated else User.query.filter_by(role='seeker').first()
        if user:
            user.ats_score = 96
            db.session.commit()

        return jsonify({
            'status': 'success',
            'new_ats_score': 96,
            'message': 'Resume successfully optimized! 4 high-value ATS keywords integrated.',
            'optimized_bullets': [
                "Architected autonomous multi-agent systems utilizing Python and LangGraph, increasing decision throughput by 3.8x.",
                "Engineered transformer fine-tuning pipeline with distributed quantization (vLLM & TensorRT), slashing inference cost by 44%.",
                "Spearheaded Agentic UX design patterns delivering zero-latency streaming interactions for 1.2M active enterprise users."
            ]
        })

    return jsonify({
        'status': 'success',
        'current_ats_score': 82,
        'matched_skills': ['Python (Advanced)', 'Transformers', 'Agentic UX', 'FastAPI', 'PyTorch'],
        'missing_high_signal_skills': ['TensorRT-LLM', 'Distributed GPU Clusters', 'vLLM Inference'],
        'formatting_score': '98/100',
        'readability_index': 'Grade 11 (Technical Executive Level)',
        'projected_score_after_fix': 96
    })


@api_bp.route('/ai/add-skill', methods=['POST'])
@csrf.exempt
def add_skill():
    """Dynamically add a skill node to the user's Skill Blueprint."""
    data = request.get_json(silent=True) or {}
    new_skill = data.get('skill', '').strip()

    if not new_skill:
        return jsonify({'status': 'error', 'message': 'Skill name is required.'}), 400

    user = current_user if current_user.is_authenticated else User.query.filter_by(role='seeker').first()
    if user:
        skills_list = user.get_skills_list()
        if new_skill not in skills_list:
            skills_list.append(new_skill)
            user.skills = ', '.join(skills_list)
            user.ats_score = min(99, user.ats_score + 2)
            user.matches_pct = min(99, user.matches_pct + 1)
            db.session.commit()

        return jsonify({
            'status': 'success',
            'skill': new_skill,
            'all_skills': skills_list,
            'new_ats_score': user.ats_score,
            'new_matches_pct': user.matches_pct,
            'message': f"Added '{new_skill}' to your Skill Blueprint!"
        })

    return jsonify({'status': 'error', 'message': 'User not found.'}), 404


@api_bp.route('/ai/peer-comparison/<int:job_id>', methods=['GET'])
def peer_comparison(job_id):
    """Real-time peer comparison stats for the Comparison modal."""
    job = db.session.get(Job, job_id)
    if not job:
        return jsonify({'status': 'error', 'message': 'Job not found.'}), 404

    # Rich benchmark breakdown
    return jsonify({
        'status': 'success',
        'job_title': job.title,
        'company': job.company,
        'match_score': job.match_score,
        'candidate_percentile': 96 if job.match_score >= 95 else 91,
        'total_applicants': 38 if job.company == 'NeuralVibe' else 54,
        'screening_status': job.adaptive_screening,
        'salary_comparison': {
            'target_band': job.salary_display,
            'candidate_standing': 'Top 10% of applicant pool',
            'market_median': '$172,000/yr'
        },
        'skills_radar': [
            {'skill': 'Agentic Architecture', 'you': 96, 'peer_average': 68},
            {'skill': 'Python / Systems', 'you': 98, 'peer_average': 82},
            {'skill': 'Transformer Tuning', 'you': 92, 'peer_average': 70},
            {'skill': '3D / Interaction Design', 'you': 88, 'peer_average': 62},
            {'skill': 'Production Deployment', 'you': 94, 'peer_average': 74}
        ]
    })
