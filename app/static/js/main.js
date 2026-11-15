/**
 * CareerForge AI — Master Client Engine
 * Includes:
 * 1. Three.js 3D Glowing Particle Mesh Wave Simulation
 * 2. Conversational Search & Smart Filter Matrix Engine
 * 3. Dynamic Interactive Skill Blueprint Graph
 * 4. Copilot Assistant with Animated Equalizer Waveform & Chat
 * 5. Quick Apply with AI Tailoring & DB Persistence
 * 6. Real-Time Peer Comparison & ATS Diagnostic Modals
 */

let particleMeshAnimId = null;
let peerRadarChart = null;
let skillsMatrixRadarChart = null;
let activeJobIdForCopilot = 1;

document.addEventListener('DOMContentLoaded', function () {
    // 1. Initialize Three.js 3D Particle Mesh Wave
    initHeroParticleWave();

    // 2. Initialize Skills Matrix Radar (if on that tab or on demand)
    initSkillsMatrixRadar();

    // 3. Initialize Skill Graph physics animation
    initSkillGraphInteractivity();

    // 4. Listen for window resize
    window.addEventListener('resize', handleWindowResize);
});

/* ==========================================================================
   1. Three.js 3D Glowing Particle Wave Mesh Simulation
   ========================================================================== */
function initHeroParticleWave() {
    const container = document.getElementById('hero-particle-mesh-container');
    if (!container) return;

    const width = container.clientWidth || 450;
    const height = container.clientHeight || 220;

    // Scene & Camera
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(55, width / height, 0.1, 1000);
    camera.position.set(0, 35, 75);
    camera.lookAt(0, 0, 0);

    // WebGL Renderer with alpha transparency
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // Particle Grid Geometry
    const cols = 55;
    const rows = 45;
    const count = cols * rows;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);

    const colorCyan = new THREE.Color(0x00f2fe);
    const colorPurple = new THREE.Color(0x8b5cf6);
    const colorMagenta = new THREE.Color(0xec4899);

    let idx = 0;
    for (let i = 0; i < cols; i++) {
        for (let j = 0; j < rows; j++) {
            const u = i / cols;
            const v = j / rows;
            const x = (i - cols / 2) * 2.2;
            const z = (j - rows / 2) * 2.2;
            const y = 0;

            positions[idx * 3] = x;
            positions[idx * 3 + 1] = y;
            positions[idx * 3 + 2] = z;

            // Interpolate colors: Magenta -> Purple -> Cyan
            const mixRatio = (u + v) * 0.5;
            const pColor = new THREE.Color();
            if (mixRatio < 0.5) {
                pColor.copy(colorMagenta).lerp(colorPurple, mixRatio * 2);
            } else {
                pColor.copy(colorPurple).lerp(colorCyan, (mixRatio - 0.5) * 2);
            }

            colors[idx * 3] = pColor.r;
            colors[idx * 3 + 1] = pColor.g;
            colors[idx * 3 + 2] = pColor.b;

            idx++;
        }
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    // Particle Texture creation
    const canvas = document.createElement('canvas');
    canvas.width = 32;
    canvas.height = 32;
    const ctx = canvas.getContext('2d');
    const grad = ctx.createRadialGradient(16, 16, 0, 16, 16, 16);
    grad.addColorStop(0, 'rgba(255,255,255,1)');
    grad.addColorStop(0.3, 'rgba(0,242,254,0.8)');
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 32, 32);

    const texture = new THREE.CanvasTexture(canvas);
    const material = new THREE.PointsMaterial({
        size: 1.8,
        vertexColors: true,
        map: texture,
        transparent: true,
        blending: THREE.AdditiveBlending,
        depthWrite: false
    });

    const particles = new THREE.Points(geometry, material);
    scene.add(particles);

    // Mouse tracking for interactive ripple
    let mouseX = 0;
    let mouseY = 0;
    container.addEventListener('mousemove', function (e) {
        const rect = container.getBoundingClientRect();
        mouseX = ((e.clientX - rect.left) / width) * 2 - 1;
        mouseY = -(((e.clientY - rect.top) / height) * 2 - 1);
    });

    // Animation Loop
    let clock = new THREE.Clock();
    function animate() {
        particleMeshAnimId = requestAnimationFrame(animate);
        const elapsedTime = clock.getElapsedTime();

        const posAttr = geometry.attributes.position;
        const posArray = posAttr.array;

        let index = 0;
        for (let i = 0; i < cols; i++) {
            for (let j = 0; j < rows; j++) {
                const u = i / cols;
                const v = j / rows;
                // Dual sine/cosine wave + mouse distortion
                const wave1 = Math.sin(u * 5 + elapsedTime * 1.4) * 6.0;
                const wave2 = Math.cos(v * 4 + elapsedTime * 1.8) * 5.0;
                const ripple = Math.sin(Math.sqrt((i - 27) * (i - 27) + (j - 22) * (j - 22)) * 0.4 - elapsedTime * 2.5) * 3.5;
                const mouseDist = Math.sin((u - (mouseX * 0.5 + 0.5)) * 6) * 4;

                posArray[index * 3 + 1] = wave1 + wave2 + ripple + mouseDist;
                index++;
            }
        }
        posAttr.needsUpdate = true;

        particles.rotation.y = Math.sin(elapsedTime * 0.2) * 0.15;
        particles.rotation.z = Math.cos(elapsedTime * 0.15) * 0.08;

        renderer.render(scene, camera);
    }
    animate();

    container._renderer = renderer;
    container._camera = camera;
}

function handleWindowResize() {
    const container = document.getElementById('hero-particle-mesh-container');
    if (container && container._renderer && container._camera) {
        const w = container.clientWidth;
        const h = container.clientHeight || 220;
        container._camera.aspect = w / h;
        container._camera.updateProjectionMatrix();
        container._renderer.setSize(w, h);
    }
}

/* ==========================================================================
   2. Conversational Search & Smart Filter Matrix Engine
   ========================================================================== */
function executeAiSearch() {
    const promptInput = document.getElementById('ai-search-prompt');
    const roleSelect = document.getElementById('filter-role');
    const skillsSelect = document.getElementById('filter-skills');
    const compSelect = document.getElementById('filter-comp');
    const modelSelect = document.getElementById('filter-model');

    const payload = {
        prompt: promptInput ? promptInput.value.trim() : '',
        role: roleSelect ? roleSelect.value : '',
        skills: skillsSelect ? skillsSelect.value : '',
        compensation: compSelect ? compSelect.value : '',
        working_model: modelSelect ? modelSelect.value : ''
    };

    // Visual feedback on search button / card
    const container = document.getElementById('openings-container');
    if (container) {
        container.style.opacity = '0.5';
    }

    fetch('/api/ai/match-careers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (container) {
            container.style.opacity = '1';
        }
        if (data.status === 'success' && data.jobs) {
            renderJobCards(data.jobs);
            // Update speech bubble in copilot with dynamic search synthesis
            const bubble = document.getElementById('copilot-speech-bubble');
            if (bubble) {
                bubble.innerText = `Filtered ${data.jobs.length} roles matching '${payload.prompt || payload.role || 'matrix query'}'. Lead match: ${data.jobs[0]?.title || 'NeuralVibe'}`;
            }
        }
    })
    .catch(err => {
        console.error('Error matching careers:', err);
        if (container) container.style.opacity = '1';
    });
}

function renderJobCards(jobs) {
    const container = document.getElementById('openings-container');
    if (!container) return;

    if (!jobs || jobs.length === 0) {
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <div class="cf-glass-card p-4">
                    <i class="bi bi-search text-cyan fs-2 mb-2 d-block"></i>
                    <h5 class="text-white">No Direct Openings Matched</h5>
                    <p class="text-muted fs-sm">Try broadening your prompt keywords or resetting the Smart Filter Matrix.</p>
                    <button class="btn cf-btn-secondary" onclick="resetFilters()">Reset Matrix Filters</button>
                </div>
            </div>`;
        return;
    }

    let html = '';
    jobs.forEach(job => {
        const isSynthetix = job.company === 'Synthetix';
        const offset = 163.36 - (163.36 * job.match_score / 100);

        let middleSection = '';
        if (isSynthetix) {
            middleSection = `
                <div class="cf-realtime-interface mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <span class="fs-xs text-muted">Real-time Interface</span>
                        <span class="text-muted fs-xxs"><i class="bi bi-three-dots"></i></span>
                    </div>
                    <div class="fs-xs text-light mb-2">Real-time peer comparisons</div>
                    <div class="d-flex gap-2">
                        <button class="btn btn-sm cf-btn-secondary" onclick="openPeerComparisonModal(${job.id}, '${job.title}', '${job.company}')">
                            <i class="bi bi-people-fill text-cyan me-1"></i> Compariton
                        </button>
                    </div>
                </div>

                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center fs-xs mb-1">
                        <span class="text-muted">Salary Estimation</span>
                        <span class="text-white fw-bold">${job.salary_display}</span>
                    </div>
                    <div class="cf-slider-track">
                        <div class="cf-slider-gradient" style="width: 78%;"></div>
                    </div>
                </div>

                <div class="mb-3 fs-xs text-muted">
                    <span>Adaptive Screening: <strong class="text-success">${job.adaptive_screening || 'Open'}</strong></span>
                </div>
            `;
        } else {
            middleSection = `
                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center fs-xs mb-1">
                        <span class="text-muted">Match Details</span>
                    </div>
                    <div class="cf-segmented-bar">
                        <span class="seg active"></span>
                        <span class="seg active"></span>
                        <span class="seg active"></span>
                        <span class="seg active"></span>
                        <span class="seg active"></span>
                    </div>
                </div>

                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center fs-xs mb-1">
                        <span class="text-muted">Salary</span>
                        <span class="text-white fw-semibold">${job.salary_display}</span>
                    </div>
                    <div class="cf-slider-track">
                        <div class="cf-slider-fill" style="width: 82%;">
                            <span class="cf-slider-handle"></span>
                        </div>
                    </div>
                </div>
            `;
        }

        const skillsPills = (job.skills || []).map(s => `<span class="cf-skill-tag">✓ ${s}</span>`).join(' ');

        html += `
            <div class="col-xl-6 job-card-wrapper" data-job-id="${job.id}">
                <div class="cf-glass-card cf-job-card h-100 d-flex flex-column">
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <div>
                            <h4 class="cf-job-title mb-1">${job.title}</h4>
                            <div class="cf-job-company-location text-muted">
                                ${job.company} (${job.working_model}${job.location.includes('NYC') ? ', NYC' : ''})
                            </div>
                        </div>

                        <div class="cf-donut-gauge" title="AI Match Calculation">
                            <svg viewBox="0 0 64 64" width="60" height="60">
                                <circle cx="32" cy="32" r="26" stroke="rgba(255, 255, 255, 0.08)" stroke-width="4.5" fill="none"/>
                                <circle cx="32" cy="32" r="26" stroke="#00f2fe" stroke-width="4.5" fill="none"
                                        stroke-dasharray="163.36" stroke-dashoffset="${offset}"
                                        stroke-linecap="round" class="cf-gauge-circle"/>
                            </svg>
                            <div class="cf-gauge-text">
                                <span class="score">${job.match_score}%</span>
                                <span class="label">${job.match_badge_text || 'AI Fit Badge'}</span>
                            </div>
                        </div>
                    </div>

                    ${middleSection}

                    <div class="mb-4">
                        <div class="fs-xs text-muted mb-2">Skills</div>
                        <div class="d-flex gap-2 flex-wrap">
                            ${skillsPills}
                        </div>
                    </div>

                    <div class="mt-auto">
                        <button type="button" class="btn cf-btn-quick-apply w-100" 
                                onclick="openQuickApplyModal(${job.id}, '${job.title}', '${job.company}', ${job.match_score}, '${job.salary_display}', '${(job.skills || []).join(', ')}')">
                            Quick Apply with AI Resume
                        </button>
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

function resetFilters() {
    document.getElementById('ai-search-prompt').value = '';
    document.getElementById('filter-role').value = '';
    document.getElementById('filter-skills').value = '';
    document.getElementById('filter-comp').value = '';
    document.getElementById('filter-model').value = '';
    executeAiSearch();
}

function toggleSearchSettings() {
    alert("AI Engine Prompt Settings:\n• Temperature: 0.15 (Deterministic Vector Re-ranking)\n• Embedding Model: Gemini Text-Embedding-004\n• Cosine Threshold: >0.82");
}

/* ==========================================================================
   3. Interactive Dynamic Skill Blueprint Graph
   ========================================================================== */
function initSkillGraphInteractivity() {
    const nodes = document.querySelectorAll('.graph-node.satellite');
    nodes.forEach(node => {
        node.addEventListener('mouseenter', function () {
            this.style.filter = 'drop-shadow(0 0 12px #00f2fe)';
        });
        node.addEventListener('mouseleave', function () {
            this.style.filter = '';
        });
    });
}

function filterBySkillNode(skillName) {
    const searchInput = document.getElementById('ai-search-prompt');
    if (searchInput) {
        searchInput.value = skillName === 'Skills' ? 'Transformers Agentic UX' : skillName;
        executeAiSearch();
    }
}

function openAddSkillModal() {
    const modalEl = document.getElementById('addSkillModal');
    if (modalEl) {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    }
}

function quickFillSkill(name) {
    const input = document.getElementById('new-skill-input');
    if (input) input.value = name;
}

function submitAddSkill() {
    const input = document.getElementById('new-skill-input');
    const skill = input ? input.value.trim() : '';
    if (!skill) return;

    fetch('/api/ai/add-skill', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skill: skill })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            // Update ATS score in subcard and header
            const atsDisp = document.getElementById('ats-score-display');
            const atsBar = document.getElementById('ats-progress-bar');
            const headerMatch = document.getElementById('header-match-pct');

            if (atsDisp) atsDisp.innerText = data.new_ats_score + '%';
            if (atsBar) atsBar.style.width = data.new_ats_score + '%';
            if (headerMatch) headerMatch.innerText = data.new_matches_pct + '%';

            // Close modal
            const modalEl = document.getElementById('addSkillModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();

            // Notify user
            showFloatingAlert(`Added "${skill}" to your Skill Blueprint! ATS Score elevated to ${data.new_ats_score}%.`, 'success');
        }
    })
    .catch(err => console.error(err));
}

function rebalanceSkillGraph() {
    const svg = document.getElementById('skill-graph-svg');
    if (svg) {
        svg.style.transform = 'scale(0.98)';
        setTimeout(() => { svg.style.transform = 'scale(1)'; }, 200);
    }
}

/* ==========================================================================
   4. Quick Apply with AI Resume Modal & Application Submission
   ========================================================================== */
function openQuickApplyModal(id, title, company, score, salary, skills) {
    activeJobIdForCopilot = id;
    document.getElementById('apply-job-title').innerText = title;
    document.getElementById('apply-job-company').innerText = `${company} (${salary})`;
    document.getElementById('apply-match-score').innerText = `${score}%`;
    document.getElementById('apply-salary-band').innerText = salary;

    const skillsContainer = document.getElementById('apply-skills-tags');
    if (skillsContainer) {
        const skillsArray = (skills || 'Python, Transformers, Agentic UX').split(',');
        skillsContainer.innerHTML = skillsArray.map(s => `<span class="cf-tag-pill active">✓ ${s.trim()}</span>`).join(' ');
    }

    // Pre-populate intelligent AI cover letter
    const textarea = document.getElementById('apply-cover-letter');
    if (textarea) {
        textarea.value = `Dear Hiring Team at ${company},\n\nI am thrilled to apply for the ${title} opening. With documented mastery in ${skills || 'Python, Transformers, and Agentic UX'}, my background directly aligns with your deterministic reasoning pipelines and autonomous infrastructure. I look forward to accelerating ${company}'s delivery velocity from day one.\n\nWarm regards,\nElena Vance`;
    }

    const modalEl = document.getElementById('quickApplyModal');
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
}

function submitQuickApply() {
    const btn = document.getElementById('confirmQuickApplyBtn');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> Delivering Application...`;
    }

    const coverLetter = document.getElementById('apply-cover-letter').value;

    fetch('/api/ai/quick-apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            job_id: activeJobIdForCopilot,
            cover_letter: coverLetter
        })
    })
    .then(res => res.json())
    .then(data => {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<i class="bi bi-send-fill me-1"></i> Confirm 1-Click Submission`;
        }

        const modalEl = document.getElementById('quickApplyModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();

        showFloatingAlert(data.message || 'Application submitted successfully!', data.status === 'already_applied' ? 'warning' : 'success');
    })
    .catch(err => {
        console.error(err);
        if (btn) btn.disabled = false;
    });
}

/* ==========================================================================
   5. Real-Time Peer Comparison & Radar Chart
   ========================================================================== */
function openPeerComparisonModal(jobId, title, company) {
    document.getElementById('peer-job-title').innerText = title;
    document.getElementById('peer-job-company').innerText = company;

    fetch(`/api/ai/peer-comparison/${jobId}`)
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            document.getElementById('peer-percentile').innerText = `Top ${100 - data.candidate_percentile}%`;
            renderPeerRadarChart(data.skills_radar);
        }
    })
    .catch(err => console.error(err));

    const modalEl = document.getElementById('peerComparisonModal');
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
}

function renderPeerRadarChart(radarData) {
    const ctx = document.getElementById('peerRadarCanvas');
    if (!ctx) return;

    if (peerRadarChart) {
        peerRadarChart.destroy();
    }

    const labels = radarData.map(d => d.skill);
    const youScores = radarData.map(d => d.you);
    const peerScores = radarData.map(d => d.peer_average);

    peerRadarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Elena Vance (You)',
                    data: youScores,
                    borderColor: '#00f2fe',
                    backgroundColor: 'rgba(0, 242, 254, 0.25)',
                    borderWidth: 2,
                    pointBackgroundColor: '#00f2fe'
                },
                {
                    label: 'Applicant Pool Avg',
                    data: peerScores,
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.15)',
                    borderWidth: 1.5,
                    borderDash: [4, 4],
                    pointBackgroundColor: '#8b5cf6'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                    grid: { color: 'rgba(255, 255, 255, 0.08)' },
                    pointLabels: {
                        color: '#cbd5e1',
                        font: { size: 10, family: 'Plus Jakarta Sans' }
                    },
                    ticks: { display: false, max: 100, min: 20 }
                }
            },
            plugins: {
                legend: {
                    labels: { color: '#ffffff', font: { size: 11 } }
                }
            }
        }
    });
}

function openApplyForPeerRole() {
    const modalEl = document.getElementById('peerComparisonModal');
    const modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) modal.hide();

    openQuickApplyModal(2, 'Senior Interactive Designer', 'Synthetix', 91, '$140k - $185k', 'Three.js, Design Systems, Generative UI');
}

/* ==========================================================================
   6. Auto-ATS Resume Diagnostic & Optimizer
   ========================================================================== */
function openAtsModal() {
    const modalEl = document.getElementById('atsModal');
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
}

function optimizeAtsScore() {
    const btn = document.getElementById('optimizeAtsBtn');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> Synthesizing ATS Vectors...`;
    }

    fetch('/api/ai/ats-scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'optimize' })
    })
    .then(res => res.json())
    .then(data => {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<i class="bi bi-check2 me-1"></i> Optimized!`;
        }

        // Update scores
        document.getElementById('ats-modal-score').innerText = '96%';
        document.getElementById('ats-modal-fit-text').innerText = '96% (Elite Match)';
        document.getElementById('ats-modal-progress-bar').style.width = '96%';
        document.getElementById('ats-score-display').innerText = '96%';
        document.getElementById('ats-progress-bar').style.width = '96%';
        document.getElementById('header-match-pct').innerText = '98%';

        document.getElementById('ats-optimized-results').classList.remove('d-none');
    })
    .catch(err => {
        console.error(err);
        if (btn) btn.disabled = false;
    });
}

/* ==========================================================================
   7. Skills Matrix Radar (Tab 2)
   ========================================================================== */
function initSkillsMatrixRadar() {
    const ctx = document.getElementById('skillsMatrixRadar');
    if (!ctx) return;

    skillsMatrixRadarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: [
                'Transformers & LLMs',
                'Agentic UX',
                'Python / Async IO',
                'Distributed GPU Infra',
                '3D WebGL / Three.js',
                'System Architecture'
            ],
            datasets: [
                {
                    label: 'Elena Vance Profile',
                    data: [96, 98, 97, 78, 92, 95],
                    borderColor: '#00f2fe',
                    backgroundColor: 'rgba(0, 242, 254, 0.25)',
                    borderWidth: 2
                },
                {
                    label: 'NeuralVibe Staff Target',
                    data: [98, 90, 95, 88, 70, 96],
                    borderColor: '#ec4899',
                    backgroundColor: 'rgba(236, 72, 153, 0.15)',
                    borderWidth: 1.5,
                    borderDash: [4, 4]
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                    grid: { color: 'rgba(255, 255, 255, 0.08)' },
                    pointLabels: { color: '#cbd5e1', font: { size: 11 } },
                    ticks: { display: false }
                }
            },
            plugins: {
                legend: { labels: { color: '#ffffff' } }
            }
        }
    });
}

/* ==========================================================================
   8. Copilot Assistant Chat & Waveform Interactivity
   ========================================================================== */
function openCopilotChat() {
    const offcanvasEl = document.getElementById('copilotChatOffcanvas');
    if (offcanvasEl) {
        const offcanvas = new bootstrap.Offcanvas(offcanvasEl);
        offcanvas.show();
    }
}

function sendCopilotQuery(promptText) {
    const input = document.getElementById('copilot-user-input');
    if (input) input.value = promptText;
    submitCopilotMessage();
}

function submitCopilotMessage() {
    const input = document.getElementById('copilot-user-input');
    const message = input ? input.value.trim() : '';
    if (!message) return;

    input.value = '';

    // Append user message bubble
    const history = document.getElementById('copilot-chat-history');
    const userMsgEl = document.createElement('div');
    userMsgEl.className = 'cf-chat-bubble user mb-3';
    userMsgEl.innerHTML = `
        <div class="cf-chat-meta text-end text-light">You • Just now</div>
        <div class="cf-chat-body">${escapeHtml(message)}</div>
    `;
    history.appendChild(userMsgEl);
    history.scrollTop = history.scrollHeight;

    // Pulse equalizer bars faster
    pulseWaveform(true);

    fetch('/api/ai/copilot-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message: message,
            active_job_id: activeJobIdForCopilot
        })
    })
    .then(res => res.json())
    .then(data => {
        pulseWaveform(false);

        // Append assistant response
        const asstMsgEl = document.createElement('div');
        asstMsgEl.className = 'cf-chat-bubble assistant mb-3';
        asstMsgEl.innerHTML = `
            <div class="cf-chat-meta">Copilot AI • Telemetry 9859 tf/sJ</div>
            <div class="cf-chat-body">${formatMarkdown(data.reply)}</div>
        `;
        history.appendChild(asstMsgEl);
        history.scrollTop = history.scrollHeight;

        // Render prompt chips
        const chipsContainer = document.getElementById('copilot-chips');
        if (chipsContainer && data.suggested_prompts) {
            chipsContainer.innerHTML = data.suggested_prompts.map(p => 
                `<button class="btn btn-sm cf-chip" onclick="sendCopilotQuery('${p.replace(/'/g, "\\'")}')">${p}</button>`
            ).join('');
        }
    })
    .catch(err => {
        pulseWaveform(false);
        console.error(err);
    });
}

function pulseWaveform(active) {
    const bars = document.querySelectorAll('.cf-waveform-bars .bar');
    bars.forEach(b => {
        b.style.animationDuration = active ? '0.4s' : '1.2s';
    });
}

function clearCopilotSession() {
    const history = document.getElementById('copilot-chat-history');
    if (history) {
        history.innerHTML = `
            <div class="cf-chat-bubble assistant mb-3">
                <div class="cf-chat-meta">Copilot AI • Reset</div>
                <div class="cf-chat-body">Context reinitialized. How may I assist your search today?</div>
            </div>`;
    }
}

function toggleCopilotMute() {
    alert("Audio simulation waveform active. Text telemetry streamed at 60 Hz.");
}

/* ==========================================================================
   Utilities & Helpers
   ========================================================================== */
function showFloatingAlert(message, category = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert cf-alert cf-alert-${category} alert-dismissible fade show position-fixed top-0 end-0 m-4 shadow-lg z-3`;
    alertDiv.style.maxWidth = '420px';
    alertDiv.innerHTML = `
        <i class="bi bi-stars me-2"></i>${escapeHtml(message)}
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => alertDiv.remove(), 300);
    }, 4500);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text == null ? '' : text;
    return div.innerHTML;
}

function formatMarkdown(text) {
    if (!text) return '';
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/• (.*?)\n/g, '<li>$1</li>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>');
}

function sortJobsBy(criterion) {
    const wrappers = Array.from(document.querySelectorAll('.job-card-wrapper'));
    const container = document.getElementById('openings-container');
    if (!container || !wrappers.length) return;

    if (criterion === 'score') {
        wrappers.sort((a, b) => parseInt(b.dataset.score || 0) - parseInt(a.dataset.score || 0));
    } else if (criterion === 'salary') {
        wrappers.sort((a, b) => parseInt(b.dataset.salary || 0) - parseInt(a.dataset.salary || 0));
    }

    wrappers.forEach(w => container.appendChild(w));
}

function refreshOpenings() {
    executeAiSearch();
}
