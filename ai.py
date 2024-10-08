"""
This module is for all the AI components in the game.
Include the path finding algorithm and the definition of AIPlayer.
I work on the feature of AIPlayer, not finished yet
"""
from queue import Queue
      
class Action:
    """
    This class define an optional action
    player - a Player object
    name - name of the action. can be "move" or "block"
    cell - cell to move or to put a block
    canceller - used in the undo method to cancel the execution of the action after checking the score
    direction - optional, direction of the block. default is 0 = horizontal
    """
    def __init__ (self, player, name, cell, direction = 0):
        self.player = player
        self.name = name
        self.cell = cell
        self.canceller = None
        self.direction = direction
        self.checkScore ()

    def __call__ (self, undo=False):
        """
        Thats how to execute the action itself
        return a Block object if a block was placed, True if player moved, False if nothing happenned (error occured)
        """
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
        """
        Undo the action after testing the score
        """
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
        return f"AIPlayer: {self.player.name} {self.name} {str (self.direction) + ' ' if self.name == 'block' else ''}{self.cell}"

    def __hash__ (self):
        return hash (repr (self))

    def checkScore (self):
        """
        Checks how good is this specific action.
        High score is better than low score.
        The function executes the action and than check the difference between the length of the path of the player
        and the length of the path of other players.
        the score is the difference between both.
        for example, if after the action the path will be 2 long and other player path will be 10 long, the score is 10,
        but if the path will be 10 long and other player path is 2 long, the score is -8.
        can return a big negative number if action is impossible.
        after the calc, undo the action.
        """
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
    """
    This function find the best action for a player to do
    based on the score of actions
    return an Action object
    """
    paths = []
    for p in player.game.players:
        path = findPath (p)
        if p is player:
            myPath = path
        else:
            paths.append (path)
    actions = set()
    moveAction = None

    # adding the optional actions of moving
    for cell in player.optionalMoves.values():
        newAction = Action (player, "move", cell)
        actions.add (newAction)
        if cell == myPath[1]:
            moveAction = newAction # moving to the next cell in shortest path is the default action
    if not moveAction:
        moveAction = actions.pop() #random element. at the end of the function all the scores will be checked

    if player.blocks:
        for path in paths: #do this for every other player
            for x in range (len(path)-1): #every cell of the opposing path
                cell1 = path[x]
                cell2 = path[x+1]
                if cell1.x == cell2.x: # the cells are on the same column
                    direction = 0
                    if cell1.y > cell2.y:
                        newAction = Action (player, "block", cell1, direction)
                    else:
                        newAction = Action (player, "block", cell2, direction)
                    if not newAction in actions:
                        actions.add (newAction)
                    if cell1.x > 1: #there is also a possibility to place a block on the cell of the left
                        newCell = player.game.board.index (cell1.x - 1, newAction.cell.y)
                        newAction = Action (player, "block", newCell, direction)
                        if not newAction in actions:
                            actions.add (newAction)
                else: #the cells are on the same row
                    direction = 1
                    if cell1.x > cell2.x:
                        newAction = Action (player, "block", cell1, direction)
                    else:
                        newAction = Action (player, "block", cell2, direction)
                    if not newAction in actions:
                        actions.add (newAction)
                    if cell1.y < player.game.board.height: #there is also a possibility to place a block on the cell of the top
                        newCell = player.game.board.index (newAction.cell.x, cell1.y + 1)
                        newAction = Action (player, "block", newCell, direction)
                        if not newAction in actions:
                            actions.add (newAction)
    for action in actions:
        if action.score > moveAction.score:
            moveAction = action
        elif moveAction.score < 0 and moveAction.name == "move" and action.name == "block" and action.score == moveAction.score:
            #the default action will be block if the player is losing
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
        pygame.time.delay (250)
        game.window.fill ((255,255,0), cell.rect)
        pygame.draw.rect (game.window, (0,0,0), cell.rect, 1)
        pygame.display.update()
    game.currentPlayer.cell = game.board.index (1,6)
    game.players[1].cell = game.board.index (9,2)
    game.board.addBlock (0, 1, 7)
    #game.board.addBlock (0, 7, 3)
    print (findAction (game.currentPlayer))
    game.display (500,500)
    pygame.time.delay (6000)
