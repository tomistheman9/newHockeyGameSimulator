# Hockey Game Simulator

The **Hockey Game Simulator** is a Python-based simulation that creates a dynamic hockey league with teams, players, and game events. It simulates real-game scenarios including regular periods, overtime, shootouts, injuries, line changes, and energy management.

## Features

- **Team Creation:**
  - Generates 32 unique teams in a "City - Team Name" format.
  - Each team includes 20 players (18 Skaters and 2 Goaltenders).
  - Skaters have random jersey numbers (1-99), offensive values (50-100), defensive values (50-100), and energy (1-25).
  - Goaltenders have random jersey numbers (1-99), defensive values (60-90), and energy (1-25).
  - Four lines per team with 5 skaters each (a skater can appear in multiple lines but only once per line).

- **Game Simulation:**
  - Simulates 3 regular periods (each with 10 iterations).
  - If needed, simulates a 10-iteration overtime period.
  - Conducts a shootout if the score remains tied after overtime, with a minimum of 3 rounds and sudden-death rounds as required.
  - Includes mechanics for:
    - **Line management:** Switches lines if the current line’s average energy falls below 18.
    - **Injury simulation:** Based on a probability formula; injured players are replaced immediately.
    - **Goal scoring:** Uses calculated shot and goal probabilities.
    - **Energy management:** Active skaters lose energy while inactive ones gain energy.

- **Interactive Menu:**
  - Simulate one or more games.
  - Display detailed statistics for each team including total games played, wins, losses (by game type), goals for/against, and injury count.
  - Adjust simulation parameters (e.g., toggle prints for goals, injuries, line changes).
  - Reset game data.

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/hockey-game-simulator.git
   cd hockey-game-simulator

2. **Create a Virtual Environment (Optional but recommended):**

3. **Install Requirements:**
If there are any external dependencies listed in `requirements.txt`:
*Note: This project uses only Python's built-in libraries, so no additional packages may be required.*

## Usage

To run the simulator, execute the main script:

You will be greeted with an interactive menu. Follow the prompts to:
- Simulate games.
- View detailed team statistics.
- Adjust simulation parameters.
- Reset data.
- Exit the simulator.

## Project Structure
hockey-game-simulator/ ├── README.md ├── .gitignore ├── hockey_game_simulator.py ├── requirements.txt # (if applicable) └── docs/ # (optional, for additional documentation)

## Contributing

Contributions are welcome! If you'd like to improve the project or add new features:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request detailing your changes.

## Acknowledgements

- Thanks to the instructors and mentors for their guidance.
- Special thanks to all contributors who helped improve this project.
