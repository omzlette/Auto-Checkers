import game
import numpy as np
import random

class Player(game.Game):
    def __init__(self):
        super().__init__()
        self.row = None
        self.col = None
        self.selected_turn = None # manually select turn

    def select_move(self, row, col):
        if (row, col) in self.selected_piece_moves:
            self.to_move = (row, col)
            self.to_capture = (self.capture_pos[self.selected_piece_moves.index((row, col))]) if self.capture_pos else None
        else:
            self.to_move = None

    def select_piece(self, row, col, board):
        moves = self.get_moves(row, col, board)
        if moves and board[row][col][0] == self.turn:
            self.selected_piece_pos = (row, col)
            self.selected_piece_moves = moves

class User(Player):
    def __init__(self):
        super().__init__()

    def input_turn(self):
        turn = input('Enter your turn (b or w): ')
        if turn == 'b' or turn == 'w':
            return turn
        print('Invalid input. Try again.')
        return self.input_turn()

    def input_piece(self):
        rowcol_str = input('Enter row and column of piece to move (Ex. A1 or a1): ')
        row, col = ord(rowcol_str[0].lower())-97, int(rowcol_str[1])-1
        if 0 <= row <= 7 and 0 <= col <= 7:
            return (row, col)
        print('Invalid input. Try again.')
        return self.input_piece()

    def input_move(self):
        rowcol_str = input('Enter row and column of move (Ex. A1 or a1): ')
        row, col = ord(rowcol_str[0].lower())-97, int(rowcol_str[1])-1
        if 0 <= row <= 7 and 0 <= col <= 7:
            return (row, col)
        print('Invalid input. Try again.')
        return self.input_move()
    
    def select_turn(self, turn):
        self.selected_turn = turn

class RandomAI(Player):
    def __init__(self):
        super().__init__()

    def make_move(self, board):
        pieces = []
        for row in range(8):
            for col in range(8):
                if board[row][col][0] == self.turn:
                    pieces.append((row, col))
        piece = random.choice(pieces)
        moves = self.get_moves(piece[0], piece[1], board)
        if moves:
            move = random.choice(moves)
            self.select_piece(piece[0], piece[1], board)
            self.select_move(move[0], move[1])
        else:
            self.make_move(board)

class GreedyAI(Player):
    def __init__(self):
        super().__init__()

class AlphaBetaAI(Player):
    # Implement minimax alpha-beta pruning algorithm
    def __init__(self):
        super().__init__()

class GenMCTSAI(Player):
    # Implement general Monte Carlo Tree Search algorithm
    def __init__(self):
        super().__init__()

class MCTSwUCTNegamaxAI(Player):
    # Implement Monte Carlo Tree Search with UCT and Negamax algorithm
    def __init__(self):
        super().__init__()