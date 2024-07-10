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
DISCONNECTION_REQUEST = 0xFF;
START = 0x99;
STOP = 0x98;
RESET = 0x97;

def initialize():
    board = Checkers()
    player1 = User('b', board.board, board.movesDone)
    player2 = AlphaBeta('w', board.board, board.movesDone)
    return player1, player2, board

def compare_board_data(board, data:bytes):
    for row, byte in enumerate(data):
        for col in range(8):
            if board[row][col].lower() in ['b', 'w'] and byte & (128 >> col) == 0:
                return False
    return True

def get_move(prevBoard, newBoard):
    # exclusive to black
    pieceFrom = None
    pieceTo = None
    capturedList = []
    for row in range(8):
        for col in range(8):
            if prevBoard[row][col] != '-' and newBoard[row][col] == 0:
                if prevBoard[row][col] in ['b', 'B']:
                    pieceFrom = (row, col)
                elif prevBoard[row][col] in ['w', 'W']:
                    capturedList.append((row, col))
            if prevBoard[row][col] in ['-'] and newBoard[row][col] != 0:
                pieceTo = (row, col)

    if capturedList:
        selectedList = [pieceFrom]
        moves = []
        
        for row, col in capturedList:
            rowDelta = row - pieceFrom[0]
            rowDelta = rowDelta // abs(rowDelta)
            colDelta = col - pieceFrom[1]
            colDelta = colDelta // abs(colDelta)
            pieceFrom = (row + rowDelta, col + colDelta)
            moves.append(pieceFrom)

        selectedList.extend(moves[:-1])
    elif pieceFrom is not None and pieceTo is not None:
        selectedList = [pieceFrom]
        moves = [pieceTo]
    else:
        selectedList = []
        moves = []

    return selectedList, moves, capturedList

def checkLegalMove(selectedList, moveList, capturedList):
    if selectedList == [] or moveList == []:
        return None
    elif selectedList != [] and moveList != []:
        if len(selectedList) != len(moveList):
            return False
        elif len(selectedList) == len(moveList):
            for i in range(len(selectedList)):
                if selectedList[i] == moveList[i]:
                    return False
                if capturedList != []:
                    if moveList[i] in capturedList:
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
                ser.write(DISCONNECTION_REQUEST)
                ser.write(DELIMITER)
                RxBuffer = ser.read_until(DELIMITER)
                if RxBuffer == ACK:
                    ser.write(CONNECTION_REQUEST)
                    ser.write(DELIMITER)
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
                    ser.write(ACK)
                    ser.write(DELIMITER)

                    ser.write(0xF1) # Send data board request
                    ser.write(DELIMITER)
                    # receive 'ACK' from MCU
                    RxBuffer = ser.read_until(DELIMITER)
                    if RxBuffer == ACK:
                        # receive board data from MCU
                        data = ser.read_until(DELIMITER)
                        boardMatch = compare_board_data(board.board, data)
                        ser.write(ACK)
                        ser.write(DELIMITER)
                        if boardMatch:
                            startFlag = True
                            TxBuffer = [0xF3] + [0b00010000] + reduce(lambda x, y: x | y, [0xF3, 0b00010000])
                        else:
                            TxBuffer = [0xF3] + [0b01000000] + reduce(lambda x, y: x | y, [0xF3, 0b01000000])
                            ser.write(bytes(TxBuffer))
                            ser.write(DELIMITER)
                        del data, RxBuffer
            
            else:
                captureFlag = False
                userPlayed = False
                botPlayed = False
                while running:
                    if ser.read_until(DELIMITER) == STOP or ser.read_until(DELIMITER) == RESET:
                        ser.write(ACK)
                        ser.write(DELIMITER)
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
                        if board.turn == 'b':
                            userPlayed = False
                            user_time = time.time()
                            while time.time() - user_time < 3:
                                ser.write(0xF1) # Send data board request
                                ser.write(DELIMITER)
                                RxBuffer = ser.read_until(DELIMITER)
                                if RxBuffer == ACK:
                                    # receive board data from MCU
                                    del RxBuffer
                                    data = ser.read_until(DELIMITER)
                                    BPieces, BMoves, BCaptures = checkLegalMove(board.board, data)
                                    ser.write(ACK)
                                    ser.write(DELIMITER)
                                    legalMove = checkLegalMove(BPieces, BMoves, BCaptures)
                                    if legalMove is True:
                                        for BPiece, BMove in zip(BPieces, BMoves):
                                            board.board, board.turn, _ = player1.update_board(board.board, BPiece, BMove)
                                            board.updateMovesDict(BPiece, BMove, 'b')
                                        TxBuffer = [0xF3] + [0b00100000] + reduce(lambda x, y: x | y, [0xF3, 0b00100000])
                                    elif legalMove is False:
                                        TxBuffer = [0xF3] + [0b10010000] + reduce(lambda x, y: x | y, [0xF3, 0b10010000])
                                    else:
                                        continue
                                    
                                    ser.write(bytes(TxBuffer))
                                    ser.write(DELIMITER)
                                    while userPlayed == False:
                                        RxBuffer = ser.read_until(DELIMITER)
                                        if RxBuffer == ACK:
                                            player1.turn = board.turn
                                            player2.turn = board.turn
                                            userPlayed = True
                                            del data
                                            del RxBuffer
                                            break
                                        else:
                                            TxBuffer = [0xF3] + [0b00100000] + reduce(lambda x, y: x | y, [0xF3, 0b00100000])
                                            ser.write(bytes(TxBuffer))
                                            ser.write(DELIMITER)

                        else:
                            botPlayed = False
                            WPiece, WMove = player2.play(board.board)
                            if WPiece is not None and WMove is not None:
                                player2.prevCount = countBlack(board.board) + countWhite(board.board)
                                board.board, board.turn, WCapture = player2.update_board(board.board, WPiece, WMove)
                                board.updateMovesDict(WPiece, WMove, 'w')
                                if WCapture is not None:
                                    captureFlag = True
                                    mappedBoard, startpos, endpos = mapping(board.board, WCapture, None)
                                    pathPoint = astar(mappedBoard, startpos, endpos)
                                    flattenPath = [item for sublist in pathPoint for item in sublist]
                                    TxBuffer = [0xF2] + flattenPath + reduce(lambda x, y: x | y, [0xF2] + flattenPath)
                                    ser.write(bytes(TxBuffer))
                                    ser.write(DELIMITER)
                                
                                ser.read(1)
                                if ser.read(1) == CMPLT:
                                    if captureFlag:
                                        mappedBoard, startpos, endpos = mapping(board.board, WCapture, WMove)
                                        pathPoint = astar(mappedBoard, startpos, endpos)
                                        flattenPath = [item for sublist in pathPoint for item in sublist]
                                        TxBuffer = [0xF2] + flattenPath + reduce(lambda x, y: x | y, [0xF2] + flattenPath)
                                        ser.write(bytes(TxBuffer))
                                        ser.write(DELIMITER)
                                    
                                        ser.read(1)
                                        if ser.read(1) == CMPLT:
                                            while botPlayed == False:
                                                ser.write(0xF1)
                                                ser.write(DELIMITER)
                                                data = ser.read_until(DELIMITER)
                                                boardMatch = compare_board_data(board.board, data)
                                                ser.write(ACK)
                                                ser.write(DELIMITER)
                                                if boardMatch:
                                                    turnByte = 0b00010000 if board.turn == 'b' else 0b00100000
                                                    TxBuffer = [0xF3] + [turnByte] + reduce(lambda x, y: x | y, [0xF3, 0b00010000])
                                                    ser.write(bytes(TxBuffer))
                                                    ser.write(DELIMITER)
                                                    RxBuffer = ser.read_until(DELIMITER)
                                                    if RxBuffer == ACK:
                                                        player1.turn = board.turn
                                                        player2.turn = board.turn
                                                        botPlayed = True
                                                        del data
                                                        del RxBuffer
                                                        break
                                                else:
                                                    TxBuffer = [0xF3] + [0b01100000] + reduce(lambda x, y: x | y, [0xF3, 0b01100000])
                                                    ser.write(bytes(TxBuffer))
                                                    ser.write(DELIMITER)
                                    
                                    else:
                                        while botPlayed == False:
                                            ser.write(0xF1)
                                            ser.write(DELIMITER)
                                            data = ser.read_until(DELIMITER)
                                            boardMatch = compare_board_data(board.board, data)
                                            ser.write(ACK)
                                            ser.write(DELIMITER)
                                            if boardMatch:
                                                TxBuffer = [0xF3] + [0b00010000] + reduce(lambda x, y: x | y, [0xF3, 0b00010000])
                                                ser.write(bytes(TxBuffer))
                                                ser.write(DELIMITER)
                                                RxBuffer = ser.read_until(DELIMITER)
                                                if RxBuffer == ACK:
                                                    player1.turn = board.turn
                                                    player2.turn = board.turn
                                                    botPlayed = True
                                                    del RxBuffer
                                                    break
                                            else:
                                                TxBuffer = [0xF3] + [0b01100000] + reduce(lambda x, y: x | y, [0xF3, 0b01100000])
                                                ser.write(bytes(TxBuffer))
                                                ser.write(DELIMITER)

                    elif isGameOver:
                        if isGameOver == 'b':
                            TxBuffer = [0xF3] + [0b00000100] + reduce(lambda x, y: x | y, [0xF3, 0b00000100])
                        elif isGameOver == 'w':
                            TxBuffer = [0xF3] + [0b00000010] + reduce(lambda x, y: x | y, [0xF3, 0b00000010])
                        elif isGameOver == 'draw':
                            TxBuffer = [0xF3] + [0b00000001] + reduce(lambda x, y: x | y, [0xF3, 0b00000001])

                        ser.write(bytes(TxBuffer))
                        ser.write(DELIMITER)

                        RxBuffer = ser.read_until(DELIMITER)
                        if RxBuffer == ACK:
                            running = False
                            startFlag = False
                            break