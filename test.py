import time
import numpy as np

row = 2
col = 3

pos = (row, col)

# print((row-row, col-row) if row < col else (row-col, col-col))

start_pos = [[' ', 'b', ' ', 'b', ' ', 'b', ' ', 'b'],
            ['b', ' ', ' ', ' ', 'b', ' ', 'b', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', 'b', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', 'w', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', 'w', ' ', ' ', ' ', 'w', ' ', 'w'],
            ['w', ' ', 'w', ' ', 'w', ' ', 'w', ' ']]

def test(row, col):
    moves = []
    start_row, start_col = (row-row, col-row) if row < col else (row-col, col-col)
    while (0 <= start_row <= 7) and (0 <= start_row <= 7):
        # if board[start_row][start_col] == ' ':
        moves.append((start_row, start_col))
        start_row += 1
        start_col += 1
    return moves

# print(test(6, 3))
# print(len(test(6, 3)))

def test2(row, col):
    moves = []
    factor = 7 - row if row < col else 7 - col
    start_row, start_col = row - factor, col + factor
    while (0 <= start_row <= 7) and (0 <= start_row <= 7):
        # if board[start_row][start_col] == ' ':
        moves.append((start_row, start_col))
        start_row += 1
        start_col -= 1
    return moves

# print(test2(6, 3))
# print(len(test2(6, 3)))

def mergetest(row, col):
    moves = []
    ascent_factor = 7 - row if row < col else 7 - col
    ascent_diag_row, ascent_diag_col = row - ascent_factor, col + ascent_factor
    descent_diag_row, descent_diag_col = (row-min(row, col), col-min(row, col))

    while (0 <= descent_diag_row <= 7) and (0 <= descent_diag_col <= 7):
        # if board[descent_diag_row][descent_diag_col] == ' ':
        moves.append((descent_diag_row, descent_diag_col))
        descent_diag_row += 1
        descent_diag_col += 1

    while (0 <= ascent_diag_row <= 7) and (0 <= ascent_diag_col <= 7):
        # if board[ascent_diag_row][ascent_diag_col] == ' ':
        moves.append((ascent_diag_row, ascent_diag_col))
        ascent_diag_row += 1
        ascent_diag_col -= 1

    return moves

# print(mergetest(1, 0))
# print(len(mergetest(6, 3)))

def get_moves(row, col, board):
    moves = []
    piece = board[row][col]
    if piece == 'b':
        try:
            if board[row+1][col-1] == ' ' and col-1 != -1:
                moves.append([row+1, col-1])
            if board[row+1][col+1] == ' ':
                moves.append([row+1, col+1])
        except IndexError:
            pass

    elif piece == 'w':
        try:
            if board[row-1][col-1] == ' ' and row-1 != -1 and col-1 != -1:
                moves.append([row-1, col-1])
            if board[row-1][col+1] == ' ' and row-1 != -1:
                moves.append([row-1, col+1])
        except IndexError:
            pass
    
    else:
        return None
    return moves

# print(get_moves(1, 4, start_pos))
# print()

start_pos[3][2] = 'h'
start_pos[3][6] = 'h'

# for row in start_pos:
#     print(row)

# moves = []

# if moves:
#     print('moves')
#     for move in moves:
#         print(move)
#     print('moves')
# else:
#     print('no moves')

board = [[' ', 'b', ' ', 'b', ' ', 'b', ' ', 'b'],
            ['b', ' ', ' ', ' ', 'b', ' ', 'b', ' '],
            [' ', 'bk', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', 'w', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', 'w', ' ', ' ', ' ', 'w', ' ', 'w'],
            ['w', ' ', 'w', ' ', 'w', ' ', 'w', ' ']]
to_capture = []


def can_capture_king_uo(row, col, board):
    moves = []
    capturables = ['w', 'wk'] if board[row][col] == 'bk' else ['b', 'bk']
    ascent_factor = 7 - row if row < col else 7 - col
    ascent_diag_row, ascent_diag_col = row - ascent_factor, col + ascent_factor
    descent_diag_row, descent_diag_col = (row-min(row, col), col-min(row, col))

    while (0 <= descent_diag_row <= 7) and (0 <= descent_diag_col <= 7):
        if board[descent_diag_row][descent_diag_col] in capturables:
            if 0 <= descent_diag_row-1 <= 7 and 0 <= descent_diag_col-1 <= 7 and descent_diag_row < row and descent_diag_col < col and board[descent_diag_row-1][descent_diag_col-1] == ' ':
                to_capture.append((descent_diag_row, descent_diag_col))
                moves.append((descent_diag_row-1, descent_diag_col-1))
            elif 0 <= descent_diag_row+1 <= 7 and 0 <= descent_diag_col+1 <= 7 and descent_diag_row > row and descent_diag_col > col and board[descent_diag_row+1][descent_diag_col+1] == ' ':
                to_capture.append((descent_diag_row, descent_diag_col))
                moves.append((descent_diag_row+1, descent_diag_col+1))
        descent_diag_row += 1
        descent_diag_col += 1

    while (0 <= ascent_diag_row <= 7) and (0 <= ascent_diag_col <= 7):
        if board[ascent_diag_row][ascent_diag_col] in capturables:
            if 0 <= ascent_diag_row-1 <= 7 and 0 <= ascent_diag_col+1 <= 7 and ascent_diag_row < row and ascent_diag_col > col and board[ascent_diag_row-1][ascent_diag_col+1] == ' ': 
                to_capture.append((ascent_diag_row, ascent_diag_col))
                moves.append((ascent_diag_row-1, ascent_diag_col-1))
            elif 0 <= ascent_diag_row+1 <= 7 and 0 <= ascent_diag_col-1 <= 7 and ascent_diag_row > row and ascent_diag_col < col and board[ascent_diag_row+1][ascent_diag_col-1] == ' ':
                to_capture.append((ascent_diag_row, ascent_diag_col))
                moves.append((ascent_diag_row+1, ascent_diag_col+1))
        ascent_diag_row += 1
        ascent_diag_col -= 1

    return moves if moves else None

def can_capture_king_o(row, col, board):
    moves = []
    piece = board[row][col]
    capturables = ['w', 'wk'] if piece == 'bk' else ['b', 'bk']
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    for delta_row, delta_col in directions:
        capture_row, capture_col = row + delta_row, col + delta_col
        descent_diag_row, descent_diag_col = row - min(row, col), col - min(row, col)

        while 0 <= capture_row < 8 and 0 <= capture_col < 8:
            if board[capture_row][capture_col] in capturables:
                if 0 <= descent_diag_row <= 7 and 0 <= descent_diag_col <= 7 and board[descent_diag_row][descent_diag_col] == ' ':
                    moves.append((capture_row-1, capture_col-1))
                    to_capture.append((descent_diag_row, descent_diag_col))

            capture_row += delta_row
            capture_col += delta_col
            descent_diag_row += delta_row
            descent_diag_col += delta_col

    return moves if moves else None

start_time_unoptimized = time.time()
for i in range(1000):
    can_capture_king_uo(row, col, board)
end_time_unoptimized = time.time()
time_taken_unoptimized = end_time_unoptimized - start_time_unoptimized

# Time the optimized function
start_time_optimized = time.time()
for i in range(1000):
    can_capture_king_o(row, col, board)
end_time_optimized = time.time()
time_taken_optimized = end_time_optimized - start_time_optimized

time_taken_unoptimized_ms = (end_time_unoptimized - start_time_unoptimized) * 1000
time_taken_optimized_ms = (end_time_optimized - start_time_optimized) * 1000

# print(f"Unoptimized function time taken: {time_taken_unoptimized_ms:.4f} milliseconds")
# print(f"Optimized function time taken: {time_taken_optimized_ms:.4f} milliseconds")

# Unoptimized function time taken: 6.5062 milliseconds
# Optimized function time taken: 13.4728 milliseconds

def testInputLoop():
    a = int(input())
    if a == 1:
        return a
    print('failed')
    return testInputLoop()

# print(testInputLoop())

# print( if any('wk' in sublist for sublist in board) else 'bye')

# print(sum(row.count('b') + row.count('bk') for row in board))

def list_sum_recursive(input_list):
    if input_list == []:
        return 0
    return input_list[0] + list_sum_recursive(input_list[1:])

# print(list_sum_recursive([1, 2, 3, 4, 5])) # ans = 15
# print([1, 2, 3, 4, 5][1:])

def factorial_recursive(n):
    if n == 1:
        return 1
    return n * factorial_recursive(n-1)

# print(factorial_recursive(5)) # ans = 120


###############################


def alpha_beta(node, depth, alpha, beta, maximizing_player):
    if depth == 0 or node.is_terminal():
        return node.value

    if maximizing_player:
        value = float('-inf')
        for child in node.generate_children():
            value = max(value, alpha_beta(child, depth - 1, alpha, beta, False))
            alpha = max(alpha, value)
            print(f'child: {child.value}, value: {value}, alpha: {alpha}, beta: {beta}')
            if beta <= alpha:
                break  # Beta cutoff
        return value
    else:
        value = float('inf')
        for child in node.generate_children():
            value = min(value, alpha_beta(child, depth - 1, alpha, beta, True))
            beta = min(beta, value)
            print(f'child: {child.value}, value: {value}, alpha: {alpha}, beta: {beta}')
            if beta <= alpha:
                break  # Alpha cutoff
        return value

# Define a basic node
class Node:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def generate_children(self):
        return self.children

    def is_terminal(self):
        return not self.children  # Node without children is considered terminal

def visualize_tree(node, depth=0, prefix=""):
    if node:
        print(" " * (depth * 4) + prefix + str(node.value))
        for i, child in enumerate(node.generate_children()):
            new_prefix = "├── " if i < len(node.children) - 1 else "└── "
            visualize_tree(child, depth + 1, new_prefix)

# Create a simple tree
root = Node(0)
child1 = Node(99)
child2 = Node(99)
child3 = Node(99)
child4 = Node(99)
child5 = Node(99)
child6 = Node(99)
child7 = Node(-1)
child8 = Node(3)
child9 = Node(5)
child10 = Node(7)
child11 = Node(-6)
child12 = Node(-4)
child13 = Node(-7)
child14 = Node(10)

root.add_child(child1)
root.add_child(child2)
child1.add_child(child3)
child1.add_child(child4)
child2.add_child(child5)
child2.add_child(child6)
child3.add_child(child7)
child3.add_child(child8)
child4.add_child(child9)
child4.add_child(child10)
child5.add_child(child11)
child5.add_child(child12)
child6.add_child(child13)
child6.add_child(child14)

# visualize_tree(root)
# Initial call
# result = alpha_beta(root, 3, float('-inf'), float('inf'), True)
# print("Result:", result)

# input = 4
# for row in range(1, input+1):
#     for col in range(row % 2, input, 2):
#             print(f'{(row-1, col)} : {row % 2},{input} : {col}')


# testList = None
# testList.append([1, 2, 3])
# print(testList)

def test_while_loop():
    a = 0
    b = 0
    while a < 10:
        print('a', a)
        a += 1

    while b < 10:
        print('b', b)
        b += 1

# test_while_loop()

# find diagonal of 8x8 checkerboard
# for i in range(8):
#     for j in range(8):
#         if i == j:
#             print(i, j)

rows, cols = 8, 8
fakeboard = [[' ', 'b', ' ', 'b', ' ', 'b', ' ', 'b'],
            ['b', ' ', ' ', ' ', 'b', ' ', 'b', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', 'B', ' ', ' ', ' ', ' '],
            [' ', ' ', 'w', ' ', 'w', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', 'w', ' ', 'w'],
            ['w', ' ', 'w', ' ', 'w', ' ', 'w', ' ']]
piecerow, piececol = 4, 3
piece = fakeboard[piecerow][piececol]
majordiag = piecerow - piececol
minordiag = piecerow + piececol
capturable = 'w' if piece.lower() == 'b' else 'b'

for checkrow in range(rows):
    for checkcol in range(cols):
        # print('1', checkrow - checkcol == majordiag)
        # print('2', checkrow + checkcol == minordiag)
        # print('3', board[checkrow][checkcol].lower() == capturable)
        if checkrow - checkcol == majordiag and fakeboard[checkrow][checkcol].lower() == capturable:
            print('majordiag', checkrow, checkcol, fakeboard[checkrow][checkcol])
            if 0 <= checkrow <= 7 and 0 <= checkcol <= 7 and fakeboard[checkrow][checkcol] == ' ':
                print('majordiag', checkrow, checkcol, fakeboard[checkrow][checkcol])
        if checkrow + checkcol == minordiag and fakeboard[checkrow][checkcol].lower() == capturable:
            print('minordiag', checkrow, checkcol, fakeboard[checkrow][checkcol])
            if 0 <= checkrow <= 7 and 0 <= checkcol <= 7 and fakeboard[checkrow][checkcol] == ' ':
                print('minordiag', checkrow, checkcol, fakeboard[checkrow][checkcol])

def testVar(a):
    newa = a
    newa += 1
    return newa