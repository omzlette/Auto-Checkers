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
        player1 = User('b', self.board)
        player2 = User('w', self.board)
        while running:
            # player1 = Minimax('b')
            # player2 = Minimax('w')

            # if self.turn == 'b' and not player1.user:
            #     _, piece, moveto = player1.playMM(self)
            #     self.select_piece(piece[0], piece[1])
            #     self.move_piece(moveto[0], moveto[1])

            # elif self.turn == 'w' and not player2.user:
            #     _, piece, moveto = player2.playMM(self)
            #     self.select_piece(piece[0], piece[1])
            #     self.move_piece(moveto[0], moveto[1])

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
                if event.type == pygame.MOUSEBUTTONDOWN and player1.user and player2.user:
                    if self.turn == 'b':
                        row, col = player1.get_mouse_pos()
                        player1.handle_mouse_click(row, col)
                    elif self.turn == 'w':
                        row, col = player2.get_mouse_pos()
                        player2.handle_mouse_click(row, col)
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

    def select_piece(self, row, col):
        # check if piece is valid and not conflicting with mandatory capture
        if self.mandatory_moves:
            if [row, col] in self.mandatory_moves:
                self.selectedPiece = (row, col)
                self.validMoves = self.get_valid_moves(row, col)
            else:
                print("You must capture")
        else:
            if self.board[row][col].lower() == 'b':
                if self.turn == 'b':
                    self.selectedPiece = (row, col)
                    self.validMoves = self.get_valid_moves(row, col)
                    print(self.selectedPiece, self.validMoves)
                else:
                    print("Not your turn")
            elif self.board[row][col].lower() == 'w':
                if self.turn == 'w':
                    self.selectedPiece = (row, col)
                    self.validMoves = self.get_valid_moves(row, col)
                else:
                    print("Not your turn")
            else:
                print("No piece selected")

    def get_valid_moves(self, row, col):
        moves = []
        capture_moves = self.can_capture(row, col)
        if capture_moves is None:
            if self.board[row][col] == 'b':
                if 0 <= row+1 <= 7 and 0 <= col-1 <= 7 and self.board[row+1][col-1] == '-':
                    moves.append([row+1, col-1])
                if 0 <= row+1 <= 7 and 0 <= col+1 <= 7 and self.board[row+1][col+1] == '-':
                    moves.append([row+1, col+1])

            elif self.board[row][col] == 'w':
                if 0 <= row-1 <= 7 and 0 <= col-1 <= 7 and self.board[row-1][col-1] == '-':
                    moves.append([row-1, col-1])
                if 0 <= row-1 <= 7 and 0 <= col+1 <= 7 and self.board[row-1][col+1] == '-':
                    moves.append([row-1, col+1])

            elif self.board[row][col] == 'B' or self.board[row][col] == 'W':
                directions = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
                for direction in directions:
                    for i in range(1, 8):
                        checkrow = row + direction[0] * i
                        checkcol = col + direction[1] * i
                        if 0 <= checkrow <= 7 and 0 <= checkcol <= 7:
                            if self.board[checkrow][checkcol] == '-':
                                moves.append([checkrow, checkcol])
                            else:
                                break
                        else:
                            break                            
        else:
            moves.extend(capture_moves)

        return moves if moves else None
    
    def can_capture(self, row, col):
        moves = []
        piece = self.board[row][col]
        if piece == 'B' or piece == 'W':
            capturable = 'w' if piece == 'B' else 'b'
            directions = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
            for direction in directions:
                for i in range(1, 8):
                    checkrow = row + direction[0] * i
                    checkcol = col + direction[1] * i
                    if 0 <= checkrow <= 7 and 0 <= checkcol <= 7:
                        if self.board[checkrow][checkcol] == '-':
                            continue
                        elif self.board[checkrow][checkcol].lower() == capturable:
                            if 0 <= checkrow+direction[0] <= 7 and 0 <= checkcol+direction[1] <= 7 and self.board[checkrow+direction[0]][checkcol+direction[1]] == '-':
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
                if 0 <= row+2 <= 7 and 0 <= col-2 <= 7 and self.board[row+1][col-1].lower() == 'w' and self.board[row+2][col-2] == '-':
                    self.capturePos.append([row+1, col-1]) if [row+1, col-1] not in self.capturePos else None
                    moves.append([row+2, col-2])
                if 0 <= row+2 <= 7 and 0 <= col+2 <= 7 and self.board[row+1][col+1].lower() == 'w' and self.board[row+2][col+2] == '-':
                    self.capturePos.append([row+1, col+1]) if [row+1, col+1] not in self.capturePos else None
                    moves.append([row+2, col+2])

            elif piece == 'w':
                if 0 <= row-2 <= 7 and 0 <= col-2 <= 7 and self.board[row-1][col-1].lower() == 'b' and self.board[row-2][col-2] == '-':
                    self.capturePos.append([row-1, col-1]) if [row-1, col-1] not in self.capturePos else None
                    moves.append([row-2, col-2])
                if 0 <= row-2 <= 7 and 0 <= col+2 <= 7 and self.board[row-1][col+1].lower() == 'b' and self.board[row-2][col+2] == '-':
                    self.capturePos.append([row-1, col+1]) if [row-1, col+1] not in self.capturePos else None
                    moves.append([row-2, col+2])

        return moves if moves else None

    def move_piece(self, row, col):
        if self.validMoves is not None and [row, col] in self.validMoves:
            self.board[row][col] = self.board[self.selectedPiece[0]][self.selectedPiece[1]]
            self.board[self.selectedPiece[0]][self.selectedPiece[1]] = '-'
            if self.capturePos != []:
                idxtoRemove = self.validMoves.index([row, col])
                self.board[self.capturePos[idxtoRemove][0]][self.capturePos[idxtoRemove][1]] = '-'
                self.capturePos = []
                self.mandatory_moves = self.get_mandatory_capture()
                # print('after capture:',self.mandatory_moves)
            self.make_king(row, col)
            self.selectedPiece = None
            self.validMoves = None
            if not self.mandatory_moves:
                self.turn = 'w' if self.turn == 'b' else 'b'
                self.mandatory_moves = self.get_mandatory_capture()
            # print(self.turn, self.mandatory_moves)
        else:
            if self.board[row][col].lower() == self.turn and self.mandatory_moves == []:
                self.selectedPiece = (row, col)
                self.validMoves = self.get_valid_moves(row, col)
            else:
                self.selectedPiece = None
                self.validMoves = None

    def get_mandatory_capture(self):
        mandatory_moves = []
        for row in range(rows):
            for col in range(cols):
                if (self.board[row][col] == 'b' or self.board[row][col] == 'B') and self.turn == 'b':
                    # print('b mandatory checking', row, col)
                    if self.can_capture(row, col):
                        # print('found b mandatory')
                        mandatory_moves.append([row, col])
                elif (self.board[row][col] == 'w' or self.board[row][col] == 'W') and self.turn == 'w':
                    if self.can_capture(row, col):
                        mandatory_moves.append([row, col])
        return mandatory_moves if mandatory_moves else []
    
    def make_king(self, row, col):
        if self.board[row][col] == 'b' and row == 7:
            self.board[row][col] = 'B'
        elif self.board[row][col] == 'w' and row == 0:
            self.board[row][col] = 'W'

    def make_move(self, piece, move):
        new_board = Checkers(self.turn, self.board)
        new_board.select_piece(piece[0], piece[1])
        new_board.move_piece(move[0], move[1])
        return new_board
    
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

    def copy_board(self):
        return copy.deepcopy(self.board)

class User(Player):
    def __init__(self, color, board):
        super().__init__(color, board)
        self.color = color
        self.user = True

    def get_mouse_pos(self):
        x, y = pygame.mouse.get_pos()
        row, col = y // squareSize, x // squareSize
        return row, col
    
    def handle_mouse_click(self, row, col):
        if (self.selectedPiece is None or self.selectedPiece == (row, col)):
            self.select_piece(row, col)
        else:
            self.move_piece(row, col)
            print(id(self.board))

class Minimax(Player):
    def __init__(self, color):
        super().__init__(color, None)
        self.oppColor = 'w' if self.color == 'b' else 'b'
        self.user = False

    def playMM(self, board):
        best_move = self.minimax(board, 5, True)
        print(best_move)
        return best_move
    
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

    # TODO: make get_all_moves() returns a dict of selectables and their moves then use it in minimax
    # TODO2: when using in minimax use selectables and loop through their moves and make_move() for each move

    def minimax(self, board, depth, maximizing):
        if depth == 0 or self.is_game_over(board):
            return self.evaluate_board(board), None, None
        
        if maximizing:
            maxEval = -np.inf
            for piece, moveto in self.get_all_moves(self.color, board).items():
                new_board = self.copy_board(board)
                eval, _, _ = self.minimax(new_board, depth-1, False)
                maxEval = max(maxEval, eval)
                if maxEval == eval:
                    bestPiece = piece
                    bestMove = moveto
            return maxEval, bestPiece, bestMove
        
        else:
            minEval = np.inf
            for piece, moveto in board.get_all_moves(self.oppColor, board).items():
                new_board = self.copy_board(board)
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
        game = Checkers(player, board)
        for row in range(rows):
            for col in range(cols):
                if board[row][col].lower() == player and game.get_valid_moves(row, col) is not None:
                    for move in game.get_valid_moves(row, col):
                        moves[(row, col)] = move
        return moves

    # def update_board(self, board, piece, move):
    #     new_board = board
    #     new_board.select_piece(piece[0], piece[1])
    #     new_board.move_piece(move[0], move[1])
    #     return new_board

def main():
    board = Checkers()
    board.run()

if __name__ == '__main__':
    main()