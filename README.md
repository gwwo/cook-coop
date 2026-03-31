

Cook-CoOp provides minimal implementation for:
- A physics-based kitchen simulator supporting multiple cooperative players
- A [Gymnasium](https://gymnasium.farama.org/) environment wrapper for RL training
- A complete [PPO](https://arxiv.org/abs/1707.06347) self-play training pipeline with 64 parallel environments
- A [Pyglet](https://github.com/pyglet/pyglet) UI for interactive visualization and human play

<br>

<p align="center">
  <img src="assets/trained-selfplay-1.gif" width="80%">
</p>

<p align="center">
  <img src="assets/trained-selfplay-2.gif" width="80%">
</p>

<p align="center">
  <img src="assets/trained-selfplay-3.gif" width="80%">
</p>

## Acknowledgement

Only the visual assets in `game_ui/assets/` are sourced from [HumanCompatibleAI/overcooked_ai](https://github.com/HumanCompatibleAI/overcooked_ai).

The game engine and UI rendering are built from scratch. Unlike `overcooked_ai`'s grid-based design, Cook-CoOp uses continuous 2D movement with AABB (axis-aligned bounding box) collision resolution, enabling physically realistic player–object interactions rather than tile-by-tile stepping.

## Project Structure

```
cook-coop/
├── game/           # Core game engine (entities, movement, collision)
├── game_env/       # Gymnasium environment wrapper and observation system
├── game_ui/        # Pyglet-based visual renderer and keyboard bindings
├── config/         # Parses ASCII layout files into game entities
├── trained/        # Pre-trained PyTorch model checkpoints
├── ppo_train.py    # PPO training script
└── play.py         # Load a trained agent and watch it play
```


## Environment Setup

### Host (virtual env)

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Docker

> Pyglet requires a display and is not installed inside the Docker containers. The UI is not needed for headless training — `ppo_train.py` runs without it.


```bash
# CPU
docker-compose up container-cpu

# GPU (requires NVIDIA GPU and NVIDIA Container Toolkit)
docker-compose up container-gpu
```

## Training

```bash
python ppo_train.py
```

Key hyperparameters (configurable via [tyro](https://brentyi.github.io/tyro/) CLI flags):

| Flag | Default | Description |
|------|---------|-------------|
| `--total-timesteps` | `1_000_000` | Total environment steps |
| `--num-envs` | `64` | Parallel environments |
| `--learning-rate` | `2.5e-5` | Adam LR |
| `--clip-coef` | `0.1` | PPO clip range |
| `--ent-coef` | `0.06` | Entropy coefficient |
| `--cuda` | `True` | Use GPU if available |
| `--seed` | `611302` | Random seed |
| `--trained-model-name` | `None` | Resume from checkpoint |

Checkpoints are saved to `trained/`.

## Playing

Watch a trained agent play interactively:

```bash
python play.py
```

This loads `trained/circuit_room_2__1671437407.pth` and opens a Pyglet window. The agent acts autonomously; human players can also join via keyboard.


## Architecture

### RL Setup

- **Algorithm**: PPO with GAE advantage estimation
- **Network**: CNN (2 conv layers) → 512-dim FC → actor (6 actions) + critic (value)
- **Observation**: In `game_env`'s observation space, each unit in the game is rendered as a 5×5 pseudo-pixels, each pixel take the value of `0`, `0.5` or `1.0`, so an 8×5 layout (e.g. `circuit_room`) produces a 40×25 1-chanel image. See the `game_env/pseudo_pixels_5x5` dir.
- **Action space**: `NOOP`, `UP`, `DOWN`, `LEFT`, `RIGHT`, `INTERACT` (6 discrete actions)
- **Reward**: Shared across all agents (sum of individual rewards per step)

### Key modules

| Module | Role |
|--------|------|
| `game/game.py` | Game tick, player actions, interaction logic |
| `game/collision.py` | AABB collision detection math |
| `game/movement.py` | Continuous movement resolution |
| `game_env/env.py` | `GameEnv`: Gymnasium `Env` wrapper |
| `game_env/observe.py` | Converts game state to pixel observations |
| `game_env/serialize.py` | Flattens dict obs/actions to arrays for batch training |
