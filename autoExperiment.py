import cv2 as cv
import numpy as np
import pyautogui
from PIL import ImageGrab

def convert_to_binary(image):
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    # remove background
    # (hmin, hmax, smin, smax, vmin, vmax) = getHSV()
    hmin = 0
    hmax = 179
    smin = 0
    smax = 255
    vmin = 124
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

def getMove(prevBoard, newBoard):
    # get the index of the changed squares
    prevBoardState = np.where(prevBoard != 0, 1, 0)
    for row in prevBoardState:
        print(row)
    changed = np.where(prevBoardState != newBoard)
    # get the number of changed squares
    if changed is not None:
        changed = list(zip(changed[0], changed[1]))
        if len(changed) == 2:
            # get the selected square
            selected = (changed[0][0], changed[0][1])
            pieceType = prevBoard[selected[0]][selected[1]]
            # check if the piece is a king
            if pieceType == 1 and changed[1][0] == 7:
                pieceType = 3
            elif pieceType == 2 and changed[1][0] == 0:
                pieceType = 4
            # get the moved square
            move = (changed[1][0], changed[1][1])
            return selected, move, pieceType
        
    return None, None, None

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
                    sorted_pieces.append(piece, square, coords)
                    break
    return board, sorted_pieces

def update_board_state(prevBoard, currBoard):
    updated_board = [row[:] for row in prevBoard]

    for row in range(8):
        for col in range(8):
            if currBoard[row][col] == 1 and prevBoard[row][col] == 0:
                _, _, pieceType = getMove(prevBoard, currBoard)
                updated_board[row][col] = pieceType
            elif currBoard[row][col] == 0 and prevBoard[row][col] != 0:
                updated_board[row][col] = 0
    
    return updated_board

def checkKing(board):
    for i in range(8):
        if board[7][i] == 1:
            board[7][i] = 3
        if board[0][i] == 2:
            board[0][i] = 4
    return board

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
    
    bot = 'b' if numGames % 2 == 0 else 'w'
    our = 'w' if numGames % 2 == 0 else 'b'
    return turn, prevBoard, bot, our

def main():
    # test update_board_state
    prevBoard = np.array([[0, 1, 0, 1, 0, 1, 0, 1],
                          [1, 0, 1, 0, 1, 0, 1, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 2, 0, 2, 0, 2, 0, 2],
                          [2, 0, 2, 0, 2, 0, 2, 0]])
    
    currBoard = np.array([[0, 1, 0, 1, 0, 1, 0, 1],
                          [1, 0, 1, 0, 1, 0, 1, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 1, 0],
                          [0, 1, 0, 1, 0, 1, 0, 0],
                          [1, 0, 1, 0, 1, 0, 1, 0]])

    selected, move, pieceType = getMove(prevBoard, currBoard)
    print(selected, move, pieceType)

    # updated_board = update_board_state(prevBoard, currBoard)

    # print("Updated board")
    # for row in updated_board:
    #     print(row)

if __name__ == '__main__':
    main()

# def main():
#     pickerwindowBG = np.zeros((300, 512, 3), np.uint8)
#     # hsvColorSlider()
#     # (hmin, hmax, smin, smax, vmin, vmax) = getHSV()
#     # cv.imshow('HSV Color Slider', pickerwindowBG)

#     hue_min = 0
#     hue_max = 179
#     sat_min = 0
#     sat_max = 255
#     val_min = 124
#     val_max = 255

#     numGames = 0
#     startedFlag = False

#     while numGames < 50:
#         if startedFlag == False:
#             print("Game started")
#             startedFlag = True
#             turn, prevBoard, bot, our = initGame(numGames)

#         print(bot, our, numGames)

#         screen = ImageGrab.grab(all_screens=True)

#         # screen right : (1920, 0, 3840, 1080)
#         # screen left : (0, 0, 1920, 1080)

#         screen = screen.crop((1920, 0, 3840, 1080))
#         screen = np.array(screen)

#         screen_binary = convert_to_binary(screen)
#         ret, corners = detect_checkers_board(screen)
#         screen = cv.cvtColor(screen, cv.COLOR_BGR2RGB)

#         if ret:
#             print("Checkers board detected")
#             screen_binary = cv.cvtColor(screen_binary, cv.COLOR_GRAY2RGB)

#             # get the pieces
#             pieces = detect_pieces(screen_binary, corners)
#             print(len(pieces), pieces)
#             for piece in pieces:
#                 x, y, w, h = piece
#                 cv.rectangle(screen_binary, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
#             # update board state
#             # newBoard, sorted_pieces = update_board_state(screen_binary, corners)
#             # if turn == bot:
#             #     selected, move = getMove(prevBoard, newBoard)

#             screen_binary = crop_board(screen_binary, corners)
            
#             cv.imshow('screen_binary', screen_binary)
#         else:
#             print("Checkers board not detected")
#             # check game end
#             endimg = cv.imread('end.png')
#             matchinfo = match_images(screen, endimg)
#             loc, w, h = matchinfo
#             if loc[0].size > 0:
#                 print("Game ended")
#                 for pt in zip(*loc[::-1]):
#                     cv.rectangle(screen, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
                
#                 # reset the board
#                 pyautogui.moveTo(loc[1][-1] + 200, loc[0][-1] + 310)
#                 pyautogui.click()
#                 numGames += 1
#                 startedFlag = False

#             else:
#                 print("Game not ended")
#         # show screen
#         cv.imshow('screen', screen)

#         if cv.waitKey(1) & 0xFF == ord('q'):
#             break
#     cv.destroyAllWindows()