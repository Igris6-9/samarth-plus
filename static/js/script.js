/* 👑 DAKASH DIVINE INTERFACE SCRIPT - HYBRID (PC + MOBILE) V2.5 */

document.addEventListener('DOMContentLoaded', () => {
    console.log(">> [SYSTEM]: Neural Interface Synced. Mode: Hybrid 🚀");

    // --- 1. NEURAL TYPING EFFECT (With Skip & Mobile Optimization) ---
    const typeElements = document.querySelectorAll('.type-effect');
    typeElements.forEach(el => {
        const text = el.getAttribute('data-text') || el.innerText;
        el.innerText = '';
        let i = 0;
        let isSkipped = false;

        // Skip typing on click/touch
        el.addEventListener('click', () => isSkipped = true);

        function type() {
            if (isSkipped) {
                el.innerText = text;
                return;
            }
            if (i < text.length) {
                el.innerText += text.charAt(i);
                i++;
                let speed = window.innerWidth < 768 ? 25 : 45;
                setTimeout(type, speed);
            }
        }
        type();
    });

    // --- 2. DYNAMIC VIEWPORT & KEYBOARD FIX ---
    const adjustViewport = () => {
        let vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    };
    window.addEventListener('resize', adjustViewport);
    adjustViewport();

    // --- 3. CHATBOT ARCHITECTURE (Auto-Scroll & Feedback) ---
    const chatForm = document.querySelector('#chat-form');
    if (chatForm) {
        const chatBox = document.querySelector('.chat-window');
        const input = document.querySelector('#chat-input');

        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const userMsg = input.value.trim();
            if (!userMsg) return;

            // Render User Bubble
            renderBubble(userMsg, 'user');
            input.value = '';
            
            // Generate Neural Loader
            const loadingId = "loader-" + Date.now();
            renderBubble("Analyzing Neural Data...", 'ai', loadingId);

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: userMsg })
                });
                const data = await response.json();
                
                document.getElementById(loadingId).remove();
                renderBubble(data.response, 'ai');

                // Mobile Haptic Feedback (Agar supported ho)
                if (window.navigator.vibrate) window.navigator.vibrate(10);

            } catch (err) {
                const loader = document.getElementById(loadingId);
                if(loader) loader.innerHTML = ">> [ALERT]: Neural Link Interrupted.";
            }
        });

        function renderBubble(msg, role, id = null) {
            const div = document.createElement('div');
            div.className = `message-${role} animate__animated ${role === 'user' ? 'animate__fadeInRight' : 'animate__fadeInLeft'}`;
            if(id) div.id = id;
            div.innerHTML = `<span class="label">${role.toUpperCase()}:</span> ${msg}`;
            chatBox.appendChild(div);
            
            // Smooth Scroll
            chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
            
            // Limit bubbles for performance on mobile
            if(chatBox.children.length > 20) chatBox.removeChild(chatBox.firstChild);
        }
    }

    // --- 4. PROGRESS GAUGES (Hybrid Trigger) ---
    const progressFills = document.querySelectorAll('.progress-fill');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const fill = entry.target;
                fill.style.width = fill.getAttribute('data-target') || '0%';
            }
        });
    }, { threshold: 0.5 });

    progressFills.forEach(f => observer.observe(f));

    // --- 5. PC EXCLUSIVE: MOUSE TRAIL ---
    if (window.innerWidth > 1024) {
        const glow = document.createElement('div');
        glow.className = 'cursor-glow';
        document.body.appendChild(glow);

        document.addEventListener('mousemove', (e) => {
            glow.style.transform = `translate(${e.clientX - 10}px, ${e.clientY - 10}px)`;
        });
    }

    // --- 6. MISSION ALERTS (Mobile Ready) ---
    window.showMissionAlert = (msg, type = 'info') => {
        const alert = document.createElement('div');
        alert.className = `mission-alert alert-${type} animate__animated animate__slideInDown`;
        alert.innerHTML = `>> [LOG]: ${msg}`;
        document.body.appendChild(alert);

        setTimeout(() => {
            alert.classList.replace('animate__slideInDown', 'animate__slideOutUp');
            setTimeout(() => alert.remove(), 500);
        }, 3500);
    };
});
