import random
import copy

class ZobristHashing:
    def __init__(self):
        self.zobrist_table = self.create_zobrist_table()

    def create_zobrist_table(self):
        table = {}
        for i in range(8):
            for j in range(8):
                table[(i, j)] = random.getrandbits(64)
        return table
    

class test:
    def __init__(self):
        self.testVariable = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def testPassin(self, variable):
        variable[0] = 100
        print(id(variable), variable)
        print(id(self.testVariable), self.testVariable)

# testObj = test()
# testObj.testPassin(testObj.testVariable)



# from player import *

# testBoard = [['-', '-', '-', 'W', '-', '-', '-', '-'],
#             ['-', '-', '-', '-', '-', '-', '-', '-'],
#             ['-', '-', '-', 'W', '-', 'b', '-', 'b'],
#             ['-', '-', '-', '-', '-', '-', 'b', '-'],
#             ['-', 'b', '-', 'w', '-', 'w', '-', 'b'],
#             ['b', '-', '-', '-', 'w', '-', '-', '-'],
#             ['-', '-', '-', 'w', '-', 'w', '-', '-'],
#             ['-', '-', '-', '-', '-', '-', 'w', '-']]

testBoard = [['-', '-', '-', '-', '-', '-', '-', '-'],
             ['-', '-', '-', '-', '-', '-', '-', '-'],
             ['-', '-', '-', '-', '-', '-', '-', '-'],
             ['-', '-', '-', '-', '-', '-', '-', '-'],
             ['-', '-', '-', '-', '-', '-', '-', '-'],
             ['-', '-', 'b', '-', 'w', '-', '-', '-'],
             ['-', '-', '-', '-', '-', 'b', '-', '-'],
             ['w', '-', 'w', '-', '-', '-', 'w', '-']]

# player1 = User('b', testBoard, {'b': [], 'w': []})
# player2 = AlphaBeta('b', testBoard, {'b': [], 'w': []})

def runawayCheckers(board, piece):
    # Check if the piece has a path of becoming a king
    blackDirections = [[1, -1], [1, 1]]
    whiteDirections = [[-1, -1], [-1, 1]]

    pieceRow = piece[0]
    pieceCol = piece[1]
    pieceColor = board[pieceRow][pieceCol].lower()

    movePath = []

    if pieceColor == 'b':
        directions = blackDirections
        oppColor = 'w'
        endRow = 7  # Row where black pieces become kings
    else:
        directions = whiteDirections
        oppColor = 'b'
        endRow = 0  # Row where white pieces become kings

    def canMove(pieceRow, pieceCol, direction):
        checkRow, checkCol = pieceRow + direction[0], pieceCol + direction[1]
        oppRowL, oppColL = checkRow + direction[0], checkCol + directions[0][1]
        oppRowR, oppColR = checkRow + direction[0], checkCol + directions[1][1]
        if 0 <= checkRow <= 7 and 0 <= checkCol <= 7 and board[checkRow][checkCol] == '-':
            if 0 <= oppRowR <= 7 and 0 <= oppColR <= 7 and board[oppRowR][oppColR].lower() != oppColor:
                if 0 <= oppRowL <= 7 and 0 <= oppColL <= 7 and board[oppRowL][oppColL].lower() != oppColor:
                    return True, checkRow, checkCol
        return False, -1, -1

    def canBridge(pieceRow, pieceCol, direction):
        bridgeRow, bridgeCol = pieceRow, pieceCol + (2 * direction[1])
        landingRow, landingCol = pieceRow + direction[0], pieceCol + direction[1]
        oppRow, oppCol = landingRow + direction[0], pieceCol
        print(bridgeRow, bridgeCol, landingRow, landingCol, oppRow, oppCol)
        if landingRow >= 0 and landingRow < 8 and landingCol >= 0 and landingCol < 8 and board[landingRow][landingCol] == '-':
            if 0 <= bridgeRow <= 7 and 0 <= bridgeCol <= 7 and board[bridgeRow][bridgeCol] != '-':
                if 0 <= oppRow <= 7 and 0 <= oppCol <= 7 and board[oppRow][oppCol].lower() == oppColor:
                    return True, landingRow, landingCol
        return False, -1, -1

    for direction in directions:
        canMoveFlag, _, _ = canMove(pieceRow, pieceCol, direction)
        if canMoveFlag:
            print('canMove', pieceRow, pieceCol, direction)
            return True
        else:
            canBridgeFlag, _, _ = canBridge(pieceRow, pieceCol, direction)
            if canBridgeFlag:
                print('canBridge', pieceRow, pieceCol, direction)
                return True

    return False

print(runawayCheckers(testBoard, (5, 2)))