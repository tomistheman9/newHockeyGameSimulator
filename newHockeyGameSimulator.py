import random
import sys
from typing import List, Optional

# -----------------------------
# Player, Line, and Team Classes
# -----------------------------

class Player:
    def __init__(self, jersey_number: int, offensive_value: int, defensive_value: int, 
                 energy: int, position: str):
        self.jersey_number = jersey_number
        self.offensive_value = offensive_value
        self.defensive_value = defensive_value
        self.energy = energy
        self.position = position
        self.injured = False
        self.injury_length = 0  # number of games player will miss
        self.goals_scored = 0
        self.active = False  # track if player is in current line

    def update_energy(self, is_active: bool) -> None:
        if is_active:
            # Active players lose between 1.5 and 6 energy per iteration
            self.energy = max(0, self.energy - random.uniform(1.5, 6))
        else:
            # Inactive players gain 1 energy per iteration (up to max of 25)
            self.energy = min(25, self.energy + 1)

    def __repr__(self):
        return (f"{self.position} #{self.jersey_number} - Off: {self.offensive_value}, "
                f"Def: {self.defensive_value}, Energy: {self.energy:.1f}, "
                f"Goals: {self.goals_scored}, Injured: {self.injured}")

class Line:
    def __init__(self, players: List[Player]):
        self.players = players

    def get_average_energy(self) -> float:
        return sum(p.energy for p in self.players) / len(self.players)
    
    def get_average_offensive_value(self) -> float:
        return sum(p.offensive_value for p in self.players) / len(self.players)
    
    def get_average_defensive_value(self) -> float:
        return sum(p.defensive_value for p in self.players) / len(self.players)
    
    def get_top_offensive_players(self, count: int = 3) -> List[Player]:
        return sorted(self.players, key=lambda p: p.offensive_value, reverse=True)[:count]
    
    def get_lowest_energy_players(self, count: int = 3) -> List[Player]:
        return sorted(self.players, key=lambda p: p.energy)[:count]

class Team:
    def __init__(self, city: str, name: str):
        self.city = city
        self.name = name
        self.players: List[Player] = []      # all skaters
        self.goaltenders: List[Player] = []    # list of goaltenders
        self.lines: List[Line] = []            # list of 4 lines (each with 5 players)
        self.current_line: Optional[Line] = None
        self.active_goaltender: Optional[Player] = None
        
        # Statistics
        self.games_played = 0
        self.regular_wins = 0
        self.overtime_wins = 0
        self.shootout_wins = 0
        self.regular_losses = 0
        self.overtime_losses = 0
        self.shootout_losses = 0
        self.goals_for = 0
        self.goals_against = 0
        self.injuries = 0

    def generate_team(self) -> None:
        # Create 18 skaters
        for _ in range(18):
            self.players.append(Player(
                jersey_number=self._generate_unique_number(),
                offensive_value=random.randint(50, 100),
                defensive_value=random.randint(50, 100),
                energy=random.randint(1, 25),
                position="Skater"
            ))

        # Create 2 goaltenders
        for _ in range(2):
            self.goaltenders.append(Player(
                jersey_number=self._generate_unique_number(),
                offensive_value=0,
                defensive_value=random.randint(60, 90),
                energy=random.randint(1, 25),
                position="Goaltender"
            ))

        # Create 4 lines (each with 5 skaters)
        self._generate_lines()
        
        # Set starting active goaltender (highest defensive value)
        self._initial_update_active_goaltender()
        # Start with the first line
        self.current_line = self.lines[0]

    def _generate_unique_number(self) -> int:
        used_numbers = {p.jersey_number for p in self.players + self.goaltenders}
        while True:
            num = random.randint(1, 99)
            if num not in used_numbers:
                return num

    def _generate_lines(self) -> None:
        self.lines = []
        available_players = self.players.copy()
        # For each line, randomly sample 5 players.
        # Note: a player may appear in more than one line, but not twice in the same line.
        for _ in range(4):
            line_players = random.sample(available_players, 5)
            self.lines.append(Line(line_players))

    def _initial_update_active_goaltender(self) -> None:
        # At team creation, simply choose the non-injured goalie with highest defensive value.
        available = [g for g in self.goaltenders if not g.injured]
        if available:
            self.active_goaltender = max(available, key=lambda g: g.defensive_value)
        else:
            # Generate an emergency goalie if both are injured (should not happen at start)
            new_goalie = Player(
                jersey_number=self._generate_unique_number(),
                offensive_value=0,
                defensive_value=random.randint(50, 80),  # emergency goalie: reduced stats
                energy=25,
                position="Goaltender"
            )
            self.goaltenders.append(new_goalie)
            self.active_goaltender = new_goalie

    def update_active_goaltender(self) -> None:
        """
        The active goaltender should always be the best available (highest defensive value)
        among non-injured goalies whose energy is at least 16.
        If the current active goalie is injured or has energy lower than 16, switch.
        If no valid goalie exists, generate an emergency goalie.
        """
        if (self.active_goaltender is None or 
            self.active_goaltender.injured or 
            self.active_goaltender.energy < 16):
            candidates = [g for g in self.goaltenders if not g.injured and g.energy >= 16]
            if candidates:
                self.active_goaltender = max(candidates, key=lambda g: g.defensive_value)
            else:
                # Generate emergency goalie with defense value between (60-10=50) and (90-10=80)
                new_goalie = Player(
                    jersey_number=self._generate_unique_number(),
                    offensive_value=0,
                    defensive_value=random.randint(50, 80),
                    energy=25,
                    position="Goaltender"
                )
                self.goaltenders.append(new_goalie)
                self.active_goaltender = new_goalie

    def update_line_energy(self) -> None:
        if self.current_line:
            for player in self.players:
                player.update_energy(player in self.current_line.players)

    def select_best_line(self) -> None:
        """
        If the current line’s average energy is lower than 18, select the line 
        (from those with no injured players) that has the highest average energy.
        """
        available_lines = [line for line in self.lines if not any(p.injured for p in line.players)]
        if not available_lines:
            self._generate_lines()
            available_lines = self.lines

        best_line = max(available_lines, key=lambda l: l.get_average_energy())
        if self.current_line != best_line:
            self.current_line = best_line

    def handle_injury(self, period: int) -> bool:
        """
        Injury probability: (Avg Energy of Current Line * 0.5 + period * 5) / 10000.
        If an injury occurs, pick a random player among the 3 with lowest energy in current line,
        mark injured (with injury_length between 10 and 40) and replace him with a new skater.
        """
        if not self.current_line:
            return False

        injury_prob = (self.current_line.get_average_energy() * 0.5 + period * 5) / 10000
        if random.random() <= injury_prob:
            candidates = self.current_line.get_lowest_energy_players(3)
            injured_player = random.choice(candidates)
            injured_player.injured = True
            injured_player.injury_length = random.randint(10, 40)
            self._replace_injured_player(injured_player)
            self.injuries += 1
            return True
        return False

    def _replace_injured_player(self, injured_player: Player) -> None:
        replacement = Player(
            jersey_number=self._generate_unique_number(),
            offensive_value=random.randint(40, 60),  # per instructions for replacement
            defensive_value=random.randint(50, 100),
            energy=random.randint(1, 25),
            position="Skater"
        )
        if injured_player in self.players:
            self.players.remove(injured_player)
            self.players.append(replacement)
        for line in self.lines:
            if injured_player in line.players:
                line.players.remove(injured_player)
                line.players.append(replacement)

    def __repr__(self):
        return f"{self.city} {self.name}"

# -----------------------------
# HockeyGameSimulator Class
# -----------------------------

class HockeyGameSimulator:
    def __init__(self):
        self.teams: List[Team] = []
        self.print_goals = True
        self.print_injuries = True
        self.print_line_changes = False
        self.default_games_to_simulate = 1

    def create_league(self) -> None:
        # List of 32 unique cities and team names (format: City TeamName)
        cities = ["New York", "Toronto", "Montreal", "Chicago", "Boston", "Los Angeles", 
                  "Vancouver", "Calgary", "Edmonton", "Ottawa", "Winnipeg", "San Jose", 
                  "Dallas", "Detroit", "Florida", "Nashville", "Carolina", "Minnesota", 
                  "Buffalo", "Columbus", "Arizona", "Philadelphia", "Pittsburgh", "St. Louis", 
                  "Tampa Bay", "Washington", "Vegas", "Seattle", "Anaheim", "Colorado", 
                  "New Jersey", "Islanders"]
        names = ["Rangers", "Maple Leafs", "Canadiens", "Blackhawks", "Bruins", "Kings", 
                 "Canucks", "Flames", "Oilers", "Senators", "Jets", "Sharks", "Stars", 
                 "Red Wings", "Panthers", "Predators", "Hurricanes", "Wild", "Sabres", 
                 "Blue Jackets", "Coyotes", "Flyers", "Penguins", "Blues", "Lightning", 
                 "Capitals", "Golden Knights", "Kraken", "Ducks", "Avalanche", "Devils", 
                 "Islanders"]
        
        # Shuffle to randomize pairings
        random.shuffle(cities)
        random.shuffle(names)
        
        for city, name in zip(cities, names):
            team = Team(city, name)
            team.generate_team()
            self.teams.append(team)

    def simulate_game(self, team1: Team, team2: Team) -> None:
        print(f"\n=== Starting Game: {team1} vs {team2} ===")
        # Reset current lines to the first line for each team
        team1.current_line = team1.lines[0]
        team2.current_line = team2.lines[0]
        # Ensure starting goaltenders are set
        team1._initial_update_active_goaltender()
        team2._initial_update_active_goaltender()
        
        # Print team parameters (offensive averages, best goalie, injuries)
        print(f"{team1} - Offensive Avg: {team1.current_line.get_average_offensive_value():.1f}, "
              f"Best Goalie Def: {team1.active_goaltender.defensive_value}, Injuries: {team1.injuries}")
        print(f"{team2} - Offensive Avg: {team2.current_line.get_average_offensive_value():.1f}, "
              f"Best Goalie Def: {team2.active_goaltender.defensive_value}, Injuries: {team2.injuries}")
        
        team1_score = team2_score = 0
        game_decision = "regular"

        # Simulate three regular periods
        for period in range(1, 4):
            print(f"\n-- Period {period} --")
            period_scores = self.simulate_period(team1, team2, period)
            team1_score += period_scores[0]
            team2_score += period_scores[1]
            print(f"Score after Period {period}: {team1} {team1_score} - {team2} {team2_score}")

        # Overtime if needed
        if team1_score == team2_score:
            print("\n-- Overtime --")
            ot_scores = self.simulate_period(team1, team2, period=4, overtime=True)
            team1_score += ot_scores[0]
            team2_score += ot_scores[1]
            if team1_score == team2_score:
                print("\n-- Shootout --")
                so_scores = self.simulate_shootout(team1, team2)
                team1_score += so_scores[0]
                team2_score += so_scores[1]
                game_decision = "shootout"
            else:
                game_decision = "overtime"

        # Update team statistics based on game decision
        self._update_game_stats(team1, team2, team1_score, team2_score, game_decision)
        print(f"\n=== Final Score: {team1} {team1_score} - {team2} {team2_score} ===")
        print(f"Game decided in {game_decision}.")

    def simulate_period(self, team1: Team, team2: Team, period: int, overtime: bool = False) -> tuple[int, int]:
        score1 = score2 = 0
        for iteration in range(10):
            # Each iteration: team1 attacks then team2 attacks.
            if self._simulate_team_iteration(team1, team2, period):
                score1 += 1
            if self._simulate_team_iteration(team2, team1, period):
                score2 += 1
            # Update energy for all players in both teams
            team1.update_line_energy()
            team2.update_line_energy()
        return score1, score2

    def _simulate_team_iteration(self, attacking_team: Team, defending_team: Team, period: int) -> bool:
        # First update defending team's active goalie (if injured or low energy)
        defending_team.update_active_goaltender()

        # Check if current line energy is low; if so, change to best available line.
        if attacking_team.current_line.get_average_energy() < 18:
            if self.print_line_changes:
                print(f"{attacking_team}: Line change due to low energy.")
            attacking_team.select_best_line()

        # Simulate injury (no injuries during shootout, so this is for regular/overtime)
        if attacking_team.handle_injury(period) and self.print_injuries:
            print(f"{attacking_team}: A player got injured!")

        # Calculate shot probability:
        # shot_prob = (((Avg Energy) + (Line Offense Avg - Opponent Line Defense Avg)) / 100) * 5
        shot_prob = ((attacking_team.current_line.get_average_energy() +
                     (attacking_team.current_line.get_average_offensive_value() -
                      defending_team.current_line.get_average_defensive_value())) / 100) * 5

        if random.random() <= shot_prob:
            # Select shooter from top 3 offensive players in current line
            shooter = random.choice(attacking_team.current_line.get_top_offensive_players())
            # Calculate goal probability:
            # goal_prob = ((shooter.energy) + (shooter.offensive_value * 0.75 - Opponent Goalie Def)) / 100
            goal_prob = ((shooter.energy + (shooter.offensive_value * 0.75 -
                         defending_team.active_goaltender.defensive_value)) / 100)
            if random.random() <= goal_prob:
                shooter.goals_scored += 1
                if self.print_goals:
                    print(f"GOAL! {attacking_team} scores via player #{shooter.jersey_number}!")
                return True
        return False

    def simulate_shootout(self, team1: Team, team2: Team) -> tuple[int, int]:
        score1 = score2 = 0
        round_num = 1
        # Continue for at least 3 rounds; then sudden death rounds until a winner.
        while True:
            print(f"\nShootout Round {round_num}")
            # Team 1 attempt
            shooter1 = random.choice([p for p in team1.players if p.position == "Skater" and not p.injured])
            # Use defending goalie of team2 (ensure update)
            team2.update_active_goaltender()
            # According to instructions, subtract shooter offensive from goalie defensive.
            if (team2.active_goaltender.defensive_value - shooter1.offensive_value) < 0:
                score1 += 1
                if self.print_goals:
                    print(f"Shootout: {team1} scores via player #{shooter1.jersey_number}!")
            else:
                if self.print_goals:
                    print(f"Shootout: {team1} miss (player #{shooter1.jersey_number}).")
            # Team 2 attempt
            shooter2 = random.choice([p for p in team2.players if p.position == "Skater" and not p.injured])
            team1.update_active_goaltender()
            if (team1.active_goaltender.defensive_value - shooter2.offensive_value) < 0:
                score2 += 1
                if self.print_goals:
                    print(f"Shootout: {team2} scores via player #{shooter2.jersey_number}!")
            else:
                if self.print_goals:
                    print(f"Shootout: {team2} miss (player #{shooter2.jersey_number}).")

            # After at least 3 rounds, if scores are not equal, we have a winner.
            if round_num >= 3 and score1 != score2:
                break
            round_num += 1

        return score1, score2

    def _update_game_stats(self, team1: Team, team2: Team, team1_score: int, 
                           team2_score: int, decision: str) -> None:
        team1.games_played += 1
        team2.games_played += 1
        team1.goals_for += team1_score
        team1.goals_against += team2_score
        team2.goals_for += team2_score
        team2.goals_against += team1_score

        if team1_score > team2_score:
            if decision == "regular":
                team1.regular_wins += 1
                team2.regular_losses += 1
            elif decision == "overtime":
                team1.overtime_wins += 1
                team2.overtime_losses += 1
            elif decision == "shootout":
                team1.shootout_wins += 1
                team2.shootout_losses += 1
        else:
            if decision == "regular":
                team2.regular_wins += 1
                team1.regular_losses += 1
            elif decision == "overtime":
                team2.overtime_wins += 1
                team1.overtime_losses += 1
            elif decision == "shootout":
                team2.shootout_wins += 1
                team1.shootout_losses += 1

    def show_team_stats(self, team: Team) -> None:
        print(f"\n=== {team} Statistics ===")
        print(f"Games Played: {team.games_played}")
        print(f"Regular Wins: {team.regular_wins}")
        print(f"Overtime Wins: {team.overtime_wins}")
        print(f"Shootout Wins: {team.shootout_wins}")
        print(f"Regular Losses: {team.regular_losses}")
        print(f"Overtime Losses: {team.overtime_losses}")
        print(f"Shootout Losses: {team.shootout_losses}")
        print(f"Goals For: {team.goals_for}")
        print(f"Goals Against: {team.goals_against}")
        print(f"Total Injuries: {team.injuries}")

        # Skaters sorted by goals scored
        skaters = [p for p in team.players if p.position == "Skater"]
        skaters_sorted = sorted(skaters, key=lambda p: p.goals_scored, reverse=True)
        print("\nSkaters (sorted by goals scored):")
        for p in skaters_sorted:
            print(f"Player #{p.jersey_number} - Goals: {p.goals_scored}, Offensive Value: {p.offensive_value}")

        # Goaltenders sorted by defensive value
        goalies_sorted = sorted(team.goaltenders, key=lambda g: g.defensive_value, reverse=True)
        print("\nGoaltenders (sorted by defensive value):")
        for g in goalies_sorted:
            print(f"Player #{g.jersey_number} - Defensive Value: {g.defensive_value}")

    # -----------------------------
    # Interactive Menu Methods
    # -----------------------------
    
    def simulate_games_menu(self) -> None:
        inp = input(f"Enter number of games to simulate (default = {self.default_games_to_simulate}): ").strip()
        num_games = int(inp) if inp.isdigit() else self.default_games_to_simulate
        
        print("\nSelect teams for simulation:")
        print("1. Random teams")
        print("2. Choose teams")
        team_choice = input("Your choice (default random): ").strip()
        if team_choice == "2":
            self._list_teams()
            try:
                team1_index = int(input("Select Team 1 (number): ").strip()) - 1
                team2_index = int(input("Select Team 2 (number): ").strip()) - 1
                if team1_index == team2_index:
                    print("Teams must be different. Using random selection instead.")
                    team1, team2 = random.sample(self.teams, 2)
                else:
                    team1 = self.teams[team1_index]
                    team2 = self.teams[team2_index]
            except (ValueError, IndexError):
                print("Invalid input. Using random teams.")
                team1, team2 = random.sample(self.teams, 2)
        else:
            team1, team2 = random.sample(self.teams, 2)
        
        for i in range(num_games):
            print(f"\n=== Simulating Game {i+1} ===")
            self.simulate_game(team1, team2)

    def show_data_menu(self) -> None:
        while True:
            print("\n--- Show Data Menu ---")
            print("1. List all teams")
            print("2. Show team statistics")
            print("3. Back")
            choice = input("Select an option: ").strip()
            if choice == "1":
                self._list_teams()
            elif choice == "2":
                self._list_teams()
                sel = input("Select a team by number: ").strip()
                if sel.isdigit():
                    idx = int(sel) - 1
                    if 0 <= idx < len(self.teams):
                        self.show_team_stats(self.teams[idx])
                    else:
                        print("Invalid selection.")
                else:
                    print("Invalid input.")
            elif choice == "3":
                break
            else:
                print("Invalid option. Try again.")

    def simulation_parameters_menu(self) -> None:
        while True:
            print("\n--- Simulation Parameters Menu ---")
            print(f"1. Toggle Print Goals (currently: {'On' if self.print_goals else 'Off'})")
            print(f"2. Toggle Print Injuries (currently: {'On' if self.print_injuries else 'Off'})")
            print(f"3. Toggle Print Line Changes (currently: {'On' if self.print_line_changes else 'Off'})")
            print("4. Back")
            choice = input("Select an option: ").strip()
            if choice == "1":
                self.print_goals = not self.print_goals
                print(f"Print Goals set to {'On' if self.print_goals else 'Off'}.")
            elif choice == "2":
                self.print_injuries = not self.print_injuries
                print(f"Print Injuries set to {'On' if self.print_injuries else 'Off'}.")
            elif choice == "3":
                self.print_line_changes = not self.print_line_changes
                print(f"Print Line Changes set to {'On' if self.print_line_changes else 'Off'}.")
            elif choice == "4":
                break
            else:
                print("Invalid option. Try again.")

    def reset_data(self) -> None:
        for team in self.teams:
            team.games_played = 0
            team.regular_wins = 0
            team.overtime_wins = 0
            team.shootout_wins = 0
            team.regular_losses = 0
            team.overtime_losses = 0
            team.shootout_losses = 0
            team.goals_for = 0
            team.goals_against = 0
            team.injuries = 0
            for p in team.players:
                p.goals_scored = 0
        print("All team data has been reset.")

    def _list_teams(self) -> None:
        print("\nAvailable Teams:")
        for idx, team in enumerate(self.teams):
            print(f"{idx+1}. {team}")

    def run(self) -> None:
        self.create_league()
        while True:
            print("\n====== Hockey Game Simulator Menu ======")
            print("1. Simulate Game(s)")
            print("2. Show Data")
            print("3. Simulation Parameters")
            print("4. Reset Data")
            print("5. Exit")
            choice = input("Select an option: ").strip()
            if choice == "1":
                self.simulate_games_menu()
            elif choice == "2":
                self.show_data_menu()
            elif choice == "3":
                self.simulation_parameters_menu()
            elif choice == "4":
                self.reset_data()
            elif choice == "5":
                print("Exiting the simulator. Goodbye!")
                sys.exit(0)
            else:
                print("Invalid option. Please try again.")

# -----------------------------
# Main entry point
# -----------------------------
if __name__ == "__main__":
    simulator = HockeyGameSimulator()
    simulator.run()
