import cv2 as cv
import numpy as np
import pyautogui
from PIL import ImageGrab
import copy
import serial
import time
import os

def convert_to_binary(image):
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    # remove background
    # (hmin, hmax, smin, smax, vmin, vmax) = getHSV()
    hmin = 0
    hmax = 108
    smin = 0
    smax = 134
    vmin = 108
    vmax = 255
    lower = np.array([hmin, smin, vmin])
    upper = np.array([hmax, smax, vmax])
    mask = cv.inRange(hsv, lower, upper)

    krn = cv.getStructuringElement(cv.MORPH_RECT, (50, 30))
    dlt = cv.dilate(mask, krn, iterations=5)
    res = 255 - cv.bitwise_and(dlt, mask)
    # # Apply threshold
    # _, res = cv.threshold(hsv, 0, 255, cv.THRESH_OTSU)
    return res

# detect checkers board
def detect_checkers_board(img):
    # convert to gray scale
    mask = convert_to_binary(img)
    # mask = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # find the chess board corners
    ret, corners = cv.findChessboardCorners(mask, (7, 7), None)
    # if found, draw corners
    if ret == True:
        # draw corners
        cv.drawChessboardCorners(img, (7, 7), corners, ret)
        return True, corners
    return False, None

def get_board_corners(corners):
    # get the corners
    corners = corners.reshape(-1, 2)
    x_delta = abs(corners[0][0] - corners[1][0])
    y_delta = abs(corners[0][1] - corners[7][1])

    # get the top left corner
    top_left = corners[0][0] - x_delta, corners[0][1] - y_delta
    # get the top right corner
    top_right = corners[6][0] + x_delta, corners[6][1] - y_delta
    # get the bottom left corner
    bottom_left = corners[42][0] - x_delta, corners[42][1] + y_delta
    # get the bottom right corner
    bottom_right = corners[48][0] + x_delta, corners[48][1] + y_delta
    return top_left, top_right, bottom_left, bottom_right

def get_board_squares(squareCoords, corners):
    # get the corners
    corners = corners.reshape(-1, 2)
    x_delta = abs(corners[0][0] - corners[1][0])
    y_delta = abs(corners[0][1] - corners[7][1])
    
    home_coords = corners[0][0] - x_delta/2, corners[0][1] - y_delta/2

    x = home_coords[0] + ((x_delta) * squareCoords[1])
    y = home_coords[1] + ((y_delta) * squareCoords[0])
    coords = (x, y)

    return coords, x_delta, y_delta

def crop_board(img, corners):
    # get the corners
    top_left, top_right, bottom_left, bottom_right = get_board_corners(corners)
    # get the width of the board
    width = int(np.sqrt((top_right[0] - top_left[0])**2 + (top_right[1] - top_left[1])**2))
    # get the height of the board
    height = int(np.sqrt((top_left[0] - bottom_left[0])**2 + (top_left[1] - bottom_left[1])**2))
    # get the perspective transform matrix
    pts1 = np.float32([top_left, top_right, bottom_left, bottom_right])
    pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
    matrix = cv.getPerspectiveTransform(pts1, pts2)
    # apply the perspective transform
    result = cv.warpPerspective(img, matrix, (width, height))
    return result

def detect_pieces(boardimg, corners):
    if corners is not None:
        # get the corners
        top_left, _, _, bottom_right = get_board_corners(corners)
        # detect white squares
        # convert to gray scale
        gray = cv.cvtColor(boardimg, cv.COLOR_BGR2GRAY)
        # apply threshold
        _, thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)
        # find contours
        contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        # get the squares
        # apply only the squares that are inside the board
        pieces = []
        for cnt in contours:
            x, y, w, h = cv.boundingRect(cnt)
            if bottom_right[0] > x > top_left[0] and bottom_right[1] > y > top_left[1]:
                if 25 < w < 50 and 25 < h < 50:
                    pieces.append((x, y, w, h))
    return pieces

def match_images(img, template):
    # convert to gray scale
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    template = cv.cvtColor(template, cv.COLOR_BGR2GRAY)
    # get the template size
    w, h = template.shape[::-1]
    # match the template
    res = cv.matchTemplate(gray, template, cv.TM_CCOEFF_NORMED)
    # get the threshold
    threshold = 0.8
    loc = np.where(res >= threshold), w, h

    return loc

def getMove(prevBoard, newBoard, turn):
    convertTurn = {'b': (1, 3), 'w': (2, 4)}
    selected = None
    move = None
    pieceType = None
    for row in range(8):
        for col in range(8):
            if prevBoard[row][col] != 0 and newBoard[row][col] == 0 and prevBoard[row][col] in convertTurn[turn]:
                selected = (row, col)
                pieceType = prevBoard[row][col]
            if prevBoard[row][col] == 0 and newBoard[row][col] != 0:
                move = (row, col)

    if selected is not None and move is not None and pieceType is not None:
        if pieceType == 1 and move[0] == 7:
            pieceType = 3
        elif pieceType == 2 and move[0] == 0:
            pieceType = 4

    return selected, move, pieceType

def getBoardState(boardimg, corners):
    pieces = detect_pieces(boardimg, corners)
    board = np.zeros((8, 8))
    sorted_pieces = []

    for row in range(8):
        for col in range(8):
            square = (row, col)
            coords, x_delta, y_delta = get_board_squares(square, corners)
            for _, piece in enumerate(pieces):
                x, y, _, _ = piece
                if coords[0] - x_delta/2 < x < coords[0] + x_delta/2 and coords[1] - y_delta/2 < y < coords[1] + y_delta/2:
                    board[row][col] = 1
                    sorted_pieces.append((piece, square, coords))
                    break
    return board, sorted_pieces

def update_board_state(prevBoard, currBoard, turn):
    convertTurn = {'b': (1, 3), 'w': (2, 4)}
    otherPlayer = 'b' if turn == 'w' else 'w'
    updated_board = copy.deepcopy(prevBoard)
    capturedPiece = []

    for row in range(8):
        for col in range(8):
            if currBoard[row][col] == 1 and prevBoard[row][col] == 0:
                _, _, pieceType = getMove(prevBoard, currBoard, turn)
                updated_board[row][col] = pieceType
            elif currBoard[row][col] == 0 and prevBoard[row][col] != 0:
                updated_board[row][col] = 0
                if prevBoard[row][col] in convertTurn[otherPlayer]:
                    capturedPiece.append((row, col))
    
    return updated_board, capturedPiece

def getMultipleCapture(prevBoard, newBoard, turn, captured):
    selected, move, _ = getMove(prevBoard, newBoard, turn)
    selectedList = [selected]
    moves = []
    
    deltaRow = move[0] - selected[0]
    deltaCol = move[1] - selected[1]
    if deltaRow < 0 or deltaCol < 0:
        captured = captured[::-1]
    
    for row, col in captured:
        rowDelta = row - selected[0]
        rowDelta = rowDelta // abs(rowDelta)
        colDelta = col - selected[1]
        colDelta = colDelta // abs(colDelta)
        selected = (row + rowDelta, col + colDelta)
        moves.append(selected)
    
    selectedList.extend(moves[:-1])

    return selectedList, moves

def initGame(numGames):
    turn = 'b'
    # initialize the board (0: empty, 1: black, 2: white, 3: black king, 4: white king)
    prevBoard = np.array([[0, 1, 0, 1, 0, 1, 0, 1],
                          [1, 0, 1, 0, 1, 0, 1, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 2, 0, 2, 0, 2, 0, 2],
                          [2, 0, 2, 0, 2, 0, 2, 0]])
    
    if numGames % 2 != 0:
        prevBoard = np.flip(prevBoard, 0)
        prevBoard = np.flip(prevBoard, 1)

    bot = 'b' if numGames % 2 == 0 else 'w'
    our = 'w' if numGames % 2 == 0 else 'b'
    return turn, prevBoard, bot, our

def main():
    numGames = 0
    startedFlag = False

    jetson = serial.Serial(
        port="COM6",
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1)

    TxBuffer = "~/miniforge3/envs/checkers/bin/python ~/Auto-Checkers/main-copy.py\r"
    print(f"Sending: {TxBuffer.strip()}")
    jetson.write(TxBuffer.encode('utf-8'))
    time.sleep(3)

    jetson.reset_input_buffer()
    jetson.reset_output_buffer()
    clear = lambda: os.system('cls')

    while numGames < 100:
        if startedFlag == False:
            print("Game started")
            startedFlag = True
            turn, prevBoard, bot, our = initGame(numGames)
            time.sleep(3)

        # time.sleep(5)
        screen = ImageGrab.grab(all_screens=True)

        # screen = screen.crop((1920, 0, 3840, 1080))
        screen = np.array(screen)

        screen_binary = convert_to_binary(screen)
        ret, corners = detect_checkers_board(screen)
        screen = cv.cvtColor(screen, cv.COLOR_BGR2RGB)

        if ret:
            # print(f"Checkers board detected, Turn: {turn}")
            time.sleep(1)
            screen_binary = cv.cvtColor(screen_binary, cv.COLOR_GRAY2RGB)

            if turn == bot:
                # get the board state
                currBoard, _ = getBoardState(screen_binary, corners)
                with open('debug-board.txt', 'w') as f:
                    for row in currBoard:
                        f.write(f'{row}\n')
                # get the move
                selected, move, _ = getMove(prevBoard, currBoard, turn)

                if selected is not None and move is not None:
                    if numGames % 2 != 0:
                        selected = (7 - selected[0], 7 - selected[1])
                        move = (7 - move[0], 7 - move[1])
                    
                    _, capturedPiece = update_board_state(prevBoard, currBoard, turn)
                    # send the move
                    if len(capturedPiece) < 2:
                        TxBuffer = f'm{selected[0]};{selected[1]},{move[0]};{move[1]}\n'
                        print(f'Sent: {TxBuffer.strip()}')
                        time.sleep(0.5)
                        jetson.write(TxBuffer.encode('utf-8'))

                        response = jetson.readline().decode('utf-8').strip()
                        print(f'Received: {response}')
                        if 'ACK' in response:
                            print("Move sent successfully")
                            # update the board state
                            currBoard, _ = getBoardState(screen_binary, corners)
                            prevBoard, _ = update_board_state(prevBoard, currBoard, turn)
                            selected = None
                            move = None
                            turn = response.replace('ACK', '')

                    else:
                        time.sleep(0.5)
                        currBoard, _ = getBoardState(screen_binary, corners)
                        selectedList, moves = getMultipleCapture(prevBoard, currBoard, turn, capturedPiece)
                        countNum = 0
                        while countNum < len(selectedList):
                            print(f'Sending move {countNum + 1} of {len(selectedList)}')
                            print(f'Selected: {selectedList[countNum]}, Move: {moves[countNum]}')
                            with open('debug-board.txt', 'a') as f:
                                f.write(f'{selectedList[countNum]}, {moves[countNum]}\n')
                            time.sleep(0.1)
                            selected, move = selectedList[countNum], moves[countNum]
                            if numGames % 2 != 0:
                                selected = (7 - selected[0], 7 - selected[1])
                                move = (7 - move[0], 7 - move[1])
                            TxBuffer = f'm{selected[0]};{selected[1]},{move[0]};{move[1]}\n'
                            print(f'Sent: {TxBuffer.strip()}')
                            jetson.write(TxBuffer.encode('utf-8'))
                            
                            response = jetson.readline().decode('utf-8').strip()
                            print(f'Received: {response}')
                            if 'ACK' in response:
                                print("Move sent successfully")
                                countNum += 1
                            else:
                                print("Move not sent")
                                break
                        
                        if countNum == len(selectedList):
                            # update the board state
                            currBoard, _ = getBoardState(screen_binary, corners)
                            prevBoard, _ = update_board_state(prevBoard, currBoard, turn)
                            selected = None
                            move = None
                            turn = response.replace('ACK', '')
                    # time.sleep(0.5)
                
            else:
                time.sleep(0.5)
                # get selection and move
                if jetson.in_waiting > 0:
                    RxBuffer = jetson.readline().decode('utf-8').strip()
                    if RxBuffer and 'm' in RxBuffer:
                        print(f'Received: {RxBuffer}')
                        RxBuffer = RxBuffer.replace('m', '')
                        selected, move, receivedTurn = RxBuffer.split(',')
                        selected = tuple(map(int, selected.split(';')))
                        move = tuple(map(int, move.split(';')))

                        jetson.write('ACK\n'.encode('utf-8'))
                        print("ACK sent")
                        if selected is not None and move is not None:
                            if numGames % 2 != 0:
                                selected = (7 - selected[0], 7 - selected[1])
                                move = (7 - move[0], 7 - move[1])

                            selectedCoords, _, _ = get_board_squares(selected, corners)
                            moveCoords, _, _ = get_board_squares(move, corners)

                            print(f'Selected: {selected}, Move: {move}'
                                  f'\nSelected Coords: {selectedCoords}, Move Coords: {moveCoords}')

                            # move the piece
                            pyautogui.moveTo(selectedCoords[0], selectedCoords[1], duration=0.25)
                            pyautogui.click()
                            pyautogui.moveTo(moveCoords[0], moveCoords[1], duration=0.25)
                            pyautogui.click()
                            
                            # update the board state
                            pieceType = prevBoard[selected[0]][selected[1]]
                            prevBoard[selected[0]][selected[1]] = 0
                            prevBoard[move[0]][move[1]] = pieceType
                            if abs(selected[0] - move[0]) >= 2:
                                rowDelta = (selected[0] - move[0])//abs(selected[0] - move[0])
                                colDelta = (selected[1] - move[1])//abs(selected[1] - move[1])
                                prevBoard[move[0] + rowDelta][move[1] + colDelta] = 0

                            turn = receivedTurn
                            selected = None
                            move = None
                            # time.sleep(0.5)
            
            # screen_binary = crop_board(screen_binary, corners)
            # print board in console
            # clear()
            # print(f"Game {numGames + 1} - Turn: {turn}")
            # print('Current board:')
            # print("  0 1 2 3 4 5 6 7")
            # for idx, row in enumerate(prevBoard):
            #     print(f"{idx} {row}")

        else:
            print("Checkers board not detected, checking game end...")
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
                jetson.write('next\n'.encode('utf-8'))
                numGames += 1
                startedFlag = False

            else:
                print("Game not ended")
    time.sleep(2.5)
        # show screen
        # cv.imshow('screen', screen)
    #     cv.imshow('screen_binary', screen_binary)

    #     if cv.waitKey(1) & 0xFF == ord('q'):
    #         break
    # cv.destroyAllWindows()

if __name__ == "__main__":
    main()