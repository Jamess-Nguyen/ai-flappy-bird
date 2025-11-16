"""
Flappy Bird AI - Main Entry Point
Run this to test your shouldJump implementation!
"""

import pygame
import sys
from flappy_bird_sim import FlappyBirdGame
from ai_controller import shouldJump


class FlappyBirdVisualizer:
    def __init__(self, game):
        pygame.init()
        self.game = game
        self.screen = pygame.display.set_mode((game.screen_width, game.screen_height))
        pygame.display.set_caption("Flappy Bird AI - CodeSignal Practice")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (135, 206, 250)
        self.GREEN = (34, 139, 34)
        self.RED = (220, 20, 60)
        self.YELLOW = (255, 215, 0)

    def draw(self, jump_decision):
        """Draw the current game state"""
        # Background
        self.screen.fill(self.BLUE)

        # Draw pipes
        for pipe in self.game.pipes:
            # Top pipe
            pygame.draw.rect(self.screen, self.GREEN,
                           (pipe.x_position, 0, 50, pipe.top_pipe))
            # Bottom pipe
            pygame.draw.rect(self.screen, self.GREEN,
                           (pipe.x_position, pipe.bottom_pipe, 50,
                            self.game.screen_height - pipe.bottom_pipe))

            # Draw gap center line (helpful for debugging)
            gap_center = (pipe.top_pipe + pipe.bottom_pipe) // 2
            pygame.draw.line(self.screen, self.YELLOW,
                           (pipe.x_position, gap_center),
                           (pipe.x_position + 50, gap_center), 2)

        # Draw pilot (bird)
        pilot = self.game.pilot
        color = self.YELLOW if jump_decision else self.RED
        pygame.draw.rect(self.screen, color,
                        (pilot.x_pos, pilot.y_pos, pilot.width, pilot.height))

        # Draw velocity indicator
        vel_end_y = pilot.y_pos + pilot.height // 2 + pilot.velocity * 5
        pygame.draw.line(self.screen, self.WHITE,
                        (pilot.x_pos + pilot.width // 2, pilot.y_pos + pilot.height // 2),
                        (pilot.x_pos + pilot.width // 2, vel_end_y), 3)

        # Draw score and info
        score_text = self.font.render(f'Score: {self.game.score}', True, self.WHITE)
        self.screen.blit(score_text, (10, 10))

        frame_text = self.small_font.render(f'Frame: {self.game.frame_count}', True, self.WHITE)
        self.screen.blit(frame_text, (10, 50))

        velocity_text = self.small_font.render(f'Velocity: {pilot.velocity:.2f}', True, self.WHITE)
        self.screen.blit(velocity_text, (10, 80))

        jump_text = self.small_font.render(f'Jump: {jump_decision}', True,
                                          self.YELLOW if jump_decision else self.WHITE)
        self.screen.blit(jump_text, (10, 110))

        # Current pipe info
        current_pipe = self.game.get_current_pipe()
        if current_pipe:
            pipe_info = self.small_font.render(
                f'Next Pipe - X: {current_pipe.x_position}, Gap: {current_pipe.top_pipe}-{current_pipe.bottom_pipe}',
                True, self.WHITE)
            self.screen.blit(pipe_info, (10, 140))

        # Game over message
        if self.game.is_game_over():
            game_over_text = self.font.render('GAME OVER!', True, self.RED)
            restart_text = self.small_font.render('Press R to restart or Q to quit', True, self.WHITE)
            self.screen.blit(game_over_text,
                           (self.game.screen_width // 2 - 100, self.game.screen_height // 2 - 50))
            self.screen.blit(restart_text,
                           (self.game.screen_width // 2 - 150, self.game.screen_height // 2))

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_r and self.game.is_game_over():
                        # Restart game
                        self.game = FlappyBirdGame(
                            screen_width=self.game.screen_width,
                            screen_height=self.game.screen_height,
                            pipe_speed=self.game.pipe_speed,
                            gravity=self.game.gravity
                        )

            if not self.game.is_game_over():
                # Get AI decision
                game_state = self.game.get_game_state()
                jump_decision = shouldJump(game_state)

                # Update game
                self.game.update(jump_decision)

                # Draw
                self.draw(jump_decision)
            else:
                # Still draw even when game over
                self.draw(False)

            self.clock.tick(60)  # 60 FPS

        pygame.quit()


def run_test_mode():
    """Run without visualization for quick testing"""
    print("Running Flappy Bird AI in test mode...")
    print("=" * 50)

    game = FlappyBirdGame()
    frame = 0

    while not game.is_game_over() and frame < 10000:  # Max 10000 frames
        game_state = game.get_game_state()
        jump_decision = shouldJump(game_state)
        game.update(jump_decision)
        frame += 1

        if frame % 100 == 0:
            print(f"Frame {frame}: Score = {game.score}, Pilot Y = {game.pilot.y_pos:.1f}")

    print("=" * 50)
    if game.is_game_over():
        print(f"Game Over! Final Score: {game.score} (Survived {frame} frames)")
    else:
        print(f"Test complete! Score: {game.score}")

    return game.score, frame


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Run in test mode (no visualization)
        run_test_mode()
    else:
        # Run with visualization
        print("Starting Flappy Bird AI Visualizer...")
        print("Controls:")
        print("  Q - Quit")
        print("  R - Restart (when game over)")
        print("\nImplement your AI logic in ai_controller.py!")
        print("=" * 50)

        game = FlappyBirdGame()
        visualizer = FlappyBirdVisualizer(game)
        visualizer.run()
