import pygame
from pygame.locals import *
import numpy as np
import random
import copy

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
    
    ## Run game
    def run(self):
        running = True
        # player1 = User('b', self.board)
        player2 = User('w', self.board)
        player1 = Minimax('b', self.board)
        # player2 = Minimax('w', self.board)
        while running:
            if self.turn == 'b':
                if player1.user:
                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            row, col = player1.get_mouse_pos()
                            piece, moveto = player1.handle_mouse_click(row, col)
                else:
                    piece, moveto = player1.playMM(self.board, 5)

                if piece is not None and moveto is not None:
                    self.board, self.turn = player1.update_board(self.board, self.turn, piece, moveto)
                    piece, moveto = None, None
            elif self.turn == 'w':
                if player2.user:
                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            row, col = player2.get_mouse_pos()
                            piece, moveto = player2.handle_mouse_click(row, col)
                else:
                    piece, moveto = player2.playMM(self.board, 5)
                
                if piece is not None and moveto is not None:
                    self.board, self.turn = player2.update_board(self.board, self.turn, piece, moveto)
                    piece, moveto = None, None

            self.screen.fill(BROWN)
            self.draw_board()
            self.draw_pieces()
            self.debug_text()
            pygame.display.flip()

            if self.is_game_over(self.board):
                running = False
                if self.countBlack(self.board) == 0:
                    print("White wins")
                elif self.countWhite(self.board) == 0:
                    print("Black wins")
                else:
                    print("Draw")

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    print(self.turn, player1.user, player2.user)
        pygame.quit()
    
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

    def countBlack(self, board):
        count = 0
        for row in range(rows):
            for col in range(cols):
                if board[row][col] == 'b' or board[row][col] == 'B':
                    count += 1
        return count

    def countWhite(self, board):
        count = 0
        for row in range(rows):
            for col in range(cols):
                if board[row][col] == 'w' or board[row][col] == 'W':
                    count += 1
        return count
    
    def is_game_over(self, board):
        return self.countBlack(board) == 0 or self.countWhite(board) == 0

class Player():
    def __init__(self, turn, board):
        self.turn = turn
        self.board = board
        self.selectedPiece = None
        self.mandatory_moves = []
        self.validMoves = None
        self.capturePos = []

    def select_piece(self, row, col, board=None, turn=None):
        # check if piece is valid and not conflicting with mandatory capture
        if board is None:
            board = self.board
        if turn is None:
            turn = self.turn
        if self.mandatory_moves:
            if [row, col] in self.mandatory_moves and board[row][col].lower() == turn:
                self.selectedPiece = (row, col)
                self.validMoves = self.get_valid_moves(row, col, board)
            else:
                print("You must capture @", self.mandatory_moves, turn)
        else:
            if board[row][col].lower() == 'b':
                if turn == 'b':
                    self.selectedPiece = (row, col)
                    self.validMoves = self.get_valid_moves(row, col, board)
                else:
                    print("Not your turn")
            elif board[row][col].lower() == 'w':
                if turn == 'w':
                    self.selectedPiece = (row, col)
                    self.validMoves = self.get_valid_moves(row, col, board)
                else:
                    print("Not your turn")
            else:
                print("No piece selected")
        return self.selectedPiece

    def get_valid_moves(self, row, col, board=None):
        if board is None:
            board = self.board
        moves = []
        capture_moves = self.can_capture(row, col, board)
        if capture_moves is None:
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
        else:
            moves.extend(capture_moves)

        return moves if moves else None
    
    def can_capture(self, row, col, board=None):
        if board is None:
            board = self.board
        moves = []
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
                                self.capturePos.append([checkrow, checkcol]) if [checkrow, checkcol] not in self.capturePos else None
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
                    self.capturePos.append([row+1, col-1]) if [row+1, col-1] not in self.capturePos else None
                    moves.append([row+2, col-2])
                if 0 <= row+2 <= 7 and 0 <= col+2 <= 7 and board[row+1][col+1].lower() == 'w' and board[row+2][col+2] == '-':
                    self.capturePos.append([row+1, col+1]) if [row+1, col+1] not in self.capturePos else None
                    moves.append([row+2, col+2])

            elif piece == 'w':
                if 0 <= row-2 <= 7 and 0 <= col-2 <= 7 and board[row-1][col-1].lower() == 'b' and board[row-2][col-2] == '-':
                    self.capturePos.append([row-1, col-1]) if [row-1, col-1] not in self.capturePos else None
                    moves.append([row-2, col-2])
                if 0 <= row-2 <= 7 and 0 <= col+2 <= 7 and board[row-1][col+1].lower() == 'b' and board[row-2][col+2] == '-':
                    self.capturePos.append([row-1, col+1]) if [row-1, col+1] not in self.capturePos else None
                    moves.append([row-2, col+2])

        return moves if moves else None

    def check_can_move(self, row, col, board=None):
        if board is None:
            board = self.board
        if board[row][col] == 'b':
            if 0 <= row+1 <= 7 and 0 <= col-1 <= 7 and board[row+1][col-1] == '-':
                return True
            if 0 <= row+1 <= 7 and 0 <= col+1 <= 7 and board[row+1][col+1] == '-':
                return True
        elif board[row][col] == 'w':
            if 0 <= row-1 <= 7 and 0 <= col-1 <= 7 and board[row-1][col-1] == '-':
                return True
            if 0 <= row-1 <= 7 and 0 <= col+1 <= 7 and board[row-1][col+1] == '-':
                return True
        elif board[row][col] == 'B' or board[row][col] == 'W':
            directions = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
            for direction in directions:
                for i in range(1, 8):
                    checkrow = row + direction[0] * i
                    checkcol = col + direction[1] * i
                    if 0 <= checkrow <= 7 and 0 <= checkcol <= 7:
                        if board[checkrow][checkcol] == '-':
                            return True
                        else:
                            break
                    else:
                        break
        return False

    def get_mandatory_capture(self, board=None, turn=None):
        if board is None:
            board = self.board
        if turn is None:
            turn = self.turn
        mandatory_moves = []
        for row in range(rows):
            for col in range(cols):
                if board[row][col].lower() == turn and turn == 'b':
                    # print('b mandatory checking', row, col)
                    if self.can_capture(row, col, board):
                        # print('found b mandatory')
                        mandatory_moves.append([row, col])
                elif board[row][col].lower() == 'w' and turn == 'w':
                    if self.can_capture(row, col, board):
                        mandatory_moves.append([row, col])
        return mandatory_moves if mandatory_moves else []
    
    def make_king(self, row, col, board=None):
        if board is None:
            board = self.board
        if board[row][col] == 'b' and row == 7:
            board[row][col] = 'B'
        elif board[row][col] == 'w' and row == 0:
            board[row][col] = 'W'
    
    def countBlack(self, board):
        count = 0
        for row in range(rows):
            for col in range(cols):
                if board[row][col] == 'b' or board[row][col] == 'B':
                    count += 1
        return count

    def countWhite(self, board):
        count = 0
        for row in range(rows):
            for col in range(cols):
                if board[row][col] == 'w' or board[row][col] == 'W':
                    count += 1
        return count
    
    def is_game_over(self, board):
        return self.countBlack(board) == 0 or self.countWhite(board) == 0

    def copy_and_play(self, piece, moveto, turn):
        new_board = copy.deepcopy(self.board)
        self.select_piece(piece[0], piece[1], new_board, turn)
        new_board, _ = self.update_board(new_board, turn, piece, moveto)
        return new_board
    
    def update_board(self, board, turn, piece, move):
        new_board = copy.deepcopy(board)
        # if self.validMoves is not None and [row, col] in self.validMoves:
        #     board[row][col] = board[self.selectedPiece[0]][self.selectedPiece[1]]
        #     board[self.selectedPiece[0]][self.selectedPiece[1]] = '-'
        #     if self.capturePos != []:
        #         idxtoRemove = self.validMoves.index([row, col])
        #         board[self.capturePos[idxtoRemove][0]][self.capturePos[idxtoRemove][1]] = '-'
        #         self.capturePos = []
        #         self.mandatory_moves = self.get_mandatory_capture(board, turn)
        #         # print('after capture:',self.mandatory_moves)
        #     self.make_king(row, col, board)
        #     self.selectedPiece = None
        #     self.validMoves = None
        #     if not self.mandatory_moves:
        #         turn = 'w' if turn == 'b' else 'b'
        #         self.mandatory_moves = self.get_mandatory_capture(board, turn)
        #     # print(self.turn, self.mandatory_moves)
        # else:
        #     if board[row][col].lower() == turn and self.mandatory_moves == []:
        #         self.selectedPiece = (row, col)
        #         self.validMoves = self.get_valid_moves(row, col, board)
        #     else:
        #         self.selectedPiece = None
        #         self.validMoves = None
        # print(self.selectedPiece, self.validMoves)
        if self.validMoves is not None and move in self.validMoves:
            new_board[move[0]][move[1]] = new_board[piece[0]][piece[1]]
            new_board[piece[0]][piece[1]] = '-'
            if self.capturePos != []:
                idxtoRemove = self.validMoves.index(move)
                new_board[self.capturePos[idxtoRemove][0]][self.capturePos[idxtoRemove][1]] = '-'
                self.capturePos = []
                self.mandatory_moves = self.get_mandatory_capture(new_board, turn)
                # print('after capture:',self.mandatory_moves)
            self.make_king(move[0], move[1], new_board)
            self.selectedPiece = None
            self.validMoves = None
            if not self.mandatory_moves:
                turn = 'w' if turn == 'b' else 'b'
                self.mandatory_moves = self.get_mandatory_capture(new_board, turn)
            # print(self.turn, self.mandatory_moves)
        else:
            if new_board[piece[0]][piece[1]].lower() == turn and self.mandatory_moves == []:
                self.selectedPiece = piece
                self.validMoves = self.get_valid_moves(piece[0], piece[1], new_board)
            else:
                self.selectedPiece = None
                self.validMoves = None
        return new_board, turn

class User(Player):
    def __init__(self, turn, board):
        super().__init__(turn, board)
        self.turn = turn
        self.user = True

    def get_mouse_pos(self):
        x, y = pygame.mouse.get_pos()
        row, col = y // squareSize, x // squareSize
        return row, col
    
    def handle_mouse_click(self, row, col):
        if (self.selectedPiece is None or self.selectedPiece == (row, col)):
            piece = self.select_piece(row, col)
            return piece, None
        else:
            if self.check_can_move(row, col):
                moveto = [row, col]
            return piece, moveto

class Minimax(Player):
    def __init__(self, turn, board):
        super().__init__(turn, board)
        self.initTurn = 'b' if self.turn == 'b' else 'w'
        self.oppTurn = 'w' if self.turn == 'b' else 'b'
        self.user = False

    def playMM(self, board, depth=5):
        _, bestPiece, bestMove = self.minimax(board, depth, True)
        return bestPiece, bestMove
    
    def evaluate_board(self, board):
        value = 0
        for row in range(rows):
            for col in range(cols):
                if board[row][col] == 'b':
                    value += 1
                elif board[row][col] == 'w':
                    value -= 1
                elif board[row][col] == 'B':
                    value += 3
                elif board[row][col] == 'W':
                    value -= 3
        return value

    def minimax(self, board, depth, maximizing):
        if depth == 0 or self.is_game_over(board):
            return self.evaluate_board(board), None, None
        
        if maximizing:
            maxEval = -np.inf
            bestPiece = None
            bestMove = None
            for piece, moveto in self.get_all_moves(self.initTurn, board).items():
                new_board = self.copy_and_play(piece, moveto, self.initTurn)
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
            for piece, moveto in self.get_all_moves(self.oppTurn, board).items():
                new_board = self.copy_and_play(piece, moveto, self.oppTurn)
                eval, _, _ = self.minimax(new_board, depth-1, True)
                minEval = min(minEval, eval)
                if minEval == eval:
                    bestPiece = piece
                    bestMove = moveto
            return minEval, bestPiece, bestMove

    def minimaxAlphaBeta(self, board, depth, alpha, beta, maximizing):
        if depth == 0 or board.is_game_over():
            return self.evaluate(board)
        
        if maximizing:
            maxEval = -np.inf
            for move in board.get_all_moves():
                eval = self.minimaxAlphaBeta(move, depth-1, alpha, beta, False)
                maxEval = max(maxEval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return maxEval
        
        else:
            minEval = np.inf
            for move in board.get_all_moves():
                eval = self.minimaxAlphaBeta(move, depth-1, alpha, beta, True)
                minEval = min(minEval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return minEval
    
    def get_all_moves(self, player, board):
        moves = {}
        for row in range(rows):
            for col in range(cols):
                if board[row][col].lower() == player and self.get_valid_moves(row, col) is not None:
                    for move in self.get_valid_moves(row, col):
                        moves[(row, col)] = move
        return moves

def main():
    board = Checkers()
    board.run()

if __name__ == '__main__':
    main()