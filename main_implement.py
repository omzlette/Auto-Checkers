import pygame
from pygame.locals import *
from checkers import *
from player import *
from pathfinding import *
from functools import reduce
import serial
import time

ACK = 0x50;
CMPLT = 0x51;
NACK = 0x60;
DELIMITER = ";"

CONNECTION_REQUEST = 0xF0;
START = 0x99;
STOP = 0x98;
RESET = 0x97;

def initialize():
    board = Checkers()
    player1 = User('b', board.board, board.movesDone)
    player2 = AlphaBeta('w', board.board, board.movesDone)
    return player1, player2, board

def compare_board_data(board, data:bytes):
    byteboard = [[0 for i in range(8)] for j in range(8)]
    for row, byte in enumerate(data):
        for col in range(8):
            if board[row][col].lower() in ['b', 'w'] and byte & (128 >> col) == 0:
                return False
    return True

def main():
    connectedMCU = False
    startFlag = False

    while True:
        if not connectedMCU:
            try:
                ser = serial.Serial('/dev/ttyUSB0', 115200)
                ser.flushInput()
                ser.flushOutput()
                ser.write(0xF0)
                # receive 'ACK' from MCU
                RxBuffer = ser.read_until(DELIMITER)
                if RxBuffer == ACK:
                    connectedMCU = True
                    player1, player2, board = initialize()
                    isGameOver = False
                    running = True
                    del RxBuffer
            except:
                print('Waiting for MCU...')
                time.sleep(1)
                continue

        else:
            if not startFlag:
                if ser.read_until(DELIMITER) == START:
                    ser.write(0xF1) # Send data board request
                    # receive 'ACK' from MCU
                    RxBuffer = ser.read_until(DELIMITER)
                    if RxBuffer == ACK:
                        # receive board data from MCU
                        del RxBuffer
                        data = ser.read_until(DELIMITER)
                        boardMatch = compare_board_data(board.board, data)
                        if boardMatch:
                            ser.write(ACK)
                            startFlag = True
                    else:
                        continue
                    continue
            
            else:
                captureFlag = False
                while running:
                    if ser.read(1) == STOP or ser.read(1) == RESET:
                        # reset or stop
                        running = False
                        startFlag = False
                        break
                    
                    # do game logic
                    if board.turn == player1.ourTurn:
                        isGameOver = is_game_over(board.board, board.movesDone, player1.mandatory_moves)
                    elif board.turn == player2.botTurn:
                        isGameOver = is_game_over(board.board, board.movesDone, player2.mandatory_moves)

                    if not isGameOver:
                        if board.turn == player1.ourTurn:
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                                    print('Early Exiting...')
                                    running = False
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    row, col = player1.get_mouse_pos()
                                    BMove = row, col
                                    board.board, board.turn, BPiece = player1.handle_mouse_click(row, col, board.board)
                                    player1.turn = board.turn
                                    player2.turn = board.turn

                        else:
                            WPiece, WMove = player2.play(board.board)
                            if WPiece is not None and WMove is not None:
                                player2.prevCount = countBlack(board.board) + countWhite(board.board)
                                board.board, board.turn, WCapture = player2.update_board(board.board, WPiece, WMove)
                                if WCapture is not None:
                                    captureFlag = True
                                    mappedBoard, startpos, endpos = mapping(board.board, WCapture, None)
                                    pathPoint = astar(mappedBoard, startpos, endpos)
                                    flattenPath = [item for sublist in pathPoint for item in sublist]
                                    TxBuffer = [0xF2] + flattenPath + reduce(lambda x, y: x | y, [0xF2] + flattenPath)
                                    ser.write(TxBuffer)
                                    ser.write(DELIMITER)
                                
                                ser.read(1)
                                if ser.read(1) == CMPLT:
                                    if captureFlag:
                                        mappedBoard, startpos, endpos = mapping(board.board, WCapture, WMove)
                                        pathPoint = astar(mappedBoard, startpos, endpos)
                                        flattenPath = [item for sublist in pathPoint for item in sublist]
                                        TxBuffer = [0xF2] + flattenPath + reduce(lambda x, y: x | y, [0xF2] + flattenPath)
                                        ser.write(TxBuffer)
                                        ser.write(DELIMITER)
                                    
                                        ser.read(1)
                                        if ser.read(1) == CMPLT:
                                            player1.turn = board.turn
                                            player2.turn = board.turn
                                    
                                    else:
                                        player1.turn = board.turn
                                        player2.turn = board.turn
