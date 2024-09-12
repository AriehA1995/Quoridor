"""
This is the basic file that contains the settings and the functionnality of the game.
classes defined here:
    QuoridorGame - the game itself
    Board - the board of the game
    Cell - the cells inside of the board
    Player - players in the game
    Block - blocks in the board
"""

import pygame
from ai import findPath
import json

class Cell:
    """
    This is the class for one cell in the board.
    every cell has x and y coordinates, when 1,1 is bottom left.
    Attributes:
        x, y - x and y value of the cell
        next - next cell in the board (or None if no exists)
        top, bottom, right, left - neighbors of the cell
        rect - pygame.Rect instance for drawing
    """
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.next = None
        self.__top = None
        self.__bottom = None
        self.__right = None
        self.__left = None
        self.rect = None

    @property
    def coord (self) -> tuple:
        """
        Returns a tuple (x, y) of the cell.
        """
        return (self.x, self.y)

    def __repr__(self):
        return "Cell (" + str(self.x) + ", " + str(self.y) + ")"

    def __next__(self):
        return self.next

    @property
    def top (self):
        return self.__top

    @top.setter
    def top (self, other):
        self.__top = other
        other.__bottom = self

    @property
    def bottom (self):
        return self.__bottom

    @property
    def right (self):
        return self.__right

    @right.setter
    def right (self, other):
        self.__right = other
        other.__left = self

    @property
    def left (self):
        return self.__left

    def __eq__(self, other) -> bool:
        try:
            return self.x == other.x and self.y == other.y
        except AttributeError:
            return False

    def __hash__ (self) -> int:
        return hash (self.coord)

    def __contains__ (self, player) -> bool:
        """
        Check if there is a player on the cell
        """
        if isinstance (player, Player):
            return player.x == self.x and player.y == self.y
        return False

    def neighbors (self, direction: str=None, rotation: int=0) -> dict:
        """
        Returns a dict with all the available directions as keys, and corresponding cell as value.
        directions are: top, bottom, right, left
        if direction specified, returns a Cell instance
        if rotation specified, will rotate based on the rotation.
        rotation can be 0, 90, 180, 270.
        """
        dictionnary = Board.directionsDict[rotation]
        if direction:
            neighbors = self.neighbors(rotation=rotation)
            if direction in neighbors:
                return neighbors[direction]
            return None
        neighbors = {}
        if self.top:
            neighbors[dictionnary["top"]] = self.__top
        if self.right:
            neighbors[dictionnary["right"]] = self.__right
        if self.bottom:
            neighbors[dictionnary["bottom"]] = self.__bottom
        if self.left:
            neighbors[dictionnary["left"]] = self.__left
        return neighbors

    def diagonals (self, direction: str, rotation: int) -> dict:
        """
        This method find the diagonals cellsrelative to a specific cell.
        returns a dictionarry of the two cells that are diagonals.
        Attributes:
        direction - top, right, bottom, left
        rotation - the rotation of the board
        """
        nextCell = self.neighbors (direction, rotation)
        if nextCell:
            if direction in ("top", "bottom"):
                return {"right": nextCell.neighbors ("right", rotation), "left": nextCell.neighbors ("left", rotation)}
            if direction in ("right", "left"):
                return {"top": nextCell.neighbors ("top", rotation), "bottom": nextCell.neighbors ("bottom", rotation)}
        return {}

    
class Block:
    """
    Class for the blocks on the board.
    every board has two cells that are in the right, stored in the rightCells attribute (tuple)
    rect attribute is for drawing the block.
    """
    def __init__ (self, cell1, cell2):
        """
        To init, two cells on the right needed.
        if the block is vertical, the top-right cell is first.
        if the block is horizontal, the top-left cell first.
        """
        if (cell1.right == cell2 or cell1.bottom == cell2) and cell2 is not None and cell1.bottom and cell2.left:
            self.rightCells = (cell1, cell2)
            self.rect = None
        else:
            raise Exception ("Can't place block here.")

    def __repr__(self):
        if self.direction:
            di = "Vertical"
            inside = "inside of"
        else:
            di = "Horizontal"
            inside = "under"
        return f"{di} block {inside} {self.rightCells[0]} and {self.rightCells[1]}."

    @property
    def direction (self) -> int:
        """
        This method checks the direction of the block.
        Returns 1 if vertical, else 0.
        """
        if self.rightCells[0].right == self.rightCells[1]:
            return 0 #the block is horizontal
        else:
            return 1 #the block is vertical

    def draw (self, surface, gapSize: int, rotation: int):
        """
        Draw the block on a surface.
        gapSize is for the width of the gap between blocks.
        rotation is for the rotation of the board.
        """
        c = self.rightCells[0].rect
        d = self.rightCells[1].rect

        if (self.direction and rotation in (0,180)) or ((not self.direction) and rotation in (90, 270)): # the block is vertical in the surface
            width = gapSize
            height = c.height * 2 + gapSize
        else: #the block is horizontal in the surface
            width = c.width * 2 + gapSize
            height = gapSize
        if rotation:
            if rotation == 90:
                if self.direction:
                    topLeftX = d.left
                    topLeftY = d.top - gapSize
                else:
                    topLeftX = c.left - gapSize
                    topLeftY = c.top
            elif rotation == 270:
                if self.direction:
                    topLeftX, topLeftY = c.bottomleft
                else:
                    topLeftX, topLeftY = d.topright
            else:
                if self.direction:
                    topLeftX, topLeftY = d.topright
                else:
                    topLeftX = d.left
                    topLeftY = d.top - gapSize
        else:
            if self.direction:
                topLeftX = c.left - gapSize
                topLeftY = c.top
            else:
                topLeftX, topLeftY = c.bottomleft
        self.rect = pygame.draw.rect (surface, (100,100,100), (topLeftX, topLeftY, width, height))
 

class Board:
    """
    This is the class for the board of the game.
    a board contains multiple cells and can contain blocks. the players are not linked to the board.
    Attribute:
        height, width - the height and width of the board (number of cells).
        first - first cell of the board (bottom left).
        blocks - list of the blocks in the board (Block instance).
        currentGap - Gap instance. used to display on the screen.
        __rotation - current rotation of the board on the screen. default value is 0.
        __bottomLeft - current bottom left cell on the screen.
    """
    cellColor = (255,127,36)
    def __init__(self, width: int, height:  int=-1):
        """
        Initialize the board, based on the given width and height. if height is not given or lower than 0, the height will like the width.
        """
        self.width = width
        if height < 0:
            self.height = width
        else:
            self.height = height

        self.first = Cell (1, 1)
        temp = self.first
        bottom = temp
        for y in range (self.height):
            for x in range (self.width):
                if x==0 and y==0:
                    continue
                newCell = Cell (x+1, y+1)
                temp.next = newCell
                if x > 0:
                    #use the setter of the right cell
                    temp.right = newCell
                temp = newCell
                if y > 0:
                    #use the setter of the top cell
                    bottom.top = newCell
                    bottom = bottom.next

        self.blocks = []
        self.currentGap = None
        self.__rotation = 0
        self.__bottomLeft = self.first

    def __iter__(self):
        """
        Iterates all the cell in the board.
        bottom row first, from left to right. and then go up.
        """
        current = self.first
        yield current
        while current.next != None:
            yield current.next
            current = current.next

    def __len__(self):
        """
        len function returns the number of cells in the board.
        """
        return self.width * self.height

    def __eq__(self, other):
        """
        check if two boards are equals based on their size.
        """
        return self.width == other.width and self.height == other.height

    def __repr__(self):
        return "Board " + str(self.width) + "x" + str(self.height)

    def getRow (self, index: int):
        """
        This method returns an generator of a specific row of the board.
        """
        current = self.first
        for i in range (index - 1):
            current = current.top
        yield current
        while current.right != None:
            yield current.right
            current = current.right

    def getCol (self, index: int):
        """
        This method returns an generator of a specific column of the board.
        """
        current = self.first
        for i in range (index - 1):
            current = current.right
        yield current
        while current.top != None:
            yield current.top
            current = current.top

    @property
    def rows (self):
        """
        This method returns an generator of all the rows of the board.
        """
        for i in range (self.height):
            yield self.getRow (i + 1)

    @property
    def cols (self):
        """
        This method returns an generator of all the columns of the board.
        """
        for i in range (self.width):
            yield self.getCol (i + 1)

    def __getitem__(self, index) -> Cell:
        """
        the board is indexed by the same order of the iter function
        """
        current = self.first
        for i in range (index):
            current = current.next
        return current

    def index (self, x: int, y: int) -> Cell:
        """
        This methods returns a cell by the given x and y coordinates. (x=1 is the left, y=1 is the bottom).
        If coordinates does not exists, returns None.
        """
        for cell in self.getCol (x):
            if cell.y == y:
                return cell
        return None

    @property
    def MAX_BLOCKS (self) -> int:
        """
        returns the number of the blocks the board can contain.
        the number is (width + 1) * (height + 1) // 5
        """
        return ((self.width + 1) * (self.height + 1)) // 5

    @property
    def rotation (self):
        return self.__rotation

    @rotation.setter
    def rotation (self, rotation: int):
        """
        This method rotate the board to the given rotation.
        Used every turn
        """
        if rotation % 90 == 0:
            self.__rotation = rotation
        else:
            raise ValueError ("Illegal rotation.")
        
    def blocked (self, cell: Cell, direction: str, boardRotation: int=1) -> bool:
        """
        This method checks if a given cell is blocked in a specific direction.
        the boardRotation argument is given if the direction is by a relative rotation and not the current rotation (__rotation attribute).
        returns True if blocked, else False.
        """
        if boardRotation == 1:
            boardRotation = self.__rotation
        nextCell = cell.neighbors(direction, boardRotation)
        if nextCell is None:
            return True # the cell is blocked in that direction because there is no cell there
        rotation = direction in (self.absoluteDirection ("top", boardRotation), self.absoluteDirection ("bottom", boardRotation)) # if vertical, rotation is True
        for block in self.blocks:
            if not block.direction == rotation: # if the direction is the same of the block direction, the block can not block the direction
                if direction in (self.absoluteDirection ("top", boardRotation), self.absoluteDirection ("right", boardRotation)):
                    if cell not in block.rightCells and nextCell in block.rightCells:
                        return True
                else:
                    if cell in block.rightCells and nextCell not in block.rightCells:
                        return True
        return False

    def canPlaceBlock (self, direction: int, cell: Cell) -> Block:
        """
        This method checks if a block can be placed in a specific place on the board.
        Arguments:
            direction - the direction of the block, can be 1 (vertical) or 0 (horizontal).
            cell - if horizontal, the cell that is on top left of the gap. if vertical, top right.
            returns a Block instance if can be placed, else None.
        """
        if direction: #vertical
            for block in self.blocks: # check if there is already a block in this place
                if block.direction:
                    if cell in block.rightCells or cell.bottom in block.rightCells:
                        return None
                else:
                    if cell == block.rightCells[1]:
                        return None
            try:
                return Block (cell, cell.bottom)
            except Exception:
                return None
        else: #horizontal
            for block in self.blocks: # check if there is already a block in this place
                if not block.direction:
                    if cell in block.rightCells or cell.right in block.rightCells:
                        return None
                else:
                    if cell.right == block.rightCells[0]:
                        return None
            try:
                return Block (cell, cell.right)
            except Exception:
                return None
                    
    def addBlock (self, direction, cellX: int, cellY: int):
        """
            This function add a block to the board.
            direction can be a string or an integer (horizontal=0, vertical=1).
            cellX and cellY are the coordinates of the right cell relative to the block.
            returns the new block if success, else returns None.
        """
        if len(self.blocks) < self.MAX_BLOCKS:
            try:
                cell = self.index (cellX, cellY)
                if isinstance(direction, str):
                    if direction.capitalize().startswith ("H"):
                        direction = 0
                    elif direction.capitalize().startswith ("V"):
                        direction = 1
                    else:
                        raise ValueError("Illegal direction")
                newBlock = self.canPlaceBlock (direction, cell)
                if newBlock:
                    self.blocks.append (newBlock)
                    return newBlock
                else:
                    print (cell)
                    raise Exception ("There is already a block here")
            except Exception as e:
                print (e)
                return None
        else:
            return None

    def draw (self, surface, cellSize: int, cellGap: int = 5):
        """
        This method draw the board on a specific surface.
        cellSize is the number of pixels of the cell, rotation of the board and cellGap is the gap between cells in pixels.
        """
        #Calculate the size of the board
        width = cellGap * (self.width+1) + cellSize * self.width
        height = cellGap * (self.height+1) + cellSize * self.height

        #Center of the window
        center = surface.get_rect().center

        #Top-Left corner of the board
        leftX = center[0] - width // 2
        topY = center[1] - height // 2
        #draw the board
        self.rect = pygame.draw.rect (surface, Board.cellColor, (leftX, topY, width, height))
        pygame.draw.rect (surface, (0,0,0), self.rect, 1)

        rotation = self.__rotation
        if rotation:
            if rotation == 90:
                self.__bottomLeft = self.index (self.width, 1)
                x = leftX + cellGap
                y = topY #start from the top left
                for cell in self:
                    y += cellGap
                    cell.rect = pygame.draw.rect (surface, (0,0,0), (x, y, cellSize, cellSize), 1)
                    if cell.x == self.width:
                        #Pass line
                        x += (cellSize + cellGap)
                        y = topY
                    else:
                        #Stay in the same line
                        y += cellSize
            elif rotation == 270:
                self.__bottomLeft = self.index (1, self.height)
                x = leftX + width - cellGap - cellSize
                y = topY + height - cellSize #start from the bottom right
                for cell in self:
                    y -= cellGap
                    cell.rect = pygame.draw.rect (surface, (0,0,0), (x, y, cellSize, cellSize), 1)
                    if cell.x == self.width:
                        #Pass line
                        x -= (cellSize + cellGap)
                        y = topY + height - cellSize
                    else:
                        #Stay in the same line
                        y -= cellSize
            else:
                self.__bottomLeft = self.index (self.width, self.height)
                x = leftX + width - cellSize
                y = topY + cellGap #start from the top right
                for cell in self:
                    x -= cellGap
                    cell.rect = pygame.draw.rect (surface, (0,0,0), (x, y, cellSize, cellSize), 1)
                    if cell.x == self.width:
                        #Pass line
                        x = leftX + width - cellSize
                        y += (cellSize + cellGap)
                    else:
                        #Stay in the same line
                        x -= cellSize
        else:
            self.__bottomLeft = self.first
            x = leftX
            y = topY + height - cellGap - cellSize #start from the bottom left
            for cell in self:
                x += cellGap
                cell.rect = pygame.draw.rect (surface, (0,0,0), (x, y, cellSize, cellSize), 1)
                if cell.x == self.width:
                    #Pass line
                    x = leftX
                    y -= (cellSize + cellGap)
                else:
                    #Stay in the same line
                    x += cellSize

        for block in self.blocks:
            block.draw (surface, cellGap, self.__rotation)

    def erase (self):
        """
        Erase the board from the surface.
        """
        self.rect = None
        for cell in self:
            cell.rect = None
        for block in self.blocks:
            block.rect = None

    directionsDict = {
            0:{"top":"top", "right":"right", "bottom":"bottom", "left":"left"},
            90:{"top":"right", "right":"bottom", "bottom":"left", "left":"top"},
            180:{"top":"bottom", "right":"left", "bottom":"top", "left":"right"},
            270:{"top":"left", "right":"top", "bottom":"right", "left":"bottom"}            
            }

    def absoluteDirection (self, direction: str = None, rotation: int = None) -> dict:
        """
        This method calculates what is the needed direction to specify to get an absolute direction.
        for example, if the board is rotated by 180 deg, to get the absolute top of the board,
        we need to set bottom that relatively will gives us the top of the board.
        Returns a dictionarry with the keys [top, right, bottom, left].
        """
        if rotation is None:
            rotation = self.__rotation
        if direction:
            return self.directionsDict[rotation][direction]
        return self.directionsDict[rotation]
                    
    def getGapByPixel (self, x: int, y: int):
        """
        This method calculates what element on the board in a specific pixel.
        Will return a Gap object if the pixel is inside a gap between cells.
        in all other cases, will return None.
        """
        from guiutil import Gap
        if self.rect: #check if the board is displayed
            if self.rect.collidepoint(x,y): #check if the pixel is inside of the board
                try:
                    temp = self.__bottomLeft
                    while temp: #find the column that is in right of the gap
                        if temp.rect.right < x:
                            temp = temp.neighbors ("right", self.__rotation)
                        elif temp.rect.right == x:
                            return None
                        else:
                            break
                    while temp: #find the cell on top of the gap
                        if temp.rect.top > y:
                            temp = temp.neighbors ("top", self.__rotation)
                        elif temp.rect.top == y:
                            return None
                        else:
                            break
                    if temp.rect.bottom < y: #the gap is horizontal. x value was increased and we need to return over the gap
                        if not temp.neighbors ("bottom", self.__rotation): #the gap is under the first line
                            return None
                        direction = 0
                    elif temp.rect.bottom == y:
                        return None
                    else: #the gap is vertical
                        direction = 1
                    if temp.rect.collidepoint (x,y): #the pixel is inside of a cell
                        return None
                    return Gap(direction, temp, self.__rotation)
                except AttributeError:
                    return None 
        return None

    def getNextGap (self, direction):
        """
        This method stores a specific Gap to be used later.
        Starts with bottom left (relative - by current rotation).
        If there is already a stored gap, will store the next gap in the board according to the given direction.
        Can specify "shift" to toogle to rotation of the gap (vertical/horizontal).
        If the next gap has a block inside, will skip the gap.
        Returns the stored gap. If there is no next empty gap in that direction, returns None.
        """
        from guiutil import Gap
        try:
            if not self.currentGap:
                self.currentGap = Gap (1, self.__bottomLeft.neighbors ("right", self.__rotation).neighbors ("top", self.__rotation), self.__rotation)
            else:
                if direction == "top":
                    self.currentGap = Gap (self.currentGap.direction, self.currentGap.rightCell.neighbors ("top", self.__rotation), self.__rotation)
                elif direction == "right":
                    self.currentGap = Gap (self.currentGap.direction, self.currentGap.rightCell.neighbors ("right", self.__rotation), self.__rotation)
                elif direction == "bottom":
                    self.currentGap = Gap (self.currentGap.direction, self.currentGap.rightCell.neighbors ("bottom", self.__rotation), self.__rotation)
                elif direction == "left":
                    self.currentGap = Gap (self.currentGap.direction, self.currentGap.rightCell.neighbors ("left", self.__rotation), self.__rotation)
                elif direction == "shift":
                    self.currentGap = Gap (not bool(self.currentGap.direction), self.currentGap.rightCell, self.__rotation)
                else:
                    raise ValueError ("Illegal direction")
            if not self.canPlaceBlock (self.currentGap.direction, self.currentGap.rightCell):
                if direction == "shift":
                    # to avoid a recursive function. check if there is a possibility in the right
                    direction = "right"
                self.currentGap = self.getNextGap (direction)
        except AttributeError:
            return None
        return self.currentGap


class Player:
    """
    Class for player.
    Attributes:
        color - The color of the player
        name - its name
        __startPosition is the starting position at the beginning of the game.
        __position - the current position of the player
        __game - the game that the player is connected to it.
        rect - pygame.Rect instance. The of the player on the surface.
        currentAction - move or block
        blocks - how many blocks he has.
        rotation - rotation of the player
        __target - list of the cells that are the target of that player (win if he is inside of one of them).
    """
    def __init__(self, name: str, color: str, startPosition: tuple):
        """
        The init method needs only the name of the player, the color and the starting position
        """
        self.color = color
        self.name = name
        self.__startPosition = startPosition
        self.__position = list(startPosition[:2])
        self.__game = None
        self.rect = None
        self.currentAction = "move"
        self.blocks = 0
        self.rotation = 0
        self.__target = None

    @property
    def x (self):
        """
            The x position of the player.
        """
        return self.__position[0]

    @x.setter
    def x (self, value):
        if value > 0:
            try:
                if value <= self.game.board.width:
                    self.__position[0] = value
                else:
                    raise ValueError (f"The board has not {(value, self.y)} cell.")
            except AttributeError:
                self.__position[0] = value
        else:
            raise ValueError ("The player must be on a positive cell.")

    @property
    def y (self):
        """
            The y position of the player.
        """
        return self.__position[1]

    @y.setter
    def y (self, value):
        if value > 0:
            try:
                if value <= self.game.board.height:
                    self.__position[1] = value
                else:
                    raise ValueError (f"The board has not {(self.x, value)} cell.")
            except AttributeError:
                self.__position[1] = value
        else:
            raise ValueError ("The player must be on a positive cell.")

    @property
    def position (self) -> tuple:
        """
            The position of the player.
            Returns a tuple (x, y).
        """
        return (self.x, self.y)

    def __repr__(self):
        return f"{self.name} the {self.color} player. {self.position}."

    @property
    def cell (self) -> Cell:
        """
            Calculates the cell of the player.
            Returns None if the player didn't start a game.
        """
        try:
            return self.game.board.index(*self.position)
        except AttributeError:
            return None

    @cell.setter
    def cell (self, newCell):
        """
            Set a cell to be the position of the player
        """
        self.x = newCell.x
        self.y = newCell.y

    @property
    def game (self):
        return self.__game

    @game.setter
    def game (self, gameInstance):
        """
            Can set a game to a player and also set None to remove the player from the game.
        """
        if gameInstance:
            self.__game = gameInstance
            gameInstance.players.append (self)
            self.blocks = gameInstance.board.MAX_BLOCKS // len (gameInstance.settings["players"])
            x, y, w, h = (*self.position, gameInstance.board.width, gameInstance.board.height)
            if x == 1:
                self.__target = ("x", w)
            elif x == w:
                self.__target = ("x", 1)
            elif y == h:
                self.__target = ("y", 1)
            else: #default target: top row
                self.__target = ("y", h)
        else:
            self.__game.players.remove (self)
            self.__position = list(self.__startPosition[:2])
            self.blocks = 0
            self.__target = None
            self.__game = None
            self.rotation = 0

    @property
    def isAi (self):
        return False
    
    @property
    def target (self):
        if self.__target:
            if self.__target [0] == "x":
                return self.game.board.getCol (self.__target[1])
            else:
                return self.game.board.getRow (self.__target[1])
        return None

    @property
    def targetAsTuple (self):
        return self.__target

    def changeAction (self):
        """
        Toggle currentAction attribute (move or block).
        """
        if self.currentAction == "move":
            self.currentAction = "block"
        else:
            self.currentAction = "move"

    def move (self, direction: str) -> bool:
        """
            Move the player 1 step to a specific direction (relative).
            Returns True if success, else False
        """
        try:
            cell = self.optionalMoves [direction]
            self.cell = cell
        except KeyError:
            return False
        return True

    def addBlock (self, direction: int, cell: Cell) -> bool:
        """
        Add a block from the blocks of the player to the board.
        direction is 1=vertical, 0= horizontal
        cell is the right of the block.
        Return True if success, else False.
        """
        if self.blocks:
            if self.game.board.addBlock (direction, cell.x, cell.y):
                for player in self.game.players:
                    if not findPath (player):
                        self.game.board.blocks.pop()
                        return False
                self.blocks -= 1
                return True
        return False

    @property
    def winner (self) -> bool:
        """
        This method checks if the player is the winner (if the player is on a cell in its target).
        """
        if self.game:
            for cell in self.target:
                if self in cell:
                    return True
        return False

    @property
    def optionalMoves (self) -> dict:
        """
        This method calculates the optional moves of the player, including blocks on the board and other players.
        Returns a dict with every optional direction and the relevant cell.
        """
        options = self.cell.neighbors (rotation=self.rotation)
        blocked = self.game.board.blocked
        for direction in list(options):
            if blocked (self.cell, direction):
                options.pop (direction)
                continue
            cell = options[direction]
            player = self.game.playerInCell (cell)
            if player:
                options[direction] = cell.neighbors (direction, self.rotation) # jump over the player
                if options[direction]:
                    if blocked (cell, direction) or self.game.playerInCell (options[direction]):
                        diagonal = self.cell.diagonals (direction, self.rotation)
                        for d in list(diagonal):
                            if blocked (cell, d) or self.game.playerInCell (diagonal[d]) or diagonal[d] is None:
                                diagonal.pop (d)
                else:
                    diagonal = self.cell.diagonals (direction, self.rotation)
                    for d in list(diagonal):
                        if blocked (cell, d) or self.game.playerInCell (diagonal[d]) or diagonal[d] is None:
                            diagonal.pop (d)
                if "diagonal" in locals():
                    if diagonal:
                        if len (diagonal) > 1:
                            options.pop (direction)
                            if direction in ("top", "bottom"):
                                options[direction + "-right"] = diagonal["right"]
                                options[direction + "-left"] = diagonal["left"]
                            else:
                                options["top-" + direction] = diagonal["top"]
                                options["bottom-" + direction] = diagonal["bottom"]
                        else:
                            options[direction] = next(iter(diagonal.values()))
                    else:
                        options.pop (direction)
        return options
        
    def draw(self):
        """
        Draw the player on the screen.
        """
        try:
            currentCell = self.cell.rect
            radius = currentCell.width * (3/8)
            self.rect = pygame.draw.circle(self.game.window, self.color, currentCell.center, radius)
            rect = self.game.board.rect
            dictionnary = {
                0: (rect.left, rect.top - 2, rect.width, 2),
                90: (rect.left - 2, rect.top, 2, rect.height),
                180: (*rect.bottomleft, rect.width, 2),
                270: (*rect.topright, 2, rect.height)
                }
            pygame.draw.rect(self.game.window, self.color, dictionnary[(self.rotation - self.game.currentPlayer.rotation) % 360])
        except AttributeError:
            print (f"Can't draw {self.name} player.")

class AIPlayer (Player):
    @property
    def isAi (self):
        """ override isAi property """
        return True
    
    def autoAction (self):
        self.move ("top")
        print (f"{self.name} moved top.")
        
class QuoridorGame:
    """
    QuoridorGame is the class for the game.
    """
    def __init__(self):
        """
        initialize the basic settings of the game.
        Basically, a game is not showed in the screen until calling the display method.
        a game starts only after calling the start method.
        Attributes:
            window - a pygame.Surface object. generated by the display method.
            board - Board instance. generated after start.
            players - list of players (Player instance). generated after start.
            buttons - list of buttons in the screen. generated after display and depending of the status of the game.
            currentPlayer - must be a Player instance included in the list of players.
            winner - Player instance, if winner exists.
            settings - a dict with the settings of the game (start and display methods use theses settings.
        """
        self.window = None
        self.board = None
        self.players = []
        self.texts = []
        self.buttons = []
        self.currentPlayer = None
        self.winner = None
        self.settings = {
            "background-color":(255,255,150),
            "players": ["Player 1", "Player 2"],
            "players-colors": {2:["red", "blue"], 4:["red", "green", "blue", "gold"]},
            "ai-players" : [],
            "board-width":9,
            "board-height":9,
            "button-color": "green4",
            "button-selected": "green"
        }
        
    def status (self, jsonformat: bool = False):
        """
        This method returns the status of the game.
        Contains board properties, details of players, and blocks positions.
        If jsonformat argument is False, returns a dict. Else, returns a json formatted string of the dict.
        """
        if jsonformat:
            return json.dumps (self.status(), indent=1)
        if not self.running:
            return {"running": False, "winner": self.winner.name if self.winner else None}
        return {
            "running": self.running,
            "board-width": self.board.width,
            "board-height": self.board.height,
            "players": [{
                "name": player.name,
                "color": player.color,
                "isAI": player.isAi,
                "x": player.x,
                "y": player.y,
                "blocks": player.blocks,
                "target": ("row " if player.targetAsTuple[0] == "y" else "column ") + str (player.targetAsTuple [1])
                } for player in self.players],
            "blocks": [{
                "direction": block.direction,
                "cells": [{"x": cell.x, "y": cell.y} for cell in block.rightCells]
                } for block in self.board.blocks],
            "current-player": self.currentPlayer.name
        }
        
    def setup (self, **kwargs):
        """
        This method takes key-word arguments and updates the corresponding setting.
        """
        for key, value in kwargs.items():
            self.settings [key.replace ("_", "-")] = value

    def start (self):
        """
        This method starts the game according to the settings.
        """
        w, h = self.settings ["board-width"], self.settings ["board-height"]
        playersNum = len (self.settings["players"])
        if playersNum == 2:
            position = ((w // 2 + 1, 1), (w // 2 + 1, h))
            rotations = (0,180)
        else:
            if not self.settings["board-width"] == self.settings["board-height"]:
                raise ValueError ("4 players must play on a squared board!")
            position = ((w // 2 + 1, 1), (w, h // 2 + 1), (w // 2 + 1, h), (1, h // 2 + 1))
            rotations = (0,90,180,270)
        self.board = Board(w, h)
        for index, player in enumerate (self.settings["players"]):
            if player in self.settings["ai-players"]:
                newPlayer = AIPlayer(player, self.settings["players-colors"][playersNum][index], position[index])
            else:
                newPlayer = Player(player, self.settings["players-colors"][playersNum][index], position[index])
            newPlayer.game = self
            newPlayer.rotation = rotations[index]
        self.currentPlayer = self.players[0]
        self.winner = None # if a winner already stored, delete it

    @property
    def running (self) -> bool:
        """
        property to know if the game is running.
        """
        return bool(self.board)

    @running.setter
    def running (self, value: bool):
        if not self.running == bool(value):
            if value:
                self.start()
            else:
                self.over()

    def over (self):
        """
        stops the game. set board and currentPlayer to None and empty the list of players.
        """
        self.board = None
        self.currentPlayer = None
        for player in list(self.players):
            player.game = None

    def nextPlayer (self):
        """
        pass the turn to the next player in the list.
        """
        if self.currentPlayer.winner:
            self.winner = self.currentPlayer
            self.over()
        else:
            index = self.players.index(self.currentPlayer)
            if index == len(self.players) - 1:
                self.currentPlayer = self.players[0]
            else:
                self.currentPlayer = self.players[index + 1]
            self.currentPlayer.currentAction = "move"
            self.board.rotation = self.currentPlayer.rotation

    def playerInCell (self, cell: Cell) -> Player:
        """
        check if there is a player in the given cell.
        returns the player instance if yes, else returns None
        """
        for player in self.players:
            if player in cell:
                return player
        return None

    def display (self, width: int, height: int, resizable: bool=False):
        """
        from here is the display of the game in the screen. this is an optional feature.
        This method display the game on the screen based on the given width and height.
        resizable - a bool.
        """
        if not self.displayed:
            pygame.init()
            pygame.display.set_caption ("Quoridor Game")
            try:
                gameIcon = pygame.image.load ("media/quoridor.ico")
                pygame.display.set_icon (gameIcon)
            except FileNotFoundError:
                print("Default icon loaded")
            print ("Game Displayed")
        if resizable:
            self.window = pygame.display.set_mode ((width, height), pygame.RESIZABLE)
        else:
            self.window = pygame.display.set_mode ((width, height))
        self.draw()

    def draw (self):
        """
        If the game is displayed, draw the current state of the game in the game window.
        If not, raises an Exception.
        """
        if self.displayed:
            if not self.running:
                self.window.fill ((0,0,0))
                image = pygame.image.load ("media/quoridor.jpg")
                image.set_alpha (128)
                image = pygame.transform.scale (image, self.window.get_size())
                self.window.blit (image, (0,0))
            else:
                self.window.fill (self.settings["background-color"])
                width, height = self.window.get_size()
                cellSize = min (width, height) // (1.6 * max (self.board.width, self.board.height))
                self.board.draw (self.window, cellSize)
                for player in self.players:
                    player.draw()
            for text in self.texts:
                text.draw(self.window)
            for button in self.buttons:
                button.draw(self.window)
            pygame.display.update()
        else:
            raise Exception ("Game is not displayed")

    def close (self):
        """
        close the game window. this method does not stop the game itself.
        """
        try:
            pygame.quit()
            print ("Window closed")
        except Exception:
            print ("Game window is not displayed")
        finally:
            self.window = None
            if self.running:
                self.board.erase()
                for player in self.players:
                    player.rect = None

    @property
    def displayed (self) -> bool:
        """
        check if the game is displayed
        the setter display the game on a screen of 500,500 (if the value is True).
        """
        return bool(self.window)

    @displayed.setter
    def displayed (self, value: bool):
        if value:
            self.display (500,500)
        else:
            self.close()
                
if __name__ == "__main__":
    def error (msg):
        print (f"[ERROR]:: {msg}")
        
    game = QuoridorGame()
    line = input ("Command >> ")
    while True:
        args = line.lower().split()
        n = len(args) - 1
        try:
            cmd = args[0]
        except IndexError:
            cmd = ""
        if cmd == "help":
            if n != 0:
                error (f"Command \"{cmd}\" require 0 arguments but {n} are given. Type \"help\" for more information.")
            else:
                with open ("help.txt", "r") as f:
                    print (f.read())
        elif cmd == "start":
            if n != 0:
                error (f"Command \"{cmd}\" require 0 arguments but {n} are given. Type \"help\" for more information.")
            else:
                if game.running:
                    error ("Game already running!")
                else:
                    game.start()
                    print (f"Game started. {game.currentPlayer.name} turn.")
                    if game.displayed:
                        game.draw()
        elif cmd == "status":
            if n != 0:
                error (f"Command \"{cmd}\" require 0 arguments but {n} are given. Type \"help\" for more information.")
            else:
                print (game.status (True))
        elif cmd == "display":
            if n > 2:
                error (f"Command \"{cmd}\" require 2 arguments but {n} are given. Type \"help\" for more information.")
            else:
                if game.displayed:
                    error ("Game already displayed!")
                else:
                    if n == 0:
                        game.display (500, 500)
                    elif n == 1:
                        try:
                            width = int (args[1])
                            game.display (width, width)
                        except TypeError:
                            error ("Size of window must be an integer.")
                        except ValueError:
                            error ("Size of window must be an integer.")
                    else:
                        try:
                            w, h = args [1:3]
                            game.display (int (w), int(h))
                        except TypeError:
                            print ("Size of window must be an integer.")
                        except ValueError:
                            error ("Size of window must be an integer.")
        elif cmd == "close":
            if n != 0:
                error (f"Command \"{cmd}\" require 0 arguments but {n} are given. Type \"help\" for more information.")
            else:
                if game.displayed:
                    pygame.event.pump()
                    game.close()
                else:
                    error ("Game is not displayed!")
        elif cmd == "move":
            if n != 1:
                error (f"Command \"{cmd}\" require 1 arguments but {n} are given. Type \"help\" for more information.")
            else:
                if game.running:
                    player = game.currentPlayer
                    if player.move (args[1].lower()):
                        game.nextPlayer()
                        if game.winner:
                            print (f"{game.winner.name} won!")
                        else:
                            print (f"{player.name} moved {args[1].lower()}. {game.currentPlayer.name} turn.")
                        if game.displayed:
                            game.draw()
                    else:
                        error (f"Can not move there.")
                else:
                    error ("The game has not started.")
        elif cmd == "block":
            if n != 3:
                error (f"Command \"{cmd}\" require 3 arguments but {n} are given. Type \"help\" for more information.")
            else:
                if game.running:
                    player = game.currentPlayer
                    board = game.board
                    try:
                        d = int (args[1]) #0 or 1
                    except ValueError:
                        d = args[1].lower() #string
                    try:
                        x = int (args[2])
                        y = int (args[3])
                    except ValueError:
                        error ("Second and third arguments must be integers.")
                    else:
                        if x < 1 or x > board.width:
                            error (f"Second argument must be between 0 and {board.width}.")
                        elif y < 1 or y > board.height:
                            error (f"Third argument must be between 0 and {board.height}.")
                        else:
                            if player.addBlock (d, board.index (x, y)):
                                game.nextPlayer()
                                print (f"Block added at ({x}, {y}). {player.name} has {player.blocks} blocks. {game.currentPlayer.name} turn.")
                                if game.displayed:
                                    game.draw()
                            else:
                                error ("Can not place a block there.")
                else:
                    error ("The game has not started.")
        elif cmd == "exit":
            if n != 0:
                error (f"Command \"{cmd}\" require 0 arguments but {n} are given. Type \"help\" for more information.")
            else:
                if game.displayed:
                    pygame.event.pump()
                    game.close()
                break
        else:
            error (f"Command {cmd} is not a command. Type \"help\" for more information.")
        while game.running and game.currentPlayer.isAi:
            #the AI player will play and than go to the next player
            if game.displayed:
                #display the current stat, and wait a second until the AI player will play
                pygame.time.delay (1000)
            game.currentPlayer.autoAction ()
            game.nextPlayer()
            if game.displayed:
                game.draw()
            if game.winner: #in case that the AI player won the game
                print (f"{game.winner.name} won!")
            else:
                print (f"{game.currentPlayer.name} turn.")
        print ()
        line = input ("Command >> ")
        if game.displayed:
            pygame.event.pump()
