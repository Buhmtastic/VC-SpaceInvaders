# Game Development Context: VC-SpaceInvaders

This document summarizes the key elements for developing the Space Invaders-style game, based on the initial design document.

## 1. Game Title

*   **Project Name**: VC-SpaceInvaders
*   **Note**: The name "Space Invaders" and its original assets are copyrighted. We will create original assets and use this project name.

## 2. Core Gameplay Mechanics

*   **Player**:
    *   Controls a laser cannon at the bottom of the screen.
    *   Moves left and right.
    *   Fires a single projectile upwards at a time. Can only fire again after the projectile hits an enemy or goes off-screen.
*   **Enemies (Invaders)**:
    *   Arranged in a 5x11 grid (55 total).
    *   Move horizontally as a group. When they reach the edge of the screen, they move down one step.
    *   Game over if they reach the bottom of the screen.
    *   Point system:
        *   Top row: 30 points
        *   Middle 2 rows: 20 points
        *   Bottom 2 rows: 10 points
*   **Defensive Bunkers**:
    *   Four bunkers located above the player.
    *   They are destructible by both player and enemy projectiles.
    *   Provide temporary cover for the player.
*   **UFO (Mystery Ship)**:
    *   Appears randomly at the top of the screen.
    *   Moves horizontally across the screen.
    *   Awards bonus points when destroyed (50-300 points).
    *   (Advanced) The score can be determined by the player's shot count.
*   **Difficulty**:
    *   The speed of the invaders increases as their numbers decrease. This is a core mechanic to replicate.

## 3. Technical Specifications

*   **Engine**: PyGame 2.x
*   **Language**: Python 3.8+
*   **Sound**:
    *   Simple beep sounds for movement, shooting, and explosions.
    *   A "heartbeat" rhythm that speeds up as enemies get closer.

## 4. Key Implementation Points

*   **Single Shot Limit**: The player can only have one laser on the screen at a time.
*   **Invader Speed**: The inverse relationship between the number of invaders and their speed is a critical feature.
*   **Bunker Destruction**: Implement a simple, multi-stage destruction state for the bunkers rather than pixel-perfect destruction.
*   **High Score**: The game should track and display a high score.

## 5. Asset Creation

*   **Graphics**: All visual assets (player ship, enemies, UFO, bunkers, projectiles) must be created as original pixel art to avoid copyright infringement.
*   **Sound**: All sound effects must be originally created.

This context file will serve as a quick reference guide throughout the development process.
