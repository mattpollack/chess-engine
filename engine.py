
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

import random

class GameActionException(Exception):
    def __init__(self, message):
        super().__init__(message)

class IllegalMove(GameActionException):
    def __init__(self, message):
        super().__init__(message)

class Concede(GameActionException):
    def __init__(self):
        super().__init__("Concede")

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
        self.hasMoved = False

    def canMove(self, start, end, board):
        raise Exception("Attempt to canMove Piece base class (not implemented)")
    
    def copy(self):
        raise Exception("Attempt to copy Piece base class (not implemented)")

    def setMoved(self):
        self.hasMoved = True

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
            # Moving forward is the first allow move (for first pawn move)
            Position(0, 0).add(displacement),
            Position(-1, 0).add(displacement),
            Position(1, 0).add(displacement),
        ]

    def canMove(self, start, end, board):
        startPiece = board.getPiece(start)

        if startPiece == None:
            return False
        
        relative = end.sub(start)
        allowedMoves = self.allowedMoves

        if not self.hasMoved:
            allowedMoves.append(Position(0, self.allowedMoves[0].y*2)) 

        if not relative in self.allowedMoves:
            return False

        otherPiece = board.getPiece(end)

        if relative.x == 0:
            return otherPiece == None
        
        return otherPiece != None and otherPiece.color != self.color
    
    def copy(self):
        return Pawn(self.color)

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
    
    def copy(self):
        return Knight(self.color)

class Bishop(Piece):
    def __init__(self, color):
        super().__init__("b", color)

    def canMove(self, start, end, board):
        startPiece = board.getPiece(start)

        if startPiece == None:
            return False
        
        relative = end.sub(start)

        if relative.y == 0 or relative.x == 0 or abs(relative.y/relative.x) != 1:
            return False

        xSign = relative.x/abs(relative.x)
        ySign = relative.y/abs(relative.y)
        distance = abs(relative.x)

        for i in range(1, distance):
            x = i*xSign
            y = i*ySign

            if board.getPiece(start.add(Position(x, y))) != None:
                return False

        otherPiece = board.getPiece(end)

        return otherPiece == None or (otherPiece != None and otherPiece.color != self.color)

    def copy(self):
        return Bishop(self.color)

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
        
        distance = abs(relative.x) + abs(relative.y)

        for i in range(1, distance):
            x = i*xSign
            y = i*ySign

            if board.getPiece(start.add(Position(x, y))) != None:
                return False

        otherPiece = board.getPiece(end)

        return otherPiece == None or (otherPiece != None and otherPiece.color != self.color)

    def copy(self):
        return Rook(self.color)

class Queen(Piece):
    def __init__(self, color):
        super().__init__("q", color)

    def canMove(self, start, end, board):
        return Rook(self.color).canMove(start, end, board) or Bishop(self.color).canMove(start, end, board)

    def copy(self):
        return Queen(self.color)

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

    def copy(self):
        return King(self.color)

class Board:
    def __init__(self):
        self.__grid = {}

    def __str__(self):
        res = "   0 1 2 3 4 5 6 7\n"

        for y in range(7, -1, -1):
            res += f'{y} '

            for x in range(0, 8, 1):
                piece = self.getPiece(Position(x, y))

                if piece == None:
                    res += "  "
                else:
                    color = " "
                    prefix = piece.prefix

                    if piece.color == "b":
                        color = "_"
                    
                    if piece.prefix == " ":
                        prefix = "p"
                
                    res += f'{color}{prefix}'

                if y < 7:
                    res += ""

            res += f' {y}\n'

        return res + "   0 1 2 3 4 5 6 7"
    
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
            raise IllegalMove((start, end))

        piece = self.getPiece(start)

        if piece == None:
            raise IllegalMove((start, end))

        if not piece.canMove(start, end, self):
            raise IllegalMove((start, end))

        self.removePiece(start)
        otherPiece = self.placePiece(piece, end)

        # Revert the move it would cause a check, could be more efficient of a check?
        if piece.color in self.playersInCheck():
            self.placePiece(piece, start)

            if otherPiece != None:
                self.placePiece(otherPiece, end)
            else:
                self.removePiece(end)

            raise IllegalMove((start, end))

        piece.setMoved()

        return otherPiece
    
    def playersInCheck(self):
        colors = {}

        for pos in self.__grid.keys():
            piece = self.__grid[pos]

            if isinstance(piece, King):
                if piece.inCheck(pos, self):
                    colors[piece.color] = True
        
        return colors.keys()
    
    # NOTE: brute force option, could be a better method for this
    def playerInCheckmate(self, color):
        for pos in self.__grid.keys():
            piece = self.__grid[pos]

            if piece.color != color:
                continue

            for x in range(8):
                for y in range(8):
                    if piece.canMove(pos, Position(x, y), self):
                        return False

        return True
    
    def copy(self):
        new = Board()

        for pos in self.__grid:
            new.placePiece(self.__grid[pos].copy(), pos)
        
        return new

class StandardGame(object):
    def __init__(self, playerA, playerB):
        self.board = Board()
        self.moveNum = 0
        self.winner = None

        # Place all pieces for each team
        for x in range(8):
           self.board.placePiece(Pawn("w"), Position(x, 1))
           self.board.placePiece(Pawn("b"), Position(x, 6))
        
        for pair in [("w", 0), ("b", 7)]:
            color = pair[0]
            y = pair[1]

            self.board.placePiece(Rook(color), Position(0, y))
            self.board.placePiece(Rook(color), Position(7, y))
            self.board.placePiece(Knight(color), Position(1, y))
            self.board.placePiece(Knight(color), Position(6, y))
            self.board.placePiece(Bishop(color), Position(2, y))
            self.board.placePiece(Bishop(color), Position(5, y))
            self.board.placePiece(Queen(color), Position(3, y))
            self.board.placePiece(King(color), Position(4, y))
        
        # Choose the first player
        coin = random.randrange(0, 2)

        if coin == 1:
            self.white = playerA
            self.black = playerB
        else:
            self.white = playerB
            self.black = playerA

    def playerLoses(self, color):
        if color == "w":
            self.winner = "b"
        else:
            self.winner = "w"

    def turn(self):
        if not self.winner == None:
            return self.winner

        player = None
        color = None

        if self.moveNum % 2 == 0:
            player = self.white
            color = "w"
        else:
            player = self.black
            color = "b"

        self.moveNum += 1

        move = None

        # Players which don't catch errors lose
        try:
            move = player.Do(self.board.copy(), color)
            start = move[0]
            end = move[1]
            piece = self.board.getPiece(start)

            if piece != None and piece.color != color:
                raise IllegalMove((start, end))

            self.board.movePiece(start, end)
        except GameActionException:
            return self.playerLoses(color)

        # Check for checkmate
        if self.board.playerInCheckmate(color):
            return self.playerLoses(color)

        # Perform all state based checks
        pieces = self.board.getPieces()
        justKings = True

        for pair in pieces:
            piece = pair[0]
            pos = pair[1]

            # Check that there aren't just two kings
            if not isinstance(piece, King):
                justKings = False

            # Check for any pawn promotions
            if isinstance(piece, Pawn) and ((piece.color == "w" and pos.y == 7) or (piece.color == "b" and pos.y == 0)):
                try:
                    promoted = player.Promote(self.board.copy(), piece, pos)

                    if not isinstance(promoted, Piece) or isinstance(promoted, Pawn):
                        raise IllegalMove

                    self.board.placePiece(promoted, pos)

                except Exception:
                    return self.playerLoses(color)

        if justKings:
            self.winner = "draw"

        return None

class PlayerCharacter(object):
    def Promote(self, board, piece, position):
        return Queen(piece.color)

    def Do(self, board, color):
        print(board)
        print(f'--- Your turn: {color} ---')
        print("Enter start x: ")
        sx = int(input())
        print("Enter start y: ")
        sy = int(input())
        print("Enter end x: ")
        ex = int(input())
        print("Enter end y: ")
        ey = int(input())

        return (Position(sx, sy), Position(ex, ey))

class MakesALegalMove(object):
    def Promote(self, board, piece, position):
        return Queen(piece.color)

    def Do(self, board, color):
        pieces = board.getPieces()
        moves = []

        for pair in pieces:
            piece = pair[0]
            start = pair[1]

            if piece.color != color:
                continue

            for x in range(8):
                for y in range(8):
                    end = Position(x, y)

                    if start != end and piece.canMove(start, end, board):
                        moves.append((start, end))

        indices = list(range(0, len(moves)))
        random.shuffle(indices)

        for i in indices:
            move = moves[i]

            try:
                board.movePiece(move[0], move[1])
            except IllegalMove:
                continue

            return move
        
        raise Concede()

# TODO:
# - [x] Pawn first move
# - [ ] En Passant
# - [x] Promotion
# - Draws
#   - [ ] Repeated actions
#   - [ ] No legal moves 
# - [ ] Non brute force move generation
# - [ ] CanMove vs IllegalMove discrepancy 
# - [x] Player character

game = StandardGame(MakesALegalMove(), PlayerCharacter())

while game.winner == None:
    game.turn()

print (game.board)
print(f'The winner is {game.winner}!')