import pygame
import pygame.font
import random
import game_settings


class Card:
    """Represents card properties and images"""

    points = {'6': 6, '7': 7, '8': 8, '9': 0, '10': 10, 'J': 2, 'Q': 3, 'A': 11}  # points to count when a round is over
    suit_names = {'H': 'HEARTS', 'D': 'DIAMONDS', 'S': 'SPADES', 'C': 'CLUBS'}

    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
        if self.value:
            self.points = Card.points[self.value]
            self.name = self.value + self.suit
        else:
            self.name = Card.suit_names[self.suit]  # special queen cards have no value and points
        self.image = pygame.image.load(f'Cards_70x105/{self.name}.bmp')
        self.focus = False  # to focus on a card in a player hand

    def __repr__(self):
        return self.name


class Deck:
    """Keeps cards, gives cards to players, manages reshuffling when active deck is empty"""

    def __init__(self, cards=None):
        if cards is None:
            cards = []
        self.cards = cards

    def give_card(self, player, quantity, used_deck, queen_cards, flags, reverse=False):

        """Gives cards from active deck to players hands. Checks if there are enough cards in the deck."""

        cards_left = len(self.cards)
        if cards_left == 0 and len(used_deck.cards) == 1:  # all cards in players hand
            return None
        if cards_left >= quantity:
            for _ in range(quantity):
                if reverse:
                    player.hand.append(self.cards.pop())  # return last card (queen) to active player when he cancels
                else:
                    player.hand.append(self.cards.pop(0))
        else:  # not enough cards in active deck
            self.reshuffle(player, quantity, used_deck, queen_cards, cards_left, flags)

    def reshuffle(self, player, quantity, used_deck, queen_cards, cards_left, flags):

        """Gives to a player last cards in active deck, removes queen cards from a used deck,
        reshuffles used deck to active deck, gives to a player remaining cards and does penalty for reshuffling"""

        player.hand += self.cards
        quantity -= cards_left

        print(f'Player {player} takes additional {5 * flags.reshuffle_count} points for reshuffle')  # log
        player.round_points += game_settings.reshuffle_penalty * flags.reshuffle_count  # penalty points for reshuffling
        flags.reshuffle_count += 1

        cards_to_shuffle = list(set(used_deck.cards[:-1]))  # remove queen cards
        for card in queen_cards:
            if card in cards_to_shuffle:
                cards_to_shuffle.remove(card)

        self.cards = cards_to_shuffle
        random.shuffle(self.cards)

        used_deck.cards = used_deck.cards[-1:]
        self.give_card(player, quantity, used_deck, queen_cards, flags)


class Player:
    """Represents bots and real players. Keeps players cards, manages bots and players turns, counts points
    in the end of a round"""

    bot_names = ['BOT1', 'BOT2']

    def __init__(self, name, bot=True):
        self.name = name
        self.bot = bot
        self.hand = []  # players cards
        self.active_flag = False  # players turn flag
        self.one_card_flag = False

        self.total_points = 0
        self.round_points = 0

        # Drawing name
        self.text_color = (240, 240, 0)
        self.back_color = (0, 100, 175)
        self.font = pygame.font.SysFont(None, 36)
        self.name_img = self.font.render(self.name, True, self.text_color, self.back_color)

    def choose_useful_cards(self, used_deck_last_card):

        """To determine best card for bot turn"""

        useful_cards = set()
        for card in self.hand:
            if card.value == 'Q':
                useful_cards.add(card)
            elif card.value == used_deck_last_card.value or card.suit == used_deck_last_card.suit:
                useful_cards.add(card)
        best_card = self.choose_best_card(useful_cards)
        return useful_cards, best_card

    def choose_best_card(self, useful_cards):

        """To determine best card (max points) for bot turn"""

        if useful_cards:
            best_card = max(useful_cards, key=lambda card: card.points)
            return best_card

    def count_round_points(self):

        """Counting end-round points"""

        if len(self.hand) == 1 and self.hand[0].value == 'Q':  # penalty if only queen left
            if self.hand[0].suit == 'S':
                self.round_points += game_settings.spades_queen_left_penalty
            else:
                self.round_points += game_settings.queen_left_penalty
        else:
            for card in self.hand:
                self.round_points += card.points
        return self.round_points

    def __repr__(self):
        return self.name

    def use_card(self, card_id, used_deck):

        """Make turn if given card can be used"""

        if not used_deck.cards:
            used_deck.cards.append(self.hand.pop(card_id))
        elif self.hand[card_id].suit == used_deck.cards[-1].suit or \
                self.hand[card_id].value == used_deck.cards[-1].value or self.hand[card_id].value == 'Q':
            used_deck.cards.append(self.hand.pop(card_id))

    def take_card(self, active_deck, used_deck, queen_cards, flags):

        """Take a card from a deck if there are no playable cards in a hand"""

        active_deck.give_card(self, 1, used_deck, queen_cards, flags)


class Turn:
    """Returns an active player to start-turn state: sorted cards, first card in focus"""

    def __init__(self, player):
        self.player = player
        self.player.hand.sort(key=Turn.sort_hand)
        self.player.active_flag = True
        self.reset_focus()

    def reset_focus(self):
        """Only first card in focus"""

        self.player.hand[0].focus = True
        for card in self.player.hand[1:]:
            card.focus = False
        self.card_taken_flag = False
        self.focus_index = 0

    @staticmethod
    def sort_hand(card):
        return card.suit, card.points


