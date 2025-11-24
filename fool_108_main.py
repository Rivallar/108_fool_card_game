import pygame.font
from game_classes import Turn
from game_state import GameState
from screens import GameScreen, StartScreen
from event_handlers import start_screen_events, check_events
import game_functions as gf
import bot
import ui

# --------------------------------------------Start-game preparations-------------------------
pygame.init()
screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption('108_fool')
g_screen = GameScreen(screen)
screen_rect = screen.get_rect()

# ------------------------------------------Start screen (to enter username)---------------------------------------

st_screen = StartScreen(screen)

while st_screen.props.start_screen_flag:

    start_screen_events(st_screen.props, st_screen.quit_but, st_screen.play_but, st_screen.username_field)
    ui.draw_start_screen(st_screen)

    if st_screen.props.name_focus:
        screen.fill(st_screen.props.text_color, st_screen.username_field_border)
    screen.fill((75, 75, 75), st_screen.username_field)

    ui.draw_text_line(st_screen.props.hint_font, st_screen.props.username_str, st_screen.props.text_color,
                      st_screen.username_field.left + 2,
                      st_screen.username_field.centery, screen)

    pygame.display.flip()

# --------------------------------------------Game preparations-----------------------------------------------------
game_state = GameState(username=st_screen.props.username_str, screen_rect=screen_rect)
g_screen.upload_card_images(card_names=[card.name for card in game_state.play_deck + game_state.queen_cards])

# --------------------------------------------Start-round preparations---------------------------------

game_state.reset_decks_and_flags()
game_state.fill_players_hands()
turn = Turn(game_state.players[0])
gf.make_first_turn(turn, game_state)  # first turn in each round starts with a random card of first player

# -----------------------------------------------------Game cycle------------------------------------


while True:

    if turn.player.bot and not game_state.flags.game_over_flag:
        bot.bot_turn(turn, game_state, g_screen)

    else:
        check_events(turn, game_state, g_screen)

    if not game_state.flags.end_game_flag:
        ui.draw_everything(game_state, g_screen)

    elif game_state.flags.game_over_flag:
        ui.draw_end_game_screen(game_state.players, game_state.flags, g_screen)
    else:
        gf.new_round(turn, screen_rect, screen, game_state)
