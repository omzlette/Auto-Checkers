import cv2 as cv
import numpy as np

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
    direction = [[1, 1], [1, -1], [-1, 1], [-1, -1]]
    # get the index of the changed squares
    changed = np.where(prevBoard != newBoard)
    # get the number of changed squares
    if changed is not None:
        changed = list(zip(changed[0], changed[1]))
        if len(changed) == 2:
            # get the selected square
            selected = (changed[0][0], changed[0][1])
            # get the moved square
            move = (changed[1][0], changed[1][1])
            # get the move direction
            move_direction = [selected[0] - move[0], selected[1] - move[1]]
            return selected, move
    
    else:
        return None, None

def update_board_state(boardimg, corners):
    pieces = detect_pieces(boardimg, corners)
    sorted_pieces = []
    board = np.zeros((8, 8), dtype=int)
    for row in range(8):
        for col in range(8):
            square = (row, col)
            coords, x_delta, y_delta = get_board_squares(square, corners)
            for idx, piece in enumerate(pieces):
                x, y, _, _ = piece
                if coords[0] - x_delta/2 < x < coords[0] + x_delta/2 and coords[1] - y_delta/2 < y < coords[1] + y_delta/2:
                    board[row][col] = 1
                    sorted_pieces.append(piece, square, coords)
                    print(idx, piece, coords, square)
                    break
    return board, sorted_pieces

def initGame(numGames):
    turn = 'b'
    # initialize the board
    prevBoard = np.array([[0, 1, 0, 1, 0, 1, 0, 1],
                          [1, 0, 1, 0, 1, 0, 1, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 1, 0, 1, 0, 1, 0, 1],
                          [1, 0, 1, 0, 1, 0, 1, 0]])
    
    bot = 'b' if numGames % 2 == 0 else 'w'
    our = 'w' if numGames % 2 == 0 else 'b'
    return turn, prevBoard, bot, our