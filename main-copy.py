import pygame
from pygame.locals import *
from checkers import *
from player import *
import serial
import time
import cv2 as cv
import numpy as np
import pyautogui
from PIL import ImageGrab
import copy

def main():
    board = Checkers()

    player1 = User('b', board.board, board.movesDone)
    # player1 = randomBot('b', board.board, board.movesDone)
    # player1 = Minimax('b', board.board, board.movesDone)
    # player1 = AlphaBeta('b', board.board, board.movesDone)
    
    # player2 = User('w', board.board, board.movesDone)
    # player2 = randomBot('w', board.board, board.movesDone)
    # player2 = Minimax('w', board.board, board.movesDone)
    player2 = AlphaBeta('w', board.board, board.movesDone)

    isGameOver = False
    running = True
    nummoves = 0
    
    pickerwindowBG = np.zeros((300, 512, 3), np.uint8)

    numGames = 0
    startedFlag = False

    while running:
        if startedFlag == False:
            print("Game started")
            startedFlag = True
            turn, prevBoard, bot, our = initGame(numGames)

        screen = ImageGrab.grab(all_screens=True)
        # print(f"Resolution: {screen.size}, Mode: {screen.mode}, Format: {screen.format}")

        # screen right : (1920, 0, 3840, 1080)
        # screen left : (0, 0, 1920, 1080)

        screen = screen.crop((1920, 0, 3840, 1080))
        screen = np.array(screen)

        screen_binary = convert_to_binary(screen)
        ret, corners = detect_checkers_board(screen)
        screen = cv.cvtColor(screen, cv.COLOR_BGR2RGB)

        if ret:
            print("Checkers board detected")
            screen_binary = cv.cvtColor(screen_binary, cv.COLOR_GRAY2RGB)

            # get the pieces
            pieces = detect_pieces(screen_binary, corners)
            print(len(pieces), pieces)
            for piece in pieces:
                x, y, w, h = piece
                cv.rectangle(screen_binary, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # update board state
            newBoard, sorted_pieces = update_board_state(screen_binary, corners)
            if turn == bot:
                selected, move = getMove(prevBoard, newBoard)

            screen_binary = crop_board(screen_binary, corners)
            
            cv.imshow('screen_binary', screen_binary)
        else:
            print("Checkers board not detected")
            # check game end
            endimg = cv.imread('end.png')
            matchinfo = match_images(screen, endimg)
            loc, w, h = matchinfo
            if loc[0].size > 0:
                print("Game ended")
                for pt in zip(*loc[::-1]):
                    cv.rectangle(screen, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
                
                # reset the board
                pyautogui.moveTo(loc[1][-1] + 200, loc[0][-1] + 310)
                pyautogui.click()
                numGames += 1
                startedFlag = False

            else:
                print("Game not ended")
        # show screen
        cv.imshow('screen', screen)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

        isGameOver = is_game_over(board.board, board.movesDone)

        board.screen.fill(BROWN)
        board.draw_board()
        board.draw_pieces()
        board.debug_text()
        pygame.display.flip()

        if not isGameOver:
            if board.turn == 'b':
                if player1.user:
                    row, col = getMove(prevBoard, newBoard)
                    board.board, board.turn = player1.update_board(board.board, row, col)
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
                    row, col = getMove(prevBoard, newBoard)
                    board.board, board.turn = player2.update_board(board.board, row, col)
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