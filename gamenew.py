import pygame
from pygame.locals import *
import numpy as np
import copy
import random

# For recording resource usage
# import os
# import pandas as pd
# import psutil
# from jtop import jtop
# import time

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (133, 84, 49)
LIGHT_BROWN = (252, 230, 215)

width, height = 400, 400
rows, cols = 8, 8
squareSize = width // rows

class Checkers:
    def __init__(self, turn='b', board=None):
        pygame.init()

        self.windowsName = 'Checkers'
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(self.windowsName)

        if board is None:
            self.board = [['-', 'b', '-', 'b', '-', 'b', '-', 'b'],
                          ['b', '-', 'b', '-', 'b', '-', 'b', '-'],
                          ['-', '-', '-', '-', '-', '-', '-', '-'],
                          ['-', '-', '-', '-', '-', '-', '-', '-'],
                          ['-', '-', '-', '-', '-', '-', '-', '-'],
                          ['-', '-', '-', '-', '-', '-', '-', '-'],
                          ['-', 'w', '-', 'w', '-', 'w', '-', 'w'],
                          ['w', '-', 'w', '-', 'w', '-', 'w', '-']]
            self.prevBoard = copy.deepcopy(self.board)
            # self.board = [['-', '-', '-', '-', '-', '-', '-', '-'],
            #               ['-', '-', '-', '-', '-', '-', '-', '-'],
            #               ['-', '-', '-', '-', '-', '-', '-', '-'],
            #               ['-', '-', '-', '-', '-', '-', '-', '-'],
            #               ['-', '-', '-', '-', '-', '-', '-', '-'],
            #               ['-', '-', '-', '-', '-', '-', '-', '-'],
            #               ['-', '-', '-', '-', '-', 'B', '-', '-'],
            #               ['-', '-', '-', '-', '-', '-', 'B', '-']]
        else:
            self.board = board
        self.turn = turn # current turn
    
    ## Draw board and pieces
    def draw_board(self):
        for row in range(rows):
            for col in range(row % 2, cols, 2):
                pygame.draw.rect(self.screen, LIGHT_BROWN, (col * squareSize, row * squareSize, squareSize, squareSize))

    def draw_pieces(self):
        for row in range(rows):
            for col in range(cols):
                if self.board[row][col] == 'b':
                    pygame.draw.circle(self.screen, BLACK, (col * squareSize + squareSize // 2, row * squareSize + squareSize // 2), squareSize // 2 - 10)
                elif self.board[row][col] == 'w':
                    pygame.draw.circle(self.screen, WHITE, (col * squareSize + squareSize // 2, row * squareSize + squareSize // 2), squareSize // 2 - 10)
                elif self.board[row][col] == 'B':
                    pygame.draw.circle(self.screen, BLACK, (col * squareSize + squareSize // 2, row * squareSize + squareSize // 2), squareSize // 2 - 10)
                    pygame.draw.circle(self.screen, WHITE, (col * squareSize + squareSize // 2, row * squareSize + squareSize // 2), squareSize // 2 - 20)
                elif self.board[row][col] == 'W':
                    pygame.draw.circle(self.screen, WHITE, (col * squareSize + squareSize // 2, row * squareSize + squareSize // 2), squareSize // 2 - 10)
                    pygame.draw.circle(self.screen, BLACK, (col * squareSize + squareSize // 2, row * squareSize + squareSize // 2), squareSize // 2 - 20)
    
    def debug_text(self):
        squareCount = 32
        for row in range(rows):
            for col in range((row % 2)-1, cols, 2):
                if col != -1:
                    font = pygame.font.SysFont('Arial', 20)
                    text = font.render(f'{squareCount}', True, (255, 0, 0))
                    self.screen.blit(text, (col * squareSize + squareSize // 2 - text.get_width() // 2, row * squareSize + squareSize // 2 - text.get_height() // 2))
                    squareCount -= 1

class Player():
    def __init__(self, turn, board):
        self.turn = turn
        self.board = board
        self.prevCount = countBlack(board) if turn == 'b' else countWhite(board)
        self.init_variables()

    def init_variables(self):
        self.selectedPiece = []
        self.mandatory_moves = []
        self.prevCapture = []
        self.validMoves = []
        self.capturePos = []

    def select_piece(self, row, col, turn, board):
        # check if piece is valid and not conflicting with mandatory capture
        selectedPiece, validMoves, capturePos = [], [], []
        self.mandatory_moves = self.get_mandatory_capture(turn, board)
        if self.mandatory_moves:
            if [row, col] in self.mandatory_moves:
                selectedPiece = [row, col]
                validMoves, capturePos = self.get_valid_moves(row, col, board)
            else:
                print("You must capture @", self.mandatory_moves, "selected piece:", [row, col])
        else:
            if board[row][col].lower() == 'b':
                if turn == 'b':
                    validMoves, capturePos = self.get_valid_moves(row, col, board)
                    if validMoves != []:
                        selectedPiece = [row, col]
                    else:
                        print("No valid moves")
                else:
                    print("Not your turn (White turn)")
            elif board[row][col].lower() == 'w':
                if turn == 'w':
                    validMoves, capturePos = self.get_valid_moves(row, col, board)
                    if validMoves != []:
                        selectedPiece = [row, col]
                    else:
                        print("No valid moves")
                else:
                    print("Not your turn (Black turn)")
            else:
                print("No piece selected")
        return selectedPiece, validMoves, capturePos
    
    def move_piece(self, moveto, turn, board):
        prevBoard = copy.deepcopy(board)
        [rowMove, colMove] = moveto
        if self.validMoves is not None and [rowMove, colMove] in self.validMoves:
            self.prevMove = [rowMove, colMove]
            board[rowMove][colMove] = board[self.selectedPiece[0]][self.selectedPiece[1]]
            board[self.selectedPiece[0]][self.selectedPiece[1]] = '-'
            if self.capturePos != []:
                idxtoRemove = self.validMoves.index([rowMove, colMove])
                board[self.capturePos[idxtoRemove][0]][self.capturePos[idxtoRemove][1]] = '-'
                self.capturePos = []
                self.mandatory_moves = self.get_mandatory_capture(turn, board, self.prevMove)
            board = self.make_king(rowMove, colMove, board)
            self.selectedPiece = []
            self.validMoves = []
            if not self.mandatory_moves:
                self.init_variables()
                turn = 'w' if turn == 'b' else 'b'
        else:
            self.selectedPiece, self.validMoves, self.capturePos = self.select_piece(rowMove, colMove, turn, board)
        return board, turn, prevBoard

    def get_valid_moves(self, row, col, board):
        moves = []
        capturePos = []
        moves, capturePos = self.can_capture(row, col, board)
        if moves == []:
            if board[row][col] == 'b':
                if 0 <= row+1 <= 7 and 0 <= col-1 <= 7 and board[row+1][col-1] == '-':
                    moves.append([row+1, col-1])
                if 0 <= row+1 <= 7 and 0 <= col+1 <= 7 and board[row+1][col+1] == '-':
                    moves.append([row+1, col+1])

            elif board[row][col] == 'w':
                if 0 <= row-1 <= 7 and 0 <= col-1 <= 7 and board[row-1][col-1] == '-':
                    moves.append([row-1, col-1])
                if 0 <= row-1 <= 7 and 0 <= col+1 <= 7 and board[row-1][col+1] == '-':
                    moves.append([row-1, col+1])

            elif board[row][col] == 'B' or board[row][col] == 'W':
                directions = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
                for direction in directions:
                    for i in range(1, 8):
                        checkrow = row + direction[0] * i
                        checkcol = col + direction[1] * i
                        if 0 <= checkrow <= 7 and 0 <= checkcol <= 7:
                            if board[checkrow][checkcol] == '-':
                                moves.append([checkrow, checkcol])
                            else:
                                break
                        else:
                            break
        return (moves, capturePos) if moves else ([], [])
    
    def can_capture(self, row, col, board):
        moves = []
        capturePos = []
        piece = board[row][col]
        if piece == 'B' or piece == 'W':
            capturable = 'w' if piece == 'B' else 'b'
            directions = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
            for direction in directions:
                for i in range(1, 8):
                    checkrow = row + direction[0] * i
                    checkcol = col + direction[1] * i
                    if 0 <= checkrow <= 7 and 0 <= checkcol <= 7:
                        if board[checkrow][checkcol] == '-':
                            continue
                        elif board[checkrow][checkcol].lower() == capturable:
                            if 0 <= checkrow+direction[0] <= 7 and 0 <= checkcol+direction[1] <= 7 and board[checkrow+direction[0]][checkcol+direction[1]] == '-':
                                capturePos.append([checkrow, checkcol]) if [checkrow, checkcol] not in capturePos else None
                                moves.append([checkrow+direction[0], checkcol+direction[1]])
                                break
                            else:
                                break
                        else:
                            break
                    else:
                        break
        else:
            if piece == 'b':
                if 0 <= row+2 <= 7 and 0 <= col-2 <= 7 and board[row+1][col-1].lower() == 'w' and board[row+2][col-2] == '-':
                    capturePos.append([row+1, col-1]) if [row+1, col-1] not in capturePos else None
                    moves.append([row+2, col-2])
                if 0 <= row+2 <= 7 and 0 <= col+2 <= 7 and board[row+1][col+1].lower() == 'w' and board[row+2][col+2] == '-':
                    capturePos.append([row+1, col+1]) if [row+1, col+1] not in capturePos else None
                    moves.append([row+2, col+2])

            elif piece == 'w':
                if 0 <= row-2 <= 7 and 0 <= col-2 <= 7 and board[row-1][col-1].lower() == 'b' and board[row-2][col-2] == '-':
                    capturePos.append([row-1, col-1]) if [row-1, col-1] not in capturePos else None
                    moves.append([row-2, col-2])
                if 0 <= row-2 <= 7 and 0 <= col+2 <= 7 and board[row-1][col+1].lower() == 'b' and board[row-2][col+2] == '-':
                    capturePos.append([row-1, col+1]) if [row-1, col+1] not in capturePos else None
                    moves.append([row-2, col+2])

        return moves, capturePos

    def get_mandatory_capture(self, turn, board, prevMove=None):
        mandatory_moves = []
        for row in range(rows):
            for col in range(cols):
                if board[row][col].lower() == 'b' and turn == 'b':
                    if self.can_capture(row, col, board)[1]:
                        if prevMove is not None:
                            if [row, col] == prevMove:
                                mandatory_moves.append([row, col])
                        else:
                            mandatory_moves.append([row, col])
                elif board[row][col].lower() == 'w' and turn == 'w':
                    if self.can_capture(row, col, board)[1]:
                        if prevMove is not None:
                            if [row, col] == prevMove:
                                mandatory_moves.append([row, col])
                        else:
                            mandatory_moves.append([row, col])
        return mandatory_moves if mandatory_moves else []
    
    def make_king(self, row, col, board):
        if board[row][col] == 'b' and row == 7:
            board[row][col] = 'B'
        elif board[row][col] == 'w' and row == 0:
            board[row][col] = 'W'
        return board
    
    def get_all_moves(self, player, board):
        moves = {}
        mandatory_moves = self.get_mandatory_capture(player, board)
        if mandatory_moves:
            for piece in mandatory_moves:
                moves[tuple(piece)] = self.get_valid_moves(piece[0], piece[1], board)[0]
        else:
            for row in range(rows):
                for col in range(cols):
                    if board[row][col].lower() == player and self.get_valid_moves(row, col, board)[0] != []:
                        moves[(row, col)] = self.get_valid_moves(row, col, board)[0]
        return moves
    
    def update_board(self, board, piece, move):
        self.selectedPiece, self.validMoves, self.capturePos = self.select_piece(piece[0], piece[1], self.turn, board)
        board, turn, _ = self.move_piece(move, self.turn, board)
        return board, turn

    def simulate_game(self, piece, move, turn, board):
        new_board = copy.deepcopy(board)
        self.selectedPiece, self.validMoves, self.capturePos = self.select_piece(piece[0], piece[1], turn, new_board)
        new_board, _, _ = self.move_piece(move, turn, new_board)
        self.init_variables()
        return new_board
    
    def shuffle_dict(self, dict):
        keys = list(dict.keys())
        np.random.shuffle(keys)
        return {key: dict[key] for key in keys}
    
    def evaluate_board(self, board):
        MANPIECE = 5
        KINGPIECE = 10
        KINGROW = 1
        PROMOTEPROTECTION = 1.5
        OTHERROWS = 3
        WALLPENALTY = 0.5
        ADJACENTBONUS = 3
        GAMEOVER = 100
        KINGPOSITIONING = 1
        # piece counting
        value = 0
        for row in range(rows):
            for col in range(cols):
                # No. of pieces (each piece = +1 point)
                if board[row][col] == self.botTurn:
                    value += MANPIECE
                elif board[row][col] == self.oppTurn:
                    value -= MANPIECE
                # No. of kings (each king = +5 points)
                if board[row][col] == self.botTurn.upper():
                    value += KINGPIECE
                elif board[row][col] == self.oppTurn.upper():
                    value -= KINGPIECE
                ### METHOD 1 ###
                # Each line (Men)
                if self.botTurn == 'b':
                    if board[row][col] == self.botTurn:
                        if 0 < row < 3:
                            value += row
                        elif row == 0 and not (col == 1 or col == 5):
                            value += KINGROW
                        # elif row == 0 and (col == 1 or col == 5):
                        #     value += PROMOTEPROTECTION
                        else:
                            value += OTHERROWS
                        # wall penalty
                        if 0 <= row <= 6 and (col == 0 or col == 7):
                            value -= WALLPENALTY
                elif self.botTurn == 'w':
                    if board[row][col] == self.botTurn:
                        if 4 < row < 7:
                            value += (7-row)
                        elif row == 7 and not (col == 2 or col == 6):
                            value += KINGROW
                        # elif row == 7 and (col == 2 or col == 6):
                        #     value += PROMOTEPROTECTION
                        else:
                            value += OTHERROWS
                        # wall penalty
                        if 0 <= row <= 6 and (col == 0 or col == 7):
                            value -= WALLPENALTY
                elif self.oppTurn == 'b':
                    if board[row][col] == self.oppTurn:
                        if 0 < row < 3:
                            value -= row
                        elif row == 0 and not (col == 1 or col == 5):
                            value -= KINGROW
                        # elif row == 0 and (col == 1 or col == 5):
                        #     value -= PROMOTEPROTECTION
                        else:
                            value -= OTHERROWS
                        # wall penalty
                        if 0 <= row <= 6 and (col == 0 or col == 7):
                            value += WALLPENALTY
                elif self.oppTurn == 'w':
                    if board[row][col] == self.oppTurn:
                        if 4 < row < 7:
                            value -= (7-row)
                        elif row == 7 and not (col == 2 or col == 6):
                            value -= KINGROW
                        # elif row == 7 and (col == 2 or col == 6):
                        #     value -= PROMOTEPROTECTION
                        else:
                            value -= OTHERROWS
                        # wall penalty
                        if 0 <= row <= 6 and (col == 0 or col == 7):
                            value += WALLPENALTY

                # # Evaluate adjacent pieces
                #     directions = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
                #     if self.botTurn == 'b':
                #         if countBlack(board) > 4:
                #             tempBAdjacent = []
                #             for direction in directions:
                #                 checkrow = row + direction[0]
                #                 checkcol = col + direction[1]
                #                 if 0 <= checkrow <= 7 and 0 <= checkcol <= 7 and board[checkrow][checkcol] == 'b':
                #                     tempBAdjacent.append(True)
                #                 else:
                #                     tempBAdjacent.append(False)
                #             for adjacent in tempBAdjacent:
                #                 if adjacent:
                #                     value += ADJACENTBONUS
                #                 else:
                #                     value -= ADJACENTBONUS

                #     elif self.botTurn == 'w':
                #         if countWhite(board) > 4:
                #             tempWAdjacent = []
                #             for direction in directions:
                #                 checkrow = row + direction[0]
                #                 checkcol = col + direction[1]
                #                 if 0 <= checkrow <= 7 and 0 <= checkcol <= 7 and board[checkrow][checkcol] == 'w':
                #                     tempWAdjacent.append(True)
                #                 else:
                #                     tempWAdjacent.append(False)
                #             if any(tempWAdjacent):
                #                 value += ADJACENTBONUS
                #             else:
                #                 value -= ADJACENTBONUS

                # King's position (Kings)
                directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
                if board[row][col] == self.botTurn.upper():
                    for delta_row, delta_col in directions:
                        capture_row, capture_col = row + delta_row, col + delta_col
                        descent_diag_row, descent_diag_col = row - min(row, col), col - min(row, col)
                        while 0 <= capture_row < 8 and 0 <= capture_col < 8:
                            if board[capture_row][capture_col] == self.oppTurn:
                                if 0 <= descent_diag_row <= 7 and 0 <= descent_diag_col <= 7 and board[descent_diag_row][descent_diag_col] == ' ':
                                    value += KINGPOSITIONING
                            capture_row += delta_row
                            capture_col += delta_col
                            descent_diag_row += delta_row
                            descent_diag_col += delta_col

                elif board[row][col] == self.oppTurn.upper():
                    for delta_row, delta_col in directions:
                        capture_row, capture_col = row + delta_row, col + delta_col
                        descent_diag_row, descent_diag_col = row - min(row, col), col - min(row, col)
                        while 0 <= capture_row < 8 and 0 <= capture_col < 8:
                            if board[capture_row][capture_col] == self.botTurn:
                                if 0 <= descent_diag_row <= 7 and 0 <= descent_diag_col <= 7 and board[descent_diag_row][descent_diag_col] == ' ':
                                    value -= KINGPOSITIONING
                            capture_row += delta_row
                            capture_col += delta_col
                            descent_diag_row += delta_row
                            descent_diag_col += delta_col

        if is_game_over(board) == self.botTurn:
            value += GAMEOVER

        return value

class User(Player):
    def __init__(self, turn, board):
        super().__init__(turn, board)
        self.user = True

    def get_mouse_pos(self):
        x, y = pygame.mouse.get_pos()
        row, col = y // squareSize, x // squareSize
        return row, col
    
    def handle_mouse_click(self, row, col, board):
        prevBoard = copy.deepcopy(board)
        turn = None
        if self.selectedPiece == []:
            self.selectedPiece, self.validMoves, self.capturePos = self.select_piece(row, col, self.turn, board)
            board, turn = board, self.turn
        else:
            board, turn, prevBoard = self.move_piece([row, col], self.turn, board)
        return board, turn, prevBoard

class Minimax(Player):
    def __init__(self, turn, depth, max_depth, board, ab = False):
        super().__init__(turn, board)
        self.botTurn = 'b' if turn == 'b' else 'w'
        self.oppTurn = 'w' if turn == 'b' else 'b'
        self.user = False
        self.increased_depth = False
        self.init_depth = depth
        self.depth = depth
        self.max_depth = max_depth
        self.ab = ab

    def play(self, board):
        self.prevCount = countBlack(board) + countWhite(board)
        _, bestPiece, bestMove = self.minimax(board, self.depth, True) if not self.ab else self.minimaxAlphaBeta(board, self.depth, -np.inf, np.inf, True)
        self.depth = self.increase_depth(board, self.depth, self.max_depth)
        return bestPiece, bestMove

    def minimax(self, board, depth, maximizing):
        if depth == 0 or is_game_over(board) in ['w', 'b']:
            return self.evaluate_board(board), None, None

        if maximizing:
            maxEval = -np.inf
            bestPiece = None
            bestMove = None
            movesdict = self.get_all_moves(self.botTurn, board)
            for piece, movetolist in movesdict.items():
                for moveto in movetolist:
                    new_board = self.simulate_game(piece, moveto, self.botTurn, board)
                    eval, _, _ = self.minimax(new_board, depth-1, False)
                    maxEval = max(maxEval, eval)
                    if maxEval == eval:
                        bestPiece = piece
                        bestMove = moveto

            return maxEval, bestPiece, bestMove
        
        else:
            minEval = np.inf
            bestPiece = None
            bestMove = None
            movesdict = self.get_all_moves(self.oppTurn, board)
            for piece, movetolist in movesdict.items():
                for moveto in movetolist:
                    new_board = self.simulate_game(piece, moveto, self.oppTurn, board)
                    eval, _, _ = self.minimax(new_board, depth-1, True)
                    minEval = min(minEval, eval)
                    if minEval == eval:
                        bestPiece = piece
                        bestMove = moveto

            return minEval, bestPiece, bestMove

    def minimaxAlphaBeta(self, board, depth, alpha, beta, maximizing):
        if depth == 0 or is_game_over(board) in ['w', 'b']:
            return self.evaluate_board(board), None, None
        
        if maximizing:
            maxEval = -np.inf
            bestPiece = None
            bestMove = None
            movesdict = self.shuffle_dict(self.get_all_moves(self.botTurn, board))
            for piece, moveto in movesdict.items():
                new_board = self.simulate_game(piece, moveto, self.botTurn, board)
                eval, _, _ = self.minimaxAlphaBeta(new_board, depth-1, alpha, beta, False)
                maxEval = max(maxEval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
                if maxEval == eval:
                    bestPiece = piece
                    bestMove = moveto
            return maxEval, bestPiece, bestMove
        
        else:
            minEval = np.inf
            bestPiece = None
            bestMove = None
            movesdict = self.shuffle_dict(self.get_all_moves(self.oppTurn, board))
            for piece, moveto in movesdict.items():
                new_board = self.simulate_game(piece, moveto, self.oppTurn, board)
                eval, _, _ = self.minimaxAlphaBeta(new_board, depth-1, alpha, beta, True)
                minEval = min(minEval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
                if minEval == eval:
                    bestPiece = piece
                    bestMove = moveto
            return minEval, bestPiece, bestMove

    def increase_depth(self, board, current_depth, max_depth):
        # Endgame = 8 pieces or less
        currCount = countBlack(board) + countWhite(board)
        ourPieces = countBlack(board) if self.botTurn == 'b' else countWhite(board)
        oppPieces = countWhite(board) if self.botTurn == 'b' else countBlack(board)

        if currCount <= 6 and ourPieces <= 4:
            return max_depth

        if not self.increased_depth:
            if (ourPieces <= oppPieces/2 or oppPieces <= ourPieces/2) and (currCount <= 12):
                self.increased_depth = True
                return current_depth + 1 if current_depth < max_depth else max_depth
            elif ourPieces <= 6 or oppPieces <= 6 and currCount <= 10:
                self.increased_depth = True
                return current_depth + 1 if current_depth < max_depth else max_depth
        else:
            if self.prevCount != currCount:
                self.increased_depth = False

        return current_depth


class randomBot(Player):
    def __init__(self, turn, board):
        super().__init__(turn, board)
        self.user = False

    def play(self, board):
        movesdict = self.shuffle_dict(self.get_all_moves(self.turn, board))
        piece = list(movesdict.keys())[0]
        moveto = random.choice(movesdict[piece])
        return piece, moveto

def main():
    # time.sleep(10)
    # t_end = time.time() + (60 * 10)
    # while time.time() < t_end:
    #     writeData(None, None, 'data/idle_resource.csv')
    #     time.sleep(2)
    
    # loops = 20
    # for loop in range(loops):
        # filename = f'data/random/winner_experiment_random_mm{depth2}.csv'

        board = Checkers()
        INITIAL_DEPTH = 5
        MAX_DEPTH = 10
        isGameOver = False
        running = True
        nummoves = 0

        player1 = User('b', board.board)
        # player1 = randomBot('b', board.board)
        # player1 = Minimax('b', INITIAL_DEPTH, MAX_DEPTH, board.board)
        # player1 = Minimax('b', INITIAL_DEPTH, MAX_DEPTH, board.board, ab=True)
        
        # player2 = User('w', board.board)
        # player2 = randomBot('w', board.board)
        player2 = Minimax('w', INITIAL_DEPTH, MAX_DEPTH, board.board)
        # player2 = Minimax('w', INITIAL_DEPTH, MAX_DEPTH, board.board, ab=True)
        
        while running:
            # for event in pygame.event.get():
            #     print('Game running')
            #     if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            #         running = False
            #         print('Early Exiting...')

            isGameOver = is_game_over(board.board)
            if isGameOver in ['b', 'w']:
                # print(countBlack(board.board), countWhite(board.board))
                # running = False
                # print('Game Over, Winner:', 'Black' if isGameOver == 'b' else 'White')
                pass
                # winnerData(loop, isGameOver, filename)

            board.screen.fill(BROWN)
            board.draw_board()
            board.draw_pieces()
            board.debug_text()
            pygame.display.flip()

            if not isGameOver:
                if board.turn == 'b':
                    if player1.user:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                                print('Early Exiting...')
                                running = False
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                row, col = player1.get_mouse_pos()
                                board.board, board.turn, board.prevBoard = player1.handle_mouse_click(row, col, board.board)
                                player1.turn = board.turn
                                player2.turn = board.turn
                    else:
                        bestPiece, bestMove = player1.play(board.board)
                        if bestPiece is not None and bestMove is not None:
                            player1.prevCount = countBlack(board.board) + countWhite(board.board)
                            board.board, board.turn = player1.update_board(board.board, bestPiece, bestMove)
                            player1.turn = board.turn
                            player2.turn = board.turn
                    
                elif board.turn == 'w':
                    if player2.user:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                                print('Early Exiting...')
                                running = False
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                row, col = player2.get_mouse_pos()
                                board.board, board.turn, board.prevBoard = player2.handle_mouse_click(row, col, board.board)
                                player1.turn = board.turn
                                player2.turn = board.turn
                    else:
                        bestPiece, bestMove = player2.play(board.board)
                        if bestPiece is not None and bestMove is not None:
                            player2.prevCount = countBlack(board.board) + countWhite(board.board)
                            board.board, board.turn = player2.update_board(board.board, bestPiece, bestMove)
                            player1.turn = board.turn
                            player2.turn = board.turn

                if board.board != board.prevBoard:
                    nummoves += 1
                    board.prevBoard = copy.deepcopy(board.board)
                    print('Moves:', nummoves, 'Turn:', board.turn)
                    print('Current Depth:', player2.depth)
            # writeData(loop, nummoves, 'data/resource_usage.csv')

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                    if countBlack(board.board) > countWhite(board.board) or isGameOver == 'b':
                        print('Game Over, Winner: Black')
                        # winnerData(loop, 'b', filename)
                    elif countBlack(board.board) < countWhite(board.board) or isGameOver == 'w':
                        print('Game Over, Winner: White')
                        # winnerData(loop, 'w', filename)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    print('Restarting...')
                    main()
        pygame.quit()

# def winnerData(loop, winner, filename='winner.csv'):
#     if os.path.isfile(filename):
#         df = pd.read_csv(filename)
#     else:
#         df = pd.DataFrame(columns=['Game', 'Winner'])
#     pd.concat([df, pd.DataFrame([[loop, winner]], columns=['Game', 'Winner'])]).to_csv(filename, index=False)

# def writeData(loopcount, nummoves, filename='resource_usage.csv'):
#     if os.path.isfile(filename):
#         df = pd.read_csv(filename)
#     else:
#         df = pd.DataFrame(columns=['CPU', 'GPU', 'RAM', 'Moves', 'Loop'])
#     with jtop() as jetson:
#         pd.concat([df, pd.DataFrame([[psutil.cpu_percent(), jetson.stats['GPU'], psutil.virtual_memory()[3]/1e+9, nummoves, loopcount]], columns=['CPU', 'GPU', 'RAM', 'Moves', 'Loop'])]).to_csv(filename, index=False)

def countBlack(board):
    count = 0
    for row in range(rows):
        for col in range(cols):
            if board[row][col].lower() == 'b':
                count += 1
    return count

def countWhite(board):
    count = 0
    for row in range(rows):
        for col in range(cols):
            if board[row][col].lower() == 'w':
                count += 1
    return count

def is_game_over(board):
    tempb = []
    tempbmove = []
    tempbcap = []

    xb = np.char.lower(np.array(board)) == 'b'
    pieceloclist = np.asarray(np.where(xb)).T.tolist()
    for pieceloc in pieceloclist:
        tempbmove.append(check_basic_valid_moves(pieceloc[0], pieceloc[1], board))
        tempbcap.append(check_basic_capture(pieceloc[0], pieceloc[1], board))
    for normMove, capMove in zip(tempbmove, tempbcap):
        tempb.append(normMove or capMove)
    if all(not i for i in tempb) or countBlack(board) == 0:
        # print('White wins', tempb, tempbmove, tempbcap)
        return 'w'

    tempw = []
    tempwmove = []
    tempwcap = []
    xw = np.char.lower(np.array(board)) == 'w'
    pieceloclist = np.asarray(np.where(xw)).T.tolist()
    for pieceloc in pieceloclist:
        tempwmove.append(check_basic_valid_moves(pieceloc[0], pieceloc[1], board))
        tempwcap.append(check_basic_capture(pieceloc[0], pieceloc[1], board))
    for normMove, capMove in zip(tempwmove, tempwcap):
        tempw.append(normMove or capMove)
    if all(not i for i in tempw) or countWhite(board) == 0:
        # print('Black wins', tempw)
        return 'b'

    return False

def check_basic_valid_moves(row, col, board):
    if board[row][col].lower() == 'b' or board[row][col] == 'W':
        if 0 <= row+1 <= 7 and 0 <= col-1 <= 7 and board[row+1][col-1] == '-':
            return True
        if 0 <= row+1 <= 7 and 0 <= col+1 <= 7 and board[row+1][col+1] == '-':
            return True
    if board[row][col].lower() == 'w' or board[row][col] == 'B':
        if 0 <= row-1 <= 7 and 0 <= col-1 <= 7 and board[row-1][col-1] == '-':
            return True
        if 0 <= row-1 <= 7 and 0 <= col+1 <= 7 and board[row-1][col+1] == '-':
            return True
    return False

def check_basic_capture(row, col, board):
    if board[row][col] == 'b':
        if 0 <= row+2 <= 7 and 0 <= col-2 <= 7 and board[row+1][col-1].lower() == 'w' and board[row+2][col-2] == '-':
            return True
        if 0 <= row+2 <= 7 and 0 <= col+2 <= 7 and board[row+1][col+1].lower() == 'w' and board[row+2][col+2] == '-':
            return True
    if board[row][col] == 'w':
        if 0 <= row-2 <= 7 and 0 <= col-2 <= 7 and board[row-1][col-1].lower() == 'b' and board[row-2][col-2] == '-':
            return True
        if 0 <= row-2 <= 7 and 0 <= col+2 <= 7 and board[row-1][col+1].lower() == 'b' and board[row-2][col+2] == '-':
            return True
    if board[row][col] == 'B' or board[row][col] == 'W':
        directions = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
        for direction in directions:
            for i in range(1, 8):
                checkrow = row + direction[0] * i
                checkcol = col + direction[1] * i
                if 0 <= checkrow <= 7 and 0 <= checkcol <= 7:
                    if board[checkrow][checkcol] == '-':
                        continue
                    elif board[checkrow][checkcol].lower() != board[row][col].lower():
                        if 0 <= checkrow+direction[0] <= 7 and 0 <= checkcol+direction[1] <= 7 and board[checkrow+direction[0]][checkcol+direction[1]] == '-':
                            return True
                    else:
                        break
                else:
                    break
    return False

if __name__ == '__main__':
    main()