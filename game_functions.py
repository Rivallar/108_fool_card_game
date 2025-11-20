import pygame
import random
from time import sleep
import game_settings
from ui import draw_end_round_screen


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


def new_round(turn, screen_rect, screen, game_state):
    """Displays round results and resets game for the next round"""

    draw_end_round_screen(screen_rect, screen, game_state.players)
    sleep(10)
    game_state.reset_decks_and_flags()
    game_state.fill_players_hands()
    make_first_turn(turn, game_state)


def make_first_turn(turn, game_state):
    """Resets some game flags, determines first player of new round and performs first turn
    with a random card automatically"""

    for player in game_state.players:
        player.active_flag = False
        player.one_card_flag = False
        player.round_points = 0

    if game_state.flags.first_player_ind + 1 < len(game_state.players):
        game_state.flags.first_player_ind += 1
    else:
        game_state.flags.first_player_ind = 0
    turn.__init__(game_state.players[game_state.flags.first_player_ind])

    first_card_ind = random.randint(0, len(turn.player.hand) - 1)
    first_card = turn.player.hand[first_card_ind]
    turn.player.use_card(first_card_ind, game_state.used_deck)

    if turn.player.bot and first_card.value == 'Q':  # bot chooses best queen card based on the most expensive card
        most_expensive_card = max(turn.player.hand, key=lambda card: card.points)
        bot_choose_queen_card(game_state.queen_cards, most_expensive_card, game_state.used_deck, game_state.flags)
    else:
        check_special(first_card, turn, game_state.players, game_state.flags, game_state.active_deck,
                      game_state.used_deck, game_state.queen_cards) 	 	# check for special card properties
    if not first_card.value == 'Q':
        game_state.flags.first_turn_flag = False
        end_turn(turn, game_state.players, game_state.flags)


def new_game(game_state, turn):

    """Starts new game (not a new round)"""

    for player in game_state.players:
        player.total_points = 0
    random.shuffle(game_state.players)
    game_state.reset_decks_and_flags()
    game_state.fill_players_hands()
    make_first_turn(turn, game_state)



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
