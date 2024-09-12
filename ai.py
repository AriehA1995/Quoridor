"""
This module is for all the AI components in the game.
Include the path finding algorithm and the definition of AIPlayer.
"""
from queue import Queue
      
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
