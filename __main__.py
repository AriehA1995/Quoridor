"""
This module is for the main game.
Include the GUI application of the game. Classes: MyGame.
"""
import pygame
from game import QuoridorGame
from guiutil import Text, Button, msgBox
from threading import Thread, Lock
from tkinter import Tk, Frame, Label, Button as tkButton, Radiobutton, Entry, IntVar, StringVar

class MyGame (QuoridorGame):
    """
    This class inherit from QuoridorGame.
    It include all the GUI of the game
    Attributes:
        gameLocker - Lock for the threads.
        textFont - main text font of the game
        __isFullScreen - bool value to check if the game is displayed on full screen
        coloredOption - store the rect the showed as 'selected'
        uncoloredOption - previous coloredOption to unselect
        optionFixed - bool to check if the selected option is selected by the mouse or the keyboard
        changeActionButton - Button to toggle the current action of the current player
        turnText - Text of which player turn
        instructionText - Text for help
        quickStartButton, newGameButton - Buttons for the main menu
        gameButtons - list of all the Buttons currently displayed
        gameTexts - list of all the Texts currently displayed
        menuButton - list of all the Buttons in the main menu
        menuTexts - list of all the Texts in the main menu
    """
    def __init__(self, width: int, height: int):
        """
        Init the game. only width and height of the screen needed.
        The default font is tahoma.
        Will start with the main menu by calling the menu method.
        """
        super().__init__()
        self.gameLocker = Lock()
        self.textFont = "tahoma"
        self.display (width, height, True)
        self.__isFullScreen = False
        self.coloredOption = None
        self.uncoloredOption = None
        self.optionFixed = False
        
        self.changeActionButton = Button (0.81, 0.3, 0.05, "Block", self.settings["button-color"], self.changeAction)
        self.turnText = Text (0.8, 0.2, 0.04, "player's turn", self.settings["background-color"], self.textFont)
        self.instructionText = Text (0.35, 0.9, 0.04, "Select the destination cell", self.settings["background-color"], self.textFont)
        self.quickStartButton = Button (0.45, 0.45, 0.05, "Quick Start", self.settings["button-color"], self.start)
        self.newGameButton = Button (0.45, 0.55, 0.05, "New Game", self.settings["button-color"], self.setup)

        self.gameButtons = [self.changeActionButton]
        self.gameTexts = [self.turnText, self.instructionText]
        self.menuButtons = [self.quickStartButton, self.newGameButton]
        self.menuTexts = []
        
        self.menu()

    def start (self):
        """
        Override the start method. added functionality to display the menu and buttons.
        """
        self.coloredOption = None
        self.uncoloredOption = None
        self.optionFixed = False
        super().start()
        self.changeActionButton.text = "Block"
        self.turnText.text = self.currentPlayer.name + "'s turn"
        self.turnText.textColor = self.currentPlayer.color
        self.instructionText.relX = 0.35
        self.instructionText.text = "Select the destination cell"
        self.buttons = list(self.gameButtons)
        self.texts = list(self.gameTexts)
        
        self.texts.append (Text (0.05, 0.12, 0.06, "Blocks", self.settings["background-color"], self.textFont))
        yValue = 0.22
        for player in self.players:
            self.texts.append (Text (0.05, yValue, 0.04, f"{player.name}: {player.blocks}", self.settings["background-color"], self.textFont, player.color))
            yValue += 0.06

        self.draw()

    def over (self):
        """
        Override the over method. Just display the menu after the game end.
        """
        self.draw()
        super().over()
        self.menu()

    def menu (self):
        """
        This method show the main menu.
        All the buttons in the menuButtons attribute will be displayed, as well as all the texts in menuTexts.
        """
        self.buttons = list(self.menuButtons)
        self.texts = list(self.menuTexts)
        if self.winner:
            from tkinter.messagebox import showinfo
            msgBox (showinfo, title="Game Over!", message=self.winner.name + " won!")
            self.winner = None
        self.draw()

    def setup (self, **kwargs):
        """
        Show the window of settings.
        """
        if kwargs:
            super().setup(**kwargs)
        else:
            def addPlayers ():
                """
                    function for switch between two and four players
                """
                if playersNum.get () == 2:
                    if len (playersNames) > 2:
                        for label in labels [2:]:
                            #delete the texts
                            label.destroy()
                        labels.pop()
                        labels.pop()
                        for entry in entries [2:]:
                            #delete the input box
                            entry.destroy()
                            playersNames.pop()  
                        entries.pop()
                        entries.pop()
                        for index, label in enumerate (labels):
                            #change color for labels
                            label.config (fg= self.settings["players-colors"][2][index])
                else:
                    if len (playersNames) < 4:
                        for n in (3, 4):
                            if len (self.settings["players"]) > 2:
                                #add the name of player that is in settings
                                name = self.settings["players"][n-1]
                            else:
                                name = "Player " + str(n)
                            playersNames.append (StringVar (value = name))
                            #add the label
                            newLabel = Label (frame, text = "Player " + str (n) + " name:")
                            labels.append (newLabel)
                            newLabel.grid (row = n + 2, column = 1)
                            #add the input box
                            newEntry = Entry (frame, textvariable = playersNames[n-1])
                            entries.append (newEntry)
                            newEntry.grid (row = n + 2, column = 2)
                        for index, label in enumerate (labels):
                            #change the color
                            label.config (fg= self.settings["players-colors"][4][index])
                
            def setupAndStart ():
                players = list(map(lambda nameVar: nameVar.get(), playersNames))
                        
                self.setup (players= players,
                            board_width = boardSize.get(),
                            board_height = boardSize.get())
                win.destroy()
                self.start()
                
            win = Tk()
            win.geometry ("400x350+350+150")
            win.title ("Game Setup")
            win.iconbitmap ("media/quoridor.ico")

            frame = Frame (win, pady=10)
            frame.pack()

            #store the number of players
            playersNum = IntVar (value=len (self.settings["players"]))
            #every entry affect another variable
            playersNames = []
            #list of ai players
            for name in self.settings["players"]:
                playersNames.append(StringVar (value = name))
            #variable for board size
            boardSize = IntVar (value = self.settings ["board-width"])

            Label (frame, text="Number of players:", font=("Arial", 16, "bold"), pady = 5, padx = 15).grid (row=1, column=1, columnspan=3)
            Radiobutton (frame, text="2", value=2, variable = playersNum, command=addPlayers).grid (row=2, column=1)
            Radiobutton (frame, text="4", value=4, variable = playersNum, command=addPlayers).grid (row=2, column=2)
            labels = []
            entries = []
            for n in range (1, len (self.settings["players"]) + 1):
                #add the text with color
                newLabel = Label (frame, text = "Player " + str (n) + " name:", padx=10, fg=self.settings["players-colors"][len (self.settings["players"])][n-1])
                labels.append (newLabel)
                newLabel.grid (row = n + 2, column = 1)
                #add input box for the name
                newEntry = Entry (frame, textvariable = playersNames[n-1])
                entries.append (newEntry)
                newEntry.grid (row = n + 2, column = 2)

            #Configure the board size
            Label (frame, text="Board Size:", font=("Arial", 16, "bold"), pady = 15, padx = 15).grid (row=7, column=1, columnspan=3)
            Label (frame, text="Small:").grid (row=8, column=1)
            Radiobutton (frame, text="5x5", variable = boardSize, value= 5, indicator=0, font=("Arial", 14), bg="light blue").grid (row=9, column=1)
            Label (frame, text="Classic:").grid (row=8, column=2)
            Radiobutton (frame, text="9x9", variable = boardSize, value= 9, indicator=0, font=("Arial", 14), bg="light blue").grid (row=9, column=2)
            Label (frame, text="Big:").grid (row=8, column=3)
            Radiobutton (frame, text="13x13", variable = boardSize, value= 13, indicator=0, font=("Arial", 14), bg="light blue").grid (row=9, column=3)

            #submit button
            tkButton (win, text="Start!", command=setupAndStart, font=("Arial", 16, "bold"), fg="green", width=20).pack()
            
            win.mainloop()
        
    def fullScreen(self):
        """
        Toggle full screen.
        """
        if self.__isFullScreen:
            pygame.display.toggle_fullscreen()
            self.window = pygame.display.set_mode(pygame.display.get_window_size(), pygame.RESIZABLE)
            self.__isFullScreen = False
        else:
            self.window = pygame.display.set_mode(pygame.display.get_window_size(), pygame.FULLSCREEN)
            self.__isFullScreen = True
            
    def changeAction (self):
        """
        Toggle curent player action (move or block).
        """
        if self.currentPlayer.currentAction == "move" and self.currentPlayer.blocks < 1:
            from tkinter.messagebox import showerror
            msgBox (showerror, title="Action restricted!", message="You have run out of blocks!")
            return False
        self.window.fill (self.settings["background-color"], self.instructionText.rect)
        if isinstance (self.coloredOption, Button):
            self.window.fill (self.settings["background-color"], self.coloredOption)
        self.setColoredOption (None)
        self.board.currentGap = None
        self.currentPlayer.changeAction ()
        if self.currentPlayer.currentAction == "block":
            self.changeActionButton.update ("Move", self.window)
            self.instructionText.relX -= 0.07
            self.instructionText.update ("Select where you want to place a block", self.window)
        else:
            self.changeActionButton.update ("Block", self.window)
            self.instructionText.relX += 0.07
            self.instructionText.update ("Select the destination cell", self.window)

    def nextPlayer (self):
        """
        Override nextPlayer method.
        Execute the selected option (stored in coloredOption) and continue to the next player in the list of players.
        """
        player = self.currentPlayer
        if not player.isAi:
            index = self.players.index(player)
            if player.currentAction == "block":
                absGap = self.coloredOption.absoluteGapForBlock
                if not player.addBlock (absGap.direction, absGap.rightCell):
                    from tkinter.messagebox import showerror
                    msgBox (showerror, title="Action restricted!", message="This block will block the way for a player!")
                    return False
                self.board.currentGap = None
            else:
                player.cell = self.coloredOption
            self.texts[index + 3].text = f"{player.name}: {player.blocks}"
            self.coloredOption = None
            self.uncoloredOption = None
            self.optionFixed = False
        super().nextPlayer()
        if self.running:
            self.changeActionButton.text = "Block"
            self.turnText.text = self.currentPlayer.name + "'s turn"
            self.turnText.textColor = self.currentPlayer.color
            self.instructionText.relX = 0.35
            self.instructionText.text = "Select the destination cell"
            self.draw()
        
    def exit(self):
        """
        Close the game. Will display an 'Are you sure?' message.
        """
        from tkinter.messagebox import askyesno
        if msgBox (askyesno, "Exit", "Are you sure you want to quit the game?"):
            self.window = None

    @property
    def cursor (self):
        """
        Define the correct form of the cursor depending if can be clicked.
        """
        mousePosition = pygame.mouse.get_pos()
        for button in self.buttons:
            if button.rect.collidepoint (mousePosition):
                self.setColoredOption (button)
                return pygame.SYSTEM_CURSOR_HAND

        if self.running:
            if self.currentPlayer.currentAction == "block":
                gap = self.board.getGapByPixel (*mousePosition)
                if gap:
                    absGap = gap.absoluteGapForBlock
                    if absGap:
                        if self.board.canPlaceBlock (absGap.direction, absGap.rightCell):
                            self.setColoredOption (gap)
                            return pygame.SYSTEM_CURSOR_HAND
            else:
                for cell in self.currentPlayer.optionalMoves.values():
                    if cell.rect.collidepoint (mousePosition):
                        self.setColoredOption (cell)
                        return pygame.SYSTEM_CURSOR_HAND
                    
        if not self.optionFixed:
            self.setColoredOption (None)
        return pygame.SYSTEM_CURSOR_ARROW

    def showCursor (self):
        """
        Display the cursor and the selected option.
        """
        while self.displayed:
            try:
                pygame.time.delay(50)
                with self.gameLocker:
                    if not self.running or not self.currentPlayer.isAi:
                        pygame.mouse.set_cursor (self.cursor)
                        self.showOption()
                        pygame.display.update()
            except Exception as e:
                print(e)
                break

    def setColoredOption (self, rect, fixed=False):
        """
        Store the selected option and set the value of the uncoloredOption to the previous selected option.
        """
        if self.coloredOption:
            self.uncoloredOption = self.coloredOption
        self.coloredOption = rect
        self.optionFixed = fixed
        
    def showOption (self):
        """
        Display the selected option.
        """
        if self.uncoloredOption:
            if isinstance (self.uncoloredOption, Button):
                self.uncoloredOption.color = self.settings["button-color"]
                self.uncoloredOption.draw (self.window)
            elif isinstance (self.uncoloredOption, pygame.Rect):
                self.window.fill (self.board.cellColor, self.uncoloredOption.union(self.uncoloredOption.next))
            else:
                self.window.fill (self.board.cellColor, self.uncoloredOption.rect)
                pygame.draw.rect (self.window, (0,0,0), self.uncoloredOption.rect, 1)
            self.uncoloredOption = None
            
        if self.coloredOption:
            if isinstance (self.coloredOption, Button):
                self.coloredOption.color = self.settings["button-selected"]
                self.coloredOption.draw (self.window)
            elif isinstance (self.coloredOption, pygame.Rect):
                self.window.fill ("red", self.coloredOption.union(self.coloredOption.next))
            else:
                self.window.fill ("red", self.coloredOption.rect)
                pygame.draw.rect (self.window, (0,0,0), self.coloredOption.rect, 1)
                
WIDTH = 700
HEIGHT = 500
directions = {pygame.K_UP:"top", pygame.K_RIGHT:"right", pygame.K_DOWN:"bottom", pygame.K_LEFT:"left"}

if __name__ == "__main__":
    game = MyGame(WIDTH, HEIGHT)
    
    cursorThread = Thread (target=game.showCursor)
    cursorThread.start()
    
    while game.displayed:
        
        while game.running and game.currentPlayer.isAi:
            #handle the AI Players
            game.currentPlayer.autoAction()
            game.nextPlayer()
        else:
            for event in pygame.event.get():
                #handle events only if the current player is the user or if the game has not started
                if event.type == pygame.QUIT:
                    with game.gameLocker:
                        game.exit()
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F2:
                        game.fullScreen()
                    elif event.key == pygame.K_ESCAPE:
                        with game.gameLocker:
                            game.exit()
                    elif event.key == pygame.K_TAB:
                        if game.running:
                            game.changeAction()
                    elif event.key in directions:
                        if game.running:
                            if game.currentPlayer.currentAction == "block":
                                gap = game.board.getNextGap(directions[event.key])
                                if gap:
                                    game.setColoredOption (gap, fixed=True)
                            else:
                                options = game.currentPlayer.optionalMoves
                                if directions[event.key] in options:
                                    game.setColoredOption (options[directions[event.key]], fixed=True)
                                else:
                                    if game.coloredOption:
                                        try:
                                            nextCell = game.coloredOption.neighbors (directions[event.key], game.currentPlayer.rotation)
                                            if nextCell in options.values():
                                                game.setColoredOption (nextCell, fixed=True)
                                        except KeyError:
                                            pass
                                    else:
                                        game.setColoredOption (next(iter(options.values())), fixed=True)
                        else:
                            if event.key == pygame.K_UP:
                                if game.coloredOption:
                                    index = game.buttons.index (game.coloredOption)
                                    if index:
                                        game.setColoredOption (game.buttons[index - 1], fixed=True)
                            elif event.key == pygame.K_DOWN:
                                if game.coloredOption:
                                    index = game.buttons.index (game.coloredOption)
                                    if index < len (game.buttons) - 1:
                                        game.setColoredOption (game.buttons[index + 1], fixed=True)
                                else:
                                    game.setColoredOption (game.buttons[0], fixed=True)
                    elif event.key == pygame.K_SPACE:
                        if game.running:
                            if game.currentPlayer.currentAction == "block" and game.coloredOption and game.optionFixed:
                                gap = game.board.getNextGap("shift")
                                if gap:
                                    game.setColoredOption (gap, fixed=True)
                    elif event.key == pygame.K_RETURN:
                        if game.optionFixed:
                            with game.gameLocker:
                                if isinstance (game.coloredOption, Button):
                                    game.coloredOption.action()
                                else:
                                    game.nextPlayer()
                        
                elif event.type == pygame.VIDEORESIZE:
                    game.draw()
                    
                elif event.type == pygame.MOUSEBUTTONUP:
                    if game.coloredOption:
                        with game.gameLocker:
                            if isinstance (game.coloredOption, Button):
                                game.coloredOption.action()
                            else:
                                game.nextPlayer()
                
    #outside of the loop, displayed attribut is False
    game.close()
