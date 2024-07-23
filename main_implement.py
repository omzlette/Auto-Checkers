from checkers import *
from player import *
from pathfinding import *
from functools import reduce
import serial
import time

ACK = 0x50
CMPLT = 0x51
NACK = 0x60
DELIMITER = 0x3b # ;
DELIMITER_ENCODE = ';'.encode('utf-8')

CONNECTION_REQUEST = 0xF0
DISCONNECTION_REQUEST = 0xFF
START = 0x99
STOP = 0x98
RESET = 0x97

def initialize():
    board = Checkers()
    player1 = User('b', board.board, board.movesDone)
    player2 = AlphaBeta('w', board.board, board.movesDone)
    return player1, player2, board

def compare_board_data(board, data:bytes):
    checkBoard = [[0 for _ in range(8)] for _ in range(8)]
    for row, byte in enumerate(data):
        checkBoard[row] = bin(byte)[2:].zfill(8)
        print(checkBoard[row], board[row])
        for col in range(8):
            if board[row][col] == '-' and checkBoard[row][col] != '0':
                return False
            elif board[row][col].lower() in ['b', 'w'] and checkBoard[row][col] != '1':
                return False
    return True

def get_move(prevBoard, data:bytes):
    # exclusive to black
    pieceFrom = None
    pieceTo = None
    capturedList = []
    newBoard = [[0 for _ in range(8)] for _ in range(8)]
    for row, byte in enumerate(data):
        newBoard[row] = bin(byte)[2:].zfill(8)
        print(newBoard[row], prevBoard[row])
        
    for row in range(8):
        for col in range(8):
            if prevBoard[row][col] != '-' and newBoard[row][col] == '0':
                if prevBoard[row][col] in ['b', 'B']:
                    pieceFrom = (row, col)
                elif prevBoard[row][col] in ['w', 'W']:
                    capturedList.append((row, col))
            if prevBoard[row][col] in ['-'] and newBoard[row][col] != '0':
                pieceTo = (row, col)

    if capturedList:
        selectedList = [pieceFrom]
        moves = []
        distDiff = []
        reverseFlag = False
        
        for row, col in capturedList:
            rowDelta = abs(row - pieceFrom[0])
            colDelta = abs(col - pieceFrom[1])
            distDiff.append((rowDelta, colDelta))
        
        if distDiff[0][0] > distDiff[1][0] or distDiff[0][1] > distDiff[1][1]:
            reverseFlag = True

        if reverseFlag:
            capturedList = capturedList[::-1]

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
                print('Connecting MCU')
                ser = serial.Serial('/dev/ttyUSB0', 115200)
                ser.flushInput()
                ser.flushOutput()
                time.sleep(1)
                packet = bytearray()
                packet.append(DISCONNECTION_REQUEST)
                packet.append(DELIMITER)
                ser.write(packet)

                RxBuffer = ser.read_until(DELIMITER_ENCODE)
                print(RxBuffer)
                if RxBuffer[0] == ACK:
                    packet = bytearray()
                    packet.append(CONNECTION_REQUEST)
                    packet.append(DELIMITER)
                    ser.write(packet)
                    # receive 'ACK' from MCU
                    RxBuffer = ser.read(2)
                    print(RxBuffer)
                    if RxBuffer[0] == ACK:
                        print('MCU Connected')
                        connectedMCU = True
                        player1, player2, board = initialize()
                        isGameOver = False
                        running = True
                        del RxBuffer
            except:
                print('Waiting for MCU...')
                time.sleep(5)

        else:
            if not startFlag:
                if ser.read(2)[0] == START:
                    print('Starting...')
                    packet = bytearray()
                    packet.append(ACK)
                    packet.append(DELIMITER)
                    ser.write(packet)

                    packet = bytearray()
                    packet.append(0xF1) # Send data board request
                    packet.append(DELIMITER)
                    ser.write(packet)

                    # receive 'ACK' from MCU
                    RxBuffer = ser.read(11)
                    print(RxBuffer)
                    if RxBuffer[0] == ACK:
                        print('Send Board Data Request ACK')
                        # receive board data from MCU
                        print(RxBuffer[2:])
                        boardMatch = compare_board_data(board.board, RxBuffer[2:-1])
                        print("Match:", boardMatch)
                        packet = bytearray()
                        packet.append(ACK)
                        packet.append(DELIMITER)
                        ser.write(packet)
                        if boardMatch:
                            startFlag = True
                            TxBuffer = [0xF3] + [0b00010000] + [reduce(lambda x, y: x | y, [0xF3, 0b00010000])]
                        else:
                            TxBuffer = [0xF3] + [0b01000000] + [reduce(lambda x, y: x | y, [0xF3, 0b01000000])]
                        
                        packet = bytearray()
                        for byte in TxBuffer:
                            packet.append(byte)
                        packet.append(DELIMITER)
                        ser.write(packet)
                        print('Update Status')
                        RxBuffer = ser.read(2)
                        print(RxBuffer)
                        if RxBuffer[0] == ACK:
                            print('Update Status ACK')
                            print('Start:', startFlag)
                            del RxBuffer
            
            else:
                captureFlag = False
                botPlayed = False
                while running:
                    print('Game Start')
                    # if ser.in_waiting == 2:
                    #     RxBuffer = ser.read(2)
                    #     print(RxBuffer)
                    #     if RxBuffer[0] == STOP or RxBuffer[0] == RESET:
                    #         print("Stopping..." if RxBuffer[0] == STOP else "Resetting...")
                    #         packet = bytearray()
                    #         packet.append(ACK)
                    #         packet.append(DELIMITER)
                    #         ser.write(packet)
                    #         # reset or stop
                    #         running = False
                    #         startFlag = False
                    #         break
                    
                    # do game logic
                    if board.turn == player1.ourTurn:
                        isGameOver = is_game_over(board.board, board.movesDone, player1.mandatory_moves)
                    elif board.turn == player2.botTurn:
                        isGameOver = is_game_over(board.board, board.movesDone, player2.mandatory_moves)

                    if not isGameOver:
                        if board.turn == 'b':
                            print('Player Turn')
                            user_time = time.time()
                            while time.time() - user_time < 3:
                                packet = bytearray()
                                packet.append(0xF1)
                                packet.append(DELIMITER)
                                ser.write(packet)
                                print('Request board')

                                RxBuffer = ser.read(11)
                                print(RxBuffer)
                                if RxBuffer[0] == ACK:
                                    # receive board data from MCU
                                    BPieces, BMoves, BCaptures = get_move(board.board, RxBuffer[2:-1])
                                    packet = bytearray()
                                    packet.append(ACK)
                                    packet.append(DELIMITER)
                                    ser.write(packet)
                                    legalMove = checkLegalMove(BPieces, BMoves, BCaptures)
                                    print("Legal?:", legalMove)
                                    if legalMove is True:
                                        for BPiece, BMove in zip(BPieces, BMoves):
                                            board.board, board.turn, _ = player1.update_board(board.board, BPiece, BMove)
                                            board.updateMovesDict(BPiece, BMove, 'b')
                                        TxBuffer = [0xF3] + [0b00100000] + [reduce(lambda x, y: x | y, [0xF3, 0b00100000])]
                                    elif legalMove is False:
                                        TxBuffer = [0xF3] + [0b10010000] + [reduce(lambda x, y: x | y, [0xF3, 0b10010000])]
                                    else:
                                        continue
                                    
                                    packet = bytearray()
                                    for byte in TxBuffer:
                                        packet.append(byte)
                                    packet.append(DELIMITER)
                                    ser.write(packet)

                                    RxBuffer = ser.read(2)
                                    print(RxBuffer)
                                    if RxBuffer[0] == ACK:
                                        player1.turn = board.turn
                                        player2.turn = board.turn
                                        del RxBuffer
                                        break
                                    else:
                                        TxBuffer = [0xF3] + [0b00100000] + [reduce(lambda x, y: x | y, [0xF3, 0b00100000])]
                                        packet = bytearray()
                                        for byte in TxBuffer:
                                            packet.append(byte)
                                        packet.append(DELIMITER)
                                        ser.write(packet)
                                        RxBuffer = ser.read(2)
                                        print(RxBuffer)
                                        if RxBuffer[0] == ACK:
                                            del RxBuffer
                                            continue

                        else:
                            botPlayed = False
                            print('Bot Turn')
                            WPiece, WMove = player2.play(board.board)
                            if WPiece is not None and WMove is not None:
                                print(WPiece, WMove)
                                player2.prevCount = countBlack(board.board) + countWhite(board.board)
                                board.prevBoard = copy.deepcopy(board.board)
                                board.board, board.turn, WCapture = player2.update_board(board.board, WPiece, WMove)
                                print(WCapture)
                                for row in board.board:
                                    print(row)
                                board.updateMovesDict(WPiece, WMove, 'w')
                                if WCapture != []:
                                    captureFlag = True
                                    mappedBoard, startpos, endpos = mapping(board.prevBoard, WCapture, None)
                                    pathPoint = astar(mappedBoard, startpos, endpos)
                                    flattenPath = [item for sublist in pathPoint for item in sublist]
                                    TxBuffer = [0xF2] + flattenPath + [reduce(lambda x, y: x | y, [0xF2] + flattenPath)]
                                    packet = bytearray()
                                    for byte in TxBuffer:
                                        packet.append(byte)
                                    packet.append(DELIMITER)
                                    ser.write(packet)
                                    print('Sent:', TxBuffer)
                                else:
                                    mappedBoard, startpos, endpos = mapping(board.prevBoard, WPiece, WMove)
                                    print(startpos, endpos)
                                    pathPoint = astar(mappedBoard, startpos, endpos)
                                    print(pathPoint)
                                    flattenPath = [item for sublist in pathPoint for item in sublist]
                                    TxBuffer = [0xF2] + flattenPath + [reduce(lambda x, y: x | y, [0xF2] + flattenPath)]
                                    packet = bytearray()
                                    for byte in TxBuffer:
                                        packet.append(byte)
                                    packet.append(DELIMITER)
                                    ser.write(packet)
                                    print('Sent:', TxBuffer)
                                
                                RxBuffer = ser.read(2)
                                print(RxBuffer)
                                if RxBuffer[0] == ACK:
                                    if captureFlag:
                                        RxBuffer = ser.read(2)
                                        print(RxBuffer)
                                        if RxBuffer[0] == CMPLT:
                                            mappedBoard, startpos, endpos = mapping(board.prevBoard, WCapture, WMove)
                                            pathPoint = astar(mappedBoard, startpos, endpos)
                                            flattenPath = [item for sublist in pathPoint for item in sublist]
                                            TxBuffer = [0xF2] + flattenPath + [reduce(lambda x, y: x | y, [0xF2] + flattenPath)]
                                            packet = bytearray()
                                            for byte in TxBuffer:
                                                packet.append(byte)
                                            packet.append(DELIMITER)
                                            ser.write(packet)
                                            print('Sent:', TxBuffer)
                                        
                                            RxBuffer = ser.read(2)
                                            print(RxBuffer)
                                            if RxBuffer[0] == ACK:
                                                RxBuffer = ser.read(2)
                                                print(RxBuffer)
                                                if RxBuffer[0] == CMPLT:
                                                    while botPlayed == False:
                                                        packet = bytearray()
                                                        packet.append(0xF1)
                                                        packet.append(DELIMITER)
                                                        ser.write(packet)

                                                        data = ser.read(11)
                                                        boardMatch = compare_board_data(board.board, data[2:-1])
                                                        packet = bytearray()
                                                        packet.append(ACK)
                                                        packet.append(DELIMITER)
                                                        ser.write(packet)
                                                        if boardMatch:
                                                            turnByte = 0b00010000 if board.turn == 'b' else 0b00100000
                                                            TxBuffer = [0xF3] + [turnByte] + [reduce(lambda x, y: x | y, [0xF3, 0b00010000])]
                                                            packet = bytearray()
                                                            for byte in TxBuffer:
                                                                packet.append(byte)
                                                            packet.append(DELIMITER)
                                                            ser.write(packet)

                                                            RxBuffer = ser.read(2)
                                                            print(RxBuffer)
                                                            if RxBuffer[0] == ACK:
                                                                player1.turn = board.turn
                                                                player2.turn = board.turn
                                                                botPlayed = True
                                                                del data
                                                                del RxBuffer
                                                                break
                                                        else:
                                                            TxBuffer = [0xF3] + [0b01100000] + [reduce(lambda x, y: x | y, [0xF3, 0b01100000])]
                                                            packet = bytearray()
                                                            for byte in TxBuffer:
                                                                packet.append(byte)
                                                            packet.append(DELIMITER)
                                                            ser.write(packet)

                                                            RxBuffer = ser.read(2)
                                                            print(RxBuffer)
                                                            if RxBuffer[0] == ACK:
                                                                del data
                                                                del RxBuffer
                                    
                                    else:
                                        RxBuffer = ser.read(2)
                                        print(RxBuffer)
                                        if RxBuffer[0] == CMPLT:
                                            while botPlayed == False:
                                                packet = bytearray()
                                                packet.append(0xF1)
                                                packet.append(DELIMITER)
                                                ser.write(packet)

                                                data = ser.read(11)
                                                boardMatch = compare_board_data(board.board, data[2:-1])
                                                packet = bytearray()
                                                packet.append(ACK)
                                                packet.append(DELIMITER)
                                                ser.write(packet)
                                                if boardMatch:
                                                    TxBuffer = [0xF3] + [0b00010000] + [reduce(lambda x, y: x | y, [0xF3, 0b00010000])]
                                                    packet = bytearray()
                                                    for byte in TxBuffer:
                                                        packet.append(byte)
                                                    packet.append(DELIMITER)
                                                    ser.write(packet)
                                                    RxBuffer = ser.read(2)
                                                    if RxBuffer[0] == ACK:
                                                        player1.turn = board.turn
                                                        player2.turn = board.turn
                                                        botPlayed = True
                                                        del data
                                                        del RxBuffer
                                                        break
                                                else:
                                                    TxBuffer = [0xF3] + [0b01100000] + [reduce(lambda x, y: x | y, [0xF3, 0b01100000])]
                                                    packet = bytearray()
                                                    for byte in TxBuffer:
                                                        packet.append(byte)
                                                    packet.append(DELIMITER)
                                                    ser.write(packet)
                                                    RxBuffer = ser.read(2)
                                                    if RxBuffer[0] == ACK:
                                                        del data
                                                        del RxBuffer

                    elif isGameOver:
                        if isGameOver == 'b':
                            TxBuffer = [0xF3] + [0b00000100] + [reduce(lambda x, y: x | y, [0xF3, 0b00000100])]
                        elif isGameOver == 'w':
                            TxBuffer = [0xF3] + [0b00000010] + [reduce(lambda x, y: x | y, [0xF3, 0b00000010])]
                        elif isGameOver == 'draw':
                            TxBuffer = [0xF3] + [0b00000001] + [reduce(lambda x, y: x | y, [0xF3, 0b00000001])]

                        packet = bytearray()
                        for byte in TxBuffer:
                            packet.append(byte)
                        packet.append(DELIMITER)
                        ser.write(packet)

                        RxBuffer = ser.read(2)
                        print(RxBuffer)
                        if RxBuffer[0] == ACK:
                            running = False
                            startFlag = False
                            break

if __name__ == '__main__':
    main()