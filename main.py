import random
import json
import csv
from typing import List, Dict, Tuple
from datetime import datetime

class Player:
    def __init__(self, name: str, batting_skill: int, bowling_skill: int, role: str):
        self.name = name
        self.batting_skill = max(min(batting_skill, 100), 1)  # Ensure skill is between 1-100
        self.bowling_skill = max(min(bowling_skill, 100), 1)
        self.role = role
        
        # Match statistics
        self.runs = 0
        self.balls_faced = 0
        self.wickets = 0
        self.overs_bowled = 0
        self.runs_conceded = 0

    def get_batting_average(self):
        return self.runs if self.balls_faced == 0 else (self.runs / self.balls_faced) * 100

    def get_bowling_economy(self):
        if self.overs_bowled == 0:
            return 0
        return (self.runs_conceded / (self.overs_bowled * 6))
    
    def to_dict(self):
        return {
            'name': self.name,
            'role': self.role,
            'batting_skill': self.batting_skill,
            'bowling_skill': self.bowling_skill,
            'match_stats': {
                'runs': self.runs,
                'balls_faced': self.balls_faced,
                'wickets': self.wickets,
                'overs_bowled': self.overs_bowled,
                'runs_conceded': self.runs_conceded,
                'batting_average': self.get_batting_average(),
                'bowling_economy': self.get_bowling_economy()
            }
        }

class Team:
    def __init__(self, name: str, players: List[Player]):
        self.name = name
        self.players = players
        self.score = 0
        self.wickets = 0
        self.current_batting_pair = [0, 1]
        self.current_bowler = None
        self.bowlers_overs = {}
    
    def to_dict(self):
        return {
            'name': self.name,
            'score': self.score,
            'wickets': self.wickets,
            'players': [player.to_dict() for player in self.players]
        }

# FieldSetting class remains unchanged
class FieldSetting:
    DEFENSIVE = {
        'slip': 1,
        'deep_fielders': 5,
        'inner_circle': 3,
        'wicket_chance_modifier': 0.8,
        'run_modifier': 0.7
    }
    ATTACKING = {
        'slip': 3,
        'deep_fielders': 2,
        'inner_circle': 4,
        'wicket_chance_modifier': 1.3,
        'run_modifier': 1.2
    }
    BALANCED = {
        'slip': 2,
        'deep_fielders': 3,
        'inner_circle': 4,
        'wicket_chance_modifier': 1.0,
        'run_modifier': 1.0
    }

class CricketMatch:
    def __init__(self, team1: Team, team2: Team, overs: int = 20):
        self.team1 = team1
        self.team2 = team2
        self.overs = overs
        self.current_batting_team = None
        self.current_bowling_team = None
        self.current_over = 0
        self.balls_in_over = 0
        self.is_powerplay = False
        self.powerplay_overs_left = min(6, overs // 3)
        self.field_setting = FieldSetting.BALANCED
        self.target = None
        self.match_data = {
            'match_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'toss_winner': None,
            'toss_decision': None,
            'first_innings': None,
            'second_innings': None,
            'result': None
        }
        
        # Shots and bowling dictionaries remain unchanged
        self.shots = {
            'Defensive Block': {'prob': 0.25, 'runs': (0, 1), 'skill_factor': 0.5},
            'Cover Drive': {'prob': 0.15, 'runs': (1, 4), 'skill_factor': 0.8},
            'Square Cut': {'prob': 0.15, 'runs': (1, 4), 'skill_factor': 0.8},
            'Pull Shot': {'prob': 0.12, 'runs': (2, 4), 'skill_factor': 0.9},
            'Straight Drive': {'prob': 0.13, 'runs': (1, 4), 'skill_factor': 0.8},
            'Lofted Shot': {'prob': 0.10, 'runs': (0, 6), 'skill_factor': 1.0},
            'Edge': {'prob': 0.10, 'runs': (0, 2), 'skill_factor': 0.3}
        }
        
        self.bowling = {
            'Fast Pace': {'prob': 0.30, 'wicket_chance': 0.15},
            'Yorker': {'prob': 0.15, 'wicket_chance': 0.25},
            'Bouncer': {'prob': 0.15, 'wicket_chance': 0.20},
            'Off Spin': {'prob': 0.20, 'wicket_chance': 0.18},
            'Leg Spin': {'prob': 0.20, 'wicket_chance': 0.22}
        }

    def conduct_toss(self) -> Tuple[Team, str]:
        """Conduct the toss and return the winning team and their decision"""
        toss_winner = random.choice([self.team1, self.team2])
        decision = random.choice(['bat', 'bowl'])
        
        print(f"\nToss: {toss_winner.name} won the toss and elected to {decision} first")
        
        self.match_data['toss_winner'] = toss_winner.name
        self.match_data['toss_decision'] = decision
        
        return toss_winner, decision

    def calculate_runs(self, min_runs: int, max_runs: int, batting_skill: int, shot_skill_factor: float, run_modifier: float) -> int:
        # Calculate adjusted max runs based on skills and modifiers
        skill_multiplier = (batting_skill / 100) * shot_skill_factor * run_modifier
        adjusted_max = max(min_runs, int(max_runs * skill_multiplier))
        return random.randint(min_runs, adjusted_max)

    def play_ball(self):
        if self.current_batting_team.wickets >= 10:
            return False
            
        batting_player = self.current_batting_team.players[
            self.current_batting_team.current_batting_pair[0]
        ]
        bowler = self.current_bowling_team.current_bowler
        
        # Apply powerplay and field setting modifiers
        wicket_modifier = (1.2 if self.is_powerplay else 1.0) * self.field_setting['wicket_chance_modifier']
        run_modifier = (1.3 if self.is_powerplay else 1.0) * self.field_setting['run_modifier']
        
        # Select bowling type
        bowl_type = random.choices(
            list(self.bowling.keys()), 
            weights=[b['prob'] for b in self.bowling.values()]
        )[0]
        
        # Calculate wicket probability
        wicket_chance = (
            self.bowling[bowl_type]['wicket_chance'] * 
            (bowler.bowling_skill / 100) * 
            (1 - batting_player.batting_skill / 150) *
            wicket_modifier
        )
        
        # Check for wicket
        if random.random() < wicket_chance:
            self.current_batting_team.wickets += 1
            bowler.wickets += 1
            print(f"OUT! {batting_player.name} is dismissed by {bowler.name} ({bowl_type})!")
            self.rotate_strike(new_batsman=True)
            return self.current_batting_team.wickets < 10
            
        # Select batting shot
        shot = random.choices(
            list(self.shots.keys()),
            weights=[s['prob'] for s in self.shots.values()]
        )[0]
        
        # Calculate runs using the new method
        min_runs, max_runs = self.shots[shot]['runs']
        shot_skill_factor = self.shots[shot]['skill_factor']
        runs = self.calculate_runs(min_runs, max_runs, batting_player.batting_skill, shot_skill_factor, run_modifier)
        
        # Update statistics
        self.current_batting_team.score += runs
        batting_player.runs += runs
        batting_player.balls_faced += 1
        bowler.runs_conceded += runs
        
        print(f"{batting_player.name} plays {shot} to {bowl_type} - {runs} runs!")
        
        if runs % 2 == 1:
            self.rotate_strike()
            
        return True

    def rotate_strike(self, new_batsman=False):
        if new_batsman:
            next_batsman = self.current_batting_team.wickets + 1
            if next_batsman < 11:
                self.current_batting_team.current_batting_pair[0] = next_batsman
        else:
            self.current_batting_team.current_batting_pair[0], self.current_batting_team.current_batting_pair[1] = \
                self.current_batting_team.current_batting_pair[1], self.current_batting_team.current_batting_pair[0]

    def play_over(self):
        bowler = self.select_bowler()
        if not bowler:
            print("No eligible bowlers available!")
            return False
            
        print(f"\nOver {self.current_over + 1} - Bowler: {bowler.name}")
        self.current_bowling_team.bowlers_overs[bowler.name] = \
            self.current_bowling_team.bowlers_overs.get(bowler.name, 0) + 1
        bowler.overs_bowled += 1
        
        for _ in range(6):
            if not self.play_ball():
                return False
            self.balls_in_over += 1
            
            if self.target and self.current_batting_team.score >= self.target:
                return False
        
        self.balls_in_over = 0
        self.current_over += 1
        
        if self.is_powerplay and self.powerplay_overs_left > 0:
            self.powerplay_overs_left -= 1
            if self.powerplay_overs_left == 0:
                self.is_powerplay = False
                print("Powerplay ended!")
        
        self.rotate_strike()
        self.print_score_summary()
        return True

    def select_bowler(self):
        available_bowlers = [
            p for p in self.current_bowling_team.players 
            if p.bowling_skill > 30 and 
            self.current_bowling_team.bowlers_overs.get(p.name, 0) < self.overs / 5
        ]
        if not available_bowlers:
            return None
        bowler = random.choice(available_bowlers)
        self.current_bowling_team.current_bowler = bowler
        return bowler
    
    def print_score_summary(self):
        batting_player = self.current_batting_team.players[self.current_batting_team.current_batting_pair[0]]
        partner = self.current_batting_team.players[self.current_batting_team.current_batting_pair[1]]
        
        print(f"\nScore: {self.current_batting_team.score}/{self.current_batting_team.wickets}")
        print(f"Overs: {self.current_over}.{self.balls_in_over}")
        if self.target:
            runs_needed = self.target - self.current_batting_team.score
            balls_left = (self.overs * 6) - (self.current_over * 6 + self.balls_in_over)
            print(f"Need {runs_needed} runs from {balls_left} balls")
        print(f"Batting: {batting_player.name} {batting_player.runs}* ({batting_player.balls_faced})")
        print(f"         {partner.name} {partner.runs}* ({partner.balls_faced})")

    def play_innings(self, batting_team: Team, bowling_team: Team):
        self.current_batting_team = batting_team
        self.current_bowling_team = bowling_team
        self.current_over = 0
        self.balls_in_over = 0
        self.is_powerplay = True
        self.powerplay_overs_left = min(6, self.overs // 3)
        
        print(f"\nInnings starting - {batting_team.name} batting")
        print("Powerplay in progress!")
        
        while self.current_over < self.overs:
            if not self.play_over():
                break
        
        self.print_innings_summary()

    def print_innings_summary(self):
        print(f"\n{self.current_batting_team.name} Innings Summary:")
        print(f"Final Score: {self.current_batting_team.score}/{self.current_batting_team.wickets}")
        print(f"Overs: {self.current_over}.{self.balls_in_over}")
        
        innings_data = {
            'team': self.current_batting_team.name,
            'score': self.current_batting_team.score,
            'wickets': self.current_batting_team.wickets,
            'overs': f"{self.current_over}.{self.balls_in_over}",
            'batting_stats': [],
            'bowling_stats': []
        }
        
        print("\nBatting Statistics:")
        for player in self.current_batting_team.players:
            if player.balls_faced > 0:
                sr = (player.runs / player.balls_faced) * 100
                print(f"{player.name}: {player.runs} runs ({player.balls_faced} balls), SR: {sr:.2f}")
                innings_data['batting_stats'].append({
                    'name': player.name,
                    'runs': player.runs,
                    'balls': player.balls_faced,
                    'strike_rate': sr
                })
        
        print("\nBowling Statistics:")
        for player in self.current_bowling_team.players:
            if player.overs_bowled > 0:
                economy = player.get_bowling_economy()
                print(f"{player.name}: {player.wickets}/{player.runs_conceded} ({player.overs_bowled} overs), Econ: {economy:.2f}")
                innings_data['bowling_stats'].append({
                    'name': player.name,
                    'wickets': player.wickets,
                    'runs_conceded': player.runs_conceded,
                    'overs': player.overs_bowled,
                    'economy': economy
                })
        
        if not self.match_data['first_innings']:
            self.match_data['first_innings'] = innings_data
        else:
            self.match_data['second_innings'] = innings_data

    def export_match_data(self, format='json'):
        """Export match data in the specified format"""
        if format.lower() == 'json':
            filename = f"match_{self.match_data['match_id']}.json"
            with open(filename, 'w') as f:
                json.dump(self.match_data, f, indent=2)
            print(f"\nMatch data exported to {filename}")
        
        elif format.lower() == 'csv':
            # Export batting statistics
            bat_filename = f"match_{self.match_data['match_id']}_batting.csv"
            with open(bat_filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Match ID', 'Innings', 'Team', 'Player', 'Runs', 'Balls', 'Strike Rate'])
                
                for innings in ['first_innings', 'second_innings']:
                    if self.match_data[innings]:
                        for stat in self.match_data[innings]['batting_stats']:
                            writer.writerow([
                                self.match_data['match_id'],
                                innings,
                                self.match_data[innings]['team'],
                                stat['name'],
                                stat['runs'],
                                stat['balls'],
                                stat['strike_rate']
                            ])
            
            # Export bowling statistics
            bowl_filename = f"match_{self.match_data['match_id']}_bowling.csv"
            with open(bowl_filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Match ID', 'Innings', 'Team', 'Player', 'Wickets', 'Runs Conceded', 'Overs', 'Economy'])
                
                for innings in ['first_innings', 'second_innings']:
                    if self.match_data[innings]:
                        for stat in self.match_data[innings]['bowling_stats']:
                            writer.writerow([
                                self.match_data['match_id'],
                                innings,
                                self.match_data[innings]['team'],
                                stat['name'],
                                stat['wickets'],
                                stat['runs_conceded'],
                                stat['overs'],
                                stat['economy']
                            ])
            
            print(f"\nMatch data exported to {bat_filename} and {bowl_filename}")

def create_player(name: str, batting: int, bowling: int, role: str) -> Player:
    return Player(name, batting, bowling, role)

def create_team(name: str, players: List[Dict]) -> Team:
    return Team(name, [
        create_player(p['name'], p['batting'], p['bowling'], p['role'])
        for p in players
    ])

def play_match(team1_data: List[Dict], team2_data: List[Dict], overs: int = 20):
    team1 = create_team("Team 1", team1_data)
    team2 = create_team("Team 2", team2_data)
    
    match = CricketMatch(team1, team2, overs)
    
    # Conduct toss
    toss_winner, decision = match.conduct_toss()
    
    # Determine batting order based on toss
    if decision == 'bat':
        batting_first = toss_winner
        bowling_first = team2 if toss_winner == team1 else team1
    else:
        bowling_first = toss_winner
        batting_first = team2 if toss_winner == team1 else team1
    
    # First innings
    print(f"\n{batting_first.name} will bat first")
    match.play_innings(batting_first, bowling_first)
    match.target = batting_first.score + 1
    
    print(f"\nTarget: {match.target} runs from {match.overs} overs")
    
    # Second innings
    match.play_innings(bowling_first, batting_first)
    
    # Determine result
    print("\nMatch Result:")
    if bowling_first.score >= match.target:
        result = f"{bowling_first.name} wins by {10 - bowling_first.wickets} wickets!"
    elif bowling_first.score < match.target - 1:
        result = f"{batting_first.name} wins by {match.target - bowling_first.score - 1} runs!"
    else:
        result = "Match tied!"
    
    print(result)
    match.match_data['result'] = result
    
    # Export match data
    match.export_match_data('json')
    match.export_match_data('csv')

if __name__ == "__main__":
    team1_data = [
        {"name": "Player1", "batting": 85, "bowling": 30, "role": "Batsman"},
        {"name": "Player2", "batting": 80, "bowling": 25, "role": "Batsman"},
        {"name": "Player3", "batting": 75, "bowling": 70, "role": "All-rounder"},
        {"name": "Player4", "batting": 70, "bowling": 40, "role": "Batsman"},
        {"name": "Player5", "batting": 65, "bowling": 75, "role": "All-rounder"},
        {"name": "Player6", "batting": 60, "bowling": 80, "role": "All-rounder"},
        {"name": "Player7", "batting": 50, "bowling": 85, "role": "Bowler"},
        {"name": "Player8", "batting": 45, "bowling": 85, "role": "Bowler"},
        {"name": "Player9", "batting": 40, "bowling": 90, "role": "Bowler"},
        {"name": "Player10", "batting": 35, "bowling": 90, "role": "Bowler"},
        {"name": "Player11", "batting": 30, "bowling": 85, "role": "Bowler"},
    ]
    
    team2_data = [
        {"name": "Opposition1", "batting": 80, "bowling": 35, "role": "Batsman"},
        {"name": "Opposition2", "batting": 85, "bowling": 30, "role": "Batsman"},
        {"name": "Opposition3", "batting": 70, "bowling": 75, "role": "All-rounder"},
        {"name": "Opposition4", "batting": 75, "bowling": 35, "role": "Batsman"},
        {"name": "Opposition5", "batting": 60, "bowling": 80, "role": "All-rounder"},
        {"name": "Opposition6", "batting": 65, "bowling": 75, "role": "All-rounder"},
        {"name": "Opposition7", "batting": 45, "bowling": 90, "role": "Bowler"},
        {"name": "Opposition8", "batting": 40, "bowling": 85, "role": "Bowler"},
        {"name": "Opposition9", "batting": 35, "bowling": 90, "role": "Bowler"},
        {"name": "Opposition10", "batting": 30, "bowling": 88, "role": "Bowler"},
        {"name": "Opposition11", "batting": 25, "bowling": 85, "role": "Bowler"},
    ]

    print("Starting Cricket Match!")
    play_match(team1_data, team2_data, overs=10)
