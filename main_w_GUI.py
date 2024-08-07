import pygame
from pygame.locals import *
from checkers import *
from player import *
import serial
import time

# Uncomment pygames related code in checkers and players files to run this code

def initGame(numGames):
    board = Checkers()
    if numGames % 2 == 0:
        player1 = User('b', board.board, board.movesDone)
        player2 = AlphaBeta('w', board.board, board.movesDone)
        # player2 = Minimax('w', board.board, board.movesDone)
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
    player2 = AlphaBeta('w', board.board, board.movesDone)

    # player2 = User('w', board.board, board.movesDone)
    # player2 = Minimax('w', board.board, board.movesDone)
    isGameOver = False
    running = True

    while running:
        if board.turn == player1.ourTurn:
            isGameOver = is_game_over(board.board, board.movesDone, player1.mandatory_moves)
        elif board.turn == player2.botTurn:
            isGameOver = is_game_over(board.board, board.movesDone, player2.mandatory_moves)

        board.screen.fill(BROWN)
        board.draw_board()
        board.draw_pieces()
        board.debug_text()

        if not isGameOver:
            pygame.display.flip()
            if board.turn == 'b':
                if player1.user:
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

                else:
                    BPiece, BMove = player1.play(board.board)
                    if BPiece is not None and BMove is not None:
                        player1.prevCount = countBlack(board.board) + countWhite(board.board)
                        board.updateMovesDict(tuple(BPiece), tuple(BMove), board.turn)
                        board.board, board.turn = player1.update_board(board.board, BPiece, BMove)
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
                            WMove = row, col
                            prevTurn = board.turn
                            board.board, board.turn, WPiece = player2.handle_mouse_click(row, col, board.board)
                            if board.board != board.prevBoard:
                                board.updateMovesDict(tuple(WPiece), tuple(WMove), prevTurn)
                            player1.turn = board.turn
                            player2.turn = board.turn

                else:
                    WPiece, WMove = player2.play(board.board)
                    if WPiece is not None and WMove is not None:
                        player2.prevCount = countBlack(board.board) + countWhite(board.board)
                        board.updateMovesDict(tuple(WPiece), tuple(WMove), board.turn)
                        board.board, board.turn, _ = player2.update_board(board.board, WPiece, WMove)
                        player1.turn = board.turn
                        player2.turn = board.turn

            if board.board != board.prevBoard:
                nummoves += 1
                board.prevBoard = copy.deepcopy(board.board)
                with open('debug.txt', 'a') as f:
                    f.write(f'Game {numGames}: {isGameOver}, No. moves: {nummoves}\n')
                    f.write(f'Moves Done: {board.movesDone}\n\n')

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
                    main()
                    
    pygame.quit()

if __name__ == '__main__':
    main()