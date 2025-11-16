"""
Flappy Bird Simulation Engine
Handles game physics, pipe generation, and collision detection
"""

class Pilot:
    def __init__(self, x_pos=50, y_pos=300, height=30, width=30, gravity=0.5, jump_velocity=-8):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.height = height
        self.width = width
        self.gravity = gravity
        self.jump_velocity = jump_velocity
        self.velocity = 0

    def jump(self):
        """Apply jump velocity to the pilot"""
        self.velocity = self.jump_velocity

    def update(self, gravity):
        """Update pilot position based on gravity"""
        self.velocity += gravity
        self.y_pos += self.velocity

    def to_dict(self):
        """Convert pilot to dictionary format for shouldJump function"""
        return {
            'xPos': self.x_pos,
            'yPos': self.y_pos,
            'height': self.height,
            'width': self.width,
            'gravity': self.gravity,
            'jumpVelocity': self.jump_velocity
        }


class Pipe:
    def __init__(self, x_position, gap_y_center=300, gap_height=150):
        self.x_position = x_position
        self.gap_y_center = gap_y_center
        self.gap_height = gap_height

        # Calculate top and bottom pipe positions
        self.top_pipe = gap_y_center - gap_height // 2  # Y position where top pipe ends
        self.bottom_pipe = gap_y_center + gap_height // 2  # Y position where bottom pipe starts

    def update(self, pipe_speed):
        """Move pipe left by pipe_speed"""
        self.x_position -= pipe_speed

    def to_dict(self):
        """Convert pipe to dictionary format for shouldJump function"""
        return {
            'topPipe': self.top_pipe,
            'bottomPipe': self.bottom_pipe,
            'xPosition': self.x_position
        }


class FlappyBirdGame:
    def __init__(self, screen_width=800, screen_height=600, pipe_speed=3, gravity=0.5):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.pipe_speed = pipe_speed
        self.gravity = gravity

        self.pilot = Pilot(x_pos=100, y_pos=screen_height // 2, gravity=gravity)
        self.pipes = []
        self.score = 0
        self.frame_count = 0
        self.game_over = False

        # Generate initial pipes
        self._generate_initial_pipes()

    def _generate_initial_pipes(self):
        """Generate initial set of pipes"""
        import random
        for i in range(4):
            x_pos = self.screen_width + i * 250
            gap_center = random.randint(150, self.screen_height - 150)
            self.pipes.append(Pipe(x_pos, gap_center))

    def get_current_pipe(self):
        """Get the next pipe that the pilot needs to pass"""
        for pipe in self.pipes:
            if pipe.x_position + 50 > self.pilot.x_pos:  # 50 is approximate pipe width
                return pipe
        return None

    def get_game_state(self):
        """Get current game state in the format expected by shouldJump"""
        current_pipe = self.get_current_pipe()

        return {
            'pilot': self.pilot.to_dict(),
            'pipeSpeed': self.pipe_speed,
            'currentPipe': current_pipe.to_dict() if current_pipe else None,
            'pipeArray': [pipe.to_dict() for pipe in self.pipes],
            'gravity': self.gravity
        }

    def check_collision(self):
        """Check if pilot collided with pipes or boundaries"""
        # Check ceiling and floor
        if self.pilot.y_pos <= 0 or self.pilot.y_pos + self.pilot.height >= self.screen_height:
            return True

        # Check pipe collision
        for pipe in self.pipes:
            # Check if pilot is at the pipe's x position
            if (pipe.x_position < self.pilot.x_pos + self.pilot.width and
                pipe.x_position + 50 > self.pilot.x_pos):  # 50 is pipe width

                # Check if pilot is outside the gap
                if (self.pilot.y_pos < pipe.top_pipe or
                    self.pilot.y_pos + self.pilot.height > pipe.bottom_pipe):
                    return True

        return False

    def update(self, should_jump):
        """Update game state for one frame"""
        if self.game_over:
            return

        self.frame_count += 1

        # Jump if AI decides to
        if should_jump:
            self.pilot.jump()

        # Update pilot position
        self.pilot.update(self.gravity)

        # Update pipes
        for pipe in self.pipes:
            pipe.update(self.pipe_speed)

        # Remove pipes that are off screen and add new ones
        self.pipes = [pipe for pipe in self.pipes if pipe.x_position > -100]

        # Add new pipe if needed
        if len(self.pipes) < 4:
            import random
            last_pipe = self.pipes[-1] if self.pipes else None
            if last_pipe:
                new_x = last_pipe.x_position + 250
            else:
                new_x = self.screen_width

            gap_center = random.randint(150, self.screen_height - 150)
            self.pipes.append(Pipe(new_x, gap_center))

        # Update score (passed a pipe)
        for pipe in self.pipes:
            if pipe.x_position + 50 == self.pilot.x_pos:
                self.score += 1

        # Check collision
        if self.check_collision():
            self.game_over = True

    def is_game_over(self):
        return self.game_over
