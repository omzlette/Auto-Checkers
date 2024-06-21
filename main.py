import pygame
from pygame.locals import *
from checkers import *
from player import *
import serial
import time

def initGame(numGames):
    board = Checkers()
    if numGames % 2 == 0:
        player1 = User('b', board.board, board.movesDone)
        # player2 = AlphaBeta('w', board.board, board.movesDone)
        player2 = Minimax('w', board.board, board.movesDone)
    else:
        player1 = AlphaBeta('b', board.board, board.movesDone)
        player2 = User('w', board.board, board.movesDone)

    return player1, player2, board

def main():
    numGames = 0

    isGameOver = False
    running = True
    nummoves = 0
    
    # player1, player2, board = initGame(numGames)
    board = Checkers()
    player1 = User('b', board.board, board.movesDone)
    # player2 = AlphaBeta('w', board.board, board.movesDone)
    player2 = Minimax('w', board.board, board.movesDone)
    # player2 = Greedy('w', board.board, board.movesDone)
    isGameOver = False
    running = True

    while running:
        isGameOver = is_game_over(board.board, board.turn, board.movesDone)

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
                            board.board, board.turn, selectedPiece = player1.handle_mouse_click(row, col, board.board)
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
                            board.board, board.turn, selectedPiece = player2.handle_mouse_click(row, col, board.board)
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
                if board.turn == 'w':
                    board.updateMovesDict(tuple(selectedPiece), (row, col), 'b')
                else:
                    board.updateMovesDict(tuple(bestPiece), tuple(bestMove), 'w')
                with open('debug.txt', 'a') as f:
                    f.write(f'Game {numGames}: {isGameOver}, No. moves: {nummoves}\n')
                    f.write(f'Moves Done: {board.movesDone}\n\n')

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
                if countBlack(board.board) > countWhite(board.board) or isGameOver == 'b':
                    print('Game Over, Winner: Black')
                elif countBlack(board.board) < countWhite(board.board) or isGameOver == 'w':
                    print('Game Over, Winner: White')
                else:
                    print('Game Over, Draw')

                with open('results.txt', 'a') as f:
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
                
                with open('results.txt', 'a') as f:
                    f.write(f'Game {numGames+1}: {isGameOver}, No. moves: {nummoves}\n')
                    f.write(f'Moves Done: {board.movesDone}\n\n')

                numGames += 1
                running = False
                    
    pygame.quit()

if __name__ == '__main__':
    main()