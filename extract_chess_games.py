import re

# Configuration
input_file = "lichess_db_standard_rated_2014-10.pgn"
output_file = "filtered_games_with_elo.txt"
max_games = 100000  # Max games to extract

# Elo Filter Settings
min_elo = 1000     # Minimum Elo for both players (set to 0 to disable)
max_elo = 1400     # Maximum Elo for both players (set to 9999 to disable)

# Patterns
white_elo_pattern = re.compile(r'\[WhiteElo "(\d+)"\]')
black_elo_pattern = re.compile(r'\[BlackElo "(\d+)"\]')
move_start_pattern = re.compile(r'^\d+\.')
eval_pattern = re.compile(r'\{[^}]*\}')

def clean_move_text(move_text):
    """Standardize move formatting"""
    move_text = eval_pattern.sub('', move_text)
    move_text = re.sub(r'\d+\.\.\.', '', move_text)
    move_text = re.sub(r'[?!]+', '', move_text)
    return ' '.join(move_text.split())

def passes_elo_filter(white, black):
    """Check if both players meet Elo requirements"""
    return (min_elo <= white <= max_elo) and (min_elo <= black <= max_elo)

game_count = 0
filtered_count = 0

with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
    white_elo = None
    black_elo = None
    collecting_moves = False
    game_moves = []

    for line in infile:
        line = line.strip()
        
        # Detect Elo ratings
        if white_match := white_elo_pattern.match(line):
            white_elo = int(white_match.group(1))
        elif black_match := black_elo_pattern.match(line):
            black_elo = int(black_match.group(1))

        # Detect moves
        if move_start_pattern.match(line):
            collecting_moves = True
            game_moves.append(clean_move_text(line))
        elif collecting_moves:
            if line == "":  # End of game
                if all([white_elo, black_elo]):
                    if passes_elo_filter(white_elo, black_elo):
                        outfile.write(f"White Elo: {white_elo}, Black Elo: {black_elo}\n")
                        outfile.write(" ".join(game_moves) + "\n\n")
                        filtered_count += 1

                    game_count += 1
                    if game_count >= max_games:
                        break

                # Reset for next game
                white_elo = black_elo = None
                collecting_moves = False
                game_moves = []
            else:
                if clean_line := clean_move_text(line):
                    game_moves.append(clean_line)

print(f"""Processed {game_count} games
Saved {filtered_count} games where both players are {min_elo}-{max_elo} Elo
Output file: {output_file}""")
