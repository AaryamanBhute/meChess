import sys
import json
import chess
from game import Game, GameDecoder

import os
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import torch.optim as optim

import os 

def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))

    games = json.load(sys.stdin, cls=GameDecoder)

    device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
    )
    
    print(f"Using {device} device")

    model = nn.Sequential(
            nn.Linear(64 + 1 + 1 + 1, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Sigmoid()
        ).to(device)
    
    criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([10.0], device=device))
    optimizer = optim.SGD(model.parameters(),lr=(1 * (10 ** (-5))))

    games = list(games.values())

    def linearize(board):
        linear_board = [board.piece_at(square) for square in chess.SQUARES]
        for i, piece in enumerate(linear_board):
            if piece == None:
                linear_board[i] = 0
                continue
            linear_board[i] = int(piece.piece_type) * (-1 if piece.color == chess.BLACK else 1)
        return linear_board

    EPOCHS = 1
    GAMES = 10
    # 10 epochs
    for i in range(EPOCHS):
        train_loss = 0.0
        # 10 games per epoch
        for j in range(GAMES):
            game = games[i * GAMES + j]
            for board, move, color in game.getMovesByPlayer('abhute23'):
                linear_board = linearize(board)
                for legal_move in board.legal_moves:
                    y = 1 if legal_move == move else 0
                    legal_move = legal_move.uci()
                                        #color                                           # from                                                               # to
                    X = torch.tensor(linear_board + [1 if color == 'White' else -1] + [(ord(legal_move[0]) - ord('a')) * 10 + int(legal_move[1])] + [(ord(legal_move[2]) - ord('a')) * 10 + int(legal_move[3])], device=device, dtype=torch.float)
                    y = torch.tensor([y], device=device, dtype=torch.float)

                    optimizer.zero_grad()
                    output = model(X)
                    loss = criterion(output,y)
                    loss.backward()

                    optimizer.step()

                    train_loss += y[0] - output[0]
                
            print(f"trained on game {i * GAMES + j}")

        
        print(f'Epoch: {i+1} / {EPOCHS} \t\t\t Training Loss:{train_loss}')

    torch.save(model.state_dict(), f'{dir_path}/model')


if __name__ == "__main__":
    main()