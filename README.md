# Cricket Match Simulator 🏏

![Python](https://img.shields.io/badge/python-v3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)
![Last Commit](https://img.shields.io/badge/last%20commit-November%202024-brightgreen)
![Status](https://img.shields.io/badge/status-stable-brightgreen)
![CodeSize](https://img.shields.io/badge/code%20size-20%20KB-blue)

A sophisticated cricket match simulator built in Python that brings the excitement of cricket to your terminal. Experience realistic match progression, detailed player statistics, and dynamic gameplay mechanics.

## 📋 Features

![Features](https://img.shields.io/badge/features-comprehensive-success)

- 🎯 Complete match simulation with two innings
- 📊 Realistic player stats and performance modeling
- 🏟️ Multiple field setting options
- ⚡ Powerplay implementation
- 📝 Ball-by-ball commentary
- 💾 Match statistics export (JSON/CSV)
- 🎮 Various batting shots and bowling styles

## 🚀 Quick Start

```python
from cricket_simulator import play_match

# Define team data
team1_data = [
    {"name": "Player1", "batting": 85, "bowling": 30, "role": "Batsman"},
    # Add more players...
]

# Start match
play_match(team1_data, team2_data, overs=20)
```

## 🏗️ Installation

![Setup](https://img.shields.io/badge/setup-easy-success)

```bash
git clone https://github.com/akshdeepsingh7/cricket-simulator.git
cd cricket-simulator
python main.py
```

## 🎮 Game Mechanics

### Player Stats
![Stats](https://img.shields.io/badge/player%20stats-dynamic-blue)

- Batting Skill: `1-100`
- Bowling Skill: `1-100`
- Roles: 
  - `Batsman`
  - `Bowler`
  - `All-rounder`

### Field Settings
![Settings](https://img.shields.io/badge/field%20settings-customizable-yellowgreen)

- 🛡️ Defensive
- ⚔️ Attacking
- ⚖️ Balanced

## 📊 Data Export

![Export](https://img.shields.io/badge/export-JSON%20%7C%20CSV-orange)

### JSON Format
```json
{
    "match_id": "20241129_121530",
    "toss_winner": "Team 1",
    "result": "Team 1 wins by 25 runs"
}
```

### CSV Format
```csv
Match ID,Innings,Team,Player,Runs,Balls,Strike Rate
20241129_121530,first_innings,Team 1,Player1,45,30,150.0
```

## 🎯 Shot Types

![Shots](https://img.shields.io/badge/shot%20types-7-blue)

- 🛡️ Defensive Block
- 🚀 Cover Drive
- ⚡ Square Cut
- 💥 Pull Shot
- ➡️ Straight Drive
- 🌟 Lofted Shot
- 📐 Edge

## 🎳 Bowling Types

![Bowling](https://img.shields.io/badge/bowling%20types-5-blue)

- ⚡ Fast Pace
- 🎯 Yorker
- 💨 Bouncer
- 🌀 Off Spin
- 🔄 Leg Spin

## 🛠️ Requirements

![Requirements](https://img.shields.io/badge/dependencies-none-success)

- Python 3.6+
- Standard Library Only

## 📝 License

![License](https://img.shields.io/badge/license-MIT-green.svg)

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributing

![Contributors](https://img.shields.io/badge/contributors-welcome-brightgreen)

1. Fork the Project
2. Create your Feature Branch
3. Commit your Changes
4. Push to the Branch
5. Open a Pull Request

## 📊 Stats

![Issues](https://img.shields.io/badge/issues-0%20open-brightgreen)
![PRs](https://img.shields.io/badge/pull%20requests-welcome-brightgreen)
![Activity](https://img.shields.io/badge/activity-high-brightgreen)

## ✨ Acknowledgments

- 🏏 International Cricket Council for game rules
- 🎮 Cricket gaming community

---
[![Made with Python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![GitHub issues](https://img.shields.io/badge/GitHub-Issues-red)](https://github.com/akshdeepsingh7/cricket-simulator/issues)
[![GitHub stars](https://img.shields.io/badge/GitHub-Stars-yellow)](https://github.com/akshdeepsingh7/cricket-simulator/stargazers)
