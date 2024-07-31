# import pygame
# from pygame.locals import *
import copy

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

        self.movesDone = {'b': [], 'w': [], 'turn': 'b'}
        if board is None:
            self.board = [['-', 'b', '-', 'b', '-', 'b', '-', 'b'],
                          ['b', '-', 'b', '-', 'b', '-', 'b', '-'],
                          ['-', '-', '-', '-', '-', '-', '-', '-'],
                          ['-', '-', '-', '-', '-', '-', '-', '-'],
                          ['-', '-', '-', '-', '-', '-', '-', '-'],
                          ['-', '-', '-', '-', '-', '-', '-', '-'],
                          ['-', 'w', '-', 'w', '-', 'w', '-', 'w'],
                          ['w', '-', 'w', '-', 'w', '-', 'w', '-']]
            # self.board = [['-', '-', '-', '-', '-', '-', '-', '-'],
            #               ['b', '-', '-', '-', '-', '-', '-', '-'],
            #               ['-', 'W', '-', '-', '-', 'b', '-', '-'],
            #               ['-', '-', 'b', '-', '-', '-', 'b', '-'],
            #               ['-', 'b', '-', '-', '-', '-', '-', '-'],
            #               ['-', '-', 'b', '-', '-', '-', '-', '-'],
            #               ['-', '-', '-', '-', '-', '-', '-', '-'],
            #               ['w', '-', 'w', '-', 'w', '-', 'w', '-']]
            # self.board = [['-', '-', '-', '-', '-', '-', '-', '-'],
            #                 ['-', '-', '-', '-', 'w', '-', '-', '-'],
            #                 ['-', '-', '-', '-', '-', '-', '-', '-'],
            #                 ['w', '-', '-', '-', '-', '-', '-', '-'],
            #                 ['-', '-', '-', '-', '-', '-', '-', '-'],
            #                 ['b', '-', 'b', '-', '-', '-', '-', '-'],
            #                 ['-', '-', '-', 'W', '-', '-', '-', 'w'],
            #                 ['w', '-', 'w', '-', 'w', '-', '-', '-']]
            self.prevBoard = copy.deepcopy(self.board)
        else:
            self.board = board
        self.turn = turn # current turn
    
    # Draw board and pieces
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
        squareCount = 32
        for row in range(rows):
            for col in range((row % 2)-1, cols, 2):
                if col != -1:
                    font = pygame.font.SysFont('Arial', 20)
                    text = font.render(f'{squareCount}', True, (255, 0, 0))
                    squareCount -= 1
                    self.screen.blit(text, (col * squareSize + squareSize - text.get_width(), row * squareSize + squareSize - text.get_height()))

    def updateMovesDict(self, piece, move, turn):
        self.movesDone[turn].append([piece, move])
        self.movesDone['turn'] = turn