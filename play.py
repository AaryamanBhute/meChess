from typing import Any
import pygame
import chess
from players import User
import os 

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

SELECTED_COLOR = (173, 216, 230)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Cell(pygame.sprite.Sprite):
    def __init__(self, id, width=80, height=80) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        self.image = pygame.Surface([width, height])
        self.color = BLACK if (id // 8 + id) % 2 == 0 else WHITE
        self.rect = None
    
    def draw(self, screen, piece, tl, selected=False):
        self.rect = self.image.get_rect(topleft=tl)
        self.image.fill(SELECTED_COLOR if selected else self.color)
        screen.blit(self.image, self.rect)
        if piece: piece.draw(screen, self.rect.center)

    def assignPiece(self, piece):
        res = self.piece
        self.piece = piece
        return res

class Piece(pygame.sprite.Sprite):
    def __init__(self, path) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load(path), (70, 70))

    def draw(self, screen, center):
        screen.blit(self.image, self.image.get_rect(center=center))

class PieceHandler():
    path_string = DIR_PATH + "/images/{color}_{name}_png_128px.png"
    names = {
        chess.PAWN: "pawn", chess.KING: "king", chess.KNIGHT: "knight",
        chess.BISHOP: "bishop", chess.ROOK: "rook", chess.QUEEN: "queen"
    }
    colors = {
        chess.BLACK: 'b', chess.WHITE: 'w'
    }
    def __init__(self) -> None:
        self.sprites = {}
    def getPiece(self, piece):
        name, color = PieceHandler.names[piece.piece_type], PieceHandler.colors[piece.color]
        if (name, color) not in self.sprites:
            self.sprites[(name, color)] = Piece(PieceHandler.path_string.format(color=color, name=name))
        return self.sprites[(name, color)]

class Board():
    # maps piece type to their sprites
    pieces = PieceHandler()

    def __init__(self, top, left, cellwidth=80) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.cells = [Cell(i) for i in range(64)]
        self.top, self.left, self.cellwidth = top, left, cellwidth
        self.board = chess.Board()

    def draw(self, screen, selected=None, reverse=True):
        for i, cell in enumerate(self.cells):
            piece = self.board.piece_at(chess.SQUARES[i])
            if piece: piece = Board.pieces.getPiece(piece)
            if reverse: tl = ((i % 8) * self.cellwidth + self.left, (i // 8) * self.cellwidth + self.top)
            else: tl = ((i % 8) * self.cellwidth + self.left, (7 - (i // 8)) * self.cellwidth + self.top)
            cell.draw(screen, piece, tl, selected == cell)
    
    def update(self, board):
        self.board = board
    
    def get_cell_at(self, pos):
        for i in range(64):
            if self.cells[i].rect.collidepoint(pos): return self.cells[i]
        return None


class Chess:
    def __init__(self, white, black) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode([680, 680])
        self.screen.fill((161, 102, 47)) # background
        self.board = Board(20, 20)
        self.true_board = chess.Board()
        self.white, self.black = white, black
        self.next = self.white

    def run(self) -> None:
        while True:
            start, end = self.next.getMove(self)

            if start and end: # attempted move
                move = f'{chess.SQUARE_NAMES[start.id]}{chess.SQUARE_NAMES[end.id]}'
                try:
                    self.true_board.push_uci(move)
                    self.next = self.black if self.next == self.white else self.white # alternate moves
                    self.board.update(self.true_board)
                    self.next.reset()
                except (chess.IllegalMoveError, chess.InvalidMoveError) :
                    print(f"ERROR MOVE: {move}")
                    self.next.reset()
                    pass
            self.board.draw(self.screen, start if not end else None)
            pygame.display.update()

def main():
    game = Chess(white=User(), black=User())
    game.run()

if __name__ == "__main__":
    main()