import pygame
import sys
import random
from game_classes import Turn, Card, Deck
from time import sleep

#--------------------------------------Start screen management--------------------------------------

def start_screen_events(st_screen, quit_but, play_but, username_field):
	
	'''Events of start screen. Manages buttons usage and username input. '''
	
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_q and not st_screen.name_focus:
				sys.exit()
			if event.key == pygame.K_RETURN:							#start game after username is entered
				check_name_and_start(st_screen)
			if st_screen.name_focus:
				if event.key == pygame.K_BACKSPACE:						#erase symbol
					st_screen.username_str = st_screen.username_str[:-1]
				elif event.key == pygame.K_RETURN:
					check_name_and_start(st_screen)
				else:
					st_screen.username_str += event.unicode				#add symbol
		if event.type == pygame.MOUSEBUTTONDOWN:
			if quit_but.rect.collidepoint(event.pos):
				sys.exit()
			elif play_but.rect.collidepoint(event.pos):
				check_name_and_start(st_screen)
			elif username_field.collidepoint(event.pos):
				st_screen.name_focus = True
			else:
				st_screen.name_focus =  False

def check_name_and_start(st_screen):
	
	'''Starts the game if username is entered.'''
	
	if st_screen.username_str:
		st_screen.start_screen_flag = False
		

#---------------------------------------Start- end-game preparations and results --------------------
    
def make_queen_cards(screen_rect):
	
	'''Creates special queen cards to choose new suit (Hearts/Diamonds/Clubs/Spades)
		and places them in the center of the screen'''
		
	queen_cards = []
	for ind, suit in enumerate(Card.suit_names.keys()):
		card = Card('', suit)											#no value is ok
		card.rect = card.image.get_rect()
		card.rect.bottom = screen_rect.centery - 120
		card.rect.left = screen_rect.centerx - 200 + 100 * ind
		queen_cards.append(card)
		
	return queen_cards

def end_game_calculations(card, turn):
	
	''' Additional bonuses and penalties when ending a round'''
	
	if card.value == 'Q':												# if a player ends a round with a queen, game points discard
		if card.suit == 'S':
			turn.player.round_points -= 40
		else:
			turn.player.round_points -= 20
	if not turn.player.one_card_flag:									# penalty if a player ends a round and forgets to push one-card hint
		turn.player.round_points += 20
		
def new_round(play_deck, active_deck, used_deck, players, queen_cards, flags, turn, screen_rect, screen):
	
	''' Displays round results and resets game for the next round '''
	
	draw_end_round_screen(screen_rect, screen, players)
	sleep(10)
	reset_decks_and_flags(play_deck, active_deck, used_deck, flags)
	fill_players_hands(players, play_deck, active_deck, used_deck, queen_cards, flags)
	make_first_turn(turn, players, flags, active_deck, used_deck, queen_cards)


	
def make_first_turn(turn, players, flags, active_deck, used_deck, queen_cards):
	
	'''Resets some game flags, determines first player of new round and performs first turn 
		with a random card automatically'''
	
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
	
	if turn.player.bot and first_card.value == 'Q':						# bot chooses best queen card based on the most expensive card in a hand
		most_expensive_card = max(turn.player.hand, key=lambda card: card.points)
		bot_choose_queen_card(queen_cards, most_expensive_card, used_deck, flags)
	else:	
		check_special(first_card, turn, players, flags, active_deck, used_deck, queen_cards)	#check for special card properties
	if not first_card.value == 'Q':
		flags.first_turn_flag = False
		end_turn(turn, players, flags)


def fill_players_hands(players, play_deck, active_deck, used_deck, queen_cards, flags):
	
	'''Gives starting hands to players. Checks if the hand is bad. If so, set starting hands again'''
	
	for player in players:
		player.hand = []
		player.active_flag = False
		active_deck.give_card(player, 5, used_deck, queen_cards, flags)	#quantity should be taken from settings!!!
		need_restart = check_restart(player.hand, player.name)			# check for bad starting hand
		if need_restart:
			break
	if need_restart:
		reset_decks_and_flags(play_deck, active_deck, used_deck, flags)
		fill_players_hands(players, play_deck, active_deck, used_deck, queen_cards, flags)
			
		

def reset_decks_and_flags(play_deck, active_deck, used_deck, flags):
	
	'''Reset decks and game flags'''
	
	full_deck = play_deck[:]        
	random.shuffle(full_deck)
	active_deck.__init__(full_deck)
	used_deck.__init__([])
	flags.reset_flags()
		
		
def check_restart(hand, name):
	
	'''Checks for bad starting hand of a player: when all cards of the same suit(ex. Diamonds)
		and there is no queens'''
		
	suit_set = set()
	value_set = set()
	for card in hand:
		suit_set.add(card.suit)
		value_set.add(card.value)
	if len(suit_set) == 1 and ('Q' not in value_set):
		print(f'{name} has bad starting hand. Round restart')			#log
		print(hand)														#log
		return True

def new_game(players, play_deck, active_deck, used_deck, queen_cards, flags, turn):
	
	'''Starts new game (not a new round)'''
	
	for player in players:
		player.total_points = 0
	random.shuffle(players)
	reset_decks_and_flags(play_deck, active_deck, used_deck, flags)
	fill_players_hands(players, play_deck, active_deck, used_deck, queen_cards, flags)
	make_first_turn(turn, players, flags, active_deck, used_deck, queen_cards)
	
#---------------------------------- Draw functions ----------------------------------------------

def draw_start_screen(screen, screen_rect, st_screen, yellow_rect,
		yellow_rect2, play_but, quit_but):
			
	'''Draws everything for start screen.'''
	
	screen.fill(st_screen.start_screen_color)
	screen.fill(st_screen.text_color, yellow_rect)						#button contours
	screen.fill(st_screen.text_color, yellow_rect2)
	play_but.draw_button()
	quit_but.draw_button()
	draw_text_line(st_screen.header_font, st_screen.big_header,
		st_screen.text_color, screen_rect.centerx - 150, 70, screen)
	draw_text_line(st_screen.hint_font, 'Enter your name: ',
		st_screen.text_color, screen_rect.centerx - 300, 200, screen)
	for ind, hint in enumerate(st_screen.hints):						#hints to play a game
		draw_text_line(st_screen.hint_font, hint, st_screen.text_color,
			screen_rect.left + 50, screen_rect.bottom - 50 - ind * 50, screen)
	
def draw_used_deck(deck, screen_rect, screen):
	
	''' Displays 2 latest cards of the used deck'''
	
	bot_rect = deck.cards[-1].image.get_rect()
	bot_rect.centerx = screen_rect.centerx - 100
	bot_rect.centery = screen_rect.centery + 5
	
	top_rect = deck.cards[-1].image.get_rect()
	top_rect.centerx = screen_rect.centerx - 85
	top_rect.centery = screen_rect.centery
	
	if len(deck.cards) > 1:
		if len(deck.cards) % 2 == 0:
			bot_rect, top_rect = top_rect, bot_rect						# a bit of alternative animation
		screen.blit(deck.cards[-2].image, bot_rect)
	screen.blit(deck.cards[-1].image, top_rect)
	
def draw_active_deck(back_img, screen_rect, screen, deck):
	
	'''Displays a block of unused cards'''
	
	back_rect = back_img.get_rect()
	back_rect.centerx = screen_rect.centerx + 20
	back_rect.centery = screen_rect.centery
	if len(deck.cards) < 4:												# changes image when the deck is almost dry
		for i in range(len(deck.cards)):
			screen.blit(back_img, ((back_rect.centerx + i * 13), 
							screen_rect.centery - 52 - i * 5))
	else:
		screen.blit(back_img, back_rect)
	
def draw_active_hand(screen_rect, screen, player, one_card_button):
	
	'''Draws the cards of an active player and one-card button'''
	
	count = len(player.hand)
	hand_width_px = 70 + 20 * (count - 1)
	start_px = int(screen_rect.centerx - hand_width_px / 2)
	image_rect = player.hand[0].image.get_rect()
	for i in range(count):
		image_rect.left = start_px + i * 20
		image_rect.bottom = screen_rect.bottom
		if player.hand[i].focus:										# focused card is a bit higher
			image_rect.bottom -= 25
		screen.blit(player.hand[i].image, image_rect)
	if count == 2 and not player.one_card_flag:							# a button to say that one card left appears when a player has 2 cards
		draw_one_card_button(one_card_button, screen_rect, image_rect)
		
		
def draw_one_card_button(one_card_button, screen_rect, image_rect):
	
	'''Draws one-card button. Its position depends on how many cards left (1 or 2)'''
	
	one_card_button.msg_image_rect.left = image_rect.right + 15
	one_card_button.msg_image_rect.bottom = screen_rect.bottom - 5
	one_card_button.rect = one_card_button.msg_image_rect
	one_card_button.draw_button()
		
def draw_name(screen_rect, screen, player, degree):
	
	'''Draws players name'''
	
	rot_name_image = pygame.transform.rotate(player.name_img, degree)
	name_img_rect = rot_name_image.get_rect()
	name_img_rect.centery = screen_rect.centery
	if degree == -90:													# rotation for left- and right-side players
		name_img_rect.left = 0
	elif degree == 90:
		name_img_rect.right = screen_rect.right
	screen.blit(rot_name_image, name_img_rect)
		
def draw_other_hands(screen_rect, screen, players_order, back_img):
	
	'''Draws cards of other (non-active) players.'''
	
	for ind, player in enumerate(players_order):
		count = len(player.hand)
		hand_width_px = 70 + 20 * (count - 1)
		
		start_px = int(screen_rect.centery - hand_width_px / 2)			# to place whole cardset left/right-center
		other_hand_image = pygame.transform.rotate(back_img, 90)
		other_hand_image_rect = other_hand_image.get_rect()
		for i in range(count):
			other_hand_image_rect.top = int(start_px + i * 20)			# each card stacked one on anothe with a little shift
			if ind == 1:
				other_hand_image_rect.right = screen_rect.right
				degree = 90
			else:
				other_hand_image_rect.left = 0
				degree = -90
			screen.blit(other_hand_image, other_hand_image_rect)
		draw_name(screen_rect, screen, player, degree)
		if player.one_card_flag:
			draw_hint(other_hand_image_rect, degree, screen)

def draw_hint(other_hand_image_rect, degree, screen):
	
	'''A dialog cloud with word "One!" to indicate that player has only one card left'''
	
	hint = pygame.image.load('Cards_70x105/ONE.png')
	hint_img = pygame.transform.rotate(hint, degree)
	hint_img_rect = hint_img.get_rect()
	
	if degree == -90:													# draw for right- or left-side player
		hint_img_rect.left = other_hand_image_rect.right
		hint_img_rect.centery = other_hand_image_rect.centery + 25
	else:
		hint_img_rect.right = other_hand_image_rect.left
		hint_img_rect.centery = other_hand_image_rect.centery - 25
	screen.blit(hint_img, hint_img_rect)
	
def draw_hands(screen_rect, screen, players, back_img, one_card_button):
	
	''' Determines active player, right- and left-side players and 
		delegates drawing to apropriate functions'''
		
	act_ind = None														# index of an active player
	for ind, player in enumerate(players):
		if player.active_flag:
			act_ind = ind
			draw_active_hand(screen_rect, screen, player, one_card_button)
	players_order = players[act_ind + 1:] + players[:act_ind]
	draw_other_hands(screen_rect, screen, players_order, back_img)
	
def draw_arrow(right_arrow, flags, screen_rect, screen):
	
	''' Draws an arrow to show which player goes next'''
	
	if not flags.reverse_flag:
		right_arrow = pygame.transform.rotate(right_arrow, 180)
	arrow_rect = right_arrow.get_rect()
	arrow_rect.centerx = screen_rect.centerx
	arrow_rect.bottom = screen_rect.bottom - 140
	screen.blit(right_arrow, arrow_rect)

def draw_queen_cards(queen_cards, screen_rect, screen):
	
	'''Draws shaded screen with special cards to choose when a player uses queen card'''
	
	draw_shade_surf(screen_rect, screen)
	for card in queen_cards:
		screen.blit(card.image, card.rect)
		
def draw_shade_surf(screen_rect, screen):
	
	'''Draws special surface during queen turn'''
	
	shade_surface = pygame.Surface([1200, 800])
	shade_color = (200, 200, 200)
	shade_surface.fill(shade_color)
	shade_surface.set_alpha(120)
	screen.blit(shade_surface, screen_rect)
		
def draw_loose_score(screen_rect, screen, flags):
	
	'''A score to loose in top right corner of the screen'''
	
	flags.loose_score_rect.right = screen_rect.right - 15
	flags.loose_score_rect.top = 15
	screen.blit(flags.loose_score_img, flags.loose_score_rect)
	
def draw_everything(bg_color, screen_rect, screen, players, back_img, used_deck,
		active_deck, right_arrow, flags, queen_cards, cancel_button, one_card_button):
			
	''' Main drawing function. Delegates tasks to other functions'''
	
	screen.fill(bg_color)
	draw_hands(screen_rect, screen, players, back_img, one_card_button)
	draw_used_deck(used_deck, screen_rect, screen)
	draw_active_deck(back_img, screen_rect, screen, active_deck)
	draw_arrow(right_arrow, flags, screen_rect, screen)
	draw_loose_score(screen_rect, screen, flags)
	
	if flags.queen_choose_flag:											
		draw_queen_cards(queen_cards, screen_rect, screen)
		if not flags.first_turn_flag:									# at first turn you can`t cancel your choice
			cancel_button.draw_button()
			
	pygame.display.flip()

def draw_end_game_screen(bg_color, screen_rect, screen, players, flags, play_again_button, quit_button):
	screen.fill(bg_color)
	
	''' Main drawing function for an end-game screen. Delegates sub-tasks to other functions'''
	
	draw_result_points(players, screen_rect, screen, flags.loosers)
	draw_loose_score(screen_rect, screen, flags)
	
	play_again_button.draw_button()
	quit_button.draw_button()
	pygame.display.flip()
	

	
def draw_end_round_screen(screen_rect, screen, players):
	
	'''Displays score information of a round'''
	
	draw_shade_surf(screen_rect, screen)
	draw_result_points(players, screen_rect, screen)
	pygame.display.flip()

def draw_text_line(font, text, text_color, x, y, screen):
	
	''' Draws a simple text line. Used by many other functions of the game.'''
	
	text_img = font.render(text, True, text_color)
	text_rect = text_img.get_rect()
	text_rect.left = x
	text_rect.centery = y
	screen.blit(text_img, text_rect)

def draw_result_points(players, screen_rect, screen, loosers=[]):
	
	'''Displaying results of a round and players who lost this time'''
	
	text_color = (240, 240, 0)
	font = pygame.font.SysFont('freemono', 36)
	header_font = pygame.font.SysFont('freemono', 24)
	
	header_string = '{0:{width}}{1:{width}}'.format('Round', 'Total', width=8)
	draw_text_line(header_font, header_string, text_color, screen_rect.centerx + 50, 130, screen)

	x = screen_rect.centerx - 150
	
	for ind, player in enumerate(players):
		result_string = f'{player.name:<10}{player.round_points:<5}{player.total_points}'
		y = 180 + 50 * ind
		draw_text_line(font, result_string, text_color, x, y, screen)
		
	if loosers:
		
		loosers_str = f'LOOSERS: {", ".join(player.name for player in loosers)}'
		text_len = len(loosers_str)
		if text_len % 2:												#to center text better
			go_text = 'GAME OVER'
		else:
			go_text = 'GAME  OVER'
		game_over_str = f'{go_text:^{text_len}}'
		
		draw_text_line(font, game_over_str, text_color, x, y + 80, screen)
		draw_text_line(font, loosers_str, text_color, x, y + 120, screen)
		
		
#--------------------------------------------Gameplay section-----------------------------------------------------------------------------------------------------------------------

def end_turn(turn, players, flags):
	
	'''Passes turn to next player'''
	
	if len(turn.player.hand) > 1:
		turn.player.one_card_flag = False								# restricts to show one-card hint if there are more than one card

	for player in players:												# log
		print(f'{player.name}: {player.hand}')
	print(f'Current player: {turn.player}')
	
	turn.player.active_flag = False
	player_ind = players.index(turn.player)								# to determine next player according to turn direction (reverse_flag)
		
	if flags.reverse_flag == False:
		if player_ind < len(players) -1:
			new_active_player = players[player_ind + 1]
		else:
			new_active_player = players[0]	
	else:
		if player_ind == 0:
			new_active_player = players[-1]
		else:
			new_active_player = players[player_ind - 1]
	turn.__init__(new_active_player)
	
	print(f'New player: {turn.player}')									# log

			
def check_special(card, turn, players, flags, active_deck, used_deck, queen_cards):
	
	''' Main logic of cards interaction. Manages special rules for different cards and end-round actions.'''
	
	if len(turn.player.hand) == 0:
		end_game_calculations(card, turn)		
		winner = turn.player.name
		flags.end_game_flag = True
	if card.value == 'A':												#Aces skip turn of next player
		end_turn(turn, players, flags)
	elif card.value == '7':												#skip next player turn and take a card
		end_turn(turn, players, flags)
		turn.player.take_card(active_deck, used_deck, queen_cards, flags)
	elif card.value == '6':												#skip next player turn and take 2 cards
		end_turn(turn, players, flags)
		turn.player.take_card(active_deck, used_deck, queen_cards, flags)
		turn.player.take_card(active_deck, used_deck, queen_cards, flags)
	elif card.value == 'Q':												#special rules for queens
		flags.queen_choose_flag = True
	elif card.value == '9':
		if flags.reverse_flag == True:
			flags.reverse_flag = False
		else:
			flags.reverse_flag = True
		
	if flags.end_game_flag:												#end-round actions
		print(f'{winner} wins this round!')								#log
		for player in players:
			round_points = player.count_round_points()
			print(f'{player} gets {round_points} points')				#log
			player.total_points += round_points
			
		loose_value = flags.loose_points
		for player in players:
			print(f'{player} have total {player.total_points} points')	#log
			if player.total_points >= loose_value:
				flags.game_over_flag = True
				flags.loosers.append(player)
				if player.total_points > flags.loose_points:
					flags.loose_points = player.total_points			#change loose points to play again till new value
				print(f'{player} looses with total {player.total_points} points')	#log
				
	
def focus_change(turn, new_focus):
	
	'''Switch focus to another card'''
	
	turn.player.hand[turn.focus_index].focus = False
	turn.player.hand[new_focus].focus = True
	turn.focus_index = new_focus

def swich_focus(key, turn):
	
	'''To navigate trough cards in hand via arrows'''
	
	if key == pygame.K_RIGHT:
		new_focus = turn.focus_index + 1
		if new_focus < len(turn.player.hand):
			focus_change(turn, new_focus)
				
	if key == pygame.K_LEFT:
		new_focus = turn.focus_index - 1
		if new_focus >= 0:
			focus_change(turn, new_focus)
			
def make_turn(turn, players, flags, active_deck, used_deck, queen_cards):
	
	'''Performs a player turn with different checks'''
	
	counter = len(turn.player.hand)										#remember length to chek if card was actually used				
	card = turn.player.hand[turn.focus_index]							#remember card to check for special properties
	turn.player.use_card(turn.focus_index, used_deck)
	if len(turn.player.hand) != counter:								
		check_special(card, turn, players, flags, active_deck, used_deck, queen_cards)
		if not flags.queen_choose_flag:
			end_turn(turn, players, flags)
			
def queen_turn(turn, used_deck, players, flags, queen_cards, cancel_button, mouse_x, mouse_y):
	
	'''Adds a chosen special queen card to the used deck or returns queen card to a hand of an active player.'''
	
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
		cancel_button, one_card_button, quit_button, play_again_button, play_deck):
			
	'''Main event function. Looks for players keyboard/mouse actions''' 
	
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_q:
				sys.exit()
		if flags.queen_choose_flag:										#choose special queen card 
			if event.type == pygame.MOUSEBUTTONDOWN:
				mouse_x, mouse_y = pygame.mouse.get_pos()
				queen_turn(turn, used_deck, players, flags, queen_cards,
					cancel_button, mouse_x, mouse_y)
				
		if flags.game_over_flag:										#when game is over
			if event.type == pygame.MOUSEBUTTONDOWN:
				mouse_x, mouse_y = pygame.mouse.get_pos()
				if quit_button.rect.collidepoint(mouse_x, mouse_y):
					sys.exit()
				if play_again_button.rect.collidepoint(mouse_x, mouse_y):
					new_game(players, play_deck, active_deck, used_deck, 
						queen_cards, flags, turn)
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_p:								#hotkey to play
					new_game(players, play_deck, active_deck, used_deck,
						queen_cards, flags, turn)
		else:	
			if event.type == pygame.KEYDOWN:
				if event.key in (pygame.K_RIGHT, pygame.K_LEFT):		#navigate through cards in hand
					swich_focus(event.key, turn)
					
				elif event.key == pygame.K_o:							#hotkey for one-card button
					if len(turn.player.hand) == 2 and not turn.player.one_card_flag:
						turn.player.one_card_flag = True
					
				
				elif event.key == pygame.K_RETURN:						#use a card in focus card
					make_turn(turn, players, flags, active_deck,
						used_deck, queen_cards)
				
					
				elif event.key == pygame.K_SPACE:						#draw a card or end a turn
					if turn.card_taken_flag:
						end_turn(turn, players, flags)
					else:
						turn.player.take_card(active_deck, used_deck,
							queen_cards, flags)
						turn.card_taken_flag = True						#you can draw 1 card from deck once per turn
						turn.player.one_card_flag = False
						focus_change(turn, len(turn.player.hand) - 1)
						
			
			elif event.type == pygame.MOUSEBUTTONDOWN:
				mouse_x, mouse_y = pygame.mouse.get_pos()
				if one_card_button.rect.collidepoint(mouse_x, mouse_y):	# push one-card button
					if len(turn.player.hand) == 2 and not turn.player.one_card_flag:
						turn.player.one_card_flag = True
					



#-------------------------------------------Bot management-----------------------------------------------------------------------------------

def bot_choose_queen_card(queen_cards, most_expensive_card, used_deck, flags):
	
	'''Helps bot to choose optimal special queen card. Looks for a card with biggest points value
		and chooses its suit.'''
		
	for card in queen_cards:
		if card.suit == most_expensive_card.suit:
			chosen_queen_card = card
	used_deck.cards.append(chosen_queen_card)
	flags.queen_choose_flag = False
	flags.first_turn_flag = False
	
def bot_turn(turn, bg_color, screen_rect, screen, players, back_img, 
		used_deck, active_deck, right_arrow, flags, queen_cards,
		cancel_button, one_card_button):
			
	'''Main logic for bot turn.'''
	
	turn.player.hand[0].focus = False
	turn.player.one_card_flag = True
	
	bot_imitates_human(bg_color, screen_rect, screen, players, back_img,	#just delay to see each step of a turn
		used_deck, active_deck, right_arrow, flags, queen_cards,
		cancel_button, one_card_button)
	
	useful_cards, best_card = turn.player.choose_useful_cards(used_deck.cards[-1])
	if not useful_cards:													# draw a card and check again
		turn.player.take_card(active_deck, used_deck, queen_cards, flags)
		
		bot_imitates_human(bg_color, screen_rect, screen, players,
			back_img, used_deck, active_deck, right_arrow, flags,
			queen_cards, cancel_button, one_card_button)
		
		useful_cards, best_card = turn.player.choose_useful_cards(used_deck.cards[-1])
		
	if not best_card:														# skip turn
		end_turn(turn, players, flags)	
	else:																	# make turn
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
			
	'''To make a turn with a queen card. After using queen need to choose best card suit.'''
	
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
			
	'''Just a delay as if human thinking.'''
	
	draw_everything(bg_color, screen_rect, screen, players, back_img,
		used_deck, active_deck, right_arrow, flags, queen_cards,
		cancel_button, one_card_button)
	sleep(2)
