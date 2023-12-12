import pygame
from pygame.locals import *
import numpy as np
import copy

#Check if using SSH
# os.environ["SDL_VIDEODRIVER"] = "wayland"

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
        # player2 = User('w', self.board)
        player1 = Minimax('b', 5, self.board)
        player2 = Minimax('w', 5, self.board)
        while running:
            self.screen.fill(BROWN)
            self.draw_board()
            self.draw_pieces()
            self.debug_text()
            pygame.display.flip()

            if self.turn == 'b':
                if player1.user:
                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            row, col = player1.get_mouse_pos()
                            player1.handle_mouse_click(row, col)
                else:
                    print('minimax 1', self.turn)
                    # bestPiece, bestMove = player1.playMM(self.board)
                    bestPiece, bestMove = player1.playAB(self.board)
                    if bestPiece is not None and bestMove is not None:
                        self.board, self.turn = player1.update_board(self.board, bestPiece, bestMove)
                        player1.turn = self.turn
                        player2.turn = self.turn
                    # self.turn = 'w'
            elif self.turn == 'w':
                if player2.user:
                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            row, col = player2.get_mouse_pos()
                            player2.handle_mouse_click(row, col)
                else:
                    print('minimax 2', self.turn)
                    # bestPiece, bestMove = player2.playMM(self.board)
                    bestPiece, bestMove = player2.playAB(self.board)
                    if bestPiece is not None and bestMove is not None:
                        self.board, self.turn = player2.update_board(self.board, bestPiece, bestMove)
                        player1.turn = self.turn
                        player2.turn = self.turn
                    # self.turn = 'b'

            if self.is_game_over(self.board):
                # running = False
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
        if self.countBlack(board) == 0 or self.countWhite(board) == 0:
            return True
        # for row in range(rows):
        #     for col in range(cols):
        #         if board[row][col].lower() == self.turn:
        #             if not self.check_valid_moves(row, col, self.turn, board):
        #                 return True
        return False
    
    # def check_valid_moves(self, row, col, turn, board):
    #     capturePiece = 'w' if turn == 'b' else 'b'
    #     if board[row][col].lower() == turn:
    #         if board[row][col] == 'b':
    #             if 0 <= row+1 <= 7 and 0 <= col-1 <= 7 and board[row+1][col-1] == '-':
    #                 return True
    #             if 0 <= row+1 <= 7 and 0 <= col+1 <= 7 and board[row+1][col+1] == '-':
    #                 return True
    #             if 0 <= row+2 <= 7 and 0 <= col-2 <= 7 and board[row+1][col-1].lower() == capturePiece and board[row+2][col-2] == '-':
    #                 return True
    #             if 0 <= row+2 <= 7 and 0 <= col+2 <= 7 and board[row+1][col+1].lower() == capturePiece and board[row+2][col+2] == '-':
    #                 return True

    #         elif board[row][col] == 'w':
    #             if 0 <= row-1 <= 7 and 0 <= col-1 <= 7 and board[row-1][col-1] == '-':
    #                 return True
    #             if 0 <= row-1 <= 7 and 0 <= col+1 <= 7 and board[row-1][col+1] == '-':
    #                 return True
    #             if 0 <= row-2 <= 7 and 0 <= col-2 <= 7 and board[row-1][col-1].lower() == capturePiece and board[row-2][col-2] == '-':
    #                 return True
    #             if 0 <= row-2 <= 7 and 0 <= col+2 <= 7 and board[row-1][col+1].lower() == capturePiece and board[row-2][col+2] == '-':
    #                 return True

    #         elif board[row][col] == 'B' or board[row][col] == 'W':
    #             directions = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
    #             for direction in directions:
    #                 for i in range(1, 8):
    #                     checkrow = row + direction[0] * i
    #                     checkcol = col + direction[1] * i
    #                     if 0 <= checkrow <= 7 and 0 <= checkcol <= 7:
    #                         if board[checkrow][checkcol] == '-':
    #                             return True
    #                         else:
    #                             break
    #                     else:
    #                         break
    #     return False

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
        if self.countBlack(board) == 0 or self.countWhite(board) == 0:
            return True
        # for row in range(rows):
        #     for col in range(cols):
        #         if board[row][col].lower() == self.turn:
        #             if self.get_valid_moves(row, col, board)[0] is None:
        #                 return True
        return False

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

    def evaluate_board(self, board):
        value = 0
        for row in range(rows):
            for col in range(cols):
                if board[row][col] == 'b':
                    value += 10
                elif board[row][col] == 'w':
                    value -= 10
                elif board[row][col] == 'B':
                    value += 50
                elif board[row][col] == 'W':
                    value -= 50
        return value

    def minimax(self, board, depth, maximizing):
        if depth == 0 or self.is_game_over(board):
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
        if depth == 0 or self.is_game_over(board):
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


def main():
    board = Checkers()
    board.run()

if __name__ == '__main__':
    main()