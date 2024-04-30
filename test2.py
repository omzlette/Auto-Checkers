import random

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

testObj = test()
testObj.testPassin(testObj.testVariable)
