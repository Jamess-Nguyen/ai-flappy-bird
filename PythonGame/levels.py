"""
Predefined level configurations for Flappy Bird AI Challenge
Each level defines the pipe placements for testing your AI
"""

LEVELS = {
    "simple": {
        "name": "Simple (1 Pipe)",
        "description": "Single pipe to test basic logic",
        "floor": {"min": 500, "max": 600},  # Floor in bottom 1/6 of screen
        "pipes": [
            {"xPosition": 400, "gapCenter": 300, "gapHeight": 150}
        ]
    },
    "medium": {
        "name": "Medium (5 Pipes)",
        "description": "Five pipes with varying gaps",
        "floor": {"min": 480, "max": 600},  # Floor in bottom 1/5 of screen
        "pipes": [
            {"xPosition": 400, "gapCenter": 300, "gapHeight": 150},
            {"xPosition": 650, "gapCenter": 250, "gapHeight": 150},
            {"xPosition": 900, "gapCenter": 350, "gapHeight": 140},
            {"xPosition": 1150, "gapCenter": 280, "gapHeight": 160},
            {"xPosition": 1400, "gapCenter": 320, "gapHeight": 150}
        ]
    },
    "hard": {
        "name": "Hard (10 Pipes)",
        "description": "Ten pipes with challenging gaps",
        "floor": {"min": 450, "max": 600},  # Floor in bottom 1/4 of screen
        "pipes": [
            {"xPosition": 400, "gapCenter": 300, "gapHeight": 150},
            {"xPosition": 650, "gapCenter": 200, "gapHeight": 140},
            {"xPosition": 900, "gapCenter": 380, "gapHeight": 140},
            {"xPosition": 1150, "gapCenter": 250, "gapHeight": 145},
            {"xPosition": 1400, "gapCenter": 350, "gapHeight": 140},
            {"xPosition": 1650, "gapCenter": 220, "gapHeight": 150},
            {"xPosition": 1900, "gapCenter": 330, "gapHeight": 140},
            {"xPosition": 2150, "gapCenter": 270, "gapHeight": 145},
            {"xPosition": 2400, "gapCenter": 310, "gapHeight": 140},
            {"xPosition": 2650, "gapCenter": 290, "gapHeight": 150}
        ]
    },
    "floor_test": {
        "name": "floor_test",
        "description": "Three pipes with very narrow gaps",
        "floor": {"min": 450, "max": 550},  # Floor varies in bottom portion
        "pipes": []
    },
    "marathon": {
        "name": "Marathon (200 Pipes!)",
        "description": "Ultimate stress test with 200 pipes",
        "floor": {"min": 480, "max": 580},
        "pipes": [
            # Generate 200 pipes with varying gap positions and heights
            # Pattern: Alternating high, medium, low gaps with varying heights
            {"xPosition": 450 + i * 200,
             "gapCenter": 150 + (i % 10) * 40,  # Cycles through Y=150 to Y=510
             "gapHeight": 140 + (i % 5) * 10}   # Gap heights: 120, 130, 140, 150, 160
            for i in range(200)
        ]
    }
}

def get_level(level_id):
    """Get level configuration by ID"""
    return LEVELS.get(level_id, LEVELS["marathon"])

def get_all_levels():
    """Get all available levels"""
    return {
        level_id: {
            "name": config["name"],
            "description": config["description"]
        }
        for level_id, config in LEVELS.items()
    }
