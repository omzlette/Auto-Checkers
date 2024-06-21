from checkers import *
from player import *
# from autoExperiment import *
import copy
import serial

def initGame(numGames):
    board = Checkers()
    if numGames % 2 == 0:
        player1 = User('b', board.board, board.movesDone)
        player2 = AlphaBeta('w', board.board, board.movesDone)
    else:
        player1 = AlphaBeta('b', board.board, board.movesDone)
        player2 = User('w', board.board, board.movesDone)

    return player1, player2, board

def main():
                   
    numGames = 0
    
    experiment = serial.Serial('/dev/ttyGS0',
                                 baudrate=115200,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 bytesize=serial.EIGHTBITS,
                                 timeout=1)

    experiment.reset_input_buffer()
    experiment.reset_output_buffer()
    while numGames < 100:
        player1, player2, board = initGame(numGames)
        isGameOver = False
        running = True
        nummoves = 0
        with open('/home/estel/Auto-Checkers/debug.txt', 'w') as f:
            f.write('')
        while running:
            isGameOver = is_game_over(board.board, board.turn, board.movesDone)

            if not isGameOver:
                if board.turn == 'b':
                    if player1.user:
                        time.sleep(1)
                        if experiment.in_waiting > 0:
                            RxBuffer = experiment.readline().decode('utf-8').strip()
                            if RxBuffer and 'm' in RxBuffer:
                                RxBuffer = RxBuffer.replace('m', '')
                                BSelected, BMove = RxBuffer.split(',')
                                BSelected = tuple(map(int, BSelected.split(';')))
                                BMove = tuple(map(int, BMove.split(';')))
                                # time.sleep(0.5)
                                
                                player1.prevCount = countBlack(board.board) + countWhite(board.board)
                                board.board, board.turn = player1.update_board(board.board, BSelected, BMove)
                                with open('/home/estel/Auto-Checkers/debug.txt', 'a') as f:
                                    f.write(f'Rx: {BSelected};; {BMove};; {board.turn}\n')
                                    for row in board.board:
                                        f.write(f'{row}\n')
                                experiment.write(f'{board.turn}ACK\n'.encode('utf-8'))

                                player1.turn = board.turn
                                player2.turn = board.turn

                    else:
                        BSelected, BMove = player1.play(board.board)
                        if BSelected is not None and BMove is not None:
                            player1.prevCount = countBlack(board.board) + countWhite(board.board)
                            board.board, board.turn = player1.update_board(board.board, BSelected, BMove)

                            TxBuffer = f'm{BSelected[0]};{BSelected[1]},{BMove[0]};{BMove[1]},{board.turn}\n'
                            experiment.write(TxBuffer.encode('utf-8'))
                            with open('/home/estel/Auto-Checkers/debug.txt', 'a') as f:
                                    f.write(f'Tx: {BSelected};; {BMove};; {board.turn}\n')
                            time.sleep(0.5)

                            player1.turn = board.turn
                            player2.turn = board.turn
                    
                elif board.turn == 'w':
                    if player2.user:
                        time.sleep(0.5)
                        if experiment.in_waiting > 0:
                            RxBuffer = experiment.readline().decode('utf-8').strip()
                            if RxBuffer and 'm' in RxBuffer:
                                RxBuffer = RxBuffer.replace('m', '')
                                WSelected, WMove = RxBuffer.split(',')
                                WSelected = tuple(map(int, WSelected.split(';')))
                                WMove = tuple(map(int, WMove.split(';')))
                                # time.sleep(0.5)

                                player2.prevCount = countBlack(board.board) + countWhite(board.board)
                                board.board, board.turn = player2.update_board(board.board, WSelected, WMove)
                                experiment.write(f'{board.turn}ACK\n'.encode('utf-8'))

                                player1.turn = board.turn
                                player2.turn = board.turn

                    else:
                        WSelected, WMove = player2.play(board.board)
                        if WSelected is not None and WMove is not None:
                            player2.prevCount = countBlack(board.board) + countWhite(board.board)
                            board.board, board.turn = player2.update_board(board.board, WSelected, WMove)

                            TxBuffer = f'm{WSelected[0]};{WSelected[1]},{WMove[0]};{WMove[1]},{board.turn}\n'
                            experiment.write(TxBuffer.encode('utf-8'))
                            with open('/home/estel/Auto-Checkers/debug.txt', 'a') as f:
                                    f.write(f'Tx: {WSelected};; {WMove};; {board.turn}\n')
                            time.sleep(0.5)

                            # response = experiment.readline().decode('utf-8').strip()
                            # if response == 'ACK':
                            #     del response
                            player1.turn = board.turn
                            player2.turn = board.turn

                if board.board != board.prevBoard:
                    nummoves += 1
                    board.prevBoard = copy.deepcopy(board.board)
                    
                    if board.turn == 'w':
                        board.updateMovesDict(tuple(BSelected), tuple(BMove), 'b')
                    else:
                        board.updateMovesDict(tuple(WSelected), tuple(WMove), 'w')
                    
                    with open('/home/estel/Auto-Checkers/debug-board.txt', 'w') as f:
                        for row in board.prevBoard:
                            f.write(f'{row}\n')
                    with open('/home/estel/Auto-Checkers/debug.txt', 'a') as f:
                        f.write(f'No. moves: {nummoves}, Moves Done: {board.movesDone}\n')

                if experiment.in_waiting > 0:
                    RxBuffer = experiment.readline().decode('utf-8').strip()
                    if 'next' in RxBuffer:
                        running = False
                        numGames += 1
                        with open('/home/estel/Auto-Checkers/results.txt', 'a') as f:
                            f.write(f'Game {numGames}: {isGameOver}, No. moves: {nummoves}\n')
                            f.write(f'Moves Done: {board.movesDone}\n\n')

            else:
                if experiment.in_waiting > 0:
                    RxBuffer = experiment.readline().decode('utf-8').strip()
                    if 'next' in RxBuffer:
                        running = False
                        numGames += 1
                        with open('/home/estel/Auto-Checkers/results.txt', 'a') as f:
                            f.write(f'Game {numGames}: {isGameOver}, No. moves: {nummoves}\n')
                            f.write(f'Moves Done: {board.movesDone}\n\n')
                        del board, player1, player2
                        

if __name__ == '__main__':
    main()