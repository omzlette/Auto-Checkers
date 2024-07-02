import pygame
from pygame.locals import *
from checkers import *
from player import *
import serial
import time

ACK = 0x50;
CMPLT = 0x51;
NACK = 0x60;

def initialize():
    board = Checkers()
    player1 = User('b', board.board, board.movesDone)
    player2 = AlphaBeta('w', board.board, board.movesDone)
    return player1, player2, board

def main():
    connectedMCU = False
    startFlag = False

    while True:
        if not connectedMCU:
            try:
                ser = serial.Serial('/dev/ttyUSB0', 115200)
                ser.flushInput()
                ser.flushOutput()
                ser.write(0xF0)
                # receive 'ACK' from MCU
                if ser.read(1) == ACK:
                    connectedMCU = True
            except:
                print('Waiting for MCU...')
                time.sleep(1)
                continue

        else:
            if not startFlag:
                if ser.read(1) == 0x99:
                    startFlag = True
                    numGames += 1
                    player1, player2, board = initialize()
                    isGameOver = False
                    running = True
                    continue
            
            else:
                while running:
                    if ser.read(1) == 0x97 or ser.read(1) == 0x98:
                        # reset or stop
                        running = False
                        startFlag = False
                        break
                    

                    # do game logic
            
