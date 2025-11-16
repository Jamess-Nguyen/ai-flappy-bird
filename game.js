/**
 * Flappy Bird AI Challenge - Standalone GitHub Pages Version
 * Complete browser-based implementation
 */

// ============================================
// LEVEL CONFIGURATIONS
// ============================================

const LEVELS = {
    simple: {
        name: "Simple (1 Pipe)",
        description: "Single pipe to test basic logic",
        floor: { min: 500, max: 600 },
        pipes: [
            { xPosition: 400, gapCenter: 300, gapHeight: 150 }
        ]
    },
    medium: {
        name: "Medium (5 Pipes)",
        description: "Five pipes with varying gaps",
        floor: { min: 480, max: 600 },
        pipes: [
            { xPosition: 400, gapCenter: 300, gapHeight: 150 },
            { xPosition: 650, gapCenter: 250, gapHeight: 150 },
            { xPosition: 900, gapCenter: 350, gapHeight: 140 },
            { xPosition: 1150, gapCenter: 280, gapHeight: 160 },
            { xPosition: 1400, gapCenter: 320, gapHeight: 150 }
        ]
    },
    hard: {
        name: "Hard (10 Pipes)",
        description: "Ten pipes with challenging gaps",
        floor: { min: 500, max: 600 },
        pipes: [
            { xPosition: 400, gapCenter: 300, gapHeight: 150 },
            { xPosition: 650, gapCenter: 200, gapHeight: 140 },
            { xPosition: 900, gapCenter: 380, gapHeight: 140 },
            { xPosition: 1150, gapCenter: 250, gapHeight: 145 },
            { xPosition: 1400, gapCenter: 350, gapHeight: 140 },
            { xPosition: 1650, gapCenter: 220, gapHeight: 150 },
            { xPosition: 1900, gapCenter: 330, gapHeight: 140 },
            { xPosition: 2150, gapCenter: 270, gapHeight: 145 },
            { xPosition: 2400, gapCenter: 310, gapHeight: 140 },
            { xPosition: 2650, gapCenter: 290, gapHeight: 150 }
        ]
    },
    floor_test: {
        name: "Floor Test",
        description: "No pipes, just floor avoidance",
        floor: { min: 500, max: 600 },
        pipes: []
    },
    marathon: {
        name: "Marathon (200 Pipes!)",
        description: "Ultimate stress test with 200 pipes",
        floor: { min: 550, max: 600 },
        pipes: Array.from({ length: 200 }, (_, i) => {
            // keep nice even horizontal spacing
            const xPosition = 400 + i * 350;

            // random gap height in [150, 200]
            const MIN_GAP_HEIGHT = 150;
            const MAX_GAP_HEIGHT = 200;
            const gapHeight =
                MIN_GAP_HEIGHT + Math.random() * (MAX_GAP_HEIGHT - MIN_GAP_HEIGHT);

            // random vertical position for the center, keeping the whole gap on screen
            const SCREEN_HEIGHT = 600;      // matches your GameEngine
            const TOP_MARGIN = 40;          // don't hug the very top
            const BOTTOM_MARGIN = 40;       // don't hug the very bottom (floor logic will still adjust vs floor)

            const minCenter = TOP_MARGIN + gapHeight / 2;
            const maxCenter = SCREEN_HEIGHT - BOTTOM_MARGIN - gapHeight / 2;
            const gapCenter =
                minCenter + Math.random() * (maxCenter - minCenter);

            return { xPosition, gapCenter, gapHeight };
        })
    }
};

// ============================================
// AI CONTROLLER
// ============================================

function shouldJump(gameState) {
    const pilot = gameState.pilot;
    const floor = gameState.floor;
    const gravity = gameState.gravity;
    const pipe = gameState.currentPipe;

    const currentY = pilot.yPos;
    const currentVelocity = pilot.velocity;
    const pilotHeight = pilot.height;
    const pilotWidth = pilot.width;

    const safetyMargin = Math.max(pilotHeight * 0.1, pilotWidth * 0.1, 5);

    // PRIORITY 1: FLOOR SAFETY
    const nextVelocity = currentVelocity + gravity;
    const nextY = currentY + nextVelocity;
    const pilotBottomNextFrame = nextY + pilotHeight;

    if (pilotBottomNextFrame + safetyMargin >= floor) {
        return true;  // Emergency floor avoidance!
    }

    // PRIORITY 2: EMERGENCY BOTTOM PIPE COLLISION
    if (pipe) {
        const gapBottom = pipe.bottomPipe;
        const pipeX = pipe.xPosition;
        const pilotX = pilot.xPos;

        const distanceToPipe = pipeX - pilotX;
        if (distanceToPipe > 0 && distanceToPipe < 150) {
            let predictedY = currentY;
            let predictedVelocity = currentVelocity;

            for (let i = 0; i < 5; i++) {
                predictedVelocity += gravity;
                predictedY += predictedVelocity;
            }

            const predictedBottom = predictedY + pilotHeight;
            if (predictedBottom >= gapBottom) {
                return true;  // Emergency bottom pipe avoidance!
            }
        }
    }

    // NO PIPE: Just maintain floor safety
    if (!pipe) {
        return false;
    }

    // PIPE EXISTS: Choose strategy based on gap position
    const gapTop = pipe.topPipe;
    const gapBottom = pipe.bottomPipe;
    const gapCenter = (gapTop + gapBottom) / 2;
    const gapHeight = gapBottom - gapTop;

    const SCREEN_CENTER = 300;

    if (gapCenter <= SCREEN_CENTER) {
        // APEX STRATEGY (For gaps in top half)
        const targetY = gapBottom - (gapHeight * 0.75);
        const apexHeight = 64;
        const minimumY = targetY + apexHeight;

        // Defensive check
        if (minimumY >= floor - 20) {
            if (pilotBottomNextFrame + safetyMargin >= gapBottom) {
                return true;
            }
            return false;
        }

        if (currentY >= minimumY) {
            return true;
        } else {
            return false;
        }
    } else {
        // BOTTOM PIPE STRATEGY (For gaps in bottom half)
        const targetY = gapBottom;

        if (pilotBottomNextFrame + safetyMargin >= targetY) {
            return true;
        }

        return false;
    }
}

// ============================================
// GAME ENGINE
// ============================================

class GameEngine {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');

        // Constants
        this.SCREEN_WIDTH = 800;
        this.SCREEN_HEIGHT = 600;
        this.PIPE_WIDTH = 60;
        this.PILOT_WIDTH = 30;
        this.PILOT_HEIGHT = 30;
        this.GRAVITY = 0.5;
        this.JUMP_VELOCITY = -8;
        this.PIPE_SPEED = 3;

        this.canvas.width = this.SCREEN_WIDTH;
        this.canvas.height = this.SCREEN_HEIGHT;

        // Game state
        this.pilot = this.createPilot();
        this.pipes = [];
        this.floorY = this.SCREEN_HEIGHT;
        this.score = 0;
        this.isGameOver = false;
        this.isRunning = false;
        this.isAutopilot = false;
        this.animationId = null;

        // Stats
        this.frameCount = 0;
        this.startTime = 0;

        // Keyboard controls
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && this.isRunning && !this.isAutopilot && !this.isGameOver) {
                e.preventDefault();
                this.jump();
            }
        });
    }

    createPilot() {
        return {
            xPos: 100,
            yPos: this.SCREEN_HEIGHT / 2,
            height: this.PILOT_HEIGHT,
            width: this.PILOT_WIDTH,
            velocity: 0,
            gravity: this.GRAVITY,
            jumpVelocity: this.JUMP_VELOCITY
        };
    }

    loadLevel(levelId) {
        const level = LEVELS[levelId];
        if (!level) return;

        // --------- FLOOR SELECTION ----------
        const floorMin = level.floor?.min ?? (this.SCREEN_HEIGHT - 80);
        const floorMax = level.floor?.max ?? this.SCREEN_HEIGHT;

        // Simple random floor in [min, max]
        this.floorY = Math.floor(
            Math.random() * (floorMax - floorMin + 1) + floorMin
        );

        // ----------------------------------------
        // CASE 1: LEVELS WITH NO PIPES (floor_test)
        // ----------------------------------------
        if (level.pipes.length === 0) {
            // Clamp floor inside canvas
            this.floorY = Math.max(0, Math.min(this.floorY, this.SCREEN_HEIGHT - 1));
            this.pipes = [];
            this.updateStats();
            return;
        }

        // ----------------------------------------
        // CASE 2: LEVELS WITH PIPES
        // ----------------------------------------
        const marginBottomFromFloor = 10;  // distance between bottomPipe and floor
        const marginTop = 0;               // min top clearance from top of screen

        const floorLimit = this.floorY - marginBottomFromFloor;

        this.pipes = level.pipes.map((pipeConfig) => {
            const gapHeight = pipeConfig.gapHeight;
            const halfGap = gapHeight / 2;

            // Allowed center range so that:
            //  topPipe >= marginTop
            //  bottomPipe <= floorLimit
            const minCenter = marginTop + halfGap;
            const maxCenter = floorLimit - halfGap;

            // If the gap is too tall for the available space, we still keep
            // its height but clamp center into the best possible spot.
            let center = pipeConfig.gapCenter;
            if (maxCenter < minCenter) {
                // No perfect placement; just put it in the middle of the band.
                center = (minCenter + maxCenter) / 2;
            } else {
                // Clamp requested center into feasible range
                if (center < minCenter) center = minCenter;
                if (center > maxCenter) center = maxCenter;
            }

            const gapTop = center - halfGap;
            const gapBottom = center + halfGap;

            return {
                topPipe: gapTop,
                bottomPipe: gapBottom,
                xPosition: pipeConfig.xPosition
            };
        });

        this.updateStats();
    }

    startManual() {
        this.reset();
        this.isAutopilot = false;
        this.isRunning = true;
        this.startTime = Date.now();
        this.gameLoop();
        this.updateStatus('Manual mode - Press SPACE to jump');
    }

    startAutopilot() {
        this.reset();
        this.isAutopilot = true;
        this.isRunning = true;
        this.startTime = Date.now();
        this.gameLoop();
        this.updateStatus('Autopilot mode - AI is flying!');
    }

    stop() {
        this.isRunning = false;
        if (this.animationId !== null) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        this.updateStatus('Game stopped');
    }

    reset() {
        this.pilot = this.createPilot();
        this.score = 0;
        this.isGameOver = false;
        this.frameCount = 0;
    }

    jump() {
        this.pilot.velocity = this.JUMP_VELOCITY;
    }

    gameLoop = () => {
        if (!this.isRunning) return;

        this.frameCount++;

        // AI decision
        if (this.isAutopilot && !this.isGameOver) {
            const gameState = this.getGameState();
            if (shouldJump(gameState)) {
                this.jump();
            }
        }

        // Update physics
        this.pilot.velocity += this.GRAVITY;
        this.pilot.yPos += this.pilot.velocity;

        // Move pipes
        for (const pipe of this.pipes) {
            pipe.xPosition -= this.PIPE_SPEED;
        }

        // Check collisions
        if (this.checkCollision()) {
            this.isGameOver = true;
            this.stop();
        }

        // Update score
        this.updateScore();

        // Render
        this.render();

        // Update stats
        if (this.frameCount % 10 === 0) {
            this.updateStats();
        }

        this.animationId = requestAnimationFrame(this.gameLoop);
    }

    checkCollision() {
        // Floor collision
        if (this.pilot.yPos + this.pilot.height >= this.floorY) {
            return true;
        }

        // Ceiling collision
        if (this.pilot.yPos <= 0) {
            return true;
        }

        // Pipe collision
        const currentPipe = this.getCurrentPipe();
        if (currentPipe) {
            const pilotLeft = this.pilot.xPos;
            const pilotRight = this.pilot.xPos + this.pilot.width;
            const pilotTop = this.pilot.yPos;
            const pilotBottom = this.pilot.yPos + this.pilot.height;

            const pipeLeft = currentPipe.xPosition;
            const pipeRight = currentPipe.xPosition + this.PIPE_WIDTH;

            // Check horizontal overlap
            if (pilotRight > pipeLeft && pilotLeft < pipeRight) {
                // Check vertical collision
                if (pilotTop < currentPipe.topPipe || pilotBottom > currentPipe.bottomPipe) {
                    return true;
                }
            }
        }

        return false;
    }

    updateScore() {
        const currentPipe = this.getCurrentPipe();
        if (currentPipe && currentPipe.xPosition + this.PIPE_WIDTH < this.pilot.xPos) {
            const passedPipes = this.pipes.filter(p => p.xPosition + this.PIPE_WIDTH < this.pilot.xPos);
            this.score = passedPipes.length;
        }
    }

    getCurrentPipe() {
        for (const pipe of this.pipes) {
            if (pipe.xPosition + this.PIPE_WIDTH > this.pilot.xPos) {
                return pipe;
            }
        }
        return null;
    }

    getGameState() {
        return {
            pilot: { ...this.pilot },
            pipeSpeed: this.PIPE_SPEED,
            currentPipe: this.getCurrentPipe(),
            pipeArray: [...this.pipes],
            gravity: this.GRAVITY,
            floor: this.floorY,
            score: this.score,
            isGameOver: this.isGameOver
        };
    }

    render() {
        // Clear canvas
        this.ctx.fillStyle = '#4285F4';
        this.ctx.fillRect(0, 0, this.SCREEN_WIDTH, this.SCREEN_HEIGHT);

        // Draw pipes
        this.ctx.fillStyle = '#0F9D58';
        for (const pipe of this.pipes) {
            // Top pipe
            this.ctx.fillRect(pipe.xPosition, 0, this.PIPE_WIDTH, pipe.topPipe);
            // Bottom pipe
            this.ctx.fillRect(
                pipe.xPosition,
                pipe.bottomPipe,
                this.PIPE_WIDTH,
                this.SCREEN_HEIGHT - pipe.bottomPipe
            );

            // Pipe borders
            this.ctx.strokeStyle = '#1a6b1a';
            this.ctx.lineWidth = 3;
            this.ctx.strokeRect(pipe.xPosition, 0, this.PIPE_WIDTH, pipe.topPipe);
            this.ctx.strokeRect(
                pipe.xPosition,
                pipe.bottomPipe,
                this.PIPE_WIDTH,
                this.SCREEN_HEIGHT - pipe.bottomPipe
            );
        }

        // Draw floor
        this.ctx.fillStyle = '#8B4513';
        this.ctx.fillRect(0, this.floorY, this.SCREEN_WIDTH, this.SCREEN_HEIGHT - this.floorY);
        this.ctx.strokeStyle = '#654321';
        this.ctx.lineWidth = 3;
        this.ctx.beginPath();
        this.ctx.moveTo(0, this.floorY);
        this.ctx.lineTo(this.SCREEN_WIDTH, this.floorY);
        this.ctx.stroke();

        // Draw pilot
        this.ctx.fillStyle = '#FFD700';
        this.ctx.fillRect(this.pilot.xPos, this.pilot.yPos, this.pilot.width, this.pilot.height);
        this.ctx.strokeStyle = '#FFA500';
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(this.pilot.xPos, this.pilot.yPos, this.pilot.width, this.pilot.height);

        // Draw score
        this.ctx.fillStyle = '#fff';
        this.ctx.font = 'bold 24px Arial';

        if (this.isGameOver) {
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
            this.ctx.fillRect(0, 0, this.SCREEN_WIDTH, this.SCREEN_HEIGHT);
            this.ctx.fillStyle = '#fff';
            this.ctx.font = 'bold 48px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('GAME OVER', this.SCREEN_WIDTH / 2, this.SCREEN_HEIGHT / 2);
            this.ctx.font = 'bold 24px Arial';
            this.ctx.textAlign = 'left';
        }
    }

    updateStats() {
        const currentPipe = this.getCurrentPipe();
        const elapsed = Date.now() - this.startTime;
        const fps = this.frameCount > 0 ? Math.round((this.frameCount / elapsed) * 1000) : 0;

        document.getElementById('pilotY').textContent = Math.round(this.pilot.yPos).toString();
        document.getElementById('pilotVelocity').textContent = this.pilot.velocity.toFixed(2);
        document.getElementById('floorY').textContent = this.floorY.toString();
        document.getElementById('totalPipes').textContent = this.pipes.length.toString();
        document.getElementById('frameCount').textContent = this.frameCount.toString();
        document.getElementById('fps').textContent = fps.toString();

        if (currentPipe) {
            document.getElementById('nextPipeX').textContent = Math.round(currentPipe.xPosition).toString();
            document.getElementById('nextPipeGap').textContent =
                `${Math.round(currentPipe.topPipe)}-${Math.round(currentPipe.bottomPipe)}`;
        } else {
            document.getElementById('nextPipeX').textContent = 'N/A';
            document.getElementById('nextPipeGap').textContent = 'N/A';
        }
    }

    updateStatus(message) {
        document.getElementById('status').textContent = message;
    }
}

// ============================================
// INITIALIZATION
// ============================================

let game;

window.addEventListener('DOMContentLoaded', () => {
    game = new GameEngine('gameCanvas');

    // Populate level selector
    const levelSelect = document.getElementById('levelSelect');
    Object.entries(LEVELS).forEach(([id, config]) => {
        const option = document.createElement('option');
        option.value = id;
        option.textContent = config.name;
        if (id === 'marathon') {
            option.selected = true;
        }
        levelSelect.appendChild(option);
    });

    // Load initial level
    game.loadLevel('marathon');
    game.startAutopilot();
});

function startManual() {
    const levelId = document.getElementById('levelSelect').value;
    game.loadLevel(levelId);
    game.startManual();
}

function startAutopilot() {
    const levelId = document.getElementById('levelSelect').value;
    game.loadLevel(levelId);
    game.startAutopilot();
}

function stopGame() {
    game.stop();
}

// Make functions available globally
window.startManual = startManual;
window.startAutopilot = startAutopilot;
window.stopGame = stopGame;
