"""
This module is for all the GUI custom elements of the game.
Include Text, Button, Gap and msgBox.
"""
import pygame
from tkinter import Tk

pygame.init()

class Text:
    """
    Class for text element.
    Attributes:
        relX, relY - the position of the text, relative to the top left of the surface (a float less than 1).
        relH - the size of the text, relative to the height of the surface (a float less than 1).
        text - the content of the text
        color - the background color of the text
        fontName - the font name of the text
        textColor - the color of the text
        x, y - the absolute position of the text in the screen
        size - the absolute size of the text in pixels
    """
    def __init__(self, relativeX: float, relativeY: float, relativeHeight: float, text: str, color, fontName: str = "david", textColor=(0,0,0)):
        """
        The init method.
        relative X/Y/Height need to be less than 1.
        text is the content of the text
        color is the background color.
        Default fonName is david, default textColor is black.
        """
        self.relX = relativeX
        self.relY = relativeY
        self.relH = relativeHeight
        self.text = text
        self.color = color
        self.fontName = fontName
        self.textColor = textColor
        self.x = 0
        self.y = 0
        self.size = 25

    @property
    def img (self) -> pygame.Surface:
        """
        Returns a pygame.Surface object that is the surface of the text.
        """
        return pygame.font.SysFont (self.fontName, self.size).render (self.text, 1, self.textColor)

    @property
    def rect (self) -> pygame.Rect:
        """
        Returns a pygame.Rect object.
        """
        return self.img.get_rect(topleft = (self.x, self.y))

    def updateProps (self, surface: pygame.Surface):
        """
        Update the x, y, size attributes, according to the text and the surface.
        """
        width, height = surface.get_size()
        self.x = int(width * self.relX)
        self.y = int(height * self.relY)
        if height > width:
            self.size = 10
        else:
            self.size = int(height * self.relH)

    def update (self, text: str, surface: pygame.Surface):
        """
        This method changes the content of the text and update the surface
        """
        self.text = text
        self.draw (surface)

    def draw (self, surface: pygame.Surface):
        """
        Draw the text on the surface.
        """
        self.updateProps (surface)
        pygame.draw.rect (surface, self.color, self.rect)
        surface.blit (self.img, self.rect.topleft)

class Button (Text):
    """
    Class for button. This class inherit from Text.
    Added attributes:
        __action - a function to execute when the button is clicked.
        args - list of arguments for the function
        kwargs - list of keyword arguments
    """
    def __init__(self, relativeX: float, relativeY: float, relativeHeight: float, text: str, color, action, args: list = [], kwargs: dict = {}):
        """
        The init is the same of the Text, except that the text color and the font will be the default.
        text - a name of a image file is optional. the image will be showed instead of a text.
        action - a function to be excuted when the button is clicked.
        args - list of arguments
        kwargs - dict of keyword arguments
        """
        super().__init__(relativeX, relativeY, relativeHeight, text, color)
        self.__action = action
        self.args = list(args)
        self.kwargs = dict(kwargs)

    @property
    def img (self):
        """
        Override the img method.
        """
        try:
            return pygame.image.load ("media/" + self.text)
        except FileNotFoundError:
            return super().img

    @property
    def rect (self):
        return pygame.Rect(self.x - 10, self.y - 10, self.img.get_width() + 20, self.img.get_height() + 20)
    
    def action (self):
        """
        This method executes the function of the button (including the args and kwargs).
        """
        self.__action (*self.args, **self.kwargs)

    def draw (self, surface):
        """
        There are two differences: the border radius and the position of the text (x and y instead of the rect)
        """
        self.updateProps (surface)
        pygame.draw.rect (surface, self.color, self.rect, border_radius = 5)
        surface.blit (self.img, (self.x, self.y))

    def click (self) -> bool:
        """
        This method checks if the button is clicked.
        If yes, trigger the action method. Returns True. Else return False.
        """
        for e in pygame.event.get (pygame.MOUSEBUTTONUP):
            if e.button == 1:
                if self.rect.collidepoint(e.pos):
                    self.action()
                    return True
        return False
    
    def hover (self) -> bool:
        """
        Check if the button is hovered by the mouse.
        Returns True if yes, else False.
        """
        if self.rect.collidepoint (pygame.mouse.get_pos()):
            pygame.mouse.set_cursor (pygame.SYSTEM_CURSOR_HAND)
            return True
        return False
    
class Gap (pygame.Rect):
    """
    Class for the gap.
    Attributes:
        leftCell - the left cell of the gap (relative).
        rightCell - the right cell of the gap (relative).
        direction - 0=horizontal, 1=vertical.
        rotation - the relative rotation.
    """
    def __init__(self, direction: int, rightCell, rotation: int):
        """
        The init method.
        direction - 0=horizontal, 1=vertical.
        rightCell - the cell that is on the right of the gap.
        rotation - the current rotation of the board
        """
        if direction:
            cellGap = rightCell.rect.left - rightCell.neighbors ("left", rotation).rect.right
            super ().__init__(rightCell.neighbors ("left", rotation).rect.topright, (cellGap, rightCell.rect.height))
            self.leftCell = rightCell.neighbors ("left", rotation)
        else:
            cellGap = rightCell.neighbors ("bottom", rotation).rect.top - rightCell.rect.bottom
            super ().__init__(rightCell.rect.bottomleft, (rightCell.rect.height, cellGap))
            self.leftCell = rightCell.neighbors ("bottom", rotation)

        self.direction = direction
        self.rightCell = rightCell
        self.rotation = rotation

    @property
    def next (self):
        """
        Returns the next gap, according the the direction of the gap.
        Return None if no next gap found.
        """
        try:
            if self.direction:
                nextCell = self.rightCell.neighbors ("bottom", self.rotation)
            else:
                nextCell = self.rightCell.neighbors ("right", self.rotation)
            return Gap (self.direction, nextCell, self.rotation)
        except AttributeError:
            return None

    @property
    def absoluteGapForBlock (self):
        """
        This method calculates the absolute gap. is for positioning blocks.
        Return a Gap instance.
        """
        if self.rotation:
            if self.next:
                if self.rotation == 90:
                    if self.direction:
                        return Gap (0, self.rightCell, 0)
                    return Gap (1, self.rightCell.top.right, 0)
                elif self.rotation == 270:
                    if self.direction:
                        return Gap (0, self.rightCell.top.left, 0)
                    return Gap (1, self.rightCell, 0)
                else:
                    if self.direction:
                        return Gap (1, self.rightCell.top.right, 0)
                    return Gap (0, self.rightCell.top.left, 0)
            return None
        else:
            return self

def msgBox (func, *args, **kwargs):
    """
    This function draw a message box on the screen.
    func - can be any tkinter message box function, with its args and kwargs.
    """
    win = Tk()
    win.withdraw()
    answer = func (*args, **kwargs)
    win.destroy()
    return answer
