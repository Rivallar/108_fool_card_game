import pygame
import sys
import random
from game_classes import Turn, Card, Deck
from time import sleep
import game_settings
from ui import draw_end_round_screen


# --------------------------------------Start screen management--------------------------------------


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


# ---------------------------------------Start- end-game preparations and results --------------------
# TODO: this function is a duplicate from bot.by due to circular import. Must be removed later.
def bot_choose_queen_card(queen_cards, most_expensive_card, used_deck, flags):

    """Helps bot to choose optimal special queen card. Looks for a card with the biggest points value
        and chooses its suit."""

    for card in queen_cards:
        if card.suit == most_expensive_card.suit:
            chosen_queen_card = card
    used_deck.cards.append(chosen_queen_card)
    flags.queen_choose_flag = False
    flags.first_turn_flag = False


def end_game_calculations(card, turn):
    """Additional bonuses and penalties when ending a round"""

    if card.value == 'Q':  # if a player ends a round with a queen, game points discard
        if card.suit == 'S':
            turn.player.round_points -= game_settings.spades_queen_finish_bonus
        else:
            turn.player.round_points -= game_settings.queen_finish_bonus
    if not turn.player.one_card_flag:  # penalty if a player ends a round and forgets to push one-card hint
        turn.player.round_points += game_settings.one_card_left_penalty


def new_round(play_deck, active_deck, used_deck, players, queen_cards, flags, turn, screen_rect, screen):
    """Displays round results and resets game for the next round"""

    draw_end_round_screen(screen_rect, screen, players)
    sleep(10)
    reset_decks_and_flags(play_deck, active_deck, used_deck, flags)
    fill_players_hands(players, play_deck, active_deck, used_deck, queen_cards, flags)
    make_first_turn(turn, players, flags, active_deck, used_deck, queen_cards)


def make_first_turn(turn, players, flags, active_deck, used_deck, queen_cards):
    """Resets some game flags, determines first player of new round and performs first turn
    with a random card automatically"""

    for player in players:
        player.active_flag = False
        player.one_card_flag = False
        player.round_points = 0

    if flags.first_player_ind + 1 < len(players):
        flags.first_player_ind += 1
    else:
        flags.first_player_ind = 0
    turn.__init__(players[flags.first_player_ind])

    first_card_ind = random.randint(0, len(turn.player.hand) - 1)
    first_card = turn.player.hand[first_card_ind]
    turn.player.use_card(first_card_ind, used_deck)

    if turn.player.bot and first_card.value == 'Q':  # bot chooses best queen card based on the most expensive card
        most_expensive_card = max(turn.player.hand, key=lambda card: card.points)
        bot_choose_queen_card(queen_cards, most_expensive_card, used_deck, flags)
    else:
        check_special(first_card, turn, players, flags, active_deck,
                      used_deck, queen_cards) 	 	# check for special card properties
    if not first_card.value == 'Q':
        flags.first_turn_flag = False
        end_turn(turn, players, flags)

# TODO: delete as it is in GameState class
def fill_players_hands(players, play_deck, active_deck, used_deck, queen_cards, flags):

    """Gives starting hands to players. Checks if the hand is bad. If so, set starting hands again"""

    for player in players:
        player.hand = []
        player.active_flag = False
        active_deck.give_card(player, game_settings.start_hand_size, used_deck, queen_cards, flags)
        need_restart = check_restart(player.hand, player.name)  # check for bad starting hand
        if need_restart:
            break
    if need_restart:
        reset_decks_and_flags(play_deck, active_deck, used_deck, flags)
        fill_players_hands(players, play_deck, active_deck, used_deck, queen_cards, flags)

# TODO: delete as it is in GameState class
def reset_decks_and_flags(play_deck, active_deck, used_deck, flags):

    """Reset decks and game flags"""

    full_deck = play_deck[:]
    random.shuffle(full_deck)
    active_deck.__init__(full_deck)
    used_deck.__init__([])
    flags.reset_flags()

# TODO: delete as it is in GameState class
def check_restart(hand, name):

    """Checks for bad starting hand of a player: when all cards of the same suit(ex. Diamonds)
        and there is no queens"""

    suit_set = set()
    value_set = set()
    for card in hand:
        suit_set.add(card.suit)
        value_set.add(card.value)
    if len(suit_set) == 1 and ('Q' not in value_set):
        if game_settings.DEBUG:
            print(f'{name} has bad starting hand. Round restart')
            print(hand)
        return True


def new_game(players, play_deck, active_deck, used_deck, queen_cards, flags, turn):

    """Starts new game (not a new round)"""

    for player in players:
        player.total_points = 0
    random.shuffle(players)
    reset_decks_and_flags(play_deck, active_deck, used_deck, flags)
    fill_players_hands(players, play_deck, active_deck, used_deck, queen_cards, flags)
    make_first_turn(turn, players, flags, active_deck, used_deck, queen_cards)



# --------------------------------------------Gameplay section------------------------------------------------------

def end_turn(turn, players, flags):

    """Passes turn to next player"""

    if len(turn.player.hand) > 1:
        turn.player.one_card_flag = False  # restricts to show one-card hint if there are more than one card

    if game_settings.DEBUG:
        for player in players:
            print(f'{player.name}: {player.hand}')
        print(f'Current player: {turn.player}')

    turn.player.active_flag = False
    player_ind = players.index(turn.player)  # to determine next player according to turn direction (reverse_flag)

    if not flags.reverse_flag:
        if player_ind < len(players) - 1:
            new_active_player = players[player_ind + 1]
        else:
            new_active_player = players[0]
    else:
        if player_ind == 0:
            new_active_player = players[-1]
        else:
            new_active_player = players[player_ind - 1]
    turn.__init__(new_active_player)

    if game_settings.DEBUG:
        print(f'New player: {turn.player}')


def check_special(card, turn, players, flags, active_deck, used_deck, queen_cards):

    """Main logic of cards interaction. Manages special rules for different cards and end-round actions."""

    if len(turn.player.hand) == 0:
        end_game_calculations(card, turn)
        winner = turn.player.name
        flags.end_game_flag = True
    if card.value == 'A':  													# Aces skip turn of next player
        end_turn(turn, players, flags)
    elif card.value == '7':  												# skip next player turn and take a card
        end_turn(turn, players, flags)
        turn.player.take_card(active_deck, used_deck, queen_cards, flags)
    elif card.value == '6':  												# skip next player turn and take 2 cards
        end_turn(turn, players, flags)
        turn.player.take_card(active_deck, used_deck, queen_cards, flags)
        turn.player.take_card(active_deck, used_deck, queen_cards, flags)
    elif card.value == 'Q':  												# special rules for queens
        flags.queen_choose_flag = True
    elif card.value == '9':													# reverts the direction of a turn
        if flags.reverse_flag:
            flags.reverse_flag = False
        else:
            flags.reverse_flag = True

    if flags.end_game_flag:  # end-round actions
        if game_settings.DEBUG:
            print(f'{winner} wins this round!')
        for player in players:
            round_points = player.count_round_points()
            if game_settings.DEBUG:
                print(f'{player} gets {round_points} points')
            player.total_points += round_points

        loose_value = flags.loose_points
        for player in players:
            if game_settings.DEBUG:
                print(f'{player} have total {player.total_points} points')
            if player.total_points >= loose_value:
                flags.game_over_flag = True
                flags.losers.append(player)
                if player.total_points > flags.loose_points:
                    flags.loose_points = player.total_points  # change loose points to play again till new value
                if game_settings.DEBUG:
                    print(f'{player} looses with total {player.total_points} points')


def focus_change(turn, new_focus):

    """Switch focus to another card"""

    turn.player.hand[turn.focus_index].focus = False
    turn.player.hand[new_focus].focus = True
    turn.focus_index = new_focus


def switch_focus(key, turn):

    """To navigate trough cards in hand via arrows"""

    if key == pygame.K_RIGHT:
        new_focus = turn.focus_index + 1
        if new_focus < len(turn.player.hand):
            focus_change(turn, new_focus)

    if key == pygame.K_LEFT:
        new_focus = turn.focus_index - 1
        if new_focus >= 0:
            focus_change(turn, new_focus)


def make_turn(turn, players, flags, active_deck, used_deck, queen_cards):

    """Performs a player turn with different checks"""

    counter = len(turn.player.hand)  # remember length to check if card was actually used
    card = turn.player.hand[turn.focus_index]  # remember card to check for special properties
    turn.player.use_card(turn.focus_index, used_deck)
    if len(turn.player.hand) != counter:
        check_special(card, turn, players, flags, active_deck, used_deck, queen_cards)
        if not flags.queen_choose_flag:
            end_turn(turn, players, flags)


def queen_turn(turn, used_deck, players, flags, queen_cards, cancel_button, mouse_x, mouse_y):

    """Adds a chosen special queen card to the used deck or returns queen card to a hand of an active player."""

    if cancel_button.rect.collidepoint(mouse_x, mouse_y) and not flags.first_turn_flag:
        flags.queen_choose_flag = False
        used_deck.give_card(turn.player, 1, used_deck, queen_cards, flags, reverse=True)
        turn.reset_focus()
    for card in queen_cards:
        if card.rect.collidepoint(mouse_x, mouse_y):
            used_deck.cards.append(card)
            flags.queen_choose_flag = False
            flags.first_turn_flag = False
            end_turn(turn, players, flags)


def check_events(turn, used_deck, players, flags, active_deck, queen_cards,
                 game_screen, play_deck):

    """Main event function. Looks for players keyboard/mouse actions"""

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                sys.exit()
        if flags.queen_choose_flag:  # choose special queen card
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                queen_turn(turn, used_deck, players, flags, queen_cards,
                           game_screen.cancel_button, mouse_x, mouse_y)

        if flags.game_over_flag:  # when game is over
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if game_screen.quit_button.rect.collidepoint(mouse_x, mouse_y):
                    sys.exit()
                if game_screen.play_again_button.rect.collidepoint(mouse_x, mouse_y):
                    new_game(players, play_deck, active_deck, used_deck,
                             queen_cards, flags, turn)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # hotkey to play
                    new_game(players, play_deck, active_deck, used_deck,
                             queen_cards, flags, turn)
        else:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RIGHT, pygame.K_LEFT):  # navigate through cards in hand
                    switch_focus(event.key, turn)

                elif event.key == pygame.K_o:  # hotkey for one-card button
                    if len(turn.player.hand) == 2 and not turn.player.one_card_flag:
                        turn.player.one_card_flag = True

                elif event.key == pygame.K_RETURN:  # use a card in focus card
                    make_turn(turn, players, flags, active_deck,
                              used_deck, queen_cards)

                elif event.key == pygame.K_SPACE:  # draw a card or end a turn
                    if turn.card_taken_flag:
                        end_turn(turn, players, flags)
                    else:
                        turn.player.take_card(active_deck, used_deck,
                                              queen_cards, flags)
                        turn.card_taken_flag = True  # you can draw 1 card from deck once per turn
                        turn.player.one_card_flag = False
                        focus_change(turn, len(turn.player.hand) - 1)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if game_screen.one_card_button.rect.collidepoint(mouse_x, mouse_y):  # push one-card button
                    if len(turn.player.hand) == 2 and not turn.player.one_card_flag:
                        turn.player.one_card_flag = True
