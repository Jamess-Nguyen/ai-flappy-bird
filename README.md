# Flappy Bird AI Challenge

A web-based Flappy Bird game with AI navigation using predictive physics and hybrid strategy selection. The AI successfully navigates through 200+ pipes using altitude maintenance and emergency collision avoidance.
## 📐 Complete Algorithm Flow

```
┌─────────────────────────────────────┐
│  shouldJump() called every frame    │
└─────────────────┬───────────────────┘
                  │
    ┌─────────────▼──────────────┐
    │ PRIORITY 1: Floor Safety   │
    │ Will hit floor next frame? │
    └─────────────┬──────────────┘
                  │
            ┌─────▼─────┐
            │    YES    │
            │  JUMP! ✅  │
            └───────────┘
                  │ NO
    ┌─────────────▼────────────────────┐
    │ PRIORITY 2: Emergency Bottom     │
    │ Pipe nearby & collision in 5?    │
    └─────────────┬────────────────────┘
                  │
            ┌─────▼─────┐
            │    YES    │
            │  JUMP! ✅  │
            └───────────┘
                  │ NO
    ┌─────────────▼──────────────┐
    │  No pipe? Return False     │
    └─────────────┬──────────────┘
                  │ Pipe exists
    ┌─────────────▼───────────────────┐
    │ Calculate gap_center            │
    │ Is gap_center ≤ 300?            │
    │ (top half vs bottom half)       │
    └─────────────┬───────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
    ┌────▼─────┐    ┌─────▼────┐
    │ TOP HALF │    │ BOT HALF │
    └────┬─────┘    └─────┬────┘
         │                │
         │                │
┌────────▼────────┐  ┌────▼──────────┐
│ APEX STRATEGY   │  │ BOTTOM PIPE   │
│                 │  │ STRATEGY      │
│ Calculate:      │  │               │
│ - target_y      │  │ Predict hit   │
│ - minimum_y     │  │ bottom pipe?  │
│                 │  │               │
│ Defensive check:│  │ If yes: JUMP  │
│ minimum_y near  │  │ If no: False  │
│ floor?          │  │               │
│                 │  │               │
│ If conflict:    │  └───────────────┘
│ → use bot pipe  │
│                 │
│ If current_y    │
│ >= minimum_y:   │
│ → JUMP          │
│ Else:           │
│ → False         │
└─────────────────┘
```

# AI Used:
1. Claude integrated with VScode

## 🎮 Quick Start

```bash
# Install dependencies
pip install uv
uv venv
source .venv/Scripts/activate
uv pip install -r requirements.txt

# Start the server
python app.py

# Open browser
# Navigate to: http://localhost:3000
```

## 🧠 AI Algorithm Overview

The AI uses a **priority-based decision system** with three levels:

```
Priority 1: Floor Safety        → Prevent floor collision
Priority 2: Emergency Bottom    → Prevent bottom pipe collision
Priority 3: Strategy Selection  → Navigate through pipe gaps depending on where the gap was position in the screen. If the gap was closer to the cieling we'd enter from jumping from the bottom. If it was closer to the floor then we'd enter by falling into it and jumping
```

---

## 🏗️ Core Logic Components

### 1. Floor Safety (Highest Priority)

**Purpose:** Prevent the pilot from hitting the floor at all costs.

**How It Works:**
```python
# Predict position in next frame
next_velocity = current_velocity + gravity
next_y = current_y + next_velocity
pilot_bottom_next_frame = next_y + pilot_height

# Jump if collision imminent
if pilot_bottom_next_frame + safety_margin >= floor:
    return True  # Emergency floor avoidance!
```

**Key Concept:** Simulates the next frame's physics to predict collision before it happens.

**Origin Prompt & Conversation w/ Claude:**
```
USER:
"Lets start by building a feature that prevents the pilot from hitting the ground:
1. Allow the pilot to fall as close to the ground as possible and only jump
   right before he hits it"

ASSISTANT:
"This is simple ground avoidance. Let me implement:
1. Read the y position of pilot
2. Check how close the bottom would be to the floor in the next frame
3. If the pilot's edge would hit the floor in the next frame then jump
4. Otherwise don't jump"

USER:
"I added a + 10 to pilot_bottom_next_frame. Because it wouldn't jump. Can you
please add an offset that checks the height and width of the pilot so that
the edge of it doesn't collide"

ASSISTANT:
"Added dynamic safety margin:
safety_margin = max(pilot_height * 0.1, pilot_width * 0.1, 5)

This scales with pilot dimensions. For 30x30 pilot: margin = 5 pixels"
```

**Lessons Learned:**
- Predictive collision detection (N frames ahead) is more reliable than reactive
- Dynamic safety margins prevent hard-coded values that break with different dimensions
- Floor avoidance must be the highest priority - it's the baseline for survival

---

### 2. Emergency Bottom Pipe Collision Check

**Purpose:** Catch cases where the pilot jumped too early and is falling into the bottom pipe.

**How It Works:**
```python
if pipe is nearby (0 < distance < 150):
    # Simulate 5 frames ahead
    predicted_y = current_y
    predicted_velocity = current_velocity

    for _ in range(5):
        predicted_velocity += gravity
        predicted_y += predicted_velocity

    predicted_bottom = predicted_y + pilot_height

    # Emergency jump if collision detected
    if predicted_bottom >= gap_bottom:
        return True  # Emergency bottom pipe avoidance!
```

**Key Concept:** Acts as a safety net when main strategy timing is slightly off.

**Origin Prompt & Conversation:**
```
USER:
"Can we add an emergency check that if the pilot will collide with the bottom
pipe it'll jump once again? There are cases where it's possible that the pilot
jumps too early"

ASSISTANT:
"Excellent safety addition! This prevents scenarios like:
- Pilot at Y=350, falling with velocity=+5
- Bottom pipe at Y=400
- Without check: Falls into pipe at Y=405 💥
- With check: Detects collision at 5 frames → jumps at Y=365 ✅

The emergency check runs BEFORE strategy logic, so it can override both apex
and bottom-pipe strategies when necessary!"
```

**Lessons Learned:**
- Main strategies can have timing edge cases
- Emergency checks should predict multiple frames ahead (5 in this case)
- Only activate when pipe is nearby to avoid false positives
- Runs BEFORE strategy logic to act as true safety override

---

### 3. Strategy Splitting: Top Half vs Bottom Half

**Purpose:** Use different navigation strategies based on gap position in screen.

**How It Works:**
```python
gap_center = (pipe['topPipe'] + pipe['bottomPipe']) / 2
SCREEN_CENTER = 300  # For 600px screen

if gap_center <= SCREEN_CENTER:
    # GAP IN TOP HALF
    # Use Apex Targeting Strategy
    return apex_strategy()
else:
    # GAP IN BOTTOM HALF
    # Use Bottom Pipe Targeting Strategy
    return bottom_pipe_strategy()
```

**Key Concept:** Different gap positions require fundamentally different approaches.

**Origin Prompt & Conversation:**
```
USER INITIAL APPROACH:
"Calculate how many jumps it would need in order to reach the middle area of
the pipes and land right outside of the width of the pipe.

This worked as long as the gap was below the second half of the screen. The
issue arose because of the ground logic kept the pilot too low down so it
wasn't possible to reach the top."

ASSISTANT ANALYSIS:
"Your approach failed because:

When gap is HIGH (Y=150-250):
- Ground logic keeps you at Y=550 ✅
- Gap is 300+ pixels above you 😟
- You need 5+ jumps to climb 300px
- That takes 80+ frames
- But by the time you detect the problem, pipe is too close!

This is a greedy algorithm - optimizing for LOCAL constraint (floor) without
considering GLOBAL goal (navigate all pipes)."

USER DECISION:
"B) It seems we may end up doing a split solution. If the pipe gap is equal or
above the center we can use the apex solution. If it's below we should consider
aiming to fall right to the bottom pipe and jumping right before we hit it so
we pass by safely"
```

**Lessons Learned:**
- One-size-fits-all strategies often fail at extremes
- Analyze failures to understand when/why they occur
- Hybrid approaches can be more robust than pure solutions
- The split point (screen center) is a critical tuning parameter

---

### 4. Apex Targeting Strategy (Top Half Gaps)

**Purpose:** Maintain altitude so jump apex threads through gap at safe height.

**How It Works:**
```python
# Calculate 3/4ths target (closer to top for safety)
target_y = gap_bottom - (gap_height * 0.75)

# Physics: One jump gives 64 pixels of height
# Calculated from: v² / (2g) = 64 / 1 = 64
apex_height = 64

# Calculate minimum Y to maintain
# If we jump from this position, apex will hit target_y
minimum_y = target_y + apex_height

# Continuous altitude maintenance
if current_y >= minimum_y:
    return True   # At or below minimum → JUMP to climb/maintain
else:
    return False  # Above minimum → let gravity work
```

**Key Concept:** Continuous altitude maintenance, not one-time positioning.

**Origin Prompt & Conversation:**
```
ASSISTANT CONFUSION:
"I'm confused. When you said 'jump when we reach the height or go below it',
I interpreted this as a one-time jump at a specific position. But if pilot is
at Y=520 and jump_start_y is Y=239, the pilot is way BELOW. Should it jump
immediately and keep jumping to climb?"

USER CLARIFICATION:
"The apex strategy is to maintain a minimum height we need to where the apex of
the next jump will be between the gap. So we always jump when we're below or
equal to the minimum height we need to be so that the next jumps apex will be
between the gap"

ASSISTANT REALIZATION:
"OH! Now I get it! This is a continuous altitude maintenance strategy!

The pilot:
- Repeatedly jumps to climb from floor to minimum height
- Once at minimum height, maintains bouncing pattern
- Apex of each bounce threads through gap at 3/4ths position
- Keeps jumping whenever current_y >= minimum_y"
```

**Example Execution Trace:**
```
Frame 0:  Y=520 (at floor), minimum=239 → JUMP ✅
Frame 1:  Y=512, minimum=239 → JUMP ✅
Frame 10: Y=450, minimum=239 → JUMP ✅
...climbing via repeated jumps...
Frame 50: Y=250, minimum=239 → JUMP ✅
Frame 70: Y=230, minimum=239 → DON'T JUMP ❌ (above minimum)
Frame 75: Y=239, minimum=239 → JUMP ✅
Frame 76: Y=231, minimum=239 → DON'T JUMP ❌
...maintains bouncing pattern around Y=235...
```

**Physics Details:**
```
Jump velocity: -8 pixels/frame (upward)
Gravity: +0.5 pixels/frame²

One jump trajectory:
Frame 0:  Jump applied, velocity = -8
Frame 1:  velocity = -7.5, climbed 8px
Frame 2:  velocity = -7.0, climbed 7.5px
...
Frame 16: velocity = 0 (apex), total climb ≈ 64px
Frame 17: velocity = +0.5, start falling
```

**Lessons Learned:**
- Continuous strategies require different thinking than one-shot actions
- Physics calculations are critical (apex_height = 64 comes from v²/2g)
- Aiming for 3/4ths (not center) provides safety margin
- The strategy naturally handles climbing AND maintaining altitude

---

### 5. Bottom Pipe Targeting Strategy (Bottom Half Gaps)

**Purpose:** Bounce along the bottom pipe edge like floor avoidance.

**How It Works:**
```python
# Treat bottom pipe like a temporary floor
target_y = gap_bottom

# Same prediction logic as floor safety
next_velocity = current_velocity + gravity
next_y = current_y + next_velocity
pilot_bottom_next_frame = next_y + pilot_height

# Jump if about to hit bottom pipe
if pilot_bottom_next_frame + safety_margin >= target_y:
    return True

return False
```

**Key Concept:** Reuse proven floor avoidance logic for low gaps.

**Origin Prompt & Conversation:**
```
USER DECISION:
"If it's below [screen center] we should consider aiming to fall right to the
bottom pipe and jumping right before we hit it so we pass by safely"

ASSISTANT IMPLEMENTATION:
"For bottom half gaps:
- Treat the bottom pipe like a floor
- Use the same prediction logic as floor safety
- Jump right before hitting it
- Result: Bounce along bottom pipe edge"
```

**Why This Works:**
- Low gaps don't need complex altitude maintenance
- Floor avoidance logic is already proven and reliable
- Bouncing along bottom edge is safe for gaps in lower screen
- Minimal code reuse from floor safety implementation

**Lessons Learned:**
- Don't overcomplicate when simple solutions work
- Reusing proven logic reduces bugs
- Bottom-half gaps have different physics constraints than top-half

---

### 6. Defensive Check: Minimum Y vs Floor Conflict

**Purpose:** Handle edge case where calculated minimum height conflicts with floor.

**How It Works:**
```python
# After calculating minimum_y for apex strategy
if minimum_y >= floor - 20:
    # EDGE CASE: Minimum height too close to floor!
    # Fall back to bottom pipe strategy
    if pilot_bottom_next_frame + safety_margin >= gap_bottom:
        return True
    return False
```

**Key Concept:** Defensive programming for theoretically impossible but mathematically possible edge cases.

**Origin Prompt & Conversation:**
```
USER QUESTION:
"Minimum y should never be below the floor right? Since we're calculating it
based on the height of the floor to ceiling?"

ASSISTANT ANALYSIS:
"Let me verify the math:

Worst case:
gap_bottom = floor - 10
target_y = (floor - 10) - (gap_height * 0.75)
minimum_y = target_y + 64
         = floor + 54 - (gap_height * 0.75)

If gap_height = 100:
minimum_y = floor + 54 - 75 = floor - 21

🚨 minimum_y could be BELOW floor!

Should we add a defensive check anyway?"

USER RESPONSE:
"I'd like to add defensive checks for future programs so they're aware of the
situation in case they think it's a potential bug"

ASSISTANT IMPLEMENTATION:
"Added defensive check with detailed comment explaining:
- Why this edge case exists
- What it means (gap very low and/or floor very high)
- What to check if it triggers (level generation, floor height, gap sizes)
- Fallback behavior (use bottom pipe strategy instead)"
```

**Code Comment Example:**
```python
# 🛡️ DEFENSIVE CHECK: Ensure minimum_y is safely above floor
# This shouldn't happen due to level generation, but check anyway
# for future-proofing and debugging
if minimum_y >= floor - 20:
    # EDGE CASE: Minimum height is too close to or below floor!
    # This means gap is very low and/or floor is very high
    # Fall back to bottom pipe strategy instead of apex strategy
    #
    # NOTE TO FUTURE DEVELOPERS:
    # If you see this triggering, check:
    # 1. Level generation - gaps extending too close to floor
    # 2. Floor randomization - floor too high for gap positions
    # 3. Gap height - very large gaps near floor cause this
```

**Lessons Learned:**
- Even "impossible" edge cases deserve defensive checks
- Future developers (including future you) benefit from detailed comments
- Math analysis can reveal theoretical edge cases
- Defensive checks should have clear fallback behavior
- Comments should explain WHEN and WHY to investigate

---

---

## 🎯 Strategy Selection Examples

### Example 1: High Gap (Y=150-250)
```
Gap center: 200 (≤ 300) → TOP HALF
Strategy: Apex Targeting

target_y = 250 - (100 * 0.75) = 175
minimum_y = 175 + 64 = 239

Behavior:
- Pilot at Y=520 → JUMP (520 >= 239)
- Pilot climbs via repeated jumps
- Reaches Y=235, maintains bouncing
- Apex of bounces at Y≈171
- Threads through gap at 3/4ths height ✅
```

### Example 2: Low Gap (Y=400-500)
```
Gap center: 450 (> 300) → BOTTOM HALF
Strategy: Bottom Pipe Targeting

target_y = 500 (bottom pipe)

Behavior:
- Pilot falls toward Y=500
- Predicts collision when Y≈490
- Jumps at Y=490
- Bounces along bottom pipe edge
- Passes through gap near bottom ✅
```

### Example 3: Edge Case (High Floor + Low Gap)
```
Floor: 400
Gap: 350-450, center=400 (> 300) → TOP HALF initially

target_y = 350 - (100 * 0.75) = 275
minimum_y = 275 + 64 = 339

Defensive check: 339 >= 400 - 20? → 339 >= 380? → NO ✅
Apex strategy proceeds normally
```

---

## 📊 Testing Levels

| Level    | Pipes | Description                    | Tests                          |
|----------|-------|--------------------------------|--------------------------------|
| Simple   | 1     | Single pipe                    | Basic logic                    |
| Medium   | 5     | Varying gaps                   | Strategy switching             |
| Hard     | 10    | Full challenge                 | Sustained performance          |
| Extreme  | 0     | No pipes (floor only)          | Floor safety in isolation      |
| Marathon | 200   | Ultimate stress test           | All strategies, long duration  |

**Marathon Pattern:**
```
Pipes 0-9:   Y=150, 190, 230, 270, 310, 350, 390, 430, 470, 510
             (Cycles from top to bottom)
Pipes 10-19: [Repeats pattern]
...
Pipes 190-199: [Repeats pattern]

Spacing: 200px apart
Total distance: ~40,000 pixels
Gap heights: 130-160px (varies)
```

---

## 🔧 Key Parameters

```python
# Physics
GRAVITY = 0.5           # Pixels/frame²
JUMP_VELOCITY = -8      # Pixels/frame (negative = upward)
APEX_HEIGHT = 64        # Pixels (calculated from physics)

# Strategy
SCREEN_CENTER = 300     # Y position (splits top/bottom half)
TARGET_RATIO = 0.75     # Aim for 3/4ths toward top

# Safety
FLOOR_SAFETY_MARGIN = max(height * 0.1, width * 0.1, 5)
EMERGENCY_FRAMES = 5    # Frames to predict ahead
EMERGENCY_DISTANCE = 150 # Pixels (when to check pipe collision)
DEFENSIVE_BUFFER = 20   # Pixels (minimum_y vs floor check)
```

---

## 🎓 Key Learnings & Design Principles

### 1. **Greedy Algorithms Fail at Global Optimization**
Floor-hugging works locally but prevents reaching high pipes. Need lookahead and planning.

### 2. **Hybrid Strategies > One-Size-Fits-All**
Different scenarios (top gaps vs bottom gaps) need fundamentally different approaches.

### 3. **Predictive > Reactive**
Simulating future frames prevents collisions better than reacting to current state.

### 4. **Defensive Checks Are Free Insurance**
Even "impossible" edge cases deserve checks with explanatory comments.

### 5. **Physics Matters**
Understanding jump mechanics (apex = 64px) is critical for accurate predictions.

### 6. **Priority Systems Prevent Conflicts**
Clear priority ordering (Floor > Emergency > Strategy) prevents contradictory decisions.

### 7. **Incremental Development Wins**
Building simple features first (floor safety) then adding complexity (pipe navigation) reduces bugs.

### 8. **Test Extremes**
Stress tests (200 pipes) reveal edge cases that small tests miss.

---

## 📁 Project Structure

```
.
├── ai_controller.py           # ⭐ Main AI logic (implement here!)
├── game_engine.py             # Physics & collision detection
├── levels.py                  # Test level configurations
├── app.py                     # FastAPI server with hot-reload
├── static/
│   ├── index.html            # Web UI
│   └── game.js               # Frontend rendering
├── requirements.txt           # Python dependencies
├── README.md                 # This file
├── Prompts.txt               # Development prompts & Q&A
├── promptlog.txt             # Full conversation log
└── APPROACH_ANALYSIS.md      # Failure analysis & lessons
```

---

## 🚀 Future Improvements

### Potential Enhancements:
1. **Multi-pipe lookahead** - Consider next 2-3 pipes for better trajectory
2. **Velocity-aware targeting** - Adjust target based on current velocity
3. **Adaptive safety margins** - Tighten margins as confidence builds
4. **Ceiling avoidance** - Add emergency check for top pipe collisions
5. **Machine learning** - Train on failures to improve parameters
6. **Performance metrics** - Track success rate by gap type/position

### Known Limitations:
- Assumes constant pipe speed (doesn't handle acceleration)
- No optimization for minimum jumps (could be more efficient)
- Doesn't handle moving floors or pipes
- Fixed 3/4ths ratio (could be adaptive)

---

## 📝 Development Timeline

**Phase 1: Scaffolding** (~15 min)
- FastAPI + WebSocket setup
- Hot-reload implementation
- Level system

**Phase 2: Floor Safety** (~10 min)
- Basic collision avoidance
- Dynamic safety margins

**Phase 3: Strategy Analysis** (~25 min)
- Understanding greedy algorithm failure
- Analyzing physics constraints

**Phase 4: Strategy Design** (~35 min)
- Hybrid approach decision
- Top/bottom split logic

**Phase 5: Implementation** (~30 min)
- Apex targeting strategy
- Bottom pipe strategy
- Defensive checks

**Phase 6: Testing & Refinement** (~10 min)
- Marathon level creation
- Emergency collision checks

**Total:** ~2 hours of focused development

---

## 🏆 Success Metrics

**Target Performance:**
- ✅ Simple (1 pipe): 100% success
- ✅ Medium (5 pipes): 100% success
- ✅ Hard (10 pipes): 100% success
- ✅ Marathon (200 pipes): High success rate
- ✅ Extreme (no pipes): Never hit floor

**Observed Results:**
The hybrid strategy successfully navigates all test levels with emergency checks providing safety net for edge cases.

---

## 🤝 Contributing

This project was developed as a learning exercise. Feel free to:
- Experiment with different strategies
- Tune parameters in `ai_controller.py`
- Create new test levels in `levels.py`
- Add new emergency checks
- Improve prediction accuracy

---

## 📚 Additional Resources

- **APPROACH_ANALYSIS.md** - Detailed failure analysis of greedy approach
- **Prompts.txt** - All development prompts with Q&A format
- **promptlog.txt** - Complete conversation history
- **ai_controller.py** - Heavily commented implementation

---

## 📜 License

This project is provided as-is for educational purposes.

---

**Built with:** Python, FastAPI, WebSockets, JavaScript Canvas, Physics Simulation

**Key Concepts:** Predictive algorithms, Hybrid strategies, Physics-based AI, Priority systems, Defensive programming
