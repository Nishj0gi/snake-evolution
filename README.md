# 🐍 Snake Evolution

A modern take on the classic Snake game with unique power-ups, multiple game modes, and polished visual effects.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/pygame-2.5.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

### 🎮 Three Game Modes
- **Classic Mode**: Traditional snake gameplay with progressive difficulty
- **Time Attack**: Race against the clock to get the highest score in 60 seconds
- **Survival Mode**: Avoid obstacles that spawn as you grow

### ⚡ Power-Up System
- **Speed Boost** (Blue): Temporarily increases movement speed
- **Shield** (Yellow): Protects you from one collision
- **Score Multiplier** (Purple): Doubles points for a limited time
- **Ghost Mode** (Orange): Pass through walls once - wraps around the screen

### 🎨 Visual Polish
- Smooth particle effects when eating food or collecting power-ups
- Transparency effects for ghost mode
- Shield visual indicator
- Grid-based clean UI

### 💾 Progression System
- Persistent high scores for each game mode (saved to `high_scores.json`)
- Progressive difficulty in Classic mode
- Dynamic obstacle spawning in Survival mode

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/snake-evolution.git
cd snake-evolution
```

2. Install dependencies:
```bash
pip install pygame
```

Or use requirements.txt:
```bash
pip install -r requirements.txt
```

## 🎯 How to Play

### Starting the Game
```bash
python snake_evolution.py
```

### Controls
- **Arrow Keys** or **WASD**: Move the snake
- **1**: Start Classic Mode
- **2**: Start Time Attack Mode
- **3**: Start Survival Mode
- **ESC**: Return to menu (during game)
- **R**: Restart (on game over screen)
- **SPACE**: Return to menu (on game over screen)
- **Q**: Quit game (from main menu)

### Objective
- Eat red food to grow and score points
- Collect power-ups (colored squares with white borders) for special abilities
- Avoid colliding with walls, obstacles (in Survival mode), or yourself
- Beat your high score!

## 🏗️ Project Structure

```
snake-evolution/
├── snake_evolution.py    # Main game file
├── requirements.txt      # Python dependencies
├── high_scores.json     # Automatically generated high score storage
└── README.md            # This file
```

## 🎓 Technical Highlights

### Object-Oriented Design
- Clean separation of concerns with classes for `Snake`, `PowerUp`, `Particle`, `Obstacle`
- Enum-based direction and power-up type management

### Game Systems
- **State Management**: Menu, game modes, and game over states
- **Collision Detection**: Snake body, walls, food, power-ups, and obstacles
- **Particle System**: Dynamic visual effects with lifecycle management
- **Timer System**: Power-up duration tracking and time-based game modes

### Advanced Features
- Progressive difficulty scaling
- Persistent data storage with JSON
- Frame-rate independent movement
- Alpha blending for visual effects

## 🎨 Customization

You can easily customize the game by modifying these constants in `snake_evolution.py`:

```python
# Screen size
WIDTH, HEIGHT = 800, 600

# Grid size (smaller = more difficult)
GRID_SIZE = 20

# Base speed (moves per second)
base_speed = 8

# Power-up duration (frames)
duration = 300
```

## 📝 Future Enhancements

Potential features to add:
- [ ] Sound effects and background music
- [ ] Additional power-ups (slow-mo, magnet, etc.)
- [ ] Multiplayer mode
- [ ] Custom skins/themes
- [ ] Achievements system
- [ ] Online leaderboards
- [ ] Level system with increasing complexity

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📄 License

This project is licensed under the MIT License - feel free to use it for your portfolio or personal projects.

## 👤 Author

Nishmitha

- GitHub: [Nishj0gi](https://github.com/Nishj0gi)

## 🙏 Acknowledgments

- Built with [Pygame](https://www.pygame.org/)
- Inspired by the classic Snake game
- Created as a portfolio project to demonstrate game development skills

---

⭐ If you found this project interesting, please consider giving it a star!
