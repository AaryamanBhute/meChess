from abc import ABC, abstractmethod
import pygame
import chess
import os
import torch
from torch import nn
import torch.optim as optim

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

class Player(ABC):
    @abstractmethod
    def getMove(): pass

    @abstractmethod
    def reset(): pass



class User(Player):
    def __init__(self) -> None:
        super().__init__()
        self.start = self.end = None # represents the current move being made
    
    def reset(self):
        self.start = self.end = None

    def getMove(self, chess, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if not self.start: self.start = chess.board.get_cell_at(pos)
                elif not self.end: self.end = chess.board.get_cell_at(pos)
        
        return self.start, self.end

class Model(Player):
    def __init__(self, model_path) -> None:
        super().__init__()

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "mps"
            if torch.backends.mps.is_available()
            else "cpu"
        )
        
        self.model = nn.Sequential(
                nn.Linear(64 + 1 + 1 + 1, 128),
                nn.ReLU(),
                nn.Linear(128, 128),
                nn.ReLU(),
                nn.Linear(128, 1),
                nn.Sigmoid()
            ).to(self.device)
        
        self.model.load_state_dict(torch.load(f'{DIR_PATH}/{model_path}'))
        self.model.eval()

        for param in self.model.parameters():
            print(param.data)
    
    def getMove(self, state, events):
        def linearize(board):
            linear_board = [board.piece_at(square) for square in chess.SQUARES]
            for i, piece in enumerate(linear_board):
                if piece == None:
                    linear_board[i] = 0
                    continue
                linear_board[i] = int(piece.piece_type) * (-1 if piece.color == chess.BLACK else 1)
            return linear_board

        move = None
        likelihood = float('-inf')
        for legal_move in state.true_board.legal_moves:
            legal_move = legal_move.uci()
            X = torch.tensor(linearize(state.true_board) + [1 if state.next == state.white else -1] + [(ord(legal_move[0]) - ord('a')) * 10 + int(legal_move[1])] + [(ord(legal_move[2]) - ord('a')) * 10 + int(legal_move[3])], device=self.device, dtype=torch.float)
            y = self.model.forward(X)
            cur_likelihood = y[0].item()

            if cur_likelihood > likelihood:
                likelihood = cur_likelihood
                move = legal_move

        def getCell(id):
            res = None
            for cell in state.board.cells:
                if cell.id == id:
                    res = cell
                    break
            return res
        
        start, end = getCell(chess.parse_square(move[:2])), getCell(chess.parse_square(move[2:]))
        
        return start, end

    def reset(self): pass