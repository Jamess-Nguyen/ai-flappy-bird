// Flappy Bird AI Challenge - Frontend Game Logic
// Handles WebSocket communication, rendering, and user input

let ws = null;
let gameState = null;
let currentMode = 'stopped';
let isRunning = false;
let lastJumpDecision = false;

// Canvas setup
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Colors
const COLORS = {
    sky: '#87ceeb',
    bird: '#ffd700',
    birdJumping: '#ff6347',
    pipe: '#228b22',
    pipeStroke: '#1a5f1a',
    gap: '#ffff00',
    velocity: '#ffffff',
    floor: '#8b4513',
    floorStroke: '#654321'
};

// Connect to WebSocket
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('✅ Connected to server');
        updateStatus('connected', 'Connected - Ready to play!');
        loadSelectedLevel();
    };

    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        handleServerMessage(message);
    };

    ws.onclose = () => {
        console.log('❌ Disconnected from server');
        updateStatus('disconnected', 'Disconnected from server');
        setTimeout(connectWebSocket, 2000); // Reconnect after 2 seconds
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}

// Handle messages from server
function handleServerMessage(message) {
    switch (message.type) {
        case 'level_loaded':
            gameState = message.state;
            render();
            console.log('📦 Level loaded:', message.level_id);
            break;

        case 'mode_changed':
            currentMode = message.mode;
            updateStatus(message.mode, `Mode: ${message.mode.toUpperCase()}`);
            isRunning = true;
            startGameLoop();
            break;

        case 'state_update':
            gameState = message.state;
            lastJumpDecision = message.shouldJump || false;
            updateUI();
            render();

            // Check if game over
            if (gameState.gameOver && isRunning) {
                isRunning = false;
                showGameOver();
            }
            break;

        case 'reset':
            gameState = message.state;
            isRunning = false;
            hideGameOver();
            render();
            updateUI();
            break;
    }
}

// Update status display
function updateStatus(className, text) {
    const statusEl = document.getElementById('status');
    statusEl.className = `status ${className}`;
    statusEl.textContent = text;
}

// Update UI stats
function updateUI() {
    if (!gameState) return;

    document.getElementById('scoreDisplay').textContent = gameState.score;
    document.getElementById('frameDisplay').textContent = gameState.frame;
    document.getElementById('velocityDisplay').textContent = gameState.pilot.velocity.toFixed(2);
    document.getElementById('jumpDisplay').textContent = lastJumpDecision ? '✅' : '❌';
}

// Render game on canvas
function render() {
    if (!gameState) return;

    // Clear canvas
    ctx.fillStyle = COLORS.sky;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw floor (if present)
    if (gameState.floor && gameState.floor < canvas.height) {
        drawFloor(gameState.floor);
    }

    // Draw pipes
    gameState.pipes.forEach(pipe => {
        drawPipe(pipe);
    });

    // Draw pilot (bird)
    drawPilot(gameState.pilot);

    // Draw velocity indicator
    drawVelocityIndicator(gameState.pilot);
}

// Draw floor
function drawFloor(floorY) {
    // Draw the floor
    ctx.fillStyle = COLORS.floor;
    ctx.fillRect(0, floorY, canvas.width, canvas.height - floorY);

    // Draw floor border
    ctx.strokeStyle = COLORS.floorStroke;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(0, floorY);
    ctx.lineTo(canvas.width, floorY);
    ctx.stroke();

    // Draw a pattern on the floor (grass-like)
    ctx.fillStyle = COLORS.floorStroke;
    for (let x = 0; x < canvas.width; x += 20) {
        ctx.fillRect(x, floorY, 2, 10);
    }
}

// Draw a pipe
function drawPipe(pipe) {
    const pipeWidth = 50;

    // Top pipe
    ctx.fillStyle = COLORS.pipe;
    ctx.fillRect(pipe.xPosition, 0, pipeWidth, pipe.topPipe);
    ctx.strokeStyle = COLORS.pipeStroke;
    ctx.lineWidth = 3;
    ctx.strokeRect(pipe.xPosition, 0, pipeWidth, pipe.topPipe);

    // Bottom pipe
    ctx.fillRect(pipe.xPosition, pipe.bottomPipe, pipeWidth, canvas.height - pipe.bottomPipe);
    ctx.strokeRect(pipe.xPosition, pipe.bottomPipe, pipeWidth, canvas.height - pipe.bottomPipe);

    // Gap indicator (yellow line)
    const gapCenter = (pipe.topPipe + pipe.bottomPipe) / 2;
    ctx.strokeStyle = COLORS.gap;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(pipe.xPosition, gapCenter);
    ctx.lineTo(pipe.xPosition + pipeWidth, gapCenter);
    ctx.stroke();
}

// Draw pilot (bird)
function drawPilot(pilot) {
    // Change color based on jump decision
    const color = lastJumpDecision ? COLORS.birdJumping : COLORS.bird;

    ctx.fillStyle = color;
    ctx.fillRect(pilot.x, pilot.y, pilot.width, pilot.height);

    // Border
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 2;
    ctx.strokeRect(pilot.x, pilot.y, pilot.width, pilot.height);
}

// Draw velocity indicator
function drawVelocityIndicator(pilot) {
    const centerX = pilot.x + pilot.width / 2;
    const centerY = pilot.y + pilot.height / 2;
    const endY = centerY + pilot.velocity * 5;

    ctx.strokeStyle = COLORS.velocity;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.lineTo(centerX, endY);
    ctx.stroke();

    // Arrow head
    const arrowSize = 5;
    if (pilot.velocity > 0) {
        // Down arrow
        ctx.beginPath();
        ctx.moveTo(centerX, endY);
        ctx.lineTo(centerX - arrowSize, endY - arrowSize);
        ctx.lineTo(centerX + arrowSize, endY - arrowSize);
        ctx.closePath();
        ctx.fillStyle = COLORS.velocity;
        ctx.fill();
    } else if (pilot.velocity < 0) {
        // Up arrow
        ctx.beginPath();
        ctx.moveTo(centerX, endY);
        ctx.lineTo(centerX - arrowSize, endY + arrowSize);
        ctx.lineTo(centerX + arrowSize, endY + arrowSize);
        ctx.closePath();
        ctx.fillStyle = COLORS.velocity;
        ctx.fill();
    }
}

// Show game over overlay
function showGameOver() {
    const gameOverEl = document.getElementById('gameOver');
    const finalScoreEl = document.getElementById('finalScore');

    if (gameState) {
        finalScoreEl.textContent = gameState.score;
    }

    gameOverEl.classList.add('show');
}

// Hide game over overlay
function hideGameOver() {
    const gameOverEl = document.getElementById('gameOver');
    gameOverEl.classList.remove('show');
}

// Game loop
function startGameLoop() {
    if (!isRunning) return;

    // Request next frame update from server
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: 'update' }));
    }

    // Continue loop at 60 FPS
    setTimeout(() => {
        if (isRunning) {
            startGameLoop();
        }
    }, 1000 / 60);
}

// Load selected level
function loadSelectedLevel() {
    const levelSelect = document.getElementById('levelSelect');
    const levelId = levelSelect.value;

    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            action: 'load_level',
            level_id: levelId
        }));
    }
}

// User actions
function startManual() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: 'start_manual' }));
    }
}

function startAutopilot() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: 'start_autopilot' }));
    }
}

function resetGame() {
    isRunning = false;
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: 'reset' }));
        loadSelectedLevel();
    }
}

function jump() {
    if (currentMode === 'manual' && ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: 'jump' }));
    }
}

// Keyboard controls
document.addEventListener('keydown', (event) => {
    if (event.code === 'Space') {
        event.preventDefault(); // Prevent page scroll
        jump();
    }
});

// Level selector change
document.getElementById('levelSelect').addEventListener('change', () => {
    resetGame();
});

// Initialize connection on page load
window.addEventListener('load', () => {
    connectWebSocket();
});
