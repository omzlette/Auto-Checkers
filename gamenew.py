import pygame
from pygame.locals import *
import numpy as np
import copy
import random
import time

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

        self.movesDone = {'b': [], 'w': []}
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
                font = pygame.font.SysFont('Arial', 20)
                text = font.render('K', True, (0, 120, 255))
                if self.board[row][col] == 'b':
                    pygame.draw.circle(self.screen, BLACK, (col * squareSize + squareSize // 2, row * squareSize + squareSize // 2), squareSize // 2 - 10)
                elif self.board[row][col] == 'w':
                    pygame.draw.circle(self.screen, WHITE, (col * squareSize + squareSize // 2, row * squareSize + squareSize // 2), squareSize // 2 - 10)
                elif self.board[row][col] == 'B':
                    pygame.draw.circle(self.screen, BLACK, (col * squareSize + squareSize // 2, row * squareSize + squareSize // 2), squareSize // 2 - 10)
                    # pygame.draw.circle(self.screen, WHITE, (col * squareSize + squareSize // 2, row * squareSize + squareSize // 2), squareSize // 2 - 20)
                    self.screen.blit(text, (col * squareSize + squareSize // 2 - text.get_width() // 2, row * squareSize + squareSize // 2 - text.get_height() // 2))
                elif self.board[row][col] == 'W':
                    pygame.draw.circle(self.screen, WHITE, (col * squareSize + squareSize // 2, row * squareSize + squareSize // 2), squareSize // 2 - 10)
                    # pygame.draw.circle(self.screen, BLACK, (col * squareSize + squareSize // 2, row * squareSize + squareSize // 2), squareSize // 2 - 20)
                    self.screen.blit(text, (col * squareSize + squareSize // 2 - text.get_width() // 2, row * squareSize + squareSize // 2 - text.get_height() // 2))
    
    def debug_text(self):
        squareCount = 0
        for row in range(rows):
            for col in range((row % 2)-1, cols, 2):
                if col != -1:
                    squareCount += 1
                    font = pygame.font.SysFont('Arial', 20)
                    text = font.render(f'{squareCount}', True, (255, 0, 0))
                    self.screen.blit(text, (col * squareSize + squareSize - text.get_width(), row * squareSize + squareSize - text.get_height()))

    def updateMovesDict(self, piece, move, turn):
        self.movesDone[turn].append([piece, move])

class Player():
    def __init__(self, turn, board, movesDone):
        self.turn = turn
        self.board = board
        self.movesDone = movesDone
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
    
    def get_all_moves(self, player, board, pieceLoc=None):
        moves = {}
        if pieceLoc is None:
            mandatory_moves = self.get_mandatory_capture(player, board)
            if mandatory_moves:
                for piece in mandatory_moves:
                    moves[tuple(piece)] = self.get_valid_moves(piece[0], piece[1], board)[0]
            else:
                for row in range(rows):
                    for col in range(cols):
                        if board[row][col].lower() == player and self.get_valid_moves(row, col, board)[0] != []:
                            moves[(row, col)] = self.get_valid_moves(row, col, board)[0]
        else:
            # Check only passed piece location
            moves[tuple(pieceLoc)] = self.get_valid_moves(pieceLoc[0], pieceLoc[1], board)[0]

        return moves
    
    def update_board(self, board, piece, move):
        self.selectedPiece, self.validMoves, self.capturePos = self.select_piece(piece[0], piece[1], self.turn, board)
        board, turn, prevBoard = self.move_piece(move, self.turn, board)
        return board, turn, prevBoard

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
        PIECECOUNT = 100
        KINGPIECE = 50
        TRAPPEDKING = 50 # negative points
        GAMEOVER = 2000
        DRAW = 0

        ourTurn = self.turn
        oppTurn = 'w' if self.turn == 'b' else 'b'
        ourVal = 3 # Starting at 3 for the turn based points
        oppVal = 0

        kingMoves = {}
        
        for row in range(rows):
            for col in range(cols):
                # No. of pieces
                if board[row][col].lower() == ourTurn:
                    ourVal += PIECECOUNT
                elif board[row][col].lower() == oppTurn:
                    oppVal += PIECECOUNT
                # No. of kings and trapped kings (Added on top of pieces)
                if board[row][col] == ourTurn.upper():
                    ourVal += KINGPIECE
                    kingMoves = self.get_all_moves(ourTurn, board, [row, col])
                    if len(kingMoves[(row, col)]) <= 1:
                        ourVal -= TRAPPEDKING
                elif board[row][col] == oppTurn.upper():
                    oppVal += KINGPIECE
                    kingMoves = self.get_all_moves(oppTurn, board, [row, col])
                    if len(kingMoves[(row, col)]) <= 1:
                        oppVal -= TRAPPEDKING



        if is_game_over(board) == ourTurn:
            ourVal += GAMEOVER
        elif is_game_over(board) == oppTurn:
            oppVal += GAMEOVER
        elif is_game_over(board) == 'draw':
            ourVal += DRAW
            oppVal += DRAW

        return ourVal - oppVal

class User(Player):
    def __init__(self, turn, board, movesDone):
        super().__init__(turn, board, movesDone)
        self.user = True

    def get_mouse_pos(self):
        x, y = pygame.mouse.get_pos()
        row, col = y // squareSize, x // squareSize
        return row, col
    
    def handle_mouse_click(self, row, col, board):
        prevBoard = copy.deepcopy(board)
        turn = None
        selectedPiece = []
        if self.selectedPiece == []:
            self.selectedPiece, self.validMoves, self.capturePos = self.select_piece(row, col, self.turn, board)
            board, turn = board, self.turn
        else:
            selectedPiece = self.selectedPiece
            board, turn, prevBoard = self.move_piece([row, col], self.turn, board)
        return board, turn, prevBoard, selectedPiece

class Minimax(Player):
    def __init__(self, turn, depth, max_depth, board, movesDone, ab = False):
        super().__init__(turn, board, movesDone)
        self.currTurn = turn
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
        minimaxTimer = time.time()
        _, bestPiece, bestMove = self.minimax(board, self.depth, True) if not self.ab else self.minimaxAlphaBeta(board, self.depth, -np.inf, np.inf, True)
        print('Minimax Time:', time.time() - minimaxTimer)
        # self.depth = self.increase_depth(board, self.depth, self.max_depth)
        return bestPiece, bestMove

    def minimax(self, board, depth, maximizing):
        if depth == 0 or is_game_over(board, self.movesDone) in ['w', 'b']:
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
        if depth == 0 or is_game_over(board, self.movesDone) in ['w', 'b']:
            return self.evaluate_board(board), None, None
        
        if maximizing:
            maxEval = -np.inf
            bestPiece = None
            bestMove = None
            movesdict = self.shuffle_dict(self.get_all_moves(self.botTurn, board))
            for piece, movetolist in movesdict.items():
                for moveto in movetolist:
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
            for piece, movetolist in movesdict.items():
                for moveto in movetolist:
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

def countKings(board):
    whiteKings = 0
    blackKings = 0
    for row in range(rows):
        for col in range(cols):
            if board[row][col] == 'B':
                blackKings += 1
            elif board[row][col] == 'W':
                whiteKings += 1
    return whiteKings, blackKings

def is_game_over(board, movesDone):
    tempb = []
    tempbmove = []
    tempbcap = []

    tempw = []
    tempwmove = []
    tempwcap = []

    blackCount = countBlack(board)
    whiteCount = countWhite(board)
    whiteKing, blackKing = countKings(board)

    blackMoveCount = len(movesDone['b'])
    whiteMoveCount = len(movesDone['w'])
    totalMoveCount = len(movesDone['b']) + len(movesDone['w'])

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

    if (blackCount == 1 and blackKing == 1) and\
       (whiteCount == 1 and whiteKing == 1) and\
       all(not i for i in tempbcap) and\
       all(not i for i in tempwcap):
        # with only 1 king each w/o any forced captures, the game should be considered a draw
        return 'draw'
    
    if blackMoveCount == 40 or whiteMoveCount == 40:
        # In the internaitonal rules, if a player makes 40 moves without a capture or a king, the game is a draw
        if blackCount + whiteCount == 24:
            return 'draw'
        if whiteKing + blackKing == 0:
            return 'draw'

    if totalMoveCount >= 12:
        # If the last 3 moves are the same, the game is a draw
        if movesDone['b'][-1] == movesDone['b'][-3] == movesDone['b'][-5] and\
           movesDone['w'][-1] == movesDone['w'][-3] == movesDone['w'][-5] and\
           movesDone['b'][-2] == movesDone['b'][-4] == movesDone['b'][-6] and\
           movesDone['w'][-2] == movesDone['w'][-4] == movesDone['w'][-6]:
            return 'draw'

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
        # player2 = Minimax('w', INITIAL_DEPTH, MAX_DEPTH, board.board)
        player2 = Minimax('w', INITIAL_DEPTH, MAX_DEPTH, board.board, ab=True)
        
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
                                board.board, board.turn, board.prevBoard, selectedPiece = player1.handle_mouse_click(row, col, board.board)
                                player1.turn = board.turn
                                player2.turn = board.turn
                    else:
                        bestPiece, bestMove = player1.play(board.board)
                        if bestPiece is not None and bestMove is not None:
                            player1.prevCount = countBlack(board.board) + countWhite(board.board)
                            board.board, board.turn, board.prevBoard = player1.update_board(board.board, bestPiece, bestMove)
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
                                board.board, board.turn, board.prevBoard, selectedPiece = player2.handle_mouse_click(row, col, board.board)
                                player1.turn = board.turn
                                player2.turn = board.turn
                    else:
                        bestPiece, bestMove = player2.play(board.board)
                        if bestPiece is not None and bestMove is not None:
                            player2.prevCount = countBlack(board.board) + countWhite(board.board)
                            board.board, board.turn, board.prevBoard = player2.update_board(board.board, bestPiece, bestMove)
                            player1.turn = board.turn
                            player2.turn = board.turn

                if board.board != board.prevBoard:
                    nummoves += 1
                    board.prevBoard = copy.deepcopy(board.board)
                    if board.turn == 'w':
                        board.updateMovesDict(tuple(selectedPiece), (row, col), 'b')
                    else:
                        board.updateMovesDict(tuple(bestPiece), tuple(bestMove), 'w')
                    print('Moves Done:', board.movesDone)
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

if __name__ == '__main__':
    main()