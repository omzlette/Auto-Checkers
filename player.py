import pygame
from pygame.locals import *
import numpy as np
import copy
import random
import time
import checkers

width, height = checkers.width, checkers.height
rows, cols = checkers.rows, checkers.cols
squareSize = checkers.squareSize

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
        return board, turn

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
                        if board[row][col] == 'b' and row + 2 == 7:
                            # If the piece is at the end of the board, it's promoted to king and stops continuing the capture
                            break
                elif board[row][col].lower() == 'w' and turn == 'w':
                    if self.can_capture(row, col, board)[1]:
                        if prevMove is not None:
                            if [row, col] == prevMove:
                                mandatory_moves.append([row, col])
                        else:
                            mandatory_moves.append([row, col])
                        if board[row][col] == 'w' and row - 2 == 0:
                            # If the piece is at the end of the board, it's promoted to king and stops continuing the capture
                            break
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
        board, turn = self.move_piece(move, self.turn, board)
        return board, turn

    def simulate_game(self, piece, move, turn, board):
        new_board = copy.deepcopy(board)
        self.selectedPiece, self.validMoves, self.capturePos = self.select_piece(piece[0], piece[1], turn, new_board)
        new_board, _ = self.move_piece(move, turn, new_board)
        self.init_variables()
        return new_board

    def runawayCheckers(self, board, piece):
        # Check if the piece has a path of becoming a king
        blackDirections = [[1, -1], [1, 1]]
        whiteDirections = [[-1, -1], [-1, 1]]

        pieceRow = piece[0]
        pieceCol = piece[1]
        pieceColor = board[pieceRow][pieceCol].lower()
        moveList = []

        for dir in blackDirections if pieceColor == 'b' else whiteDirections:
            checkRow, checkCol = pieceRow + dir[0], pieceCol + dir[1]
            if 0 <= checkRow <= 7 and 0 <= checkCol <= 7 and board[checkRow][checkCol] == '-':
                tempBoard = copy.deepcopy(board)
                tempBoard[pieceRow][pieceCol], tempBoard[checkRow][checkCol] = '-', pieceColor
                moveList = self.runawayCheckers(tempBoard, (checkRow, checkCol))
                moveList.append((checkRow, checkCol))

        return moveList[::-1]
    
    def evaluate_board(self, board, maximizing=True):
        # Evaluation function for the board
        # The bot is always maximizing, the opponent is always minimizing
        # Can only be used for implementing algorithms that require evaluation function

        PIECECOUNT = 100
        KINGPIECE = 50
        TRAPPEDKING = 50 # negative points
        DOGHOLE = 10
        BACKRANK = 20
        GAMEOVER = 2000
        DRAW = 0

        totalPieces = 0
        for row in range(rows):
            totalPieces += sum(list(map(lambda x: True if x.lower() in ['b', 'w'] else False, board[row])))

        # Multiplier for making the bot favor more pieces
        if totalPieces < 8:
            MULTIPLIER = 5/6
        elif totalPieces >= 8 and totalPieces <= 10:
            MULTIPLIER = 1
        elif totalPieces >= 11 and totalPieces <= 13:
            MULTIPLIER = 7/6
        else:
            MULTIPLIER = 4/3

        ourTurn = self.botTurn if maximizing else self.oppTurn
        oppTurn = self.oppTurn if maximizing else self.botTurn
        ourVal = 3 # Turn value
        oppVal = 0

        for row in range(rows):
            for col in range(cols):
                # No. of pieces
                if board[row][col].lower() == ourTurn:
                    ourVal += PIECECOUNT * MULTIPLIER
                elif board[row][col].lower() == oppTurn:
                    oppVal += PIECECOUNT * MULTIPLIER
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

                # Runaway Checkers
                # If the bot has a path to become a king, it's better for the bot
                if board[row][col] == ourTurn and row >= 4:
                    runaway = self.runawayCheckers(board, [row, col])
                    numMovestoKing = 7 - row
                    if len(runaway) == numMovestoKing and numMovestoKing > 0:
                        ourVal += KINGPIECE - (numMovestoKing * 3)
                elif board[row][col] == oppTurn and row <= 3:
                    runaway = self.runawayCheckers(board, [row, col])
                    numMovestoKing = row
                    if len(runaway) == numMovestoKing and numMovestoKing > 0:
                        oppVal += KINGPIECE - (numMovestoKing * 3)


        # Dog-Hole (putting ourselves in a dog hole is no good)
        # For black, h2 (28) with white on g1 (32). For white, a7 (5) with black on b8 (1).
        if board[7][6].lower() == 'w' and board[6][7].lower() == 'b' and ourTurn == 'w':
            ourVal -= DOGHOLE
        elif board[7][6].lower() == 'w' and board[6][7].lower() == 'b' and oppTurn == 'w':
            oppVal -= DOGHOLE
        
        if board[0][1].lower() == 'b' and board[1][0].lower() == 'w' and oppTurn == 'b':
            oppVal -= DOGHOLE
        elif board[0][1].lower() == 'b' and board[1][0].lower() == 'w' and ourTurn == 'b':
            ourVal -= DOGHOLE

        # Back Rank (making the other side getting a king is better)
        # If one side have lower opportunity to get a king by the other side blocking, it's better for the blocker. 
        # +20 to the blocker
        backrankB = list(map(lambda x: True if x.lower() == 'b' else False, board[0]))
        backrankW = list(map(lambda x: True if x.lower() == 'w' else False, board[7]))
        
        backrankBCount = sum(backrankB)
        backrankWCount = sum(backrankW)

        if backrankBCount > backrankWCount and ourTurn == 'b':
            ourVal += BACKRANK
        elif backrankWCount > backrankBCount and oppTurn == 'b':
            oppVal += BACKRANK

        if backrankWCount > backrankBCount and ourTurn == 'w':
            ourVal += BACKRANK
        elif backrankBCount > backrankWCount and oppTurn == 'w':
            oppVal += BACKRANK

        # Win/Lose/Draw
        if is_game_over(board, self.movesDone) == ourTurn:
            ourVal += GAMEOVER
        elif is_game_over(board, self.movesDone) == oppTurn:
            oppVal += GAMEOVER
        elif is_game_over(board, self.movesDone) == 'draw':
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
        turn = None
        selectedPiece = []
        if self.selectedPiece == []:
            self.selectedPiece, self.validMoves, self.capturePos = self.select_piece(row, col, self.turn, board)
            board, turn = board, self.turn
        else:
            selectedPiece = self.selectedPiece
            board, turn = self.move_piece([row, col], self.turn, board)
        return board, turn, selectedPiece

class Minimax(Player):
    def __init__(self, turn, board, movesDone):
        super().__init__(turn, board, movesDone)
        self.botTurn = 'b' if turn == 'b' else 'w'
        self.oppTurn = 'w' if turn == 'b' else 'b'
        self.user = False
        self.timer = 0
        self.timeLimit = 30

    def iterativeDeepening(self, board):
        bestPiece = None
        bestMove = None
        bestValue = -np.inf
        depth = 1
        self.timer = time.time()
        while True:
            if time.time() - self.timer > self.timeLimit: break
            value, piece, move = self.minimax(board, depth, True)
            print('Depth:', depth, 'Time:', time.time() - self.timer, f'Value: {value} Piece: {piece} Move: {move}')
            if value > bestValue:
                bestValue = value
                bestPiece = piece
                bestMove = move
            if value >= 2000:
                # If the bot wins, return the move
                bestValue = value
                bestPiece = piece
                bestMove = move
                break
            depth += 1
        print(f'Time taken: {time.time() - self.timer} seconds, Depth: {depth}, Value: {bestValue}, Piece: {bestPiece}, Move: {bestMove}')
        return bestValue, bestPiece, bestMove

    def play(self, board):
        # self.prevCount = countBlack(board) + countWhite(board)
        mandatory_moves = self.get_mandatory_capture(self.botTurn, board)
        if len(mandatory_moves) == 1:
            bestPiece, bestMove = mandatory_moves[0], self.get_valid_moves(mandatory_moves[0][0], mandatory_moves[0][1], board)[0][0]
        else:
            _, bestPiece, bestMove = self.iterativeDeepening(board)
        return bestPiece, bestMove
        
    def minimax(self, board, depth, maximizing):
        if depth == 0 or is_game_over(board, self.movesDone) in ['w', 'b', 'draw'] or time.time() - self.timer > self.timeLimit:
            return self.evaluate_board(board, maximizing), None, None

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

class AlphaBeta(Minimax):
    def __init__(self, turn, board, movesDone):
        super().__init__(turn, board, movesDone)
        self.zobristtable = self.initTable()
        self.hashtable = {}

    def play(self, board):
        # self.prevCount = countBlack(board) + countWhite(board)
        mandatory_moves = self.get_mandatory_capture(self.botTurn, board)
        if len(mandatory_moves) == 1:
            bestPiece, bestMove = mandatory_moves[0], self.get_valid_moves(mandatory_moves[0][0], mandatory_moves[0][1], board)[0][0]
        else:
            _, bestPiece, bestMove = self.iterativeDeepening(board)
        return bestPiece, bestMove

    def iterativeDeepening(self, board):
        bestPiece = None
        bestMove = None
        bestValue = -np.inf
        depth = 1
        self.timer = time.time()
        while True:
            if time.time() - self.timer > self.timeLimit: break
            value, piece, move = self.alphaBeta(board, depth, -np.inf, np.inf, True)
            print('Depth:', depth, 'Time:', time.time() - self.timer, f'Value: {value} Piece: {piece} Move: {move}')
            if value >= bestValue:
                bestValue = value
                bestPiece = piece
                bestMove = move
            if value >= 2000:
                # If the bot wins, return the move
                bestValue = value
                bestPiece = piece
                bestMove = move
                break
            depth += 1
        print(f'Time taken: {time.time() - self.timer} seconds, Depth: {depth}, Value: {bestValue}, Piece: {bestPiece}, Move: {bestMove}')
        return bestValue, bestPiece, bestMove

    def alphaBeta(self, board, depth, alpha, beta, maximizing):
        maxEval = -np.inf
        bestPiece = None
        bestMove = None
        movesdict = self.get_all_moves(self.botTurn, board)

        if depth == 0 or is_game_over(board, self.movesDone) in ['w', 'b', 'draw'] or time.time() - self.timer >= self.timeLimit:
            return self.evaluate_board(board), None, None

        transposition = self.probeTransposition(board)
        if transposition is not None and transposition['depth'] >= depth:
            # Checking for saved depth higher or equal to current depth
            # because higher depth means more accurate evaluation
            if transposition['value'] > transposition['beta']:
                # Lower Bound, fails high, Alpha is the lower bound
                # Fail high means there exists a better move, meaning it's > beta
                # Updating alpha to ensure that we won't prune moves that are better
                alpha = max(alpha, transposition['value'])
            elif transposition['value'] < transposition['alpha']:
                # Upper Bound, fails low, Beta is the upper bound
                # Fail low means there exists no moves that can make it > alpha
                # Updating beta to ensure that we won't explore moves that are worse
                beta = min(beta, transposition['value'])
            else:
                # Exact Value
                return transposition['value'], None, None
        
        if maximizing:
            maxEval = -np.inf
            bestPiece = None
            bestMove = None
            movesdict = self.get_all_moves(self.botTurn, board)
            for piece, movetolist in movesdict.items():
                for moveto in movetolist:
                    new_board = self.simulate_game(piece, moveto, self.botTurn, board)
                    eval, _, _ = self.alphaBeta(new_board, depth-1, alpha, beta, False)
                    maxEval = max(maxEval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
                    if maxEval == eval:
                        bestPiece = piece
                        bestMove = moveto
            
            self.storeTransposition(board, depth, maxEval, alpha, beta)
            return maxEval, bestPiece, bestMove
        
        else:
            minEval = np.inf
            bestPiece = None
            bestMove = None
            movesdict = self.get_all_moves(self.oppTurn, board)
            for piece, movetolist in movesdict.items():
                for moveto in movetolist:
                    new_board = self.simulate_game(piece, moveto, self.oppTurn, board)
                    eval, _, _ = self.alphaBeta(new_board, depth-1, alpha, beta, True)
                    minEval = min(minEval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
                    if minEval == eval:
                        bestPiece = piece
                        bestMove = moveto

            self.storeTransposition(board, depth, minEval, alpha, beta)
            return minEval, bestPiece, bestMove
            
    def squareMapping(self, square):
        squareMapping = { 1: (0, 1),  2: (0, 3),  3: (0, 5),  4: (0, 7),
                          5: (1, 0),  6: (1, 2),  7: (1, 4),  8: (1, 6),
                          9: (2, 1), 10: (2, 3), 11: (2, 5), 12: (2, 7),
                         13: (3, 0), 14: (3, 2), 15: (3, 4), 16: (3, 6),
                         17: (4, 1), 18: (4, 3), 19: (4, 5), 20: (4, 7),
                         21: (5, 0), 22: (5, 2), 23: (5, 4), 24: (5, 6),
                         25: (6, 1), 26: (6, 3), 27: (6, 5), 28: (6, 7),
                         29: (7, 0), 30: (7, 2), 31: (7, 4), 32: (7, 6)}
        row = squareMapping[square][0]
        col = squareMapping[square][1]
        return row, col
    
    def get_square(self, row, col):
        squareMapping = {(0, 1): 1, (0, 3): 2, (0, 5): 3, (0, 7): 4,
                         (1, 0): 5, (1, 2): 6, (1, 4): 7, (1, 6): 8,
                         (2, 1): 9, (2, 3): 10, (2, 5): 11, (2, 7): 12,
                         (3, 0): 13, (3, 2): 14, (3, 4): 15, (3, 6): 16,
                         (4, 1): 17, (4, 3): 18, (4, 5): 19, (4, 7): 20,
                         (5, 0): 21, (5, 2): 22, (5, 4): 23, (5, 6): 24,
                         (6, 1): 25, (6, 3): 26, (6, 5): 27, (6, 7): 28,
                         (7, 0): 29, (7, 2): 30, (7, 4): 31, (7, 6): 32}
        return squareMapping[(row, col)]

    #Zobrist Hashing

    # How it works
    # 1. Create a table of random numbers for each piece in each square
    # 2. XOR the random number of the piece in the square
    # 3. When a move is made, XOR the random number of the piece in the square

    def randInt(self):
        return random.getrandbits(64)

    def pieceIndices(self, piece):
        if piece == 'b':
            return 0
        elif piece == 'w':
            return 1
        elif piece == 'B':
            return 2
        elif piece == 'W':
            return 3
        else:
            return -1

    def initTable(self):
        table = [[self.randInt() for _ in range(4)] for _ in range(32)]
        return table
    
    def hashBoard(self, board, zobristtable):
        hash = 0
        zobristtableCopy = copy.deepcopy(zobristtable)
        for row in range(rows):
            for col in range(cols):
                piece = board[row][col]
                if piece != '-':
                    squareIDX = self.get_square(row, col) - 1 # -1 because the square starts from 1
                    pieceIndex = self.pieceIndices(piece)
                    hash ^= zobristtableCopy[squareIDX][pieceIndex]
        return hash
    
    def storeTransposition(self, board, depth, value, alpha, beta):
        hash = self.hashBoard(board, self.zobristtable)
        self.hashtable[hash] = {'depth': depth, 'value': value, 'alpha': alpha,'beta': beta}

    def probeTransposition(self, board):
        hash = self.hashBoard(board, self.zobristtable)
        if hash in self.hashtable:
            return self.hashtable[hash]
        return None

class randomBot(Player):
    def __init__(self, turn, board):
        super().__init__(turn, board)
        self.user = False

    def shuffle_dict(self, dict):
        keys = list(dict.keys())
        np.random.shuffle(keys)
        return {key: dict[key] for key in keys}

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