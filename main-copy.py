from checkersDupe import *
from playerDupe import *
# from autoExperiment import *
import copy
import serial

def initGame():
    board = Checkers()
    player1 = User('b', board.board, board.movesDone)
    player2 = AlphaBeta('w', board.board, board.movesDone)

    return player1, player2, board

def main():    
    experiment = serial.Serial('/dev/ttyGS0',
                                 baudrate=115200,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 bytesize=serial.EIGHTBITS,
                                 timeout = None)

    experiment.reset_input_buffer()
    experiment.reset_output_buffer()
    numGames = 0
    while numGames < 20:
        player1, player2, board = initGame()
        isGameOver = False
        running = True
        nummoves = 0
        with open('/home/estel/Auto-Checkers/debug.txt', 'w') as f:
            f.write('')
        while running:
            if board.turn == player1.ourTurn:
                isGameOver = is_game_over(board.board, board.movesDone, player1.mandatory_moves)
            elif board.turn == player2.botTurn:
                isGameOver = is_game_over(board.board, board.movesDone, player2.mandatory_moves)

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
                                board.board, board.turn, _ = player1.update_board(board.board, BSelected, BMove)
                                with open('/home/estel/Auto-Checkers/debug.txt', 'a') as f:
                                    f.write(f'Rx: {BSelected};; {BMove};; {board.turn}\n')
                                    for row in board.board:
                                        f.write(f'{row}\n')
                                experiment.write(f'{board.turn}ACK\n'.encode('utf-8'))

                                player1.turn = board.turn
                                player2.turn = board.turn
                            elif 'next' in RxBuffer:
                                result = RxBuffer.replace('next', '')
                                running = False
                                numGames += 1
                                with open('/home/estel/Auto-Checkers/results.txt', 'a') as f:
                                    f.write(f'{numGames},{nummoves},{board.movesDone},{result}\n')
                                del board, player1, player2, RxBuffer
                                break
                    
                elif board.turn == 'w':
                    if experiment.in_waiting > 0:
                        RxBuffer = experiment.readline().decode('utf-8').strip()
                        if 'next' in RxBuffer:
                            result = RxBuffer.replace('next', '')
                            running = False
                            numGames += 1
                            with open('/home/estel/Auto-Checkers/results.txt', 'a') as f:
                                f.write(f'{numGames},{nummoves},{board.movesDone},{result}\n')
                            del board, player1, player2, RxBuffer
                            break
                    WSelected, WMove = player2.play(board.board)
                    if WSelected is not None and WMove is not None:
                        player2.prevCount = countBlack(board.board) + countWhite(board.board)
                        board.board, board.turn, _ = player2.update_board(board.board, WSelected, WMove)

                        TxBuffer = f'm{WSelected[0]};{WSelected[1]},{WMove[0]};{WMove[1]},{board.turn}\n'
                        experiment.write(TxBuffer.encode('utf-8'))
                        with open('/home/estel/Auto-Checkers/debug.txt', 'a') as f:
                            f.write(f'Tx: {WSelected};; {WMove};; {board.turn}\n')
                            for row in board.board:
                                f.write(f'{row}\n')
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

            else:
                if experiment.in_waiting > 0:
                    RxBuffer = experiment.readline().decode('utf-8').strip()
                    if 'next' in RxBuffer:
                        running = False
                        numGames += 1
                        with open('/home/estel/Auto-Checkers/results.txt', 'a') as f:
                            f.write(f'{numGames},{nummoves},{board.movesDone},{isGameOver}\n')
                        del board, player1, player2, RxBuffer
                        break
                        

if __name__ == '__main__':
    main()