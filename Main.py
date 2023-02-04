from selenium.webdriver.common.by import By
from selenium_chrome import Chrome
from stockfish import Stockfish
import keyboard
import operator

enginepath = "/Users/darre/Documents/Engines/Stockfish15"
suggestions = 3


class Piece:
    def get_type(self):
        return self.name

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name

def get_fen(pieces):
    # create piece objects for each piece and add them to a new array
    pieceObjects = []
    if len(pieces) != 0:
        for i in range(len(pieces)):
            #print(pieces[i].get_attribute("class"))

            className = pieces[i].get_attribute("class")

            # detect fucked up pieces
            datax = 16
            datay = 17
            datapiece = 7
            datacol = 6

            if "piece square" in className:
                #fucked up piece
                # piece square-61 wk
                datax = 13
                datay = 14
                datapiece = 17
                datacol = 16

            finalPieceName = className[datapiece]

            if className[datacol] == "w":
                finalPieceName = finalPieceName.upper()

            p = Piece(int(className[datax]), int(className[datay]), finalPieceName)

            pieceObjects.append(p)

    # now we have a giant pool of pieces which are completely unsorted
    # the pool is malleable, however, so we can now begin sorting everything

    # for each column
    final = ""
    for y in range(7, -1, -1):
        # generate a row of all pieces with correct y value
        row = [pieceObj for pieceObj in pieceObjects if pieceObj.y == y + 1]

        # put all the pieces in the row in order
        row = sorted(row, key=operator.attrgetter('x'))

        # fill in all blank spaces

        fullrow = ""
        if len(row) == 0:
            fullrow = "8/"
        else:
            for x in range(len(row)):
                actualX = row[x].get_x()
                if x == 0:
                    # if first item in list
                    if actualX > 1:
                        fullrow = fullrow + str(actualX - 1)

                if len(row) > 1 or x != 0:
                    # fuck you
                    # check to the left of the item

                    # get actual x of previous element
                    actualXpre = row[x - 1].get_x()

                    # subtract rightmost x from left element to get distance between
                    # reverse that
                    dst = actualX - actualXpre

                    # if the item is more than one square apart insert white space
                    if dst > 1:
                        fullrow = fullrow + str(dst - 1)


                fullrow = fullrow + row[x].get_type()

                if x == len(row) - 1:
                    # if final item in row
                    if 8 - actualX != 0:
                        fullrow = fullrow + str(8 - actualX)


            fullrow = fullrow + "/"

        final = final + fullrow

    #print(final)

    final = final[:-1]
    return final


def getCol(chrome):
    clock = chrome.find(By.CLASS_NAME, "clock-component")
    clockData = clock.get_attribute("class")


    if "clock-bottom" in clockData:
        if "clock-white" in clockData:
            return "w"
        else:
            return "b"
    else:
        if "clock-white" in clockData:
            return "b"
        else:
            return "w"

def checkTurn(chrome):
    clock = chrome.find(By.CLASS_NAME, "clock-bottom")
    clockData = clock.get_attribute("class")
    return "player-turn" in clockData

def main():
    chrome = Chrome()
    chrome.get('https://www.chess.com/play/online')
    #print(dir(chrome))

    stockfish = Stockfish(enginepath)

    while 1:
        try:
            # get a list of all pieces
            pieces = chrome.find_all(By.CLASS_NAME, "piece")

            # true - white, false - black
            color = getCol(chrome)

            fen = ""
            if len(pieces) > 0:
                fen = get_fen(pieces)

            # print(f"querying with {fen} {color}")

            if keyboard.is_pressed('q'):
                if checkTurn(chrome):
                    stockfish.set_fen_position(f"{fen} {color}")
                    # print(stockfish.get_top_moves(suggestions))
                    moves = stockfish.get_top_moves(suggestions)
                    print()
                    for i in range(len(moves)):
                        print(moves[i])

                else:
                    print("It is not your turn")

        except Exception as e:
            if e == "The Stockfish process has crashed":
                print(e)
                stockfish = Stockfish(enginepath)

if __name__ == '__main__':
    main()
