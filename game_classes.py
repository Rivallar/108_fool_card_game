import pygame
import pygame.font
import random
import game_settings


class Card:

	"""Represents card properties and images"""

	points = {'6': 6, '7': 7, '8': 8, '9': 0, '10': 10, 'J': 2, 'Q': 3, 'A': 11}		# points to count when a round is over
	suit_names = {'H': 'HEARTS', 'D': 'DIAMONDS', 'S': 'SPADES', 'C': 'CLUBS'}
	
	def __init__(self, value, suit):
		self.value = value
		self.suit = suit
		if self.value:																
			self.points = Card.points[self.value]
			self.name = self.value + self.suit
		else:
			self.name = Card.suit_names[self.suit]							# special queen cards have no value and points
		self.image = pygame.image.load(f'Cards_70x105/{self.name}.bmp')
		self.focus = False													# to focus on a card in a player hand
		
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
		if cards_left == 0 and len(used_deck.cards) == 1:					# all cards in players hand
			return None
		if cards_left >= quantity:
			for _ in range(quantity):
				if reverse:														
					player.hand.append(self.cards.pop())					# return last card (queen) to active player when he cancels
				else:
					player.hand.append(self.cards.pop(0))
		else:																# not enough cards in active deck
			self.reshuffle(player, quantity, used_deck, queen_cards, cards_left, flags)

	def reshuffle(self, player, quantity, used_deck, queen_cards, cards_left, flags):
		
		"""Gives to a player last cards in active deck, removes queen cards from a used deck,
		reshuffles used deck to active deck, gives to a player remaining cards and does penalty for reshuffling"""
		
		player.hand += self.cards
		quantity -= cards_left
		
		print(f'Player {player} takes additional {5 * flags.reshuffle_count} points for reshuffle')		# log
		player.round_points += game_settings.reshuffle_penalty * flags.reshuffle_count		# penalty points for reshuffling
		flags.reshuffle_count += 1
		
		cards_to_shuffle = list(set(used_deck.cards[:-1]))					# remove queen cards
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
		self.hand = []													# players cards
		self.active_flag = False										# players turn flag
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
		
		if len(self.hand) == 1 and self.hand[0].value == 'Q':			# penalty if only queen left
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


class GameFlags:
	
	"""Keeps important settings and information about game-state"""
	
	def __init__(self):
	
		self.loose_points = game_settings.loose_points		# points to loose the game
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
		

class Button:

	"""Manages in-game buttons"""
	
	def __init__(self, screen, msg, width, height, button_color, text_color=(255, 255, 255)):
		
		self.screen = screen
		
		self.screen_rect = self.screen.get_rect()
		
		# dimensions&properties of the button
		self.width, self.height = width, height
		self.button_color = button_color
		self.text_color = text_color
		self.font = pygame.font.SysFont(None, 48)
		
		self.rect = pygame.Rect(0, 0, self.width, self.height)
		self.rect.center = self.screen_rect.center						
		
		self.prep_msg(msg)
		
	def prep_msg(self, msg):
		
		"""Renders text string to image."""
		
		self.msg_image = self.font.render(msg, True, self.text_color, self.button_color)
		self.msg_image_rect = self.msg_image.get_rect()
		self.msg_image_rect.center = self.rect.center
		
	def reposition(self, x_shift, y_shift):
		
		"""To shift a button to correct place"""
		
		self.msg_image_rect.centerx = self.screen_rect.centerx + x_shift
		self.msg_image_rect.centery = self.screen_rect.centery + y_shift
		self.rect.center = self.msg_image_rect.center
		
	def draw_button(self):
		self.screen.fill(self.button_color, self.rect)
		self.screen.blit(self.msg_image, self.msg_image_rect)


class StartScreenProperties:
	
	"""Represents initial screen to fill your name and read hints"""
	
	def __init__(self):
		self.name_focus = False
		self.start_screen_flag = True
		
		self.start_screen_color = (0, 0, 0)
		self.text_color = (240, 240, 0)
		
		self.big_header = '108 FOOL GAME'
		self.header_font = pygame.font.SysFont(None, 66)
		self.hint_font = pygame.font.SysFont(None, 42)
		
		self.username_str = ''
		self.hints = [
			'> Press Q to quit',
			'> Use arrows to navigate through your cards',
			'> Press ENTER button to use the selected card',
			'> SPACE BAR to draw a card or pass your turn']
