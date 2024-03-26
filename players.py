from abc import ABC, abstractmethod
import pygame

class Player(ABC):
    @abstractmethod
    def getMove(board):
        pass

class User(Player):
    def __init__(self) -> None:
        super().__init__()
        self.start = self.end = None # represents the current move being made
    
    def reset(self):
        self.start = self.end = None

    def getMove(self, chess):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            elif event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if not self.start: self.start = chess.board.get_cell_at(pos)
                elif not self.end: self.end = chess.board.get_cell_at(pos)
        
        return self.start, self.end