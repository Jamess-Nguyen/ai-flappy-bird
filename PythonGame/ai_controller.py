"""
AI Controller for Flappy Bird
Hybrid Strategy: Apex targeting for high gaps, bottom-pipe targeting for low gaps
"""

def shouldJump(game_state):
    """
    Hybrid navigation strategy:
    - For gaps in top half: Maintain altitude so jump apex hits 3/4ths target
    - For gaps in bottom half: Bounce along bottom pipe like floor avoidance
    - Floor safety always takes priority

    Args:
        game_state (dict): Dictionary containing:
            - pilot (dict): {xPos, yPos, height, width, gravity, jumpVelocity, velocity}
            - pipeSpeed (float): Speed at which pipes approach per frame
            - currentPipe (dict): {topPipe, bottomPipe, xPosition} - the next pipe to pass
            - pipeArray (list): List of all pipe dicts
            - gravity (float): Gravity applied to pilot per frame
            - floor (float): Y position where floor starts
    """
    pilot = game_state['pilot']
    floor = game_state['floor']
    gravity = game_state['gravity']
    pipe = game_state['currentPipe']

    # Extract pilot state
    current_y = pilot['yPos']
    current_velocity = pilot['velocity']
    pilot_height = pilot['height']
    pilot_width = pilot['width']

    # Calculate safety margin based on pilot dimensions
    safety_margin = max(pilot_height * 0.1, pilot_width * 0.1, 5)

    # ========================================
    # PRIORITY 1: FLOOR SAFETY (Highest Priority)
    # ========================================
    # Always prevent floor collision regardless of pipe strategy

    next_velocity = current_velocity + gravity
    next_y = current_y + next_velocity
    pilot_bottom_next_frame = next_y + pilot_height

    if pilot_bottom_next_frame + safety_margin >= floor:
        return True  # Emergency floor avoidance!

    # ========================================
    # PRIORITY 2: EMERGENCY BOTTOM PIPE COLLISION
    # ========================================
    # If we're on a collision course with the bottom pipe, jump NOW!
    # This catches cases where we jumped too early and are falling into the pipe

    if pipe:
        gap_bottom = pipe['bottomPipe']
        pipe_x = pipe['xPosition']
        pilot_x = pilot['xPos']

        # Only check if pipe is nearby (within reasonable range)
        distance_to_pipe = pipe_x - pilot_x
        if 0 < distance_to_pipe < 150:  # Pipe is close!

            # Predict if we'll collide with bottom pipe
            # Check a few frames ahead to catch early
            frames_to_check = 5
            predicted_y = current_y
            predicted_velocity = current_velocity

            for _ in range(frames_to_check):
                predicted_velocity += gravity
                predicted_y += predicted_velocity

            predicted_bottom = predicted_y + pilot_height

            # Emergency jump if we're going to hit the bottom pipe!
            if predicted_bottom+5 >= gap_bottom:
                return True  # Emergency bottom pipe avoidance!

    # ========================================
    # NO PIPE: Just maintain floor safety
    # ========================================

    if not pipe:
        return False  # Floor safety already handled above

    # ========================================
    # PIPE EXISTS: Choose strategy based on gap position
    # ========================================

    gap_top = pipe['topPipe']
    gap_bottom = pipe['bottomPipe']
    gap_center = (gap_top + gap_bottom) / 2
    gap_height = gap_bottom - gap_top

    # Determine which half of screen the gap is in
    # Lower Y values = top of screen, Higher Y values = bottom of screen
    SCREEN_CENTER = 300  # Assuming 600px screen height

    # ========================================
    # STRATEGY SPLIT: Top Half vs Bottom Half
    # ========================================

    if gap_center <= SCREEN_CENTER:
        # ========================================
        # APEX STRATEGY (For gaps in top half)
        # ========================================
        # Maintain minimum altitude so that the APEX of each jump
        # reaches the 3/4ths target position within the gap

        # Calculate target Y position (3/4ths from bottom of gap toward top)
        target_y = gap_bottom - (gap_height * 0.75)

        # Physics: Jump gives 64 pixels of height
        # (calculated from: v² / (2g) = 64 / 1 = 64)
        apex_height = 64

        # Calculate minimum Y we need to maintain
        # If we jump from this position, apex will hit target_y
        minimum_y = target_y + apex_height

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

            # Use bottom pipe strategy as fallback
            if pilot_bottom_next_frame + safety_margin >= gap_bottom:
                return True
            return False

        # Normal apex strategy logic:
        # Jump whenever we're at or below minimum height to maintain altitude
        if current_y >= minimum_y:
            return True  # Maintain altitude / climb
        else:
            return False  # Above minimum, let gravity work

    else:
        # ========================================
        # BOTTOM PIPE STRATEGY (For gaps in bottom half)
        # ========================================
        # Treat the bottom pipe like a floor
        # Jump right before hitting it, bounce along bottom edge

        target_y = gap_bottom

        # Same prediction logic as floor safety
        # Jump if we're about to hit the bottom pipe
        if pilot_bottom_next_frame + safety_margin >= target_y:
            return True

        return False
