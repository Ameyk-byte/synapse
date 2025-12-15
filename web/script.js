// DOM Elements
const messagesArea = document.getElementById('messagesArea');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const micBtn = document.getElementById('micBtn');
const learningBox = document.getElementById('learningBox');
const learningList = document.getElementById('learningList');

// Helper to add message to chat
function addMessage(text, isUser = false) {
    const div = document.createElement('div');
    div.className = `message ${isUser ? 'user' : 'bot'}`;
    // Parse links if any (simple regex)
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const htmlText = text.replace(urlRegex, '<a href="$1" target="_blank" style="color: inherit; text-decoration: underline;">$1</a>');
    div.innerHTML = htmlText;
    messagesArea.appendChild(div);
    messagesArea.scrollTop = messagesArea.scrollHeight;
}

// Send Message Logic
async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    addMessage(text, true);
    userInput.value = '';

    // Call Python
    const response = await eel.process_query(text)();
    if (response) {
        addMessage(response.text, false);
        // Speech is handled by backend calling TextToSpeech, 
        // OR we can trigger it here if backend returns audio data.
        // For now, backend handles TTS execution directly via TextToSpeech module 
        // but we can also use browser TTS as fallback if needed.
    }
}

// Type on Enter
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendMessage();
});

sendBtn.addEventListener('click', sendMessage);

// Mic Logic
micBtn.addEventListener('click', async () => {
    micBtn.classList.add('recording');
    try {
        const text = await eel.listen_to_speech()();
        if (text) {
            userInput.value = text;
            sendMessage();
        }
    } catch (e) {
        console.error("Speech error", e);
    } finally {
        micBtn.classList.remove('recording');
    }
});

// Exposed Function for Learning Resources
eel.expose(updateLearningResources);
function updateLearningResources(resources) {
    if (!resources || resources.length === 0) {
        learningBox.style.display = 'none';
        return;
    }

    learningList.innerHTML = '';
    resources.forEach(r => {
        const div = document.createElement('div');
        div.className = 'learning-item';
        div.innerHTML = `
            <div><strong>${r.title}</strong> <span style="font-size:0.8em; opacity:0.7">(${r.level})</span></div>
            <div style="font-size:0.8em; margin-top:2px;">${r.type} • ${r.duration_min} min</div>
            <a href="${r.url}" target="_blank">Open Resource</a>
        `;
        learningList.appendChild(div);
    });
    learningBox.style.display = 'flex';
}


// --- Three.js Visualizer ---
const container = document.getElementById('visualizer');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });

renderer.setSize(container.clientWidth, container.clientHeight);
container.appendChild(renderer.domElement);

const geometry = new THREE.IcosahedronGeometry(1, 4); // Detailed sphere
const material = new THREE.MeshBasicMaterial({
    color: 0x00f2ff,
    wireframe: true,
    transparent: true,
    opacity: 0.5
});
const sphere = new THREE.Mesh(geometry, material);
scene.add(sphere);

camera.position.z = 2.5;

// Animation
function animate() {
    requestAnimationFrame(animate);

    sphere.rotation.x += 0.005;
    sphere.rotation.y += 0.005;

    // Breathing effect
    const time = Date.now() * 0.001;
    const scale = 1 + Math.sin(time) * 0.05;
    sphere.scale.set(scale, scale, scale);

    renderer.render(scene, camera);
}
animate();

// Handle Resize
window.addEventListener('resize', () => {
    // Only update if visualizer is visible/container exists
    if (!container) return;
    const width = container.clientWidth;
    const height = container.clientHeight;
    renderer.setSize(width, height);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
});
