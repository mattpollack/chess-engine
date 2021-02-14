
"""

Prefixes
K = king
Q = queen
R = rook
B = bishop
N = knight
Pawn has none

prefix + x if capturing + position

if there are overlapping moves
1) file of departure
2) rank of departure
3) both file and rank of departure

when a pawn promotes, the new piece type is at the end e8Q

kindside castling = O-O
queenside castling = O-O-O

game notation
1. white move, black move
2. ...

"""

class Position(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(a, b):
        return isinstance(b, Position) and a.x == b.x and a.y == b.y
    
    def __str__(self):
        return f'{chr(ord("a") + self.y)}{self.x + 1}'
    
    def __hash__(self):
        return hash((self.x, self.y))

    def add(a, b):
        return Position(a.x + b.x, a.y + b.y)
    
    def sub(a, b):
        return Position(a.x - b.x, a.y - b.y)

class Piece(object):
    def __init__(self, prefix, color):
        self.prefix = prefix
        self.color = color

    # NOTE: maybe consider some sort of exception handling here, not really sure what's idiomatic python
    def canMove(self, start, end, board):
        return False

class Pawn(Piece):
    def __init__(self, color):
        super().__init__(" ", color)

        displacement = None

        if self.color == "w":
            displacement = Position(0, 1)
        
        if self.color == "b":
            displacement = Position(0, -1)
        
        # Precompute allowed moves before checking the board
        self.allowedMoves = [
            Position(-1, 0).add(displacement),
            Position(0, 0).add(displacement),
            Position(1, 0).add(displacement),
        ]

    def canMove(self, start, end, board):
        startPiece = board.getPiece(start)

        if startPiece == None:
            return False
        
        relative = end.sub(start)

        if not relative in self.allowedMoves:
            return False

        otherPiece = board.getPiece(end)

        if relative.x == 0:
            return otherPiece == None
        
        return otherPiece != None and otherPiece.color != self.color

class Knight(Piece):
    def __init__(self, color):
        super().__init__("n", color)

        # Precompute allowed moves before checking the board
        self.allowedMoves = [
            Position(-1, 2),
            Position(1, 2),
            Position(2, 1),
            Position(2, -1),
            Position(1, -2),
            Position(-1, -2),
            Position(-2, -1),
            Position(-2, 1),
        ]

    def canMove(self, start, end, board):
        startPiece = board.getPiece(start)

        if startPiece == None:
            return False
        
        relative = end.sub(start)

        if not relative in self.allowedMoves:
            return False
        
        otherPiece = board.getPiece(end)

        return otherPiece == None or (otherPiece != None and otherPiece.color != self.color)

class Bishop(Piece):
    def __init__(self, color):
        super().__init__("b", color)

    def canMove(self, start, end, board):
        startPiece = board.getPiece(start)

        if startPiece == None:
            return False
        
        relative = end.sub(start)

        if abs(relative.y/relative.x) != 1:
            return False

        xSign = relative.x/abs(relative.x)
        ySign = relative.y/abs(relative.y)
        distance = abs(relative.x)-1

        for i in range(1, distance):
            x = i*xSign
            y = i*ySign

            if board.getPiece(start.add(Position(x, y))) != None:
                return False

        otherPiece = board.getPiece(end)

        return otherPiece == None or (otherPiece != None and otherPiece.color != self.color)

class Rook(Piece):
    def __init__(self, color):
        super().__init__("r", color)

    def canMove(self, start, end, board):
        startPiece = board.getPiece(start)

        if startPiece == None:
            return False
        
        relative = end.sub(start)

        if relative.x != 0 and relative.y != 0:
            return False

        xSign = 0
        ySign = 0
        if abs(relative.x) > 0:
            xSign = relative.x/abs(relative.x)
        if abs(relative.y) > 0:
            ySign = relative.y/abs(relative.y)
        
        distance = abs(relative.x) + abs(relative.y) - 1

        for i in range(1, distance):
            x = i*xSign
            y = i*ySign

            if board.getPiece(start.add(Position(x, y))) != None:
                return False

        otherPiece = board.getPiece(end)

        return otherPiece == None or (otherPiece != None and otherPiece.color != self.color)

class Queen(Piece):
    def __init__(self, color):
        super().__init__("q", color)

    def canMove(self, start, end, board):
        return Rook(self.color).canMove(start, end, board) or Bishop(self.color).canMove(start, end, board)

class King(Piece):
    def __init__(self, color):
        super().__init__("k", color)

    def canMove(self, start, end, board):
        startPiece = board.getPiece(start)

        if startPiece == None:
            return False
        
        relative = end.sub(start)

        if abs(relative.x) > 1 or abs(relative.y) > 1:
            return False
        
        otherPiece = board.getPiece(end)

        return otherPiece == None or (otherPiece != None and otherPiece.color != self.color)

    def inCheck(self, kingPos, board):
        for pair in board.getPieces():
            piece = pair[0]
            pos = pair[1]

            if piece.color != self.color and piece.canMove(pos, kingPos, board):
                return True
        
        return False

class Board:
    def __init__(self):
        self.__grid = {}

    def __str__(self):
        res = ""

        for y in range(7, -1, -1):
            for x in range(0, 8, 1):
                piece = self.getPiece(Position(x, y))
                
                if piece == None:
                    res += "  "
                else:
                    res += f'{piece.color}{piece.prefix}'

                if y < 7:
                    res += ""

            res += "\n"

        return res + "<><><><><><><><>"
    
    def getPiece(self, position):
        try:
            return self.__grid[position]
        except KeyError:
            return None
    
    def getPieces(self):
        pieces = []

        for pos in self.__grid.keys():
            piece = self.__grid[pos]
            pieces.append((self.__grid[pos], pos))

        return pieces

    def removePiece(self, position):
        del self.__grid[position]
    
    def placePiece(self, piece, position):
        previousPiece = None

        try:
            previousPiece = self.__grid[position]
        except KeyError:
            previouspiece = None

        self.__grid[position] = piece

        return previousPiece

    def inBounds(self, position):
        return position.x >= 0 and position.x < 8 and position.y >= 0 and position.y < 8

    def movePiece(self, start, end):
        if not self.inBounds(start) or not self.inBounds(end) or start == end:
            return None

        piece = self.getPiece(start)

        if piece == None:
            return None

        if not piece.canMove(start, end, self):
            return None

        self.removePiece(start)
        return self.placePiece(piece, end)
    
    def playersInCheck(self):
        colors = {}

        for pos in self.__grid.keys():
            piece = self.__grid[pos]

            if isinstance(piece, King):
                if piece.inCheck(pos, self):
                    colors[piece.color] = True
        
        return colors.keys()
        



# TEST CONFIGURATION
board = Board()
board.placePiece(Pawn("b"), Position(0, 2))
board.placePiece(Pawn("w"), Position(1, 1))
board.placePiece(Knight("b"), Position(1, 4))
board.placePiece(Bishop("w"), Position(3, 5))
board.placePiece(Rook("b"), Position(0, 5))
board.placePiece(Queen("b"), Position(5, 2))
board.placePiece(Queen("w"), Position(2, 0))
board.placePiece(King("w"), Position(6, 6))

print(board)
print(board.playersInCheck())

board.movePiece(Position(1, 1), Position(0, 2))
print(board)
print(board.playersInCheck())

board.movePiece(Position(1, 4), Position(0, 2))
print(board)
print(board.playersInCheck())

board.movePiece(Position(3, 5), Position(0, 2))
print(board)
print(board.playersInCheck())

board.movePiece(Position(0, 5), Position(0, 2))
print(board)
print(board.playersInCheck())

board.movePiece(Position(2, 0), Position(0, 2))
print(board)
print(board.playersInCheck())

board.movePiece(Position(5, 2), Position(0, 2))
print(board)
print(board.playersInCheck())

board.movePiece(Position(0, 2), Position(0, 6))
print(board)
print(board.playersInCheck())

board.placePiece(Pawn("w"), Position(3, 6))
print(board)
print(board.playersInCheck())