"""
Keeps classes with visual data like colors, fonts, elements sizes and positions on a screen
"""
import pygame
import pygame.font


class Button:
    """Manages in-game buttons"""

    def __init__(self, screen, msg, width, height, button_color, text_color=(255, 255, 255),
                 shift: tuple[int, int] = None):
        self.screen = screen

        self.screen_rect = self.screen.get_rect()

        # dimensions&properties of the button
        self.width, self.height = width, height
        self.button_color = button_color
        self.text_color = text_color
        self.font = pygame.font.SysFont(None, 48)

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center

        self.prep_msg(msg)

        if shift and len(shift) == 2:
            self.reposition(*shift)

    def prep_msg(self, msg):
        """Renders text string to image."""

        self.msg_image = self.font.render(msg, True, self.text_color, self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def reposition(self, x_shift, y_shift):
        """To shift a button to correct place"""

        self.msg_image_rect.centerx = self.screen_rect.centerx + x_shift
        self.msg_image_rect.centery = self.screen_rect.centery + y_shift
        self.rect.center = self.msg_image_rect.center

    def draw_button(self):
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)


class StartScreenProperties:
    """Represents initial screen to fill your name and read hints"""

    def __init__(self):
        self.name_focus = False
        self.start_screen_flag = True

        self.start_screen_color = (0, 0, 0)
        self.text_color = (240, 240, 0)
        self.button_color = (20, 20, 20)

        self.big_header = '108 FOOL GAME'
        self.header_font = pygame.font.SysFont(None, 66)
        self.hint_font = pygame.font.SysFont(None, 42)

        self.username_str = ''
        self.hints = [
            '> Press Q to quit',
            '> Use arrows to navigate through your cards',
            '> Press ENTER button to use the selected card',
            '> SPACE BAR to draw a card or pass your turn']


class StartScreen:

    def __init__(self, screen):
        self.props = StartScreenProperties()
        self.screen = screen
        self.screen_rect = self.screen.get_rect()
        self.username_field = pygame.Rect(self.screen_rect.centerx - 50, 175, 350, 50)
        self.username_field_border = pygame.Rect(self.username_field.left - 2, self.username_field.top - 2, 354, 54)
        self.quit_but_border = pygame.Rect(self.screen_rect.centerx + 100, self.screen_rect.centery - 100, 100, 50)
        self.quit_but = Button(screen=screen,
                               msg='Quit',
                               width=self.quit_but_border.width - 4,
                               height=self.quit_but_border.height - 4,
                               button_color=self.props.button_color,
                               text_color=self.props.text_color,
                               shift=self.get_shift(self.screen_rect, self.quit_but_border)
                               )

        self.play_but_border = pygame.Rect(self.screen_rect.centerx - 100, self.screen_rect.centery - 100, 100, 50)
        self.play_but = Button(screen=screen,
                               msg='Play',
                               width=self.play_but_border.width - 4,
                               height=self.play_but_border.height - 4,
                               button_color=self.props.button_color,
                               text_color=self.props.text_color,
                               shift=self.get_shift(self.screen_rect, self.play_but_border)
                               )

    @staticmethod
    def get_shift(rect, button_border: pygame.Rect) -> tuple[int, int]:
        shift_x = button_border.centerx - rect.centerx
        shift_y = button_border.centery - rect.centery
        return shift_x, shift_y


class GameScreen:
    def __init__(self, screen):
        self.screen = screen
        self.screen_rect = self.screen.get_rect()
        self.bg_color = (87, 168, 88)
        self.back_img = pygame.image.load('Cards_70x105/back.bmp')
        self.right_arrow = pygame.image.load('Cards_70x105/arrow.png')
        self.cancel_button = Button(screen, 'Cancel', 200, 50, (255, 0, 0))
        self.one_card_button = Button(screen, 'One!', 100, 50, (255, 0, 0))
        self.play_again_button = Button(screen, 'Play again', 200, 50, (255, 0, 0), shift=(-70, 50))
        self.quit_button = Button(screen, 'Quit', 100, 60, (255, 0, 0), shift=(150, 50))