import pygame
from pygame.locals import *
from checkers import *
from player import *
import pyserial

def main():
    INITIAL_DEPTH = 5
    isGameOver = False
    running = True
    nummoves = 0

    """
    INIT
        (Arduino -> Jetson) 1. Get the board state from Arduino via USB
        (Jetson)            2. Match the board state with the current initial board state

        if board state is not matched:
        (Jetson -> Arduino) 3. Send the serial command to Arduino to show reset request message (LEDs)
        
    PLAY
        **Player moves first (Black)
        1. Get the board state from Arduino via USB (Get every x seconds)
        2. Match the board state with the current board state
        3. Decode which piece moved and where it moved

        if the move is valid:
        4. Update the board state
        5. AI's turn (White)

        if the move is invalid:
        4. Send the serial command to Arduino to show invalid move message (LEDs)
        5. Wait for the player to make a valid move

        6. Play until the game is over
        
    """



    board = Checkers()

    player1 = User('b', board.board, board.movesDone)
    # player1 = randomBot('b', board.board, board.movesDone)
    # player1 = Minimax('b', INITIAL_DEPTH, board.board, board.movesDone)
    # player1 = AlphaBeta('b', INITIAL_DEPTH, board.board, board.movesDone)
    
    # player2 = User('w', board.board, board.movesDone)
    # player2 = randomBot('w', board.board, board.movesDone)
    # player2 = Minimax('w', INITIAL_DEPTH, board.board, board.movesDone)
    player2 = AlphaBeta('w', INITIAL_DEPTH, board.board, board.movesDone)
    
    while running:
        isGameOver = is_game_over(board.board, board.movesDone)

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
                print('Moves Done:', board.movesDone)
                print('Moves:', nummoves, 'Turn:', board.turn)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
                if countBlack(board.board) > countWhite(board.board) or isGameOver == 'b':
                    print('Game Over, Winner: Black')
                    # winnerData(loop, 'b', filename)
                elif countBlack(board.board) < countWhite(board.board) or isGameOver == 'w':
                    print('Game Over, Winner: White')
                    # winnerData(loop, 'w', filename)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                print('Restarting...')
                main()
    pygame.quit()

if __name__ == '__main__':
    main()