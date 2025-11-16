"""
Flappy Bird Game Engine for Web Version
Handles game physics, collision detection, and state management
"""

import random

class GameEngine:
    def __init__(self, screen_width=800, screen_height=600, pipe_speed=3, gravity=0.5):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.pipe_speed = pipe_speed
        self.gravity = gravity

        # Pilot (bird) configuration
        self.pilot_x = 100
        self.pilot_y = screen_height // 2
        self.pilot_width = 30
        self.pilot_height = 30
        self.pilot_velocity = 0
        self.jump_velocity = -8

        # Floor configuration (Y position where floor starts)
        self.floor_y = screen_height  # Default: no visible floor

        # Game state
        self.pipes = []
        self.score = 0
        self.frame_count = 0
        self.game_over = False
        self.passed_pipes = set()

        # Mode
        self.autopilot = False

    def load_level(self, level_config):
        """Load a level from configuration"""
        self.reset()

        # Set floor position (randomized in bottom 1/4 of screen)
        floor_config = level_config.get("floor", {})
        if "min" in floor_config and "max" in floor_config:
            self.floor_y = random.randint(floor_config["min"], floor_config["max"])
        else:
            # Default: floor in bottom 1/4 of screen
            min_floor = int(self.screen_height * 0.75)
            self.floor_y = random.randint(min_floor, self.screen_height)

        # Create pipes from level config
        for pipe_config in level_config["pipes"]:
            gap_top = pipe_config["gapCenter"] - pipe_config["gapHeight"] // 2
            gap_bottom = pipe_config["gapCenter"] + pipe_config["gapHeight"] // 2

            # Ensure gap doesn't extend into floor
            if gap_bottom > self.floor_y:
                gap_bottom = self.floor_y - 10  # 10px safety margin
                gap_top = gap_bottom - pipe_config["gapHeight"]

            pipe = {
                "xPosition": pipe_config["xPosition"],
                "topPipe": gap_top,
                "bottomPipe": gap_bottom
            }
            self.pipes.append(pipe)

    def reset(self):
        """Reset game to initial state"""
        self.pilot_y = self.screen_height // 2
        self.pilot_velocity = 0
        self.pipes = []
        self.score = 0
        self.frame_count = 0
        self.game_over = False
        self.passed_pipes = set()

    def jump(self):
        """Make the pilot jump"""
        if not self.game_over:
            self.pilot_velocity = self.jump_velocity

    def get_current_pipe(self):
        """Get the next pipe that needs to be navigated"""
        for i, pipe in enumerate(self.pipes):
            if pipe["xPosition"] + 50 > self.pilot_x:  # 50 is pipe width
                return i, pipe
        return None, None

    def get_game_state(self):
        """Get game state in the format expected by shouldJump function"""
        current_pipe_idx, current_pipe = self.get_current_pipe()

        return {
            "pilot": {
                "xPos": self.pilot_x,
                "yPos": self.pilot_y,
                "height": self.pilot_height,
                "width": self.pilot_width,
                "gravity": self.gravity,
                "jumpVelocity": self.jump_velocity,
                "velocity": self.pilot_velocity
            },
            "pipeSpeed": self.pipe_speed,
            "currentPipe": current_pipe,
            "pipeArray": self.pipes,
            "gravity": self.gravity,
            "floor": self.floor_y
        }

    def check_collision(self):
        """Check if pilot collided with pipes or boundaries"""
        # Check ceiling
        if self.pilot_y <= 0:
            return True

        # Check floor collision
        if self.pilot_y + self.pilot_height >= self.floor_y:
            return True

        # Check pipe collision
        for pipe in self.pipes:
            # Check if pilot is at the pipe's x position
            if (pipe["xPosition"] < self.pilot_x + self.pilot_width and
                pipe["xPosition"] + 50 > self.pilot_x):  # 50 is pipe width

                # Check if pilot is outside the gap
                if (self.pilot_y < pipe["topPipe"] or
                    self.pilot_y + self.pilot_height > pipe["bottomPipe"]):
                    return True

        return False

    def update_score(self):
        """Update score based on passed pipes"""
        for i, pipe in enumerate(self.pipes):
            # Check if pipe just passed the pilot
            if pipe["xPosition"] + 50 < self.pilot_x and i not in self.passed_pipes:
                self.score += 1
                self.passed_pipes.add(i)

    def update(self, should_jump=False):
        """Update game state for one frame"""
        if self.game_over:
            return

        self.frame_count += 1

        # Jump if instructed
        if should_jump:
            self.jump()

        # Update pilot velocity and position
        self.pilot_velocity += self.gravity
        self.pilot_y += self.pilot_velocity

        # Update pipes position
        for pipe in self.pipes:
            pipe["xPosition"] -= self.pipe_speed

        # Update score
        self.update_score()

        # Check collision
        if self.check_collision():
            self.game_over = True

    def get_render_state(self):
        """Get state for rendering on frontend"""
        return {
            "pilot": {
                "x": self.pilot_x,
                "y": self.pilot_y,
                "width": self.pilot_width,
                "height": self.pilot_height,
                "velocity": self.pilot_velocity
            },
            "pipes": self.pipes,
            "score": self.score,
            "frame": self.frame_count,
            "gameOver": self.game_over,
            "screenWidth": self.screen_width,
            "screenHeight": self.screen_height,
            "floor": self.floor_y
        }
