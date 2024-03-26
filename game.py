import chess
from json import JSONEncoder, JSONDecoder

class GameEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Game):
            return o.__dict__ | {'__class__': 'Game'}
        return super().default(o)

class GameDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if '__class__' in dct and dct['__class__'] == 'Game':
            return Game(dct['white'], dct['black'], dct['moves'])
        return dct
    
class Game:
    def __init__(self, w=None, b=None, m=None) -> None:
        self.white, self.black, self.moves = w, b, m if m else []
    
    def getMovesByColor(self, color="White"):
        board = chess.Board()

        if not self.moves: return
        if color == "Black": board.push_uci(self.moves[0])

        # board state is that of the game before moves[i] is made, moves[i] is the move made by the target color
        for i in range(0 if color == "White" else 1, len(self.moves), 2):
            yield board, chess.Move.from_uci(self.moves[i])
            board.push_uci(self.moves[i])
            if i + 1 < len(self.moves): board.push_uci(self.moves[i + 1])
    
    def getMovesByPlayer(self, player):
        if self.white == player:
            for board, move in self.getMovesByColor("White"):
                yield board, move, "White"
        elif self.black == player:
            for board, move in self.getMovesByColor("Black"):
                yield board, move, "Black"