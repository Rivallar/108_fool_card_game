from time import sleep

import game_settings
from game_functions import end_turn, make_turn
from ui import draw_everything


def bot_choose_queen_card(queen_cards, most_expensive_card, used_deck, flags):

    """Helps bot to choose optimal special queen card. Looks for a card with the biggest points value
        and chooses its suit."""

    for card in queen_cards:
        if card.suit == most_expensive_card.suit:
            chosen_queen_card = card
    used_deck.cards.append(chosen_queen_card)
    flags.queen_choose_flag = False
    flags.first_turn_flag = False


def bot_turn(turn, bg_color, screen_rect, screen, players, back_img,
             used_deck, active_deck, right_arrow, flags, queen_cards,
             cancel_button, one_card_button):

    """Main logic for bot turn."""

    turn.player.hand[0].focus = False
    turn.player.one_card_flag = True

    bot_imitates_human(bg_color, screen_rect, screen, players, back_img,  # just delay to see each step of a turn
                       used_deck, active_deck, right_arrow, flags, queen_cards,
                       cancel_button, one_card_button)

    useful_cards, best_card = turn.player.choose_useful_cards(used_deck.cards[-1])
    if not useful_cards:  # draw a card and check again
        turn.player.take_card(active_deck, used_deck, queen_cards, flags)

        bot_imitates_human(bg_color, screen_rect, screen, players,
                           back_img, used_deck, active_deck, right_arrow, flags,
                           queen_cards, cancel_button, one_card_button)

        useful_cards, best_card = turn.player.choose_useful_cards(used_deck.cards[-1])

    if not best_card:  # skip turn
        end_turn(turn, players, flags)
    else:  # make turn
        best_card.focus = True

        bot_imitates_human(bg_color, screen_rect, screen, players, back_img,
                           used_deck, active_deck, right_arrow, flags, queen_cards,
                           cancel_button, one_card_button)

        turn.focus_index = turn.player.hand.index(best_card)
        if best_card.value == 'Q':
            bot_uses_queen(turn, bg_color, screen_rect, screen, players,
                           back_img, used_deck, active_deck, right_arrow, flags,
                           queen_cards, cancel_button, one_card_button)
        else:
            make_turn(turn, players, flags, active_deck, used_deck, queen_cards)


def bot_uses_queen(turn, bg_color, screen_rect, screen, players, back_img,
                   used_deck, active_deck, right_arrow, flags, queen_cards,
                   cancel_button, one_card_button):

    """To make a turn with a queen card. After using queen need to choose best card suit."""

    most_expensive_card = max(turn.player.hand, key=lambda card: card.points)
    make_turn(turn, players, flags, active_deck, used_deck, queen_cards)
    bot_choose_queen_card(queen_cards, most_expensive_card, used_deck, flags)
    if not flags.end_game_flag:
        bot_imitates_human(bg_color, screen_rect, screen, players, back_img,
                           used_deck, active_deck, right_arrow, flags, queen_cards,
                           cancel_button, one_card_button)

    end_turn(turn, players, flags)


def bot_imitates_human(bg_color, screen_rect, screen, players, back_img,
                       used_deck, active_deck, right_arrow, flags, queen_cards,
                       cancel_button, one_card_button):

    """Just a delay as if human thinking."""

    draw_everything(bg_color, screen_rect, screen, players, back_img,
                    used_deck, active_deck, right_arrow, flags, queen_cards,
                    cancel_button, one_card_button)
    sleep(game_settings.bot_turn_sleep)