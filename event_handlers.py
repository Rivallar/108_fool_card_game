
"""
Functions to handle events during the game and while displaying menu screen
"""
import pygame
import sys

import game_functions as gf


def start_screen_events(screen_props, quit_but, play_but, username_field):
    """Events of start screen. Manage buttons usage and username input. """

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q and not screen_props.name_focus:
                sys.exit()
            if event.key == pygame.K_RETURN:  # start game after username is entered
                check_name_and_start(screen_props)
            if screen_props.name_focus:
                if event.key == pygame.K_BACKSPACE:  # erase symbol
                    screen_props.username_str = screen_props.username_str[:-1]
                elif event.key == pygame.K_RETURN:
                    check_name_and_start(screen_props)
                else:
                    screen_props.username_str += event.unicode  # add symbol
        if event.type == pygame.MOUSEBUTTONDOWN:
            if quit_but.rect.collidepoint(event.pos):
                sys.exit()
            elif play_but.rect.collidepoint(event.pos):
                check_name_and_start(screen_props)
            elif username_field.collidepoint(event.pos):
                screen_props.name_focus = True
            else:
                screen_props.name_focus = False


def check_name_and_start(st_screen):
    """Starts the game if username is entered."""

    if st_screen.username_str:
        st_screen.start_screen_flag = False


def check_events(turn, game_state, game_screen):

    """Main event function. Looks for players keyboard/mouse actions"""

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                sys.exit()
        if game_state.flags.queen_choose_flag:  # choose special queen card
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                gf.queen_turn(turn, game_state.used_deck, game_state.players, game_state.flags, game_state.queen_cards,
                           game_screen.cancel_button, mouse_x, mouse_y)

        if game_state.flags.game_over_flag:  # when game is over
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if game_screen.quit_button.rect.collidepoint(mouse_x, mouse_y):
                    sys.exit()
                if game_screen.play_again_button.rect.collidepoint(mouse_x, mouse_y):
                    gf.new_game(game_state, turn)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # hotkey to play
                    gf.new_game(game_state, turn)
        else:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RIGHT, pygame.K_LEFT):  # navigate through cards in hand
                    gf.switch_focus(event.key, turn)

                elif event.key == pygame.K_o:  # hotkey for one-card button
                    if len(turn.player.hand) == 2 and not turn.player.one_card_flag:
                        turn.player.one_card_flag = True

                elif event.key == pygame.K_RETURN:  # use a card in focus card
                    gf.make_turn(turn, game_state.players, game_state.flags, game_state.active_deck,
                              game_state.used_deck, game_state.queen_cards)

                elif event.key == pygame.K_SPACE:  # draw a card or end a turn
                    if turn.card_taken_flag:
                        gf.end_turn(turn, game_state.players, game_state.flags)
                    else:
                        turn.player.take_card(game_state.active_deck, game_state.used_deck,
                                              game_state.queen_cards, game_state.flags)
                        turn.card_taken_flag = True  # you can draw 1 card from deck once per turn
                        turn.player.one_card_flag = False
                        gf.focus_change(turn, len(turn.player.hand) - 1)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if game_screen.one_card_button.rect.collidepoint(mouse_x, mouse_y):  # push one-card button
                    if len(turn.player.hand) == 2 and not turn.player.one_card_flag:
                        turn.player.one_card_flag = True