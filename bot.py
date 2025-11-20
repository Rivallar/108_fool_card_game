from time import sleep

import game_settings
from game_functions import end_turn, make_turn
from ui import draw_everything


def bot_choose_queen_card(game_state, most_expensive_card):

    """Helps bot to choose optimal special queen card. Looks for a card with the biggest points value
        and chooses its suit."""

    for card in game_state.queen_cards:
        if card.suit == most_expensive_card.suit:
            chosen_queen_card = card
            game_state.used_deck.cards.append(chosen_queen_card)
    game_state.flags.queen_choose_flag = False
    game_state.flags.first_turn_flag = False


def bot_turn(turn, game_state, game_screen):

    """Main logic for bot turn."""

    turn.player.hand[0].focus = False
    turn.player.one_card_flag = True

    bot_imitates_human(game_state,  # just delay to see each step of a turn
                       game_screen)

    useful_cards, best_card = turn.player.choose_useful_cards(game_state.used_deck.cards[-1])
    if not useful_cards:  # draw a card and check again
        turn.player.take_card(game_state.active_deck, game_state.used_deck, game_state.queen_cards, game_state.flags)

        bot_imitates_human(game_state, game_screen)

        useful_cards, best_card = turn.player.choose_useful_cards(game_state.used_deck.cards[-1])

    if not best_card:  # skip turn
        end_turn(turn, game_state.players, game_state.flags)
    else:  # make turn
        best_card.focus = True

        bot_imitates_human(game_state, game_screen)

        turn.focus_index = turn.player.hand.index(best_card)
        if best_card.value == 'Q':
            bot_uses_queen(turn, game_state, game_screen)
        else:
            make_turn(turn, game_state.players, game_state.flags, game_state.active_deck, game_state.used_deck, game_state.queen_cards)


def bot_uses_queen(turn, game_state, game_screen):

    """To make a turn with a queen card. After using queen need to choose best card suit."""

    most_expensive_card = max(turn.player.hand, key=lambda card: card.points)
    make_turn(turn, game_state.players, game_state.flags, game_state.active_deck, game_state.used_deck, game_state.queen_cards)
    bot_choose_queen_card(game_state, most_expensive_card)
    if not game_state.flags.end_game_flag:
        bot_imitates_human(game_state, game_screen)

    end_turn(turn, game_state.players, game_state.flags)


def bot_imitates_human(game_state, g_screen):

    """Just a delay as if human thinking."""

    draw_everything(game_state, g_screen)
    sleep(game_settings.bot_turn_sleep)
