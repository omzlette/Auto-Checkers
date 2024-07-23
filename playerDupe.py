import numpy as np
import copy
import random
import time
from itertools import zip_longest
import checkersDupe as checkers

width, height = checkers.width, checkers.height
rows, cols = checkers.rows, checkers.cols
squareSize = checkers.squareSize

class Player():
    def __init__(self, turn, board, movesDone):
        self.turn = turn
        self.board = board
        self.movesDone = movesDone
        self.prevCount = countBlack(board) if turn == 'b' else countWhite(board)
        self.init_variables()

    def init_variables(self):
        self.selectedPiece = []
        self.mandatory_moves = []
        self.prevCapture = []
        self.prevMove = []
        self.validMoves = []
        self.capturePos = []

    def select_piece(self, row, col, turn, board):
        # check if piece is valid and not conflicting with mandatory capture
        selectedPiece, validMoves, capturePos = [], [], []
        self.mandatory_moves = self.get_mandatory_capture(turn, board, self.prevMove)
        if self.mandatory_moves:
            if [row, col] in self.mandatory_moves:
                selectedPiece = [row, col]
                validMoves, capturePos = self.get_valid_moves(row, col, board)
            # else:
            #     print("You must capture @", self.mandatory_moves, "selected piece:", [row, col])
        else:
            if board[row][col].lower() == 'b':
                if turn == 'b':
                    validMoves, capturePos = self.get_valid_moves(row, col, board)
                    if validMoves != []:
                        selectedPiece = [row, col]
                #     else:
                #         print("No valid moves")
                # else:
                #     print("Not your turn (White turn)")
            elif board[row][col].lower() == 'w':
                if turn == 'w':
                    validMoves, capturePos = self.get_valid_moves(row, col, board)
                    if validMoves != []:
                        selectedPiece = [row, col]
                    # else:
                    #     print("No valid moves")
            #     else:
            #         print("Not your turn (Black turn)")
            # else:
            #     print("No piece selected")
        return selectedPiece, validMoves, capturePos
    
    def move_piece(self, moveto, turn, board):
        [rowMove, colMove] = moveto
        if self.validMoves is not None and [rowMove, colMove] in self.validMoves:
            self.prevMove = [rowMove, colMove]
            board[rowMove][colMove] = board[self.selectedPiece[0]][self.selectedPiece[1]]
            board[self.selectedPiece[0]][self.selectedPiece[1]] = '-'
            if self.capturePos != []:
                idxtoRemove = self.validMoves.index([rowMove, colMove])
                board[self.capturePos[idxtoRemove][0]][self.capturePos[idxtoRemove][1]] = '-'
                self.prevMove = [rowMove, colMove]
                self.capturePos = []
                self.mandatory_moves = self.get_mandatory_capture(turn, board, self.prevMove)
            board = self.make_king(rowMove, colMove, board)
            self.selectedPiece = []
            self.validMoves = []
            if not self.mandatory_moves:
                self.init_variables()
                turn = 'w' if turn == 'b' else 'b'
        else:
            self.selectedPiece, self.validMoves, self.capturePos = self.select_piece(rowMove, colMove, turn, board)
        return board, turn

    def get_valid_moves(self, row, col, board):
        moves = []
        capturePos = []
        moves, capturePos = self.can_capture(row, col, board)
        if moves == []:
            if board[row][col] == 'b':
                if 0 <= row+1 <= 7 and 0 <= col-1 <= 7 and board[row+1][col-1] == '-':
                    moves.append([row+1, col-1])
                if 0 <= row+1 <= 7 and 0 <= col+1 <= 7 and board[row+1][col+1] == '-':
                    moves.append([row+1, col+1])

            elif board[row][col] == 'w':
                if 0 <= row-1 <= 7 and 0 <= col-1 <= 7 and board[row-1][col-1] == '-':
                    moves.append([row-1, col-1])
                if 0 <= row-1 <= 7 and 0 <= col+1 <= 7 and board[row-1][col+1] == '-':
                    moves.append([row-1, col+1])

            elif board[row][col] == 'B' or board[row][col] == 'W':
                directions = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
                for direction in directions:
                    for i in range(1, 8):
                        checkrow = row + direction[0] * i
                        checkcol = col + direction[1] * i
                        if 0 <= checkrow <= 7 and 0 <= checkcol <= 7:
                            if board[checkrow][checkcol] == '-':
                                moves.append([checkrow, checkcol])
                            else:
                                break
                        else:
                            break
        return (moves, capturePos) if moves else ([], [])
    
    def can_capture(self, row, col, board):
        moves = []
        capturePos = []
        piece = board[row][col]
        if piece == 'B' or piece == 'W':
            capturable = 'w' if piece == 'B' else 'b'
            directions = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
            for direction in directions:
                for i in range(1, 8):
                    checkrow = row + direction[0] * i
                    checkcol = col + direction[1] * i
                    if 0 <= checkrow <= 7 and 0 <= checkcol <= 7:
                        if board[checkrow][checkcol] == '-':
                            continue
                        elif board[checkrow][checkcol].lower() == capturable:
                            if 0 <= checkrow+direction[0] <= 7 and 0 <= checkcol+direction[1] <= 7 and board[checkrow+direction[0]][checkcol+direction[1]] == '-':
                                capturePos.append([checkrow, checkcol]) if [checkrow, checkcol] not in capturePos else None
                                moves.append([checkrow+direction[0], checkcol+direction[1]])
                                break
                            else:
                                break
                        else:
                            break
                    else:
                        break
        else:
            if piece == 'b':
                if 0 <= row+2 <= 7 and 0 <= col-2 <= 7 and board[row+1][col-1].lower() == 'w' and board[row+2][col-2] == '-':
                    capturePos.append([row+1, col-1]) if [row+1, col-1] not in capturePos else None
                    moves.append([row+2, col-2])
                if 0 <= row+2 <= 7 and 0 <= col+2 <= 7 and board[row+1][col+1].lower() == 'w' and board[row+2][col+2] == '-':
                    capturePos.append([row+1, col+1]) if [row+1, col+1] not in capturePos else None
                    moves.append([row+2, col+2])

            elif piece == 'w':
                if 0 <= row-2 <= 7 and 0 <= col-2 <= 7 and board[row-1][col-1].lower() == 'b' and board[row-2][col-2] == '-':
                    capturePos.append([row-1, col-1]) if [row-1, col-1] not in capturePos else None
                    moves.append([row-2, col-2])
                if 0 <= row-2 <= 7 and 0 <= col+2 <= 7 and board[row-1][col+1].lower() == 'b' and board[row-2][col+2] == '-':
                    capturePos.append([row-1, col+1]) if [row-1, col+1] not in capturePos else None
                    moves.append([row-2, col+2])

        return moves, capturePos

    def get_mandatory_capture(self, turn, board, prevMove=[]):
        mandatory_moves = []
        for row in range(rows):
            for col in range(cols):
                if board[row][col].lower() == 'b' and turn == 'b':
                    if self.can_capture(row, col, board)[1]:
                        if prevMove != []:
                            if [row, col] == prevMove:
                                mandatory_moves.append([row, col])
                        else:
                            mandatory_moves.append([row, col])
                        if board[row][col] == 'b' and row + 2 == 7:
                            # If the piece is at the end of the board, it's promoted to king and stops continuing the capture
                            break
                elif board[row][col].lower() == 'w' and turn == 'w':
                    if self.can_capture(row, col, board)[1]:
                        if prevMove != []:
                            if [row, col] == prevMove:
                                mandatory_moves.append([row, col])
                        else:
                            mandatory_moves.append([row, col])
                        if board[row][col] == 'w' and row - 2 == 0:
                            # If the piece is at the end of the board, it's promoted to king and stops continuing the capture
                            break
        return mandatory_moves if mandatory_moves else []
    
    def make_king(self, row, col, board):
        if board[row][col] == 'b' and row == 7:
            board[row][col] = 'B'
        elif board[row][col] == 'w' and row == 0:
            board[row][col] = 'W'
        return board
    
    def get_all_moves(self, player, board, pieceLoc=None):
        moves = {}
        if self.mandatory_moves and pieceLoc is None:
            for piece in self.mandatory_moves:
                if board[piece[0]][piece[1]].lower() == player:
                    moves[tuple(piece)] = self.get_valid_moves(piece[0], piece[1], board)[0]
        
        if pieceLoc is not None:
            # Check only passed piece location
            moves[tuple(pieceLoc)] = self.get_valid_moves(pieceLoc[0], pieceLoc[1], board)[0]
        else:
            mandatory_moves = self.get_mandatory_capture(player, board)
            if mandatory_moves:
                for piece in mandatory_moves:
                    moves[tuple(piece)] = self.get_valid_moves(piece[0], piece[1], board)[0]
            else:
                for row in range(rows):
                    for col in range(cols):
                        if board[row][col].lower() == player and self.get_valid_moves(row, col, board)[0] != []:
                            moves[(row, col)] = self.get_valid_moves(row, col, board)[0]

        return moves
    
    def update_board(self, board, piece, move):
        self.selectedPiece, self.validMoves, self.capturePos = self.select_piece(piece[0], piece[1], self.turn, board)
        capture_piece = self.capturePos
        board, turn = self.move_piece(move, self.turn, board)
        return board, turn, capture_piece

    def simulate_game(self, piece, move, turn, board):
        new_board = copy.deepcopy(board)
        self.selectedPiece, self.validMoves, self.capturePos = self.select_piece(piece[0], piece[1], turn, new_board)
        new_board, _ = self.move_piece(move, turn, new_board)
        return new_board

    def runawayCheckers(self, board, piece):
        # Check if the piece has a path of becoming a king
        blackDirections = [[1, -1], [1, 1]]
        whiteDirections = [[-1, -1], [-1, 1]]

        pieceRow = piece[0]
        pieceCol = piece[1]
        pieceColor = board[pieceRow][pieceCol].lower()

        if pieceColor == 'b':
            directions = blackDirections
            oppColor = 'w'
        else:
            directions = whiteDirections
            oppColor = 'b'

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
            if landingRow >= 0 and landingRow < 8 and landingCol >= 0 and landingCol < 8 and board[landingRow][landingCol] == '-':
                if 0 <= bridgeRow <= 7 and 0 <= bridgeCol <= 7 and board[bridgeRow][bridgeCol] != '-':
                    if 0 <= oppRow <= 7 and 0 <= oppCol <= 7 and board[oppRow][oppCol].lower() == oppColor:
                        return True, landingRow, landingCol
            return False, -1, -1

        for direction in directions:
            canMoveFlag, _, _ = canMove(pieceRow, pieceCol, direction)
            if canMoveFlag:
                return True
            else:
                canBridgeFlag, _, _ = canBridge(pieceRow, pieceCol, direction)
                if canBridgeFlag:
                    return True

        return False
    
    def evaluate_board(self, board, verbose=False):
        vprint = print if verbose else lambda *a, **k: None
        # Evaluation function for the board
        # The bot is always maximizing, the opponent is always minimizing
        # Can only be used for implementing algorithms that require evaluation function

        PIECECOUNT = 100
        KINGPIECE = 50
        TRAPPEDKING = 50 # negative points
        DOGHOLE = 10
        BACKRANK = 20
        GAMEOVER = 2000
        DRAW = 0

        totalPieces = 0
        for row in range(rows):
            totalPieces += sum(list(map(lambda x: True if x.lower() in ['b', 'w'] else False, board[row])))

        # # Multiplier for making the bot favor more pieces
        # if totalPieces < 8:
        #     MULTIPLIER = 5/6
        # elif totalPieces >= 8 and totalPieces <= 10:
        #     MULTIPLIER = 1
        # elif totalPieces >= 11 and totalPieces <= 13:
        #     MULTIPLIER = 7/6
        # else:
        #     MULTIPLIER = 4/3
        MULTIPLIER = 1

        ourRunawayAdded = False
        oppRunawayAdded = False

        ourTurn = self.botTurn
        oppTurn = self.oppTurn
        vprint(f'Bot Turn: {ourTurn}, Opponent Turn: {oppTurn}')
        ourVal = 3 # Turn value
        oppVal = 0

        for row in range(rows):
            for col in range(cols):
                # No. of pieces
                if board[row][col].lower() == ourTurn:
                    ourVal += PIECECOUNT * MULTIPLIER
                    vprint(f'Our Piece Count ({PIECECOUNT * MULTIPLIER}): {ourVal}, Total Value: {ourVal - oppVal}')
                elif board[row][col].lower() == oppTurn:
                    oppVal += PIECECOUNT * MULTIPLIER
                    vprint(f'Opponent Piece Count ({PIECECOUNT * MULTIPLIER}): {oppVal}, Total Value: {ourVal - oppVal}')
                # No. of kings and trapped kings (Added on top of pieces)
                if board[row][col] == ourTurn.upper():
                    ourVal += KINGPIECE
                    vprint(f'Our King Piece ({KINGPIECE}): {ourVal}, Total Value: {ourVal - oppVal}')
                    kingMoves = self.get_all_moves(ourTurn, board, [row, col])
                    vprint(f'Our King Moves {row, col}:', kingMoves)
                    # for rowb in board:
                    #     debugToFile(f'{rowb}\n', 'debug-eval.txt')
                    # debugToFile(f'Our -- {ourTurn} -- King Moves {row, col}: {kingMoves}\n', 'debug-eval.txt')
                    if len(kingMoves[(row, col)]) == 0:
                        ourVal -= TRAPPEDKING
                        vprint(f'Our Trapped King (-{TRAPPEDKING}): {ourVal}, Total Value: {ourVal - oppVal}')
                elif board[row][col] == oppTurn.upper():
                    oppVal += KINGPIECE
                    vprint(f'Opponent King Piece ({KINGPIECE}): {oppVal}, Total Value: {ourVal - oppVal}')
                    kingMoves = self.get_all_moves(oppTurn, board, [row, col])
                    vprint('Opponent King Moves:', kingMoves)
                    if kingMoves == {}:
                        oppVal -= TRAPPEDKING
                        vprint(f'Opponent Trapped King (-{TRAPPEDKING}): {oppVal}, Total Value: {ourVal - oppVal}')

                # # Runaway Checkers
                # # If the bot has a path to become a king, it's better for the bot
                # if board[row][col] == ourTurn and not ourRunawayAdded:
                #     if ourTurn == 'b' and row >= 4:
                #         runawayFlag = self.runawayCheckers(board, [row, col])
                #         if runawayFlag:
                #             numMovestoKing = 7 - row
                #             ourVal += KINGPIECE - (numMovestoKing * 3)
                #             ourRunawayAdded = True
                #             vprint(f'Our Runaway Checkers ({KINGPIECE - (numMovestoKing * 3)}): {ourVal}, Total Value: {ourVal - oppVal}')
                #     elif ourTurn == 'w' and row <= 3:
                #         runawayFlag = self.runawayCheckers(board, [row, col])
                #         if runawayFlag:
                #             numMovestoKing = row
                #             ourVal += KINGPIECE - (numMovestoKing * 3)
                #             ourRunawayAdded = True
                #             vprint(f'Our Runaway Checkers ({KINGPIECE - (numMovestoKing * 3)}): {ourVal}, Total Value: {ourVal - oppVal}')
                # elif board[row][col] == oppTurn and not oppRunawayAdded:
                #     if oppTurn == 'b' and row >= 4:
                #         runawayFlag = self.runawayCheckers(board, [row, col])
                #         if runawayFlag:
                #             numMovestoKing = 7 - row
                #             oppVal += KINGPIECE - (numMovestoKing * 3)
                #             oppRunawayAdded = True
                #             vprint(f'Opponent Runaway Checkers ({KINGPIECE - (numMovestoKing * 3)}): {oppVal}, Total Value: {ourVal - oppVal}')
                #     elif oppTurn == 'w' and row <= 3:
                #         runawayFlag = self.runawayCheckers(board, [row, col])
                #         if runawayFlag:
                #             numMovestoKing = row
                #             oppVal += KINGPIECE - (numMovestoKing * 3)
                #             oppRunawayAdded = True
                #             vprint(f'Opponent Runaway Checkers ({KINGPIECE - (numMovestoKing * 3)}): {oppVal}, Total Value: {ourVal - oppVal}')

        # Dog-Hole (putting ourselves in a dog hole is no good)
        # For black, h2 (28) with white on g1 (32). For white, a7 (5) with black on b8 (1).
        if board[7][6].lower() == 'w' and board[6][7].lower() == 'b' and ourTurn == 'w':
            ourVal -= DOGHOLE
            vprint(f'Our Dog Hole ({DOGHOLE}): {ourVal}, Total Value: {ourVal - oppVal}')
        elif board[7][6].lower() == 'w' and board[6][7].lower() == 'b' and oppTurn == 'w':
            oppVal -= DOGHOLE
            vprint(f'Opponent Dog Hole ({DOGHOLE}): {oppVal}, Total Value: {ourVal - oppVal}')
        
        if board[0][1].lower() == 'b' and board[1][0].lower() == 'w' and oppTurn == 'b':
            oppVal -= DOGHOLE
            vprint(f'Opponent Dog Hole ({DOGHOLE}): {oppVal}, Total Value: {ourVal - oppVal}')
        elif board[0][1].lower() == 'b' and board[1][0].lower() == 'w' and ourTurn == 'b':
            ourVal -= DOGHOLE
            vprint(f'Our Dog Hole ({DOGHOLE}): {ourVal}, Total Value: {ourVal - oppVal}')

        # Back Rank (making the other side getting a king harder is better)
        # If one side have lower opportunity to get a king by the other side blocking, it's better for the blocker. 
        # +20 to the blocker
        backrankB = list(map(lambda x: True if x.lower() == 'b' else False, board[0]))
        backrankW = list(map(lambda x: True if x.lower() == 'w' else False, board[7]))
        
        backrankBCount = sum(backrankB)
        backrankWCount = sum(backrankW)
        vprint(f'Back Rank: {backrankB}, {backrankW}')
        vprint(f'Back Rank: {backrankBCount}, {backrankWCount}')

        if backrankBCount > backrankWCount and ourTurn == 'b':
            ourVal += BACKRANK
            vprint(f'Our Back Rank ({BACKRANK}): {ourVal}, Total Value: {ourVal - oppVal}')
        elif backrankBCount > backrankWCount and oppTurn == 'b':
            oppVal += BACKRANK
            vprint(f'Opponent Back Rank ({BACKRANK}): {oppVal}, Total Value: {ourVal - oppVal}')

        elif backrankWCount > backrankBCount and ourTurn == 'w':
            ourVal += BACKRANK
            vprint(f'Our Back Rank ({BACKRANK}): {ourVal}, Total Value: {ourVal - oppVal}')
        elif backrankWCount > backrankBCount and oppTurn == 'w':
            oppVal += BACKRANK
            vprint(f'Opponent Back Rank ({BACKRANK}): {oppVal}, Total Value: {ourVal - oppVal}')

        # Win/Lose/Draw
        if is_game_over(board, self.movesDone, self.mandatory_moves) == ourTurn:
            ourVal += GAMEOVER
            vprint(f'Game Over ({ourTurn}): {ourVal}, Total Value: {ourVal - oppVal}')
        elif is_game_over(board, self.movesDone, self.mandatory_moves) == oppTurn:
            oppVal += GAMEOVER
            vprint(f'Game Over ({oppTurn}): {oppVal}, Total Value: {ourVal - oppVal}')
        elif is_game_over(board, self.movesDone, self.mandatory_moves) == 'draw':
            ourVal += DRAW
            oppVal += DRAW
            vprint(f'Draw: {ourVal}, Total Value: {ourVal - oppVal}')

        return ourVal - oppVal

class User(Player):
    def __init__(self, turn, board, movesDone):
        super().__init__(turn, board, movesDone)
        self.user = True
        self.ourTurn = 'b' if turn == 'b' else 'w'
        self.oppTurn = 'w' if turn == 'b' else 'b'

    # def get_mouse_pos(self):
    #     x, y = pygame.mouse.get_pos()
    #     row, col = y // squareSize, x // squareSize
    #     return row, col
    
    def handle_mouse_click(self, row, col, board):
        turn = None
        selectedPiece = []
        if self.selectedPiece == []:
            self.selectedPiece, self.validMoves, self.capturePos = self.select_piece(row, col, self.turn, board)
            board, turn = board, self.turn
        else:
            selectedPiece = self.selectedPiece
            board, turn = self.move_piece([row, col], self.turn, board)
        return board, turn, selectedPiece

class Minimax(Player):
    def __init__(self, turn, board, movesDone):
        super().__init__(turn, board, movesDone)
        self.botTurn = 'b' if turn == 'b' else 'w'
        self.oppTurn = 'w' if turn == 'b' else 'b'
        self.user = False
        self.timer = 0
        self.timeLimit = 20

    def perform_all_move(self, piece, initialMove, turn, board):
        new_board = self.simulate_game(piece, initialMove, turn, board)
        oppTurn = 'w' if turn == 'b' else 'b'
        checkNextCapture = False
        finalMove = initialMove
        move_sequence = [initialMove]

        if abs(finalMove[0] - piece[0]) >= 2 and abs(finalMove[1] - piece[1]) >= 2:
            captureLoc = ((finalMove[0] + piece[0]) // 2, (finalMove[1] + piece[1]) // 2)
            if board[captureLoc[0]][captureLoc[1]].lower() == oppTurn:
                checkNextCapture = True

        while checkNextCapture:
            captureMoves, _ = self.can_capture(finalMove[0], finalMove[1], new_board)
            if captureMoves != []:
                for captureMove in captureMoves:
                    new_board = self.simulate_game(finalMove, captureMove, turn, new_board)
                    move_sequence.append(captureMove)
                    finalMove = captureMove
            else:
                break

        return new_board, initialMove, move_sequence

    def iterativeDeepening(self, board):
        lastPiece = None
        lastMove = None
        lastVal = -np.inf
        lastDepth = None
        depth = 1
        self.timer = time.time()
        while True:
            if time.time() - self.timer > self.timeLimit: break
            value, piece, move = self.minimax(board, depth, True)
            lastDepth = depth
            lastVal = value
            lastPiece = piece
            lastMove = move
            if value >= 2000:
                break
            depth += 1
        debugToFile(f'Depth: {depth}, Last Depth: {lastDepth}, Val: {lastVal}, Piece: {lastPiece}, Move: {lastMove}', 'depthExperiment.txt')
        return lastVal, lastPiece, lastMove

    def play(self, board):
        if not self.mandatory_moves:
            mandatory_moves = self.get_mandatory_capture(self.botTurn, board)
            if len(mandatory_moves) == 1:
                piece, move = mandatory_moves[0], self.get_valid_moves(mandatory_moves[0][0], mandatory_moves[0][1], board)[0][0]
            else:
                _, piece, move = self.iterativeDeepening(board)
        else:
            if board[self.mandatory_moves[0][0]][self.mandatory_moves[0][1]].lower() == self.botTurn:
                piece = self.mandatory_moves[0]
                if len(self.get_valid_moves(piece[0], piece[1], board)[0]) == 1:
                    move = self.get_valid_moves(piece[0], piece[1], board)[0][0]
            else:
                _, piece, move = self.iterativeDeepening(board)
        return piece, move
        
    def minimax(self, board, depth, maximizing):
        debugToFile(f"Entering depth {depth} for board state:", 'debug-minimax.txt')
        for row in board:
            debugToFile(' '.join(row), 'debug-minimax.txt')
        if depth == 0 or is_game_over(board, self.movesDone, self.mandatory_moves) in ['w', 'b', 'draw'] or time.time() - self.timer > self.timeLimit:
            return self.evaluate_board(board), None, None

        if maximizing:
            maxEval = -np.inf
            bestPiece = None
            bestMove = None
            movesdict = self.get_all_moves(self.botTurn, board)
            for piece, movetolist in movesdict.items():
                for initialMove in movetolist:
                    debugToFile('-'*20, 'debug-minimax.txt')
                    debugToFile(f'Max Evaluation for {piece} -> {initialMove} @ Depth {depth}', 'debug-minimax.txt')
                    new_board, _, _ = self.perform_all_move(piece, initialMove, self.botTurn, board)
                    eval, _, _ = self.minimax(new_board, depth-1, False)
                    debugToFile(f'Evaluated child node @ Depth {depth} with value: {eval}', 'debug-minimax.txt')
                    if eval > maxEval:
                        debugToFile(f'Updating bestPiece: {piece}, bestMove: {initialMove}', 'debug-minimax.txt')
                        maxEval = max(maxEval, eval)
                        bestPiece = piece
                        bestMove = initialMove

            return maxEval, bestPiece, bestMove
        
        else:
            minEval = np.inf
            bestPiece = None
            bestMove = None
            movesdict = self.get_all_moves(self.oppTurn, board)
            for piece, movetolist in movesdict.items():
                for initialMove in movetolist:
                    debugToFile(f'Min Evaluation for {piece} -> {initialMove} @ Depth {depth}', 'debug-minimax.txt')
                    new_board, _, _ = self.perform_all_move(piece, initialMove, self.oppTurn, board)
                    eval, _, _ = self.minimax(new_board, depth-1, True)
                    debugToFile(f'Evaluated child node @ Depth {depth} with value: {eval}', 'debug-minimax.txt')
                    if eval < minEval:
                        debugToFile(f'Updating bestPiece: {piece}, bestMove: {initialMove}', 'debug-minimax.txt')
                        minEval = min(minEval, eval)
                        bestPiece = piece
                        bestMove = initialMove

            return minEval, bestPiece, bestMove


class AlphaBeta(Minimax):
    def __init__(self, turn, board, movesDone):
        super().__init__(turn, board, movesDone)
        self.zobristtable = self.initTable()
        self.hashtable = {}

    def play(self, board):
        if self.mandatory_moves == []:
            mandatory_moves = self.get_mandatory_capture(self.botTurn, board)
            if len(mandatory_moves) == 1:
                piece, move = mandatory_moves[0], self.get_valid_moves(mandatory_moves[0][0], mandatory_moves[0][1], board)[0][0]
            else:
                _, piece, move = self.iterativeDeepening(board)
        else:
            if board[self.mandatory_moves[0][0]][self.mandatory_moves[0][1]].lower() == self.botTurn:
                piece = self.mandatory_moves[0]
                if len(self.get_valid_moves(piece[0], piece[1], board)[0]) == 1:
                    move = self.get_valid_moves(piece[0], piece[1], board)[0][0]
                else:
                    _, piece, move = self.iterativeDeepening(board)
            else:
                _, piece, move = self.iterativeDeepening(board)
        return piece, move

    def iterativeDeepening(self, board):
        lastDepth = 0
        lastVal = -np.inf
        lastPiece = None
        lastMove = None
        depth = 1
        self.timer = time.time()
        while True:
            if time.time() - self.timer > self.timeLimit: break
            value, piece, move = self.alphaBeta(board, depth, -np.inf, np.inf, True)
            lastDepth = depth
            lastVal = value
            lastPiece = piece
            lastMove = move
            if value >= 2000:
                break
            depth += 1
            # debugToFile(f'Next Depth: {depth}, Last Depth: {lastDepth}, Val: {lastVal}, Piece: {lastPiece}, Move: {lastMove}', 'depthExperiment.txt')
        debugToFile(f'Depth: {depth}, Last Depth: {lastDepth}, Val: {lastVal}, Piece: {lastPiece}, Move: {lastMove}', 'depthExperiment.txt')
        return lastVal, lastPiece, lastMove

    def alphaBeta(self, board, depth, alpha, beta, maximizing):
        bestPiece = None
        bestMove = None
        # movesdict = self.get_all_moves(self.botTurn, board)
        # debugToFile(f'Depth: {depth}, movesdict: {movesdict}', 'depthExperiment.txt')
        # debugToFile(f'Mandatory Moves: {self.mandatory_moves}', 'depthExperiment.txt')
        # debugToFile(f'Previous Move: {self.prevMove}', 'depthExperiment.txt')

        with open('debug-alphabeta.txt', 'a') as f:
            f.write(f'-'*20)
            f.write(f'\nBot Turn: {self.botTurn}\n')
            f.write(f'Depth: {depth}\n')
            f.write(f'Board:\n')
            for row in board:
                f.write(' '.join(row) + '\n')
            f.write(f'Evaluation: {self.evaluate_board(board)}, Alpha: {alpha}, Beta: {beta}\n')
            f.write(f'-'*20)

        if depth == 0 or is_game_over(board, self.movesDone, self.mandatory_moves) in ['w', 'b', 'draw'] or time.time() - self.timer >= self.timeLimit:
            return self.evaluate_board(board), None, None

        transposition = self.probeTransposition(board)
        if transposition is not None and transposition['depth'] >= depth:
            # Checking for saved depth higher or equal to current depth
            # because higher depth means more accurate evaluation
            if transposition['value'] > transposition['beta']:
                # Lower Bound, fails high, Alpha is the lower bound
                # Fail high means there exists a better move, meaning it's > beta
                # Updating alpha to ensure that we won't prune moves that are better
                alpha = max(alpha, transposition['value'])
            elif transposition['value'] < transposition['alpha']:
                # Upper Bound, fails low, Beta is the upper bound
                # Fail low means there exists no moves that can make it > alpha
                # Updating beta to ensure that we won't explore moves that are worse
                beta = min(beta, transposition['value'])
            else:
                # Exact Value
                return transposition['value'], transposition['piece'], transposition['move']
        
        if maximizing:
            maxEval = -np.inf
            bestPiece = None
            bestMove = None
            movesdict = self.get_all_moves(self.botTurn, board)
            for piece, movetolist in movesdict.items():
                if len(movesdict.keys()) == 1 and len(movetolist) == 1:
                    return self.evaluate_board(board), piece, movetolist[0]
                for initialMove in movetolist:
                    new_board, _, _ = self.perform_all_move(piece, initialMove, self.botTurn, board)
                    eval, _, _ = self.alphaBeta(new_board, depth-1, alpha, beta, False)
                    alpha = max(alpha, maxEval)
                    if eval > maxEval:
                        maxEval = max(maxEval, eval)
                        bestPiece = piece
                        bestMove = initialMove
                    if beta <= alpha:
                        break

            self.storeTransposition(board, depth, maxEval, bestPiece, bestMove, alpha, beta)
            return maxEval, bestPiece, bestMove
        
        else:
            minEval = np.inf
            bestPiece = None
            bestMove = None
            movesdict = self.get_all_moves(self.oppTurn, board)
            for piece, movetolist in movesdict.items():
                if len(movesdict.keys()) == 1 and len(movetolist) == 1:
                    return self.evaluate_board(board), piece, movetolist[0]
                for initialMove in movetolist:
                    new_board, _, _ = self.perform_all_move(piece, initialMove, self.oppTurn, board)
                    eval, _, _ = self.alphaBeta(new_board, depth-1, alpha, beta, True)
                    beta = min(beta, minEval)
                    if eval < minEval:
                        minEval = min(minEval, eval)
                        bestPiece = piece
                        bestMove = initialMove
                    if beta <= alpha:
                        break

            self.storeTransposition(board, depth, minEval, bestPiece, bestMove, alpha, beta)
            return minEval, bestPiece, bestMove
            
    def squareMapping(self, square):
        squareMapping = { 32: (0, 1),  31: (0, 3),  30: (0, 5),  29: (0, 7),
                          28: (1, 0),  27: (1, 2),  26: (1, 4),  25: (1, 6),
                          24: (2, 1), 23: (2, 3), 22: (2, 5), 21: (2, 7),
                         20: (3, 0), 19: (3, 2), 18: (3, 4), 17: (3, 6),
                         16: (4, 1), 15: (4, 3), 14: (4, 5), 13: (4, 7),
                         12: (5, 0), 11: (5, 2), 10: (5, 4), 9: (5, 6),
                         8: (6, 1), 7: (6, 3), 6: (6, 5), 5: (6, 7),
                         4: (7, 0), 3: (7, 2), 2: (7, 4), 1: (7, 6)}
        row = squareMapping[square][0]
        col = squareMapping[square][1]
        return row, col
    
    def get_square(self, row, col):
        squareMapping = {(0, 1): 32, (0, 3): 31, (0, 5): 30, (0, 7): 29,
                         (1, 0): 28, (1, 2): 27, (1, 4): 26, (1, 6): 25,
                         (2, 1): 24, (2, 3): 23, (2, 5): 22, (2, 7): 21,
                         (3, 0): 20, (3, 2): 19, (3, 4): 18, (3, 6): 17,
                         (4, 1): 16, (4, 3): 15, (4, 5): 14, (4, 7): 13,
                         (5, 0): 12, (5, 2): 11, (5, 4): 10, (5, 6): 9,
                         (6, 1): 8, (6, 3): 7, (6, 5): 6, (6, 7): 5,
                         (7, 0): 4, (7, 2): 3, (7, 4): 2, (7, 6): 1}
        return squareMapping[(row, col)]

    #Zobrist Hashing

    # How it works
    # 1. Create a table of random numbers for each piece in each square
    # 2. XOR the random number of the piece in the square
    # 3. When a move is made, XOR the random number of the piece in the square

    def randInt(self):
        return random.getrandbits(64)

    def pieceIndices(self, piece):
        if piece == 'b':
            return 0
        elif piece == 'w':
            return 1
        elif piece == 'B':
            return 2
        elif piece == 'W':
            return 3
        else:
            return -1

    def initTable(self):
        table = [[self.randInt() for _ in range(4)] for _ in range(32)]
        return table
    
    def hashBoard(self, board, zobristtable):
        hash = 0
        for row in range(rows):
            for col in range(cols):
                piece = board[row][col]
                if piece != '-':
                    squareIDX = self.get_square(row, col) - 1 # -1 because the square starts from 1
                    pieceIndex = self.pieceIndices(piece)
                    hash ^= zobristtable[squareIDX][pieceIndex]
        return hash
    
    def storeTransposition(self, board, depth, value, piece, move, alpha, beta):
        hash = self.hashBoard(board, self.zobristtable)
        self.hashtable[hash] = {'depth': depth, 'value': value, 'piece': piece, 'move': move, 'alpha': alpha,'beta': beta}

    def probeTransposition(self, board):
        hash = self.hashBoard(board, self.zobristtable)
        if hash in self.hashtable:
            return self.hashtable[hash]
        return None

class randomBot(Player):
    def __init__(self, turn, board):
        super().__init__(turn, board)
        self.user = False

    def shuffle_dict(self, dict):
        keys = list(dict.keys())
        np.random.shuffle(keys)
        return {key: dict[key] for key in keys}

    def play(self, board):
        movesdict = self.shuffle_dict(self.get_all_moves(self.turn, board))
        piece = list(movesdict.keys())[0]
        moveto = random.choice(movesdict[piece])
        return piece, moveto

def countBlack(board):
    count = 0
    for row in range(rows):
        for col in range(cols):
            if board[row][col].lower() == 'b':
                count += 1
    return count

def countWhite(board):
    count = 0
    for row in range(rows):
        for col in range(cols):
            if board[row][col].lower() == 'w':
                count += 1
    return count

def countKings(board):
    whiteKings = 0
    blackKings = 0
    for row in range(rows):
        for col in range(cols):
            if board[row][col] == 'B':
                blackKings += 1
            elif board[row][col] == 'W':
                whiteKings += 1
    return whiteKings, blackKings

def is_game_over(board, movesDone, mandatory_moves):
    currentTurn = 'b' if movesDone['turn'] == 'w' else 'w'

    tempb = []
    tempbmove = []
    tempbcap = []

    tempw = []
    tempwmove = []
    tempwcap = []

    blackCount = countBlack(board)
    whiteCount = countWhite(board)
    whiteKing, blackKing = countKings(board)

    blackMoveCount = len(movesDone['b'])
    whiteMoveCount = len(movesDone['w'])
    totalMoveCount = len(movesDone['b']) + len(movesDone['w'])

    xb = np.char.lower(np.array(board)) == 'b'
    pieceloclist = np.asarray(np.where(xb)).T.tolist()
    for pieceloc in pieceloclist:
        tempbmove.append(check_basic_valid_moves(pieceloc[0], pieceloc[1], board))
        tempbcap.append(check_basic_capture(pieceloc[0], pieceloc[1], board))
    for normMove, capMove in zip_longest(tempbmove, tempbcap):
        tempb.append(normMove or capMove)

    xw = np.char.lower(np.array(board)) == 'w'
    pieceloclist = np.asarray(np.where(xw)).T.tolist()
    for pieceloc in pieceloclist:
        tempwmove.append(check_basic_valid_moves(pieceloc[0], pieceloc[1], board))
        tempwcap.append(check_basic_capture(pieceloc[0], pieceloc[1], board))
    for normMove, capMove in zip_longest(tempwmove, tempwcap):
        tempw.append(normMove or capMove)

    if mandatory_moves:
        if board[mandatory_moves[0][0]][mandatory_moves[0][1]].lower() == movesDone['turn']:
            return False
    else:
        if currentTurn == 'w' and all(not i for i in tempb):
            if all(not i for i in tempwcap):
                return 'w'
        elif currentTurn == 'b' and all(not i for i in tempw):
            if all(not i for i in tempbcap):
                return 'b'

    if (blackCount == 1 and blackKing == 1) and\
       (whiteCount == 1 and whiteKing == 1) and\
       all(not i for i in tempbcap) and\
       all(not i for i in tempwcap):
        # with only 1 king each w/o any forced captures, the game should be considered a draw
        return 'draw'
    
    if blackMoveCount == 40 or whiteMoveCount == 40:
        # In the internaitonal rules, if a player makes 40 moves without a capture or a king, the game is a draw
        if blackCount + whiteCount == 24:
            return 'draw'
        if whiteKing + blackKing == 0:
            return 'draw'

    if totalMoveCount >= 12:
        # If the last 3 moves are the same, the game is a draw
        if movesDone['b'][-1] == movesDone['b'][-3] == movesDone['b'][-5] and\
           movesDone['w'][-1] == movesDone['w'][-3] == movesDone['w'][-5] and\
           movesDone['b'][-2] == movesDone['b'][-4] == movesDone['b'][-6] and\
           movesDone['w'][-2] == movesDone['w'][-4] == movesDone['w'][-6]:
            return 'draw'

    return False

def check_basic_valid_moves(row, col, board):
    if board[row][col].lower() == 'b' or board[row][col] == 'W':
        if 0 <= row+1 <= 7 and 0 <= col-1 <= 7 and board[row+1][col-1] == '-':
            return True
        if 0 <= row+1 <= 7 and 0 <= col+1 <= 7 and board[row+1][col+1] == '-':
            return True
    if board[row][col].lower() == 'w' or board[row][col] == 'B':
        if 0 <= row-1 <= 7 and 0 <= col-1 <= 7 and board[row-1][col-1] == '-':
            return True
        if 0 <= row-1 <= 7 and 0 <= col+1 <= 7 and board[row-1][col+1] == '-':
            return True
    return False

def check_basic_capture(row, col, board):
    if board[row][col] == 'b':
        if 0 <= row+2 <= 7 and 0 <= col-2 <= 7 and board[row+1][col-1].lower() == 'w' and board[row+2][col-2] == '-':
            return True
        if 0 <= row+2 <= 7 and 0 <= col+2 <= 7 and board[row+1][col+1].lower() == 'w' and board[row+2][col+2] == '-':
            return True
    if board[row][col] == 'w':
        if 0 <= row-2 <= 7 and 0 <= col-2 <= 7 and board[row-1][col-1].lower() == 'b' and board[row-2][col-2] == '-':
            return True
        if 0 <= row-2 <= 7 and 0 <= col+2 <= 7 and board[row-1][col+1].lower() == 'b' and board[row-2][col+2] == '-':
            return True
    if board[row][col] == 'B' or board[row][col] == 'W':
        directions = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
        for direction in directions:
            for i in range(1, 8):
                checkrow = row + direction[0] * i
                checkcol = col + direction[1] * i
                if 0 <= checkrow <= 7 and 0 <= checkcol <= 7:
                    if board[checkrow][checkcol] == '-':
                        continue
                    elif board[checkrow][checkcol].lower() != board[row][col].lower():
                        if 0 <= checkrow+direction[0] <= 7 and 0 <= checkcol+direction[1] <= 7 and board[checkrow+direction[0]][checkcol+direction[1]] == '-':
                            return True
                    else:
                        break
                else:
                    break
    return False

def debugToFile(msg, file):
    with open(file, 'a') as f:
        f.write(msg + '\n')