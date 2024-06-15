import pygame
from pygame.locals import *
from checkers import *
from player import *
from autoExperiment import *
import copy
import serial

def initGame(numGames):
    board = Checkers()
    if numGames % 2 == 0:
        player1 = User('b', board.board, board.movesDone)
        player2 = AlphaBeta('w', board.board, board.movesDone)
    else:
        player1 = AlphaBeta('b', board.board, board.movesDone)
        player2 = User('w', board.board, board.movesDone)

    return player1, player2, board

def main():
    isGameOver = False
    running = True
    nummoves = 0

    numGames = 0
    
    experiment = serial.Serial('/dev/ttyUSB3',
                                 baudrate=115200,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 bytesize=serial.EIGHTBITS,
                                 timeout=1)

    while numGames < 50:
        while running:
            player1, player2, board = initGame(numGames)

            isGameOver = is_game_over(board.board, board.movesDone)

            board.screen.fill(BROWN)
            board.draw_board()
            board.draw_pieces()
            board.debug_text()
            pygame.display.flip()

            if not isGameOver:
                if board.turn == 'b':
                    if player1.user:
                        RxBuffer = experiment.readline().decode('utf-8').strip()
                        if RxBuffer and 'm' in RxBuffer:
                            RxBuffer = RxBuffer.replace('m', '')
                            selectedPiece, move = RxBuffer.split(',')
                            selectedPiece = tuple(map(int, selectedPiece.split(';')))
                            move = tuple(map(int, move.split(';')))

                            board.board, board.turn = player1.update_board(board.board, selectedPiece, move)
                            RxBuffer = ''
                            player1.turn = board.turn
                            player2.turn = board.turn

                    else:
                        bestPiece, bestMove = player1.play(board.board)
                        if bestPiece is not None and bestMove is not None:
                            player1.prevCount = countBlack(board.board) + countWhite(board.board)
                            board.board, board.turn = player1.update_board(board.board, bestPiece, bestMove)

                            TxBuffer = f'{bestPiece[0]};{bestPiece[1]},{bestMove[0]};{bestMove[1]}\n'
                            experiment.write(TxBuffer.encode('utf-8'))

                            TxBuffer = ''
                            player1.turn = board.turn
                            player2.turn = board.turn
                    
                elif board.turn == 'w':
                    if player2.user:
                        RxBuffer = experiment.readline().decode('utf-8').strip()
                        if RxBuffer and 'm' in RxBuffer:
                            RxBuffer = RxBuffer.replace('m', '')
                            selectedPiece, move = RxBuffer.split(',')
                            selectedPiece = tuple(map(int, selectedPiece.split(';')))
                            move = tuple(map(int, move.split(';')))

                            board.board, board.turn = player2.update_board(board.board, selectedPiece, move)
                            RxBuffer = ''
                            player1.turn = board.turn
                            player2.turn = board.turn


                    else:
                        bestPiece, bestMove = player2.play(board.board)
                        if bestPiece is not None and bestMove is not None:
                            player2.prevCount = countBlack(board.board) + countWhite(board.board)
                            board.board, board.turn = player2.update_board(board.board, bestPiece, bestMove)

                            TxBuffer = f'm{bestPiece[0]};{bestPiece[1]},{bestMove[0]};{bestMove[1]}\n'
                            experiment.write(TxBuffer.encode('utf-8'))

                            TxBuffer = ''
                            player1.turn = board.turn
                            player2.turn = board.turn

                if board.board != board.prevBoard:
                    nummoves += 1
                    board.prevBoard = copy.deepcopy(board.board)
                    if board.turn == 'w':
                        board.updateMovesDict(tuple(selectedPiece), tuple(move), 'b')
                    else:
                        board.updateMovesDict(tuple(bestPiece), tuple(bestMove), 'w')

            else:
                running = False
                numGames += 1
                with open('results.txt', 'a') as f:
                    f.write(f'Game {numGames}: {isGameOver}, No. moves: {nummoves}\n')
                    f.write(f'Moves Done: {board.movesDone}\n\n')

    pygame.quit()

if __name__ == '__main__':
    main()