import pygame.font
import random

import game_settings
from game_classes import Card, Deck, Player


class GameFlags:
    """Keeps important settings and information about game-state"""

    def __init__(self):
        self.loose_points = game_settings.loose_points  # points to loose the game
        self.first_player_ind = 0

        self.text_color = (240, 240, 0)
        self.font = pygame.font.SysFont(None, 36)
        self.reset_flags()

    def reset_flags(self):
        self.game_over_flag = False
        self.end_game_flag = False
        self.reverse_flag = False
        self.queen_choose_flag = False
        self.first_turn_flag = True
        self.losers = []

        self.reshuffle_count = 1

        self.prep_loose_score()

    def prep_loose_score(self):
        """To show loose-points on the screen during the game"""

        self.loose_string = f'Loose points: {self.loose_points}'
        self.loose_score_img = self.font.render(self.loose_string, True, self.text_color)
        self.loose_score_rect = self.loose_score_img.get_rect()


class GameState:

    """A class to keep track of a state of the game. Like cards in decks and players hands, game flags etc.
    Also provides interface to change this state."""

    def __init__(self, username, screen_rect):
        self.flags = GameFlags()
        self.players = self.make_players(username)
        self.play_deck = self.make_play_deck()
        self.queen_cards = self.make_queen_cards(screen_rect)
        self.active_deck = Deck()
        self.used_deck = Deck()

    @staticmethod
    def make_players(username: str) -> list[Player]:
        """Creates a list of players including bots in random order."""
        players = [Player(username, bot=False)]
        players.extend([Player(name) for name in Player.bot_names])
        random.shuffle(players)     # random order each game
        return players

    @staticmethod
    def make_play_deck() -> list[Card]:
        """Initialises all regular cards for the game"""
        play_deck = []  # created once, copied to active_deck each round
        for key in Card.points.keys():
            for suit in Card.suit_names.keys():
                play_deck.append(Card(key, suit))
        return play_deck

    @staticmethod
    def make_queen_cards(screen_rect) -> list[Card]:
        """Creates special queen cards to choose new suit (Hearts/Diamonds/Clubs/Spades)
            and places them in the center of the screen"""

        queen_cards = []
        for ind, suit in enumerate(Card.suit_names.keys()):
            card = Card('', suit)  # no value is ok
            card.rect = card.image.get_rect()
            card.rect.bottom = screen_rect.centery - 120
            card.rect.left = screen_rect.centerx - 200 + 100 * ind
            queen_cards.append(card)

        return queen_cards

    def reset_decks_and_flags(self):

        """Reset decks and game flags"""

        full_deck = self.play_deck[:]
        random.shuffle(full_deck)
        self.active_deck = Deck(full_deck)
        self.used_deck = Deck()
        self.flags.reset_flags()

    def fill_players_hands(self):

        """Gives starting hands to players. Checks if the hand is bad. If so, set starting hands again"""

        need_restart = False
        for player in self.players:
            player.hand = []
            player.active_flag = False
            self.active_deck.give_card(player, game_settings.start_hand_size, self.used_deck,
                                       self.queen_cards, self.flags)
            need_restart = self.check_restart(player.hand, player.name)  # check for bad starting hand
            if need_restart:
                break
        if need_restart:
            self.reset_decks_and_flags()
            self.fill_players_hands()

    @staticmethod
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