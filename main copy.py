import pygame
from pygame.locals import *
from checkers import *
from player import *
import pandas as pd
import serial
import time

def initGame():
    board = Checkers()
    player1 = User('b', board.board, board.movesDone)
    player2 = User('w', board.board, board.movesDone)

    return player1, player2, board

def main():
    numGames = 0

    isGameOver = False
    running = True
    nummoves = 0
    BNumMoves = 0
    WNumMoves = 0
    
    # player1, player2, board = initGame(numGames)
    board = Checkers()
    player1 = User('b', board.board, board.movesDone)
    player2 = User('w', board.board, board.movesDone)
    movesDone = {'b': [[(1, 6), (2, 7)], [(0, 5), (1, 6)], [(1, 2), (2, 1)], [(2, 1), (3, 2)], [(1, 4), (2, 3)], [(0, 1), (1, 2)], [(1, 2), (3, 0)], [(1, 0), (3, 2)], [(2, 7), (3, 6)], [(3, 6), (4, 7)], [(4, 7), (6, 5)], [(3, 2), (4, 1)], [(0, 3), (1, 2)], [(1, 6), (2, 5)], [(2, 5), (3, 6)], [(2, 3), (3, 2)], [(3, 6), (4, 7)], [(4, 7), (6, 5)], [(4, 7), (6, 5)], [(6, 5), (7, 4)], [(4, 1), (5, 0)], [(7, 4), (5, 6)], [(0, 7), (1, 6)], [(5, 6), (7, 4)], [(7, 4), (5, 6)], [(5, 6), (4, 7)], [(4, 7), (7, 4)], [(7, 4), (4, 1)], [(4, 1), (5, 2)], [(1, 6), (2, 7)], [(3, 0), (4, 1)], [(5, 2), (4, 3)], [(4, 3), (3, 4)], [(3, 4), (0, 7)], [(0, 7), (5, 2)], [(5, 2), (0, 7)], [(0, 7), (5, 2)], [(5, 2), (2, 5)], [(2, 5), (1, 4)], [(4, 1), (5, 2)], [(1, 4), (2, 3)], [(2, 3), (1, 4)], [(1, 4), (3, 2)], [(3, 2), (1, 4)], [(1, 4), (4, 7)], [(4, 7), (2, 5)], [(2, 5), (3, 6)], [(3, 6), (4, 5)], [(4, 5), (5, 4)], [(5, 4), (4, 5)], [(4, 5), (5, 4)], [(5, 4), (3, 6)], [(3, 6), (2, 5)], [(2, 5), (5, 2)], [(5, 2), (4, 1)], [(4, 1), (5, 2)], [(5, 2), (0, 7)], [(0, 7), (5, 2)]], 'w': [[(6, 1), (5, 0)], [(5, 0), (4, 1)], [(4, 1), (3, 0)], [(6, 3), (5, 2)], [(3, 0), (2, 1)], [(5, 2), (4, 3)], [(4, 3), (2, 1)], [(6, 5), (5, 4)], [(6, 7), (5, 6)], [(5, 4), (4, 5)], [(7, 4), (5, 6)], [(4, 5), (3, 6)], [(3, 6), (2, 7)], [(2, 7), (1, 6)], [(1, 6), (0, 5)], [(0, 5), (1, 4)], [(1, 4), (0, 3)], [(2, 1), (4, 3)], [(4, 3), (3, 2)], [(3, 2), (2, 1)], [(2, 1), (1, 0)], [(1, 0), (0, 1)], [(0, 1), (1, 0)], [(1, 0), (0, 1)], [(0, 1), (1, 0)], [(1, 0), (0, 1)], [(0, 1), (1, 0)], [(1, 0), (0, 1)], [(0, 1), (1, 0)], [(1, 0), (0, 1)], [(0, 1), (1, 0)], [(1, 0), (0, 1)], [(0, 1), (1, 0)], [(1, 0), (0, 1)], [(0, 1), (1, 0)], [(1, 0), (0, 1)], [(0, 1), (1, 0)], [(1, 0), (0, 1)], [(0, 1), (1, 0)], [(1, 0), (4, 3)], [(4, 3), (6, 1)], [(6, 1), (5, 2)], [(5, 2), (4, 1)], [(4, 1), (3, 0)], [(3, 0), (2, 1)], [(2, 1), (1, 0)], [(1, 0), (0, 1)], [(0, 1), (1, 0)], [(1, 0), (0, 1)], [(0, 1), (1, 0)], [(1, 0), (0, 1)], [(0, 1), (1, 0)], [(1, 0), (0, 1)], [(0, 1), (1, 0)], [(1, 0), (0, 1)], [(0, 1), (1, 0)], [(1, 0), (0, 1)]], 'turn': 'w'}

    isGameOver = False
    running = True

    while running:
        if board.turn == player1.ourTurn:
            isGameOver = is_game_over(board.board, board.movesDone, player1.mandatory_moves)
        elif board.turn == player2.ourTurn:
            isGameOver = is_game_over(board.board, board.movesDone, player2.mandatory_moves)

        board.screen.fill(BROWN)
        board.draw_board()
        board.draw_pieces()
        board.debug_text()

        if not isGameOver:
            pygame.display.flip()
            if board.turn == 'b':
                if player1.user:
                    try:
                        BPiece, BMove = movesDone['b'][BNumMoves]
                        print("B:", movesDone['b'][BNumMoves], BNumMoves, nummoves)
                        BNumMoves += 1
                        board.board, board.turn, _ = player1.update_board(board.board, BPiece, BMove)
                        player1.turn = board.turn
                        player2.turn = board.turn
                        waitNext = True
                        while waitNext:
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                                    print('Early Exiting...')
                                    waitNext = False
                                    running = False
                                    break
                                if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                                    waitNext = False
                                    break
                    
                    except IndexError:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                                print('Early Exiting...')
                                running = False
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                row, col = player1.get_mouse_pos()
                                BMove = row, col
                                prevTurn = board.turn
                                board.board, board.turn, BPiece = player1.handle_mouse_click(row, col, board.board)
                                if board.board != board.prevBoard:
                                    board.updateMovesDict(tuple(BPiece), tuple(BMove), prevTurn)
                                player1.turn = board.turn
                                player2.turn = board.turn
                
            elif board.turn == 'w':
                if player2.user:
                    try:
                        WPiece, WMove = movesDone['w'][WNumMoves]
                        print("W:", movesDone['w'][WNumMoves], WNumMoves, nummoves)
                        WNumMoves += 1
                        board.board, board.turn, _ = player2.update_board(board.board, WPiece, WMove)
                        player1.turn = board.turn
                        player2.turn = board.turn
                        waitNext = True
                        while waitNext:
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                                    print('Early Exiting...')
                                    waitNext = False
                                    running = False
                                    break
                                if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                                    waitNext = False
                                    break

                    except IndexError:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                                print('Early Exiting...')
                                running = False
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                row, col = player2.get_mouse_pos()
                                WMove = row, col
                                prevTurn = board.turn
                                board.board, board.turn, WPiece = player2.handle_mouse_click(row, col, board.board)
                                if board.board != board.prevBoard:
                                    board.updateMovesDict(tuple(WPiece), tuple(WMove), prevTurn)
                                player1.turn = board.turn
                                player2.turn = board.turn

            if board.board != board.prevBoard:
                nummoves += 1
                board.prevBoard = copy.deepcopy(board.board)

        else:
            alphaRect = pygame.Surface((400, 200))
            alphaRect.set_alpha(128)
            alphaRect.fill((255, 255, 255))
            board.screen.blit(alphaRect, (width // 2 - 200, height // 2 - 100))
            font = pygame.font.SysFont('Arial', 60)
            text = font.render('Game Over', True, (0, 0, 0))
            board.screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                    if countBlack(board.board) > countWhite(board.board) or isGameOver == 'b':
                        print('Game Over, Winner: Black')
                    elif countBlack(board.board) < countWhite(board.board) or isGameOver == 'w':
                        print('Game Over, Winner: White')
                    else:
                        print('Game Over, Draw')

                    with open('results-replay.txt', 'a') as f:
                        f.write(f'Game {numGames+1}: {isGameOver}, No. moves: {nummoves}\n')
                        f.write(f'Moves Done: {board.movesDone}\n\n')

                    numGames += 1
                    running = False
                    
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    if countBlack(board.board) > countWhite(board.board) or isGameOver == 'b':
                        print('Game Over, Winner: Black')
                    elif countBlack(board.board) < countWhite(board.board) or isGameOver == 'w':
                        print('Game Over, Winner: White')
                    else:
                        print('Game Over, Draw')
                    print('Restarting...')
                    
                    with open('results-replay.txt', 'a') as f:
                        f.write(f'Game {numGames+1}: {isGameOver}, No. moves: {nummoves}\n')
                        f.write(f'Moves Done: {board.movesDone}\n\n')

                    numGames += 1
                    running = False
                    main()
                    
    pygame.quit()

if __name__ == '__main__':
    main()