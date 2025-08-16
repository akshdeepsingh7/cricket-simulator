import random
import json
import csv
from typing import List, Dict, Tuple, Optional
from datetime import datetime

WICKET_CHANCE_BATTING_SKILL_DIVISOR = 150
MIN_BOWLING_SKILL_FOR_SELECTION = 30
POWERPLAY_RUN_MODIFIER = 1.3
POWERPLAY_WICKET_MODIFIER = 1.2
DEFAULT_OVERS = 20

class Player:
    def __init__(self, name: str, batting_skill: int, bowling_skill: int, role: str):
        self.name = name
        self.batting_skill = max(min(batting_skill, 100), 1)
        self.bowling_skill = max(min(bowling_skill, 100), 1)
        self.role = role
        self.runs = 0
        self.balls_faced = 0
        self.wickets = 0
        self.overs_bowled = 0
        self.runs_conceded = 0

    def get_strike_rate(self) -> float:
        if self.balls_faced == 0:
            return 0.0
        return (self.runs / self.balls_faced) * 100

    def get_bowling_economy(self) -> float:
        if self.overs_bowled == 0:
            return 0.0
        return self.runs_conceded / self.overs_bowled
    
    def to_dict(self) -> Dict:
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
                'strike_rate': self.get_strike_rate(),
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
        self.current_bowler: Optional[Player] = None
        self.bowlers_overs: Dict[str, int] = {}
    
    def get_on_strike_batsman(self) -> Player:
        return self.players[self.current_batting_pair[0]]

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'score': self.score,
            'wickets': self.wickets,
            'players': [player.to_dict() for player in self.players]
        }

class FieldSetting:
    DEFENSIVE = {'wicket_chance_modifier': 0.8, 'run_modifier': 0.7}
    ATTACKING = {'wicket_chance_modifier': 1.3, 'run_modifier': 1.2}
    BALANCED = {'wicket_chance_modifier': 1.0, 'run_modifier': 1.0}

class CricketMatch:
    def __init__(self, team1: Team, team2: Team, overs: int = DEFAULT_OVERS):
        self.team1 = team1
        self.team2 = team2
        self.overs = overs
        self.current_batting_team: Optional[Team] = None
        self.current_bowling_team: Optional[Team] = None
        self.current_over = 0
        self.balls_in_over = 0
        self.is_powerplay = False
        self.powerplay_overs_left = min(6, overs // 4)
        self.field_setting = FieldSetting.BALANCED
        self.target: Optional[int] = None
        self.match_data = {
            'match_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'toss_winner': None,
            'toss_decision': None,
            'first_innings': None,
            'second_innings': None,
            'result': None
        }
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
        toss_winner = random.choice([self.team1, self.team2])
        decision = random.choice(['bat', 'bowl'])
        print(f"\nToss: {toss_winner.name} won the toss and elected to {decision} first.")
        self.match_data['toss_winner'] = toss_winner.name
        self.match_data['toss_decision'] = decision
        return toss_winner, decision

    def _calculate_runs(self, shot: Dict, batting_skill: int, run_modifier: float) -> int:
        min_runs, max_runs = shot['runs']
        skill_multiplier = (batting_skill / 100) * shot['skill_factor'] * run_modifier
        adjusted_max = max(min_runs, int(max_runs * skill_multiplier))
        return random.randint(min_runs, adjusted_max)

    def _calculate_wicket_chance(self, bowl_type: Dict, batsman: Player, bowler: Player, wicket_modifier: float) -> float:
        base_chance = bowl_type['wicket_chance']
        bowler_factor = bowler.bowling_skill / 100
        batsman_factor = 1 - (batsman.batting_skill / WICKET_CHANCE_BATTING_SKILL_DIVISOR)
        return base_chance * bowler_factor * batsman_factor * wicket_modifier

    def play_ball(self):
        if self.current_batting_team.wickets >= 10:
            return False
            
        batsman = self.current_batting_team.get_on_strike_batsman()
        bowler = self.current_bowling_team.current_bowler
        
        wicket_modifier = (POWERPLAY_WICKET_MODIFIER if self.is_powerplay else 1.0) * self.field_setting['wicket_chance_modifier']
        run_modifier = (POWERPLAY_RUN_MODIFIER if self.is_powerplay else 1.0) * self.field_setting['run_modifier']
        
        bowl_type_name = random.choices(list(self.bowling.keys()), weights=[b['prob'] for b in self.bowling.values()])[0]
        bowl_type_data = self.bowling[bowl_type_name]
        
        wicket_chance = self._calculate_wicket_chance(bowl_type_data, batsman, bowler, wicket_modifier)
        if random.random() < wicket_chance:
            self.current_batting_team.wickets += 1
            bowler.wickets += 1
            print(f"OUT! {batsman.name} is dismissed by {bowler.name} ({bowl_type_name})!")
            self.rotate_strike(new_batsman=True)
            return self.current_batting_team.wickets < 10
            
        shot_name = random.choices(list(self.shots.keys()), weights=[s['prob'] for s in self.shots.values()])[0]
        shot_data = self.shots[shot_name]
        runs = self._calculate_runs(shot_data, batsman.batting_skill, run_modifier)
        
        self.current_batting_team.score += runs
        batsman.runs += runs
        batsman.balls_faced += 1
        bowler.runs_conceded += runs
        
        print(f"{self.current_over}.{self.balls_in_over + 1}: {batsman.name} plays {shot_name} to {bowl_type_name} - {runs} runs!")
        
        if runs % 2 == 1:
            self.rotate_strike()
        return True

    def rotate_strike(self, new_batsman=False):
        if new_batsman:
            next_batsman_index = self.current_batting_team.wickets + 1
            if next_batsman_index < 11:
                self.current_batting_team.current_batting_pair[0] = next_batsman_index
        else:
            pair = self.current_batting_team.current_batting_pair
            pair[0], pair[1] = pair[1], pair[0]

    def play_over(self):
        bowler = self.select_bowler()
        if not bowler:
            print("No eligible bowlers available! Innings ends.")
            return False
            
        print(f"\nOver {self.current_over + 1} - Bowler: {bowler.name}")
        self.current_bowling_team.bowlers_overs[bowler.name] = self.current_bowling_team.bowlers_overs.get(bowler.name, 0) + 1
        bowler.overs_bowled += 1
        
        self.balls_in_over = 0
        for _ in range(6):
            if not self.play_ball():
                return False
            self.balls_in_over += 1
            if self.target and self.current_batting_team.score >= self.target:
                return False
        
        self.current_over += 1
        
        if self.is_powerplay:
            self.powerplay_overs_left -= 1
            if self.powerplay_overs_left == 0:
                self.is_powerplay = False
                print("Powerplay has ended!")
        
        self.rotate_strike()
        self.print_score_summary()
        return True

    def select_bowler(self) -> Optional[Player]:
        max_overs_per_bowler = self.overs / 5
        
        primary_candidates = [
            p for p in self.current_bowling_team.players 
            if p.bowling_skill > MIN_BOWLING_SKILL_FOR_SELECTION and 
            self.current_bowling_team.bowlers_overs.get(p.name, 0) < max_overs_per_bowler
        ]
        
        available_bowlers = primary_candidates or [
            p for p in self.current_bowling_team.players 
            if self.current_bowling_team.bowlers_overs.get(p.name, 0) < max_overs_per_bowler
        ]

        if not available_bowlers:
            return None
            
        bowler_weights = [p.bowling_skill for p in available_bowlers]
        selected_bowler = random.choices(available_bowlers, weights=bowler_weights, k=1)[0]
        self.current_bowling_team.current_bowler = selected_bowler
        return selected_bowler
    
    def print_score_summary(self):
        bat_team = self.current_batting_team
        on_strike = bat_team.players[bat_team.current_batting_pair[0]]
        non_strike = bat_team.players[bat_team.current_batting_pair[1]]
        
        print(f"\n--- Score: {bat_team.score}/{bat_team.wickets} | Overs: {self.current_over} ---")
        if self.target:
            runs_needed = self.target - bat_team.score
            balls_left = (self.overs * 6) - (self.current_over * 6)
            if runs_needed > 0 and balls_left > 0:
                print(f"Target: {self.target} | Need {runs_needed} runs from {balls_left} balls")
        print(f"On Strike:  {on_strike.name:<15} {on_strike.runs:<3}* ({on_strike.balls_faced})")
        print(f"Non-Strike: {non_strike.name:<15} {non_strike.runs:<3}* ({non_strike.balls_faced})")

    def play_innings(self, batting_team: Team, bowling_team: Team):
        self.current_batting_team = batting_team
        self.current_bowling_team = bowling_team
        self.current_over = 0
        self.balls_in_over = 0
        self.is_powerplay = True
        self.powerplay_overs_left = min(6, self.overs // 4)
        
        print(f"\n{'='*20}\n Innings of {batting_team.name}\n{'='*20}")
        if self.powerplay_overs_left > 0:
            print(f"Powerplay: First {self.powerplay_overs_left} overs.")
        
        while self.current_over < self.overs:
            if not self.play_over():
                break
        self.print_innings_summary()

    def print_innings_summary(self):
        bat_team = self.current_batting_team
        bowl_team = self.current_bowling_team
        print(f"\n--- End of Innings: {bat_team.name} ---")
        print(f"Final Score: {bat_team.score}/{bat_team.wickets} ({self.current_over}.{self.balls_in_over} overs)")
        
        innings_data = {
            'batting_team_name': bat_team.name,
            'bowling_team_name': bowl_team.name,
            'score': bat_team.score,
            'wickets': bat_team.wickets,
            'overs': f"{self.current_over}.{self.balls_in_over}",
            'batting_stats': [],
            'bowling_stats': []
        }
        
        print("\nBatting Statistics:")
        for player in bat_team.players:
            if player.balls_faced > 0 or (player == bat_team.get_on_strike_batsman() and bat_team.wickets < 10):
                sr = player.get_strike_rate()
                print(f"{player.name:<15}: {player.runs:<3} ({player.balls_faced:<3} balls) SR: {sr:6.2f}")
                innings_data['batting_stats'].append({
                    'name': player.name, 'runs': player.runs, 'balls': player.balls_faced, 'strike_rate': sr
                })
        
        print("\nBowling Statistics:")
        for player in bowl_team.players:
            if player.overs_bowled > 0:
                econ = player.get_bowling_economy()
                print(f"{player.name:<15}: {player.overs_bowled:<2} ov, {player.runs_conceded:<3} runs, {player.wickets:<2} wkts, Econ: {econ:5.2f}")
                innings_data['bowling_stats'].append({
                    'name': player.name, 'wickets': player.wickets, 'runs_conceded': player.runs_conceded, 'overs': player.overs_bowled, 'economy': econ
                })
        
        if not self.match_data['first_innings']:
            self.match_data['first_innings'] = innings_data
        else:
            self.match_data['second_innings'] = innings_data

    def export_match_data(self, format='json'):
        match_id = self.match_data['match_id']
        if format.lower() == 'json':
            filename = f"match_{match_id}.json"
            with open(filename, 'w') as f:
                json.dump(self.match_data, f, indent=4)
            print(f"\nMatch data exported to {filename}")
        
        elif format.lower() == 'csv':
            bat_filename = f"match_{match_id}_batting.csv"
            with open(bat_filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Match ID', 'Innings', 'Team', 'Player', 'Runs', 'Balls', 'Strike Rate'])
                for key in ['first_innings', 'second_innings']:
                    if self.match_data[key]:
                        data = self.match_data[key]
                        for stat in data['batting_stats']:
                            writer.writerow([match_id, key, data['batting_team_name'], stat['name'], stat['runs'], stat['balls'], stat['strike_rate']])
            
            bowl_filename = f"match_{match_id}_bowling.csv"
            with open(bowl_filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Match ID', 'Innings', 'Team', 'Player', 'Wickets', 'Runs Conceded', 'Overs', 'Economy'])
                for key in ['first_innings', 'second_innings']:
                    if self.match_data[key]:
                        data = self.match_data[key]
                        for stat in data['bowling_stats']:
                             writer.writerow([match_id, key, data['bowling_team_name'], stat['name'], stat['wickets'], stat['runs_conceded'], stat['overs'], stat['economy']])
            
            print(f"Match data exported to {bat_filename} and {bowl_filename}")

def create_team(name: str, players_data: List[Dict]) -> Team:
    players = [Player(p['name'], p['batting'], p['bowling'], p['role']) for p in players_data]
    return Team(name, players)

def play_match(team1_data: List[Dict], team2_data: List[Dict], overs: int = DEFAULT_OVERS):
    team1 = create_team("Team Alpha", team1_data)
    team2 = create_team("Team Bravo", team2_data)
    
    match = CricketMatch(team1, team2, overs)
    
    toss_winner, decision = match.conduct_toss()
    
    is_team1_batting_first = (toss_winner is team1 and decision == 'bat') or \
                              (toss_winner is team2 and decision == 'bowl')
    
    batting_first, bowling_first = (team1, team2) if is_team1_batting_first else (team2, team1)
    
    match.play_innings(batting_first, bowling_first)
    match.target = batting_first.score + 1
    print(f"\nTarget for {bowling_first.name} is {match.target} runs from {match.overs} overs.")
    
    match.play_innings(bowling_first, batting_first)
    
    print("\n--- Match Result ---")
    score1, score2 = batting_first.score, bowling_first.score
    
    if score2 >= match.target:
        wickets_left = 10 - bowling_first.wickets
        result = f"{bowling_first.name} won by {wickets_left} wickets!"
    elif score1 > score2:
        run_margin = score1 - score2
        result = f"{batting_first.name} won by {run_margin} runs!"
    else:
        result = "The match is a tie!"
    
    print(result)
    match.match_data['result'] = result
    
    match.export_match_data('json')
    match.export_match_data('csv')

if __name__ == "__main__":
    team_alpha_players = [
        {"name": "A. Sharma", "batting": 85, "bowling": 30, "role": "Batsman"},
        {"name": "B. Kumar", "batting": 80, "bowling": 25, "role": "Batsman"},
        {"name": "C. Singh", "batting": 75, "bowling": 70, "role": "All-rounder"},
        {"name": "D. Mehta", "batting": 70, "bowling": 40, "role": "Batsman"},
        {"name": "E. Patel", "batting": 65, "bowling": 75, "role": "All-rounder"},
        {"name": "F. Khan", "batting": 60, "bowling": 80, "role": "All-rounder"},
        {"name": "G. Iyer", "batting": 50, "bowling": 85, "role": "Bowler"},
        {"name": "H. Reddy", "batting": 45, "bowling": 85, "role": "Bowler"},
        {"name": "I. Gupta", "batting": 40, "bowling": 90, "role": "Bowler"},
        {"name": "J. Das", "batting": 35, "bowling": 90, "role": "Bowler"},
        {"name": "K. Lal", "batting": 30, "bowling": 85, "role": "Bowler"},
    ]
    team_bravo_players = [
        {"name": "L. Rao", "batting": 80, "bowling": 35, "role": "Batsman"},
        {"name": "M. Joshi", "batting": 85, "bowling": 30, "role": "Batsman"},
        {"name": "N. Verma", "batting": 70, "bowling": 75, "role": "All-rounder"},
        {"name": "O. Jain", "batting": 75, "bowling": 35, "role": "Batsman"},
        {"name": "P. Nair", "batting": 60, "bowling": 80, "role": "All-rounder"},
        {"name": "Q. Mishra", "batting": 65, "bowling": 75, "role": "All-rounder"},
        {"name": "R. Saxena", "batting": 45, "bowling": 90, "role": "Bowler"},
        {"name": "S. Tiwari", "batting": 40, "bowling": 85, "role": "Bowler"},
        {"name": "T. Agarwal", "batting": 35, "bowling": 90, "role": "Bowler"},
        {"name": "U. Yadav", "batting": 30, "bowling": 88, "role": "Bowler"},
        {"name": "V. Shah", "batting": 25, "bowling": 85, "role": "Bowler"},
    ]

    print("Starting T10 Cricket Match Simulation!")
    play_match(team_alpha_players, team_bravo_players, overs=10)
