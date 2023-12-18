# Men move (1 block diagonally, forward only)
## Row can only +1 from current position
## Column can only +1 or -1 from current position

# King move (multiple blocks diagonally, forward and backward)
## Row can be any number from current position
## Column can be any number from current position

# Men Capture (2 blocks diagonally, forward only, over opponent)
## Row can only +2 from current position
## Column can only +2 or -2 from current position

# King Capture (multiple blocks diagonally, forward and backward, over opponent)
## Must land 1 slot past opponent
## Can capture accross the board

# Crowning
## w crown when moved to row = 0
## b crown when moved to row = 7

import numpy as np

class Game:
    def __init__(self):
        self.white_men = 'w'
        self.white_king = 'wk'
        self.black_men = 'b'
        self.black_king = 'bk'

        self.start_pos = [['-', 'b', '-', 'b', '-', 'b', '-', 'b'],
                          ['b', '-', 'b', '-', 'b', '-', 'b', '-'],
                          ['-', '-', '-', '-', '-', '-', '-', '-'],
                          ['-', '-', '-', '-', '-', '-', '-', '-'],
                          ['-', '-', '-', '-', '-', '-', '-', '-'],
                          ['-', '-', '-', '-', '-', '-', '-', '-'],
                          ['-', 'w', '-', 'w', '-', 'w', '-', 'w'],
                          ['w', '-', 'w', '-', 'w', '-', 'w', '-']]

        self.board = self.start_pos
        self.turn = 'b' # black goes first (black and white are the only two options)
        self.selected_piece_pos = None # position of the selected piece: (row, col)
        self.selected_piece_moves = None # moves that the selected piece can make: [(row, col), (row, col), ...]
        self.capture_pos = None # position of pieces that can be captured: [(row, col), (row, col), ...]
        self.to_move = None # position to move to: (row, col)
        self.to_capture = None # position of piece to capture: (row, col)

    def get_moves(self, row, col, board):
        moves = []
        if board[row][col] == 'b':
            capture_moves = self.can_capture(row, col, board)
            if capture_moves is None:
                if 0 <= row+1 <= 7 and 0 <= col-1 <= 7 and board[row+1][col-1] == '-':
                    moves.append([row+1, col-1])
                if 0 <= row+1 <= 7 and 0 <= col+1 <= 7 and board[row+1][col+1] == '-':
                    moves.append([row+1, col+1])
            else:
                moves.extend(capture_moves)

        elif board[row][col] == 'w':
            capture_moves = self.can_capture(row, col, board)
            if capture_moves is None:
                if 0 <= row-1 <= 7 and 0 <= col-1 <= 7 and board[row-1][col-1] == '-':
                    moves.append([row-1, col-1])
                if 0 <= row-1 <= 7 and 0 <= col+1 <= 7 and board[row-1][col+1] == '-':
                    moves.append([row-1, col+1])
            else:
                moves.extend(capture_moves)

        elif board[row][col] == 'bk' or board[row][col] == 'wk':
            capture_moves = self.can_capture_king(row, col, board)
            if capture_moves is None:
                ascent_factor = 7 - row if row < col else 7 - col
                ascent_diag_row, ascent_diag_col = row - ascent_factor, col + ascent_factor
                descent_diag_row, descent_diag_col = (row-min(row, col), col-min(row, col))

                while (0 <= descent_diag_row <= 7) and (0 <= descent_diag_col <= 7):
                    if board[descent_diag_row][descent_diag_col] == '-':
                        moves.append((descent_diag_row, descent_diag_col))
                    descent_diag_row += 1
                    descent_diag_col += 1

                while (0 <= ascent_diag_row <= 7) and (0 <= ascent_diag_col <= 7):
                    if board[ascent_diag_row][ascent_diag_col] == '-':
                        moves.append((ascent_diag_row, ascent_diag_col))
                    ascent_diag_row += 1
                    ascent_diag_col -= 1
            else:
                moves.extend(capture_moves)

        return moves if moves else None

    def can_capture(self, row, col, board):
        moves = []
        if board[row][col] == 'b':
            if 0 <= row+2 <= 7 and 0 <= col-2 <= 7 and board[row+1][col-1] == 'w':
                self.capture_pos.append((row+1, col-1))
                moves.append((row+2, col-2))
            if 0 <= row+2 <= 7 and 0 <= col+2 <= 7 and board[row+1][col+1] == 'w':
                self.capture_pos.append((row+1, col+1))
                moves.append((row+2, col+2))

        elif board[row][col] == 'w':
            if 0 <= row-2 <= 7 and 0 <= col-2 <= 7 and board[row-1][col-1] == 'b':
                self.capture_pos.append((row-1, col-1))
                moves.append((row-2, col-2))
            if 0 <= row-2 <= 7 and 0 <= col+2 <= 7 and board[row-1][col+1] == 'b':
                self.capture_pos.append((row-1, col+1))
                moves.append((row-2, col+2))

        return moves if moves else None

    def can_capture_king(self, row, col, board):
        moves = []
        capturables = ['w', 'wk'] if board[row][col] == 'bk' else ['b', 'bk']
        ascent_factor = 7 - row if row < col else 7 - col
        ascent_diag_row, ascent_diag_col = row - ascent_factor, col + ascent_factor
        descent_diag_row, descent_diag_col = (row-min(row, col), col-min(row, col))
        print(ascent_diag_row, ascent_diag_col, descent_diag_row, descent_diag_col)

        while (0 <= descent_diag_row <= 7) and (0 <= descent_diag_col <= 7):
            if board[descent_diag_row][descent_diag_col] in capturables:
                if 0 <= descent_diag_row-1 <= 7 and 0 <= descent_diag_col-1 <= 7 and descent_diag_row < row and descent_diag_col < col and board[descent_diag_row-1][descent_diag_col-1] == '-':
                    self.capture_pos.append((descent_diag_row, descent_diag_col))
                    moves.append((descent_diag_row-1, descent_diag_col-1))
                elif 0 <= descent_diag_row+1 <= 7 and 0 <= descent_diag_col+1 <= 7 and descent_diag_row > row and descent_diag_col > col and board[descent_diag_row+1][descent_diag_col+1] == '-':
                    self.capture_pos.append((descent_diag_row, descent_diag_col))
                    moves.append((descent_diag_row+1, descent_diag_col+1))
            descent_diag_row += 1
            descent_diag_col += 1

        while (0 <= ascent_diag_row <= 7) and (0 <= ascent_diag_col <= 7):
            if board[ascent_diag_row][ascent_diag_col] in capturables:
                if 0 <= ascent_diag_row-1 <= 7 and 0 <= ascent_diag_col+1 <= 7 and ascent_diag_row < row and ascent_diag_col > col and board[ascent_diag_row-1][ascent_diag_col+1] == '-': 
                    self.capture_pos.append((ascent_diag_row, ascent_diag_col))
                    moves.append((ascent_diag_row-1, ascent_diag_col-1))
                elif 0 <= ascent_diag_row+1 <= 7 and 0 <= ascent_diag_col-1 <= 7 and ascent_diag_row > row and ascent_diag_col < col and board[ascent_diag_row+1][ascent_diag_col-1] == '-':
                    self.capture_pos.append((ascent_diag_row, ascent_diag_col))
                    moves.append((ascent_diag_row+1, ascent_diag_col+1))
            ascent_diag_row += 1
            ascent_diag_col -= 1

        return moves if moves else None

    def is_king(self, tomove_row, tomove_col):
        if tomove_row == 0 or tomove_col == 7:
            return True
        return False
    
    def check_king(self, board):
        if self.turn == 'b':
            return any('bk' in row for row in board)
        elif self.turn == 'w':
            return any('wk' in row for row in board)
        
    def is_game_over(self):
        black = sum(row.count('b') + row.count('bk') for row in self.board)
        white = sum(row.count('w') + row.count('wk') for row in self.board)

        if black == 0 or white == 0:
            return True
        
        #3 times repetition

        #40 moves without capture or kinging

    def update_board(self):
        if self.to_move:
            (row, col) = self.to_move
            self.board[row][col] = self.board[self.selected_piece_pos[0]][self.selected_piece_pos[1]]
            if self.is_king(row, col) and 'k' not in self.board[row][col]:
                self.board[row][col] += 'k'
            self.board[self.selected_piece_pos[0]][self.selected_piece_pos[1]] = '-'
            self.selected_piece_pos = None
            self.selected_piece_moves = None
            self.capture_pos = None

        if self.to_capture:
            (row, col) = self.to_capture
            self.board[row][col] = '-'

    def show_board(self):
        while self.to_move or self.to_capture:
            row, col = self.to_move
            self.update_board()
            moves = self.get_moves(row, col, self.board)
            if len(moves) == 1:
                self.to_move = moves[0]
            elif len(moves) > 1:
                self.selected_piece_pos = (row, col)
                self.selected_piece_moves = moves
                break
            else:
                self.turn = 'w' if self.turn == 'b' else 'b' # switch turns
                self.to_move = None
                self.to_capture = None

        print('Turn:', 'Black\n' if self.turn == 'b' else 'White\n')
        print('  1 2 3 4 5 6 7 8')
        for i, row in enumerate(self.board):
            print(chr(i+97), end=' ')
            for col in row:
                print(col, end=' ')
            print()
        