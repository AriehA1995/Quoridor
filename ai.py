"""
This module is for all the AI components in the game.
Include the path finding algorithm and the definition of AIPlayer.
some change
"""
from queue import Queue

class Action:
    def __init__ (self, player, name, cell, direction = 0):
        self.player = player
        self.name = name
        self.cell = cell
        self.canceller = None
        self.direction = direction
        self.checkScore ()

    def __call__ (self, undo=False):
        if self.name == "block":
            block = self.player.addBlock (self.direction, self.cell)
            if block:
                if undo:
                    self.canceller = len (self.player.game.board.blocks)
            return block
        else:
            if undo:
                self.canceller = self.player.cell
            self.player.cell = self.cell
            return True

    def undo (self):
        if self.canceller:
            if self.name == "block":
                self.player.game.board.blocks.pop (self.canceller - 1)
                self.player.blocks += 1
            else:
                self.player.cell = self.canceller
            self.canceller = None
        else:
            raise Exception ("Can not undo the last action.")

    def __repr__ (self):
        return f"{self.player.name} {self.name} {str (self.direction) + ' ' if self.name == 'block' else ''}{self.cell} = {self.score}"

    def __hash__ (self):
        return hash (repr (self))

    def checkScore (self):
        if self(True):
            shortest = len (self.player.game.board)
            for p in self.player.game.players:
                path = findPath (p)
                length = len (path)
                if p is self.player:
                    myLength = length
                else:
                    if length < shortest:
                        shortest = length
            self.__score = shortest - myLength
            self.undo()
        else:
            self.__score = len (self.player.game.board) * -1

    @property
    def score (self):
        return self.__score
        
def findPath (player)-> list:
    """
    A function the find the shortest path to win (go to its target) for the player.
    Use the A* algorithm.
    Returns a list of the cells.
    """
    startCell = player.cell
    board = player.game.board
    target = set (player.target)
    if startCell in target:
        return [startCell]
    visited = set ()
    q = Queue ()
    q.put ([startCell])
    visited.add (startCell)

    while not q.empty():
        path = q.get()
        currentCell = path [-1] #the last cell in the current path
        for direction, cell in currentCell.neighbors().items():
            if cell in visited or board.blocked (currentCell, direction, 0): #cell already checked or cannot go there, skip the cell
                continue
            newPath = path + [cell]
            if cell in target:
                return newPath
            visited.add (cell)
            q.put (newPath)
            
    return []
        
def findAction (player):
    shortest = len (player.game.board)
    paths = []
    for p in player.game.players:
        path = findPath (p)
        length = len (path)
        if p is player:
            myPath = path
            myLength = length
        else:
            paths.append (path)
            if length < shortest:
                shortest = length
    actions = set()
    moveAction = Action (player, "move", myPath[1])
    if player.blocks:
        for path in paths:
            for x in range (len(path)-1):
                cell1 = path[x]
                cell2 = path[x+1]
                if cell1.x == cell2.x:
                    direction = 0
                    if cell1.y > cell2.y:
                        newAction = Action (player, "block", cell1, direction)
                    else:
                        newAction = Action (player, "block", cell2, direction)
                    if not newAction in actions:
                        actions.add (newAction)
                    if cell1.x > 1:
                        newCell = player.game.board.index (cell1.x - 1, newAction.cell.y)
                        newAction = Action (player, "block", newCell, direction)
                        if not newAction in actions:
                            actions.add (newAction)
                else:
                    direction = 1
                    if cell1.x > cell2.x:
                        newAction = Action (player, "block", cell1, direction)
                    else:
                        newAction = Action (player, "block", cell2, direction)
                    if not newAction in actions:
                        actions.add (newAction)
                    if cell1.y < player.game.board.height:
                        newCell = player.game.board.index (newAction.cell.x, cell1.y + 1)
                        newAction = Action (player, "block", newCell, direction)
                        if not newAction in actions:
                            actions.add (newAction)
    for action in actions:
        if action.score > moveAction.score:
            moveAction = action
    return moveAction
         
    
if __name__ == "__main__":
    from game import QuoridorGame, pygame
    pygame.init()
    game = QuoridorGame ()
    game.start()
    game.board.addBlock (0, 4, 5)
    game.board.addBlock (0, 6, 8)
    path = findPath (game.currentPlayer)
    game.displayed = True
    for cell in path:
        #pygame.time.delay (250)
        game.window.fill ((255,255,0), cell.rect)
        pygame.draw.rect (game.window, (0,0,0), cell.rect, 1)
    pygame.display.update()
    findAction (game.currentPlayer)
