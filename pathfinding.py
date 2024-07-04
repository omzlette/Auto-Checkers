# A-Star Algorithm

import numpy as np

class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

def astar(maze, start, end):
    def get_direction(from_pos, to_pos):
        return (to_pos[0] - from_pos[0], to_pos[1] - from_pos[1])

    # Initialize start and end nodes
    start_node = Node(None, start)
    end_node = Node(None, end)

    # Initialize open and closed lists
    open_list = []
    closed_list = []

    open_list.append(start_node)

    while open_list:
        # Get current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent

            # Extract crucial points where direction changes
            crucial_points = [path[0]]  # Start with the starting point
            for i in range(1, len(path) - 1):
                direction_prev = get_direction(path[i - 1], path[i])
                direction_next = get_direction(path[i], path[i + 1])
                if direction_prev != direction_next:
                    crucial_points.append(path[i])
            crucial_points.append(path[-1])  # End with the end point

            return crucial_points[::-1]  # Return reversed crucial points

        # Generate children
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:  # Adjacent squares
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[0]) - 1) or node_position[1] < 0:
                continue

            if maze[node_position[0]][node_position[1]] != 0:
                continue

            new_node = Node(current_node, node_position)
            children.append(new_node)

        # Loop through children
        for child in children:
            if child in closed_list:
                continue

            child.g = current_node.g + 1
            child.h = np.sqrt(((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2))
            child.f = child.g + child.h

            if any(child == open_node and child.g > open_node.g for open_node in open_list):
                continue

            open_list.append(child)

def mapping(board, start, end):
    blackCaptured = [[0 for _ in range(15)] for _ in range(2)]
    whiteCaptured = [[0 for _ in range(15)] for _ in range(2)]
    maze = [[0 for _ in range(15)] for _ in range(15)]
    countB = 0
    countW = 0
    
    mappedStart = ((start[0]*2) + 2, start[1]*2) # change from 8x8 to 17x15
    mappedEnd = ((end[0]*2) + 2, end[1]*2) if end is not None else None
    
    # change from 8x8 to 15x15
    for i in range(8):
        for j in range(8):
            maze[i*2][j*2] = 1 if board[i][j].lower() in ['b', 'w'] else 0
            if board[i][j].lower() == 'b':
                countB += 1
            elif board[i][j].lower() == 'w':
                countW += 1

    BLeft = 8 - countB
    WLeft = 8 - countW

    for b in range(BLeft):
        blackCaptured[0][b * 2] = 1

    for w in range(WLeft):
        whiteCaptured[1][w * 2] = 1

    # append captured
    for row in range(2):
        maze.insert(row, blackCaptured[row])
        maze.append(whiteCaptured[row])

    if mappedEnd is None:
        # captured piece location
        mappedEnd = ((WLeft) * 2, 18)
        whiteCaptured[1][WLeft] = 0

    return maze, mappedStart, mappedEnd

def main():
    # Board will be changed to checkers board from main.py
    board = [['-', 'b', '-', 'b', '-', 'b', '-', 'b'],
            ['b', '-', 'b', '-', 'b', '-', 'b', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', 'w', '-', 'w', '-', 'w', '-', 'w'],
            ['w', '-', 'w', '-', 'w', '-', 'w', '-']]
    
    maze, start, end = mapping(board, (1, 0), (3, 3))

    print(f"Dimensions of maze: {len(maze)}x{len(maze[0])}")
    print(f"Start: {start}")
    print(f"End: {end}")

    # for row in maze:
    #     print(row)

    path = astar(maze, start, end)
    print(path)

    for i in range(len(path)):
        maze[path[i][0]][path[i][1]] = 5

    for i in range(len(maze)):
        print(maze[i])

if __name__ == '__main__':
    main()