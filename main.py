import csv
import chess
from game import Game, GameEncoder
from collections import defaultdict
from converter.pgn_data import PGNData
import json

def main():
    games = defaultdict(Game)

    with open('output_game_info.csv') as game_info:
        info = csv.reader(game_info)
        for i, row in enumerate(info):
            if i == 0: continue
            id = row[0]
            games[id].white = row[6]
            games[id].black = row[7]

    with open('output_moves.csv') as moves:
        info = csv.reader(moves)
        for i, row in enumerate(info):
            if i == 0: continue
            id = row[0]
            games[id].moves.append(row[5])

    print(json.dumps(games, cls=GameEncoder))
    
    # all games have been built
if __name__ == "__main__":
    main()