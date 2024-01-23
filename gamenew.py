import pygame
from pygame.locals import *
import numpy as np
import copy

# For recording resource usage
import os
import pandas as pd
import psutil
from jtop import jtop
import time

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (133, 84, 49)
LIGHT_BROWN = (252, 230, 215)

width, height = 800, 800
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
        for row in range(rows):
            for col in range(cols):
                font = pygame.font.SysFont('Arial', 20)
                text = font.render(f'{row}, {col}', True, (255, 0, 0))
                self.screen.blit(text, (col * squareSize + squareSize // 2 - text.get_width() // 2, row * squareSize + squareSize // 2 - text.get_height() // 2))

class Player():
    def __init__(self, turn, board):
        self.turn = turn
        self.board = board
        self.init_variables()

    def init_variables(self):
        self.selectedPiece = None
        self.mandatory_moves = []
        self.validMoves = None
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
                    selectedPiece = (row, col)
                    validMoves, capturePos = self.get_valid_moves(row, col, board)
                else:
                    print("Not your turn (White turn)")
            elif board[row][col].lower() == 'w':
                if turn == 'w':
                    selectedPiece = [row, col]
                    validMoves, capturePos = self.get_valid_moves(row, col, board)
                else:
                    print("Not your turn (Black turn)")
            else:
                print("No piece selected")
        return selectedPiece, validMoves, capturePos

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

    def get_mandatory_capture(self, turn, board):
        mandatory_moves = []
        for row in range(rows):
            for col in range(cols):
                if (board[row][col] == 'b' or board[row][col] == 'B') and turn == 'b':
                    if self.can_capture(row, col, board)[1]:
                        mandatory_moves.append([row, col])
                elif (board[row][col] == 'w' or board[row][col] == 'W') and turn == 'w':
                    if self.can_capture(row, col, board)[1]:
                        mandatory_moves.append([row, col])
        return mandatory_moves if mandatory_moves else []
    
    def make_king(self, row, col, board):
        if board[row][col] == 'b' and row == 7:
            board[row][col] = 'B'
        elif board[row][col] == 'w' and row == 0:
            board[row][col] = 'W'
        return board
    
    def move_piece(self, moveto, turn, board):
        [rowMove, colMove] = moveto
        if self.validMoves is not None and [rowMove, colMove] in self.validMoves:
            board[rowMove][colMove] = board[self.selectedPiece[0]][self.selectedPiece[1]]
            board[self.selectedPiece[0]][self.selectedPiece[1]] = '-'
            if self.capturePos != []:
                idxtoRemove = self.validMoves.index([rowMove, colMove])
                board[self.capturePos[idxtoRemove][0]][self.capturePos[idxtoRemove][1]] = '-'
                self.capturePos = []
                self.mandatory_moves = self.get_mandatory_capture(turn, board)
            board = self.make_king(rowMove, colMove, board)
            self.selectedPiece = None
            self.validMoves = None
            if not self.mandatory_moves:
                turn = 'w' if turn == 'b' else 'b'
        else:
            if board[rowMove][colMove].lower() == self.turn and self.mandatory_moves == []:
                self.selectedPiece = (rowMove, colMove)
                self.validMoves, self.capturePos = self.get_valid_moves(rowMove, colMove, board)
            else:
                self.selectedPiece = None
                self.validMoves = None
        return board, turn
    
    def get_all_moves(self, player, board):
        moves = {}
        mandatory_moves = self.get_mandatory_capture(player, board)
        if mandatory_moves:
            for piece in mandatory_moves:
                for move in self.get_valid_moves(piece[0], piece[1], board)[0]:
                    moves[tuple(piece)] = move
        else:
            for row in range(rows):
                for col in range(cols):
                    if board[row][col].lower() == player and self.get_valid_moves(row, col, board)[0] is not None:
                        for move in self.get_valid_moves(row, col, board)[0]:
                            moves[(row, col)] = move
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
    
    def shuffle_dict(self, dict):
        keys = list(dict.keys())
        np.random.shuffle(keys)
        return {key: dict[key] for key in keys}
    
def evaluate_board(self, board):
    # piece counting
    value = 0
    for row in range(rows):
        for col in range(cols):
            # No. of pieces (each piece = +1 point)
            if board[row][col] == self.botTurn:
                value += 1
            elif board[row][col] == self.oppTurn:
                value -= 1
            # No. of kings (each king = +5 points)
            if board[row][col] == self.botTurn.upper():
                value += 5
            elif board[row][col] == self.oppTurn.upper():
                value -= 5
            ### METHOD 1 ###
            # Each line (Men)
            if board[row][col] == self.botTurn:
                if row < 3:
                    value += row
                else:
                    value += 3
                # Crossed middle line (col)
                if col == 0 or col == 7:
                    value += 1
                else:
                    value += 2
            elif board[row][col] == self.oppTurn:
                if (7 - row) < 3:
                    value -= (7 - row)
                else:
                    value -= 3
                # Crossed middle line (col)
                if col == 0 or col == 7:
                    value -= 1
                else:
                    value -= 2
            ### METHOD 2 ###
            # Each line (Men)
            # if board[row][col] == self.botTurn:
            #     if row == 0:
            #         value += 2
            #     elif row == 1 and (col == 0 or col == 7):
            #         value += 1
            #     else:
            #         value += 3
            # elif board[row][col] == self.oppTurn:
            #     if row == 7:
            #         value -= 2
            #     elif row == 6 and (col == 0 or col == 7):
            #         value -= 1
            #     else:
            #         value -= 3
            
            # King's position (Kings)
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            if board[row][col] == self.botTurn.upper():
                for delta_row, delta_col in directions:
                    capture_row, capture_col = row + delta_row, col + delta_col
                    descent_diag_row, descent_diag_col = row - min(row, col), col - min(row, col)
                    while 0 <= capture_row < 8 and 0 <= capture_col < 8:
                        if board[capture_row][capture_col] == self.oppTurn:
                            if 0 <= descent_diag_row <= 7 and 0 <= descent_diag_col <= 7 and board[descent_diag_row][descent_diag_col] == ' ':
                                value += 1
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
                                value -= 1
                        capture_row += delta_row
                        capture_col += delta_col
                        descent_diag_row += delta_row
                        descent_diag_col += delta_col
                
    if is_game_over(board) == self.botTurn:
        value += 100
    elif is_game_over(board) == self.oppTurn:
        value -= 100
    return value

class User(Player):
    def __init__(self, turn, board):
        super().__init__(turn, board)
        self.user = True

    def get_mouse_pos(self):
        x, y = pygame.mouse.get_pos()
        row, col = y // squareSize, x // squareSize
        return row, col
    
    def handle_mouse_click(self, row, col):
        if (self.selectedPiece is None or self.selectedPiece == (row, col)):
            self.selectedPiece, self.validMoves, self.capturePos = self.select_piece(row, col, self.board)
        else:
            self.move_piece([row, col], self.turn, self.board)

class Minimax(Player):
    def __init__(self, turn, depth, board):
        super().__init__(turn, board)
        self.botTurn = 'b' if turn == 'b' else 'w'
        self.oppTurn = 'w' if turn == 'b' else 'b'
        self.user = False
        self.depth = depth

    def playMM(self, board):
        _, bestPiece, bestMove = self.minimax(board, self.depth, True)
        return bestPiece, bestMove
    
    def playAB(self, board):
        _, bestPiece, bestMove = self.minimaxAlphaBeta(board, self.depth, -np.inf, np.inf, True)
        return bestPiece, bestMove

    def minimax(self, board, depth, maximizing):
        if depth == 0 or is_game_over(board) in ['w', 'b']:
            return self.evaluate_board(board), None, None
        
        if maximizing:
            maxEval = -np.inf
            bestPiece = None
            bestMove = None
            movesdict = self.shuffle_dict(self.get_all_moves(self.botTurn, board))
            for piece, moveto in movesdict.items():
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
            movesdict = self.shuffle_dict(self.get_all_moves(self.oppTurn, board))
            for piece, moveto in movesdict.items():
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

class randomBot(Player):
    def __init__(self, turn, board):
        super().__init__(turn, board)
        self.user = False

    def playRandom(self, board):
        movesdict = self.shuffle_dict(self.get_all_moves(self.turn, board))
        piece = list(movesdict.keys())[0]
        moveto = movesdict[piece]
        return piece, moveto

def main():
    # time.sleep(10)
    # t_end = time.time() + (60 * 10)
    # while time.time() < t_end:
    #     writeData(None, None, 'data/idle_resource.csv')
    #     time.sleep(2)
    
    loops = 20
    # for depth1 in range(1, 6):
    for depth2 in range(1, 6):
        for loop in range(loops):
            filename = f'data/random/winner_experiment_random_mm{depth2}.csv'

            board = Checkers()
            running = True  
            nummoves = 0
            # player1 = User('b', board.board)
            # player2 = User('w', board.board)
            player1 = randomBot('b', board.board)
            # player2 = randomBot('w', board.board)
            # player1 = Minimax('b', depth1, board.board)
            player2 = Minimax('w', depth2, board.board)
            
            while running:
                isGameOver = is_game_over(board.board)
                if isGameOver in ['b', 'w']:
                    print(countBlack(board.board), countWhite(board.board))
                    running = False
                    print('Game Over, Winner: ', isGameOver, 'Game No.:', loop)
                    winnerData(loop, isGameOver, filename)

                board.screen.fill(BROWN)
                board.draw_board()
                board.draw_pieces()
                board.debug_text()
                pygame.display.flip()

                if not isGameOver:
                    if board.turn == 'b':
                        if player1.user:
                            for event in pygame.event.get():
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    row, col = player1.get_mouse_pos()
                                    player1.handle_mouse_click(row, col)
                        else:
                            bestPiece, bestMove = player1.playRandom(board.board)
                            # bestPiece, bestMove = player1.playMM(board.board)
                            # bestPiece, bestMove = player1.playAB(board.board)
                            if bestPiece is not None and bestMove is not None:
                                board.board, board.turn = player1.update_board(board.board, bestPiece, bestMove)
                                player1.turn = board.turn
                                player2.turn = board.turn
                            # self.turn = 'w'
                        nummoves += 1
                        
                    elif board.turn == 'w':
                        if player2.user:
                            for event in pygame.event.get():
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    row, col = player2.get_mouse_pos()
                                    player2.handle_mouse_click(row, col)
                        else:
                            bestPiece, bestMove = player2.playMM(board.board)
                            # bestPiece, bestMove = player2.playAB(board.board)
                            if bestPiece is not None and bestMove is not None:
                                board.board, board.turn = player2.update_board(board.board, bestPiece, bestMove)
                                player1.turn = board.turn
                                player2.turn = board.turn
                            # self.turn = 'b'
                        nummoves += 1        
                
                # writeData(loop, nummoves, 'data/resource_usage.csv')

                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        running = False
                        if countBlack(board.board) > countWhite(board.board):
                            print('Game Over, Winner: Black', 'Game No.:', loop)
                            winnerData(loop, 'b', filename)
                        elif countBlack(board.board) < countWhite(board.board):
                            print('Game Over, Winner: White', 'Game No.:', loop)
                            winnerData(loop, 'w', filename)
                        # else:
                        #     running = True
                        #     player1 = Minimax('b', depth1, board.board)
                        #     player2 = Minimax('w', depth2, board.board)
                        #     board = Checkers()
                        #     nummoves = 0
                #     if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                #         print(self.turn, player1.user, player2.user)
            pygame.quit()

def winnerData(loop, winner, filename='winner.csv'):
    if os.path.isfile(filename):
        df = pd.read_csv(filename)
    else:
        df = pd.DataFrame(columns=['Game', 'Winner'])
    pd.concat([df, pd.DataFrame([[loop, winner]], columns=['Game', 'Winner'])]).to_csv(filename, index=False)

def writeData(loopcount, nummoves, filename='resource_usage.csv'):
    if os.path.isfile(filename):
        df = pd.read_csv(filename)
    else:
        df = pd.DataFrame(columns=['CPU', 'GPU', 'RAM', 'Moves', 'Loop'])
    with jtop() as jetson:
        pd.concat([df, pd.DataFrame([[psutil.cpu_percent(), jetson.stats['GPU'], psutil.virtual_memory()[3]/1e+9, nummoves, loopcount]], columns=['CPU', 'GPU', 'RAM', 'Moves', 'Loop'])]).to_csv(filename, index=False)

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

    xb = np.char.lower(np.array(board)) == 'b'
    pieceloclist = np.asarray(np.where(xb)).T.tolist()
    for pieceloc in pieceloclist:
        tempb.append(check_basic_valid_moves(pieceloc[0], pieceloc[1], board))
    if all(not i for i in tempb) or countBlack(board) == 0:
        return 'w'

    tempw = []
    xw = np.char.lower(np.array(board)) == 'w'
    pieceloclist = np.asarray(np.where(xw)).T.tolist()
    for pieceloc in pieceloclist:
        tempw.append(check_basic_valid_moves(pieceloc[0], pieceloc[1], board))
    if all(not i for i in tempw) or countWhite(board) == 0:
        return 'b'
    
    return False

def check_basic_valid_moves(row, col, board):
    if board[row][col].lower() == 'b' or board[row][col] == 'W':
        if 0 <= row+1 <= 7 and 0 <= col-1 <= 7 and board[row+1][col-1] == '-':
            return True
        if 0 <= row+1 <= 7 and 0 <= col+1 <= 7 and board[row+1][col+1] == '-':
            return True
    elif board[row][col].lower() == 'w' or board[row][col] == 'B':
        if 0 <= row-1 <= 7 and 0 <= col-1 <= 7 and board[row-1][col-1] == '-':
            return True
        if 0 <= row-1 <= 7 and 0 <= col+1 <= 7 and board[row-1][col+1] == '-':
            return True
    return False

if __name__ == '__main__':
    main()