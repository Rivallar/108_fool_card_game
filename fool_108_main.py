import pygame
import pygame.font
import random
from game_classes import Player, Card, Deck, Turn, GameFlags, Button, StartScreenProperties
import game_functions as gf
import bot


# --------------------------------------------Start-game preparations-------------------------
pygame.init()
screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption('108_fool')
bg_color = (87, 168, 88)
back_img = pygame.image.load('Cards_70x105/back.bmp')
right_arrow = pygame.image.load('Cards_70x105/arrow.png')

screen_rect = screen.get_rect()

# ------------------------------------------Start screen (to enter username)---------------------------------------

st_screen = StartScreenProperties()

username_field = pygame.Rect(screen_rect.centerx - 50, 175, 350, 50)
username_field_border = pygame.Rect(username_field.left - 2, username_field.top - 2, 354, 54)

yellow_rect = pygame.Rect(screen_rect.centerx + 100, screen_rect.centery - 100, 100, 50)
quit_but = Button(screen, 'Quit', yellow_rect.width - 4, yellow_rect.height - 4, (20, 20, 20), (240, 240, 0))
quit_but.reposition(yellow_rect.centerx - screen_rect.centerx, yellow_rect.centery - screen_rect.centery)

yellow_rect2 = pygame.Rect(screen_rect.centerx - 100, screen_rect.centery - 100, 100, 50)
play_but = Button(screen, 'Play', yellow_rect2.width - 4, yellow_rect2.height - 4, (20, 20, 20), (240, 240, 0))
play_but.reposition(yellow_rect2.centerx - screen_rect.centerx, yellow_rect2.centery - screen_rect.centery)

while st_screen.start_screen_flag:

    gf.start_screen_events(st_screen, quit_but, play_but, username_field)
    gf.draw_start_screen(screen, screen_rect, st_screen, yellow_rect, yellow_rect2, play_but, quit_but)

    if st_screen.name_focus:
        screen.fill(st_screen.text_color, username_field_border)
    screen.fill((75, 75, 75), username_field)

    gf.draw_text_line(st_screen.hint_font, st_screen.username_str, st_screen.text_color, username_field.left + 2,
                      username_field.centery, screen)

    pygame.display.flip()

# --------------------------------------------Game preparations-----------------------------------------------------
# Creating players
players = [Player(st_screen.username_str, bot=False)]
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
        gf.draw_everything(bg_color, screen_rect, screen, players, back_img, used_deck, active_deck, right_arrow, flags,
                           queen_cards, cancel_button, one_card_button)

    elif flags.game_over_flag:
        gf.draw_end_game_screen(bg_color, screen_rect, screen, players, flags, play_again_button, quit_button)
    else:
        gf.new_round(play_deck, active_deck, used_deck, players, queen_cards, flags, turn, screen_rect, screen)
