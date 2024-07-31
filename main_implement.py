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
BOARDREQUEST = 0xF1
MOTORREQUEST = 0xF2
UPDATEREQUEST = 0xF3
DISCONNECTION_REQUEST = 0xFF
START = 0x99
STOP = 0x98

# MODES
INIT = 0
RUNNING = 1
RESET_IDLE = 2

DISCONNECTED = 0
CONNECTED = 1

def initialize():
    board = Checkers()
    player1 = User('b', board.board, board.movesDone)
    player2 = AlphaBeta('w', board.board, board.movesDone)
    return player1, player2, board

def checksum(buffer):
    return reduce(lambda x, y: x ^ y, buffer)

def compare_board_data(board, data:bytes):
    checksum = reduce(lambda x, y: x ^ y, data[:-1])
    if checksum == data[-1]:
        checkBoard = [[0 for _ in range(8)] for _ in range(8)]
        for row, byte in enumerate(data[:-1]):
            checkBoard[row] = bin(byte)[2:].zfill(8)
            for col in range(8):
                if board[row][col] == '-' and checkBoard[row][col] != '0':
                    return False
                elif board[row][col].lower() in ['b', 'w'] and checkBoard[row][col] != '1':
                    return False
        return True
    else:
        return False

def get_move(prevBoard, data:bytes):
    # exclusive to black
    pieceFrom = None
    pieceTo = None
    capturedList = []
    newBoard = [[0 for _ in range(8)] for _ in range(8)]
    for row, byte in enumerate(data):
        newBoard[row] = bin(byte)[2:].zfill(8)
        print(newBoard[row], prevBoard[row])
    print(len(newBoard), len(prevBoard))
        
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
    user_timer = 0
    MOTORREQUEST_ACK_FLAG = False
    MAIN_STATE = 0
    CONNECTION_STATE = 0
    PREVMODE = None
    MODE = None
    TURN = 'b'
    while True:
        if CONNECTION_STATE == DISCONNECTED:
            try:
                print('Connecting MCU')
                ser = serial.Serial('/dev/ttyUSB0', 115200)
                # ser = serial.Serial('COM5', 115200)
                ser.flushInput()
                ser.flushOutput()
                time.sleep(1)
                packet = bytearray()
                packet.append(DISCONNECTION_REQUEST)
                packet.append(DELIMITER)
                ser.write(packet)

                RxBuffer = ser.read_until(DELIMITER_ENCODE)
                if RxBuffer[0] == ACK:
                    packet = bytearray()
                    packet.append(CONNECTION_REQUEST)
                    packet.append(DELIMITER)
                    ser.write(packet)
                    # receive 'ACK' from MCU
                    RxBuffer = ser.read_until(DELIMITER_ENCODE)
                    if RxBuffer[0] == ACK:
                        print('MCU Connected')
                        CONNECTION_STATE = CONNECTED
                        player1, player2, board = initialize()
                        isGameOver = False
                        del RxBuffer
            except:
                print('Waiting for MCU...')
                time.sleep(5)

        elif CONNECTION_STATE == CONNECTED:
            while ser.in_waiting > 0:
                buffer = ser.read_until(DELIMITER_ENCODE)
                if len(buffer) == 2:
                    MODE = buffer[0]
                    print(MODE, PREVMODE, TURN)
                    break
                elif len(buffer) == 9:
                    MODE = BOARDREQUEST
                    board_data = buffer[:-1]
                    print(MODE, PREVMODE, TURN)
                    print(board_data)
                    break

            if MAIN_STATE == INIT:
                if MODE == START:
                    print('Start Button Pressed')
                    packet = bytearray()
                    packet.append(ACK)
                    packet.append(DELIMITER)
                    ser.write(packet)

                    packet = bytearray()
                    packet.append(BOARDREQUEST)
                    packet.append(DELIMITER)
                    ser.write(packet)

                    print('Request Board, INIT')
                    PREVMODE = BOARDREQUEST
                    MODE = None

                elif MODE == STOP:
                    print('Stopping...')
                    packet = bytearray()
                    packet.append(ACK)
                    packet.append(DELIMITER)
                    ser.write(packet)

                    MAIN_STATE = INIT
                    MODE = None
                    continue
                
                elif PREVMODE == UPDATEREQUEST and MODE == ACK:
                    print('Changing state to RUNNING')
                    MAIN_STATE = RUNNING
                    if packet is not None:
                        del packet
                    PREVMODE = None
                    MODE = None

                elif PREVMODE == UPDATEREQUEST and MODE == NACK:
                    print('Update Request Failed')
                    if packet is not None:
                        del packet
                    PREVMODE = None
                    MODE = None

                elif MODE == BOARDREQUEST:
                    print('Comparing Board Data')
                    print(board_data)
                    boardMatch = compare_board_data(board.board, board_data)

                    packet = bytearray()
                    packet.append(ACK)
                    packet.append(DELIMITER)
                    ser.write(packet)

                    if boardMatch:
                        TxBuffer = [UPDATEREQUEST] + [0b00010000] + [reduce(lambda x, y: x ^ y, [UPDATEREQUEST, 0b00010000])]
                    else:
                        TxBuffer = [UPDATEREQUEST] + [0b01000000] + [reduce(lambda x, y: x ^ y, [UPDATEREQUEST, 0b01000000])]
                    
                    packet = bytearray()
                    for byte in TxBuffer:
                        packet.append(byte)
                    packet.append(DELIMITER)
                    ser.write(packet)

                    PREVMODE = UPDATEREQUEST
                    MODE = None

            elif MAIN_STATE == RUNNING:
                if TURN == player1.ourTurn:
                    isGameOver = is_game_over(board.board, board.movesDone, player1.mandatory_moves)
                elif TURN == player2.botTurn:
                    isGameOver = is_game_over(board.board, board.movesDone, player2.mandatory_moves)
                               
                if MODE == STOP:
                    print('Stopping...')
                    packet = bytearray()
                    packet.append(ACK)
                    packet.append(DELIMITER)
                    ser.write(packet)

                    MAIN_STATE = INIT
                    MODE = None
                    continue

                elif MODE == BOARDREQUEST and TURN == 'b':
                    print('Request Board Data, RUNNING, Black Turn')
                    BPieces, BMoves, BCaptures = get_move(board.board, board_data)
                    packet = bytearray()
                    packet.append(ACK)
                    packet.append(DELIMITER)
                    ser.write(packet)

                    legalMove = checkLegalMove(BPieces, BMoves, BCaptures)
                    print('Legal Move (Black Turn)?:', legalMove)
                    if legalMove is True:
                        for BPiece, BMove in zip(BPieces, BMoves):
                            board.board, board.turn, _ = player1.update_board(board.board, BPiece, BMove)
                            board.updateMovesDict(BPiece, BMove, 'b')
                        byteTurn = 0b00100000 if board.turn == 'w' else 0b00010000
                        TxBuffer = [UPDATEREQUEST] + [byteTurn] + [reduce(lambda x, y: x ^ y, [UPDATEREQUEST, byteTurn])]
                    elif legalMove is False:
                        TxBuffer = [UPDATEREQUEST] + [0b01010000] + [reduce(lambda x, y: x ^ y, [UPDATEREQUEST, 0b01010000])]
                    else:
                        byteTurn = 0b00100000 if board.turn == 'w' else 0b00010000
                        TxBuffer = [UPDATEREQUEST] + [byteTurn] + [reduce(lambda x, y: x ^ y, [UPDATEREQUEST, byteTurn])]
                    
                    packet = bytearray()
                    for byte in TxBuffer:
                        packet.append(byte)
                    packet.append(DELIMITER)
                    ser.write(packet)

                    PREVMODE = UPDATEREQUEST
                    MODE = None

                elif MODE == BOARDREQUEST and TURN == 'w':
                    print('Request Board Data, RUNNING, White Turn')
                    boardMatch = compare_board_data(board.board, board_data)
                    packet = bytearray()
                    packet.append(ACK)
                    packet.append(DELIMITER)
                    ser.write(packet)

                    print('Board Matched (White Turn)?:', boardMatch)

                    if boardMatch:
                        byteTurn = 0b00100000 if board.turn == 'w' else 0b00010000
                        TxBuffer = [UPDATEREQUEST] + [byteTurn] +[reduce(lambda x, y: x ^ y, [UPDATEREQUEST, byteTurn])]
                        packet = bytearray()
                        for byte in TxBuffer:
                            packet.append(byte)
                        packet.append(DELIMITER)
                        ser.write(packet)

                        PREVMODE = UPDATEREQUEST
                        MODE = None

                    else:
                        TxBuffer = [UPDATEREQUEST] + [0b01100000] + [reduce(lambda x, y: x ^ y, [UPDATEREQUEST, 0b01100000])]
                        packet = bytearray()
                        for byte in TxBuffer:
                            packet.append(byte)
                        packet.append(DELIMITER)
                        ser.write(packet)
                        
                        buffer = ser.read_until(DELIMITER_ENCODE)
                        if buffer[0] == ACK:
                            packet = bytearray()
                            packet.append(BOARDREQUEST)
                            packet.append(DELIMITER)
                            ser.write(packet)

                            PREVMODE = None
                            MODE = BOARDREQUEST
                        elif buffer[0] == STOP:
                            PREVMODE = None
                            MODE = STOP

                elif PREVMODE == UPDATEREQUEST and MODE == ACK and TURN == 'b':
                    print('Update Request, Black Turn')
                    TURN = board.turn
                    player1.turn = board.turn
                    player2.turn = board.turn

                    if packet is not None:
                        del packet
                    PREVMODE = None
                    MODE = None

                elif PREVMODE == UPDATEREQUEST and MODE == ACK and TURN == 'w':
                    print('Update Request, White Turn')
                    TURN = board.turn
                    player1.turn = board.turn
                    player2.turn = board.turn

                    if packet is not None:
                        del packet
                    PREVMODE = None
                    MODE = None

                elif PREVMODE == UPDATEREQUEST and MODE == NACK:
                    print('Update Request Failed, RUNNING')
                    byteTurn = 0b00100000 if board.turn == 'w' else 0b00010000
                    TxBuffer = [UPDATEREQUEST] + [byteTurn] + [reduce(lambda x, y: x ^ y, [UPDATEREQUEST, byteTurn])]
                    packet = bytearray()
                    for byte in TxBuffer:
                        packet.append(byte)
                    packet.append(DELIMITER)
                    ser.write(packet)

                    if packet is not None:
                        del packet
                    PREVMODE == UPDATEREQUEST
                    MODE = None

                elif MOTORREQUEST_ACK_FLAG is True:
                    MOTORREQUEST_ACK_FLAG = False
                    if captureFlag:
                        print('Requesting Next Piece Motor Move')
                        mappedBoard, startpos, endpos = mapping(board.prevBoard, WPiece, WMove)
                        pathPoint = astar(mappedBoard, startpos, endpos)
                        flattenPath = [item for sublist in pathPoint for item in sublist]
                        TxBuffer = [MOTORREQUEST] + flattenPath + [reduce(lambda x, y: x ^ y, [MOTORREQUEST] + flattenPath)]
                        packet = bytearray()
                        for byte in TxBuffer:
                            packet.append(byte)
                        packet.append(DELIMITER)
                        ser.write(packet)

                        buffer = ser.read_until(DELIMITER_ENCODE)
                        if buffer[0] == ACK:
                            MOTORREQUEST_ACK_FLAG = True
                            PREVMODE = None
                            MODE = None
                        elif buffer[0] == STOP:
                            PREVMODE = None
                            MODE = STOP
                    
                    else:
                        print('Wait for Motor Done')
                        buffer = ser.read_until(DELIMITER_ENCODE)
                        if buffer[0] == CMPLT:
                            packet = bytearray()
                            packet.append(BOARDREQUEST)
                            packet.append(DELIMITER)
                            ser.write(packet)

                            buffer = ser.read_until(DELIMITER_ENCODE)
                            if buffer[0] == ACK:
                                PREVMODE = None
                                MODE = BOARDREQUEST
                            elif buffer[0] == STOP:
                                PREVMODE = None
                                MODE = STOP
                        elif buffer[0] == STOP:
                            PREVMODE = None
                            MODE = STOP

                if not isGameOver:
                    if TURN == 'b':
                        if time.time() - user_timer >= 3:
                            print('Player Turn')
                            packet = bytearray()
                            packet.append(BOARDREQUEST)
                            packet.append(DELIMITER)
                            ser.write(packet)
                            user_timer = time.time()

                    elif TURN == 'w' and MODE != BOARDREQUEST and PREVMODE != UPDATEREQUEST:
                        print('AI Turn')
                        WPiece, WMove = player2.play(board.board)
                        if WPiece is not None and WMove is not None:
                            player2.prevCount = countBlack(board.board) + countWhite(board.board)
                            board.prevBoard = copy.deepcopy(board.board)
                            board.board, board.turn, WCapture = player2.update_board(board.board, WPiece, WMove)
                            board.updateMovesDict(WPiece, WMove, 'w')

                            print('AI Search Done')

                            if WCapture != []:
                                captureFlag = True
                                mappedBoard, startpos, endpos = mapping(board.prevBoard, WCapture, None)
                                pathPoint = astar(mappedBoard, startpos, endpos)
                                flattenPath = [item for sublist in pathPoint for item in sublist]
                                TxBuffer = [MOTORREQUEST] + flattenPath + [reduce(lambda x, y: x ^ y, [MOTORREQUEST] + flattenPath)]
                                
                                packet = bytearray()
                                for byte in TxBuffer:
                                    packet.append(byte)
                                packet.append(DELIMITER)
                                ser.write(packet)

                                buffer = ser.read_until(DELIMITER_ENCODE)
                                if buffer[0] == ACK:
                                    print('Motor Request ACK')
                                    MOTORREQUEST_ACK_FLAG = True
                                    PREVMODE = None
                                    MODE = None
                                elif buffer[0] == STOP:
                                    PREVMODE = None
                                    MODE = STOP

                            else:
                                captureFlag = False
                                mappedBoard, startpos, endpos = mapping(board.prevBoard, WPiece, WMove)
                                pathPoint = astar(mappedBoard, startpos, endpos)
                                print(pathPoint)
                                flattenPath = [item for sublist in pathPoint for item in sublist]
                                TxBuffer = [MOTORREQUEST] + flattenPath + [reduce(lambda x, y: x ^ y, [MOTORREQUEST] + flattenPath)]
                                packet = bytearray()
                                for byte in TxBuffer:
                                    packet.append(byte)
                                packet.append(DELIMITER)
                                ser.write(packet)
                                print('Motor Request:', packet)

                                buffer = ser.read_until(DELIMITER_ENCODE)
                                print('Buffer Motor Request ACK:', buffer)
                                if buffer[0] == ACK:
                                    print('Motor Request ACK')
                                    MOTORREQUEST_ACK_FLAG = True
                                    PREVMODE = None
                                    MODE = None
                                elif buffer[0] == STOP:
                                    PREVMODE = None
                                    MODE = STOP
                                    continue
                
                else:
                    if isGameOver == 'b':
                        TxBuffer = [0xF3] + [0b00000100] + [reduce(lambda x, y: x ^ y, [0xF3, 0b00000100])]
                    elif isGameOver == 'w':
                        TxBuffer = [0xF3] + [0b00000010] + [reduce(lambda x, y: x ^ y, [0xF3, 0b00000010])]
                    elif isGameOver == 'draw':
                        TxBuffer = [0xF3] + [0b00000001] + [reduce(lambda x, y: x ^ y, [0xF3, 0b00000001])]

                    packet = bytearray()
                    for byte in TxBuffer:
                        packet.append(byte)
                    packet.append(DELIMITER)
                    ser.write(packet)

                    MODE = None

                    buffer = ser.read_until(DELIMITER_ENCODE)
                    if len(buffer) == 2:
                        MODE = buffer[0]
                        if MODE == ACK:
                            MAIN_STATE = RESET_IDLE
                        elif MODE == STOP:
                            print('Stopping...')
                            packet = bytearray()
                            packet.append(ACK)
                            packet.append(DELIMITER)
                            ser.write(packet)

                            MAIN_STATE = INIT

            elif MAIN_STATE == RESET_IDLE:
                buffer = ser.read_until(DELIMITER_ENCODE)
                if len(buffer) == 2:
                    MODE = buffer[0]
                    if MODE == RESET:
                        print('Resetting...')
                        packet = bytearray()
                        packet.append(ACK)
                        packet.append(DELIMITER)
                        ser.write(packet)

                        PREVMODE = None
                        MODE = None
                        del buffer, packet

                        MAIN_STATE = INIT
                        break

if __name__ == '__main__':
    main()