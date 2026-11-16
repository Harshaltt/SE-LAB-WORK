# Lava Escape Repair Lab

This project is a vertical platformer survival game using **Pygame**. It introduces students to jump physics, platform landing collision logic, vertical camera tracking, rising hazard mechanics, and procedural level generation within an object-oriented codebase
---

## What's Provided

A working Lava Escape game with:

- A player avatar capable of running left/right and jumping across elevated platforms (`A`/`D`/Arrow Keys and `W`/`UP`/`SPACE`)
- Procedurally generated platforms ascending vertically from a starting ground floor
- A smooth upward-scrolling camera tracking player progress
- A rising lava hazard that gradually accelerates upward as time elapses
- Real-time height measurement HUD and Game Over / Victory state overlays with restart functionality

It has **one deliberate bug** and **three optional features** left as tasks to implement. You are expected to **analyze**, **interact with an AI assistant**, and **complete/fix** the game to make it fully functional and more interesting.

### **Use an LLM (e.g. ChatGPT or Claude) as your debugging and pair-programming partner for this lab.**
---

## Getting Started

### Setup

1. Make sure you have Python 3.10+ installed.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the game:

```bash
python main.py
```

**Controls:** 
| Key | Action |
|-----|--------|
| A/D or Left/Right | Move |
| SPACE / W / UP | Jump |
| R | Restart |

## Tasks to Complete

Each task must be completed using an iterative process involving LLM suggestions and your critical code review.

### Task 1: Fix the one-way platform penetration bug

When jumping up through the bottom of a platform while falling back down, or when grazing the underside of a platform during an upward leap, the player's landing condition triggers incorrectly. In player.update(), the platform collision check evaluates: if self.rect.colliderect(p) and self.vel_y > 0 and self.rect.bottom <= p.bottom + 10:
   
Because self.rect.bottom <= p.bottom + 10 is overly generous, the player can clip through the underside of platforms or get snapped to the top of a platform even when their feet barely entered from below. Fix the vertical collision resolution so the player only lands if their feet were strictly above or near the platform's top edge before moving downward in that frame (e.g., verifying self.rect.bottom - self.vel_y <= p.top + 2), ensuring clean, reliable one-way platform physics.

### Task 2: Implement crumbling platforms

Make select platforms unstable. When the player lands on a crumbling platform, trigger a 1-second countdown timer or visual shaking animation before the platform breaks and vanishes from self.platforms, forcing the player to keep moving rapidly.
 
### Task 3: Implement spring bounce platforms

Add special yellow spring platforms throughout the generated platform list. When the player lands on a spring platform, launch them upward with double jump velocity (e.g., setting vel_y = -22) along with an energetic recoil animation.

### Task 4: Implement a lava surge warning and speed HUD

Provide visual feedback for rising danger by adding a danger meter HUD element that fills up as self.lava_rise increases. Additionally, every 15 seconds trigger a brief "Lava Burst" warning that temporarily accelerates the lava's ascent speed for 3 seconds before returning to normal.
---

## Expected Behavior

- The player can jump through the bottoms of platforms and land securely on their top surfaces without snagging or clipping through.
- The camera follows the player upward as higher platforms are reached.   
- The lava continuously rises from the bottom of the screen at an increasing rate.
- Touching the rising lava triggers the LAVA GOT YOU! game over banner.
- Reaching the top platform triggers the ESCAPED! victory banner.
- Pressing R resets the player, camera, lava position, and platforms for a fresh run.

## Folder Structure

```
lava-escape/
├── main.py
├── requirements.txt
├── game/
│   ├── __init__.py
│   ├── game_engine.py
│   ├── player.py
│   └── world.py
└── README.md
```

## Submission Checklist

Submission is only the following three things:

- [] A 10-second video of gameplay **before** your changes, showing the bug/broken behavior
- [] A 10-second video of gameplay **after** your changes, showing the bug fixed and the new features working
- [] The Chat/LLM used page link, with the complete chat history

---

## Lab 4 – Changes Made (PES2UG24CS183)

Each change was made by prompting an AI assistant (Claude), reviewing and testing the result, and committing each task separately.

| # | Change | Files |
|---|--------|-------|
| Task 1 | **Fixed the one-way platform penetration bug.** The player now lands only if their feet were at/above the platform top *before* this frame's movement (`prev_bottom <= p.top + 2`) and have now reached it. Jumping up through, or grazing, the underside no longer snaps the player on top. This also fixes `on_ground` flickering True/False every frame while standing, which made jumps register only on alternate frames. | `game/player.py` |
| Extra fix | **Camera start position.** The camera started at `cam_y = 0`, which left the player and ground below the visible screen. It now starts centred on the player. | `game/game_engine.py` |
| Task 2 | **Crumbling platforms.** About 22% of platforms are unstable (cracked texture). Landing on one starts a 1-second countdown with an intensifying shake and red glow, then the platform is removed from `self.platforms`. The ground, first and goal platforms are always solid. | `game/world.py`, `game/game_engine.py`, `game/player.py` |
| Task 3 | **Spring bounce platforms.** Yellow spring platforms launch the player with `vel_y = -22` (a normal jump is -13), with a damped coil recoil animation on the spring and a stretch animation on the player. | `game/world.py`, `game/player.py`, `game/game_engine.py` |
| Task 4 | **Lava surge warning and speed HUD.** A HUD panel shows height and a countdown to the next burst. A danger meter fills green to yellow to red as `self.lava_rise` increases, with a live `LAVA xN` speed readout. Every 15 s a **LAVA BURST!** (with a 1 s "incoming" pre-warning and a pulsing red screen edge) speeds the lava up 2.2x for 3 s, then returns to normal. | `game/game_engine.py` |

Platforms are now a `Platform` class that subclasses `pygame.Rect` with a `kind` of `normal`, `crumble` or `spring`, so all existing Rect collision code keeps working.

**Platform legend:** brown = normal, brown with cracks = crumbles 1 s after landing, yellow with coil = spring.

---

## Gameplay video

[`videos/gameplay_before_and_after.mp4`](videos/gameplay_before_and_after.mp4): the original game first (before), then the updated game with the danger HUD, lava bursts and new platforms (after).

## AI chat history

[`chat_history_PES2UG24CS183.pdf`](chat_history_PES2UG24CS183.pdf): the complete conversation with the AI assistant (Claude) used to fix the bug and add the features.
