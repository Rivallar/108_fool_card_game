import pygame
import pygame.font
import random
from game_classes import Player, Card, Deck, Turn, GameFlags, Button, StartScreen
import game_functions as gf
import bot
import ui


# --------------------------------------------Start-game preparations-------------------------
pygame.init()
screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption('108_fool')
bg_color = (87, 168, 88)
back_img = pygame.image.load('Cards_70x105/back.bmp')
right_arrow = pygame.image.load('Cards_70x105/arrow.png')

screen_rect = screen.get_rect()

# ------------------------------------------Start screen (to enter username)---------------------------------------

st_screen = StartScreen(screen_rect, screen)

while st_screen.props.start_screen_flag:

    gf.start_screen_events(st_screen.props, st_screen.quit_but, st_screen.play_but, st_screen.username_field)
    ui.draw_start_screen(screen, screen_rect, st_screen)

    if st_screen.props.name_focus:
        screen.fill(st_screen.props.text_color, st_screen.username_field_border)
    screen.fill((75, 75, 75), st_screen.username_field)

    ui.draw_text_line(st_screen.props.hint_font, st_screen.props.username_str, st_screen.props.text_color, st_screen.username_field.left + 2,
                      st_screen.username_field.centery, screen)

    pygame.display.flip()

# --------------------------------------------Game preparations-----------------------------------------------------
# Creating players
players = [Player(st_screen.props.username_str, bot=False)]
[players.append(Player(name)) for name in Player.bot_names]
random.shuffle(players)  # random order each game

# Creating cards and card decks
play_deck = []  # created once, copied to active_deck each round
for key in Card.points.keys():
    for suit in Card.suit_names.keys():
        play_deck.append(Card(key, suit))

queen_cards = gf.make_queen_cards(screen_rect)  # additional cards for queens cards

active_deck = Deck()
used_deck = Deck()

# Creating button objects
cancel_button = Button(screen, 'Cancel', 200, 50, (255, 0, 0))
one_card_button = Button(screen, 'One!', 100, 50, (255, 0, 0))

play_again_button = Button(screen, 'Play again', 200, 50, (255, 0, 0))
play_again_button.reposition(-70, 50)

quit_button = Button(screen, 'Quit', 100, 60, (255, 0, 0))
quit_button.reposition(150, 50)

flags = GameFlags()

# --------------------------------------------Start-round preparations---------------------------------

gf.reset_decks_and_flags(play_deck, active_deck, used_deck, flags)
gf.fill_players_hands(players, play_deck, active_deck, used_deck, queen_cards, flags)
turn = Turn(players[0])
gf.make_first_turn(turn, players, flags, active_deck, used_deck,
                   queen_cards)  # first turn in each round starts with a random card of first player

# -----------------------------------------------------Game cycle------------------------------------


while True:

    if turn.player.bot and not flags.game_over_flag:
        bot.bot_turn(turn, bg_color, screen_rect, screen, players, back_img, used_deck, active_deck, right_arrow, flags,
                    queen_cards, cancel_button, one_card_button)

    else:
        gf.check_events(turn, used_deck, players, flags, active_deck, queen_cards, cancel_button, one_card_button,
                        quit_button, play_again_button, play_deck)

    if not flags.end_game_flag:
        ui.draw_everything(bg_color, screen_rect, screen, players, back_img, used_deck, active_deck, right_arrow, flags,
                           queen_cards, cancel_button, one_card_button)

    elif flags.game_over_flag:
        ui.draw_end_game_screen(bg_color, screen_rect, screen, players, flags, play_again_button, quit_button)
    else:
        gf.new_round(play_deck, active_deck, used_deck, players, queen_cards, flags, turn, screen_rect, screen)
