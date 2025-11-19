import pygame

import game_settings


def draw_start_screen(st_screen):

    """Draws everything for start screen."""

    st_screen.screen.fill(st_screen.props.start_screen_color)
    st_screen.screen.fill(st_screen.props.text_color, st_screen.quit_but_border)  # button contours
    st_screen.screen.fill(st_screen.props.text_color, st_screen.play_but_border)
    st_screen.play_but.draw_button()
    st_screen.quit_but.draw_button()
    draw_text_line(st_screen.props.header_font, st_screen.props.big_header,
                   st_screen.props.text_color, st_screen.screen_rect.centerx - 150, 70, st_screen.screen)
    draw_text_line(st_screen.props.hint_font, 'Enter your name: ',
                   st_screen.props.text_color, st_screen.screen_rect.centerx - 300, 200, st_screen.screen)
    for ind, hint in enumerate(st_screen.props.hints):  # hints to play a game
        draw_text_line(st_screen.props.hint_font, hint, st_screen.props.text_color,
                       st_screen.screen_rect.left + 50, st_screen.screen_rect.bottom - 50 - ind * 50, st_screen.screen)


def draw_used_deck(deck, screen_rect, screen):

    """Displays 2 latest cards of the used deck"""

    bot_rect = deck.cards[-1].image.get_rect()
    bot_rect.centerx = screen_rect.centerx - 100
    bot_rect.centery = screen_rect.centery + 5

    top_rect = deck.cards[-1].image.get_rect()
    top_rect.centerx = screen_rect.centerx - 85
    top_rect.centery = screen_rect.centery

    if len(deck.cards) > 1:
        if len(deck.cards) % 2 == 0:
            bot_rect, top_rect = top_rect, bot_rect  # a bit of alternative animation
        screen.blit(deck.cards[-2].image, bot_rect)
    screen.blit(deck.cards[-1].image, top_rect)


def draw_active_deck(back_img, screen_rect, screen, deck):

    """Displays a block of unused cards"""

    back_rect = back_img.get_rect()
    back_rect.centerx = screen_rect.centerx + 20
    back_rect.centery = screen_rect.centery
    if len(deck.cards) < 4:  # changes image when the deck is almost dry
        for i in range(len(deck.cards)):
            screen.blit(back_img, ((back_rect.centerx + i * 13),
                                   screen_rect.centery - 52 - i * 5))
    else:
        screen.blit(back_img, back_rect)


def draw_active_hand(game_screen, player):

    """Draws the cards of an active player and one-card button"""

    count = len(player.hand)
    hand_width_px = 70 + 20 * (count - 1)
    start_px = int(game_screen.screen_rect.centerx - hand_width_px / 2)
    image_rect = player.hand[0].image.get_rect()
    for i in range(count):
        image_rect.left = start_px + i * 20
        image_rect.bottom = game_screen.screen_rect.bottom
        if player.hand[i].focus:  # focused card is a bit higher
            image_rect.bottom -= 25
        if not player.bot or game_settings.DEBUG:
            game_screen.screen.blit(player.hand[i].image, image_rect)
        else:
            game_screen.screen.blit(game_screen.back_img, image_rect)
    if count == 2 and not player.one_card_flag:  # a button to say that one card left appears when a player has 2 cards
        draw_one_card_button(game_screen.one_card_button, game_screen.screen_rect, image_rect)


def draw_one_card_button(one_card_button, screen_rect, image_rect):

    """Draws one-card button. Its position depends on how many cards left (1 or 2)"""

    one_card_button.msg_image_rect.left = image_rect.right + 15
    one_card_button.msg_image_rect.bottom = screen_rect.bottom - 5
    one_card_button.rect = one_card_button.msg_image_rect
    one_card_button.draw_button()


def draw_name(screen_rect, screen, player, degree):

    """Draws players name"""

    rot_name_image = pygame.transform.rotate(player.name_img, degree)
    name_img_rect = rot_name_image.get_rect()
    name_img_rect.centery = screen_rect.centery
    if degree == -90:  # rotation for left- and right-side players
        name_img_rect.left = 0
    elif degree == 90:
        name_img_rect.right = screen_rect.right
    screen.blit(rot_name_image, name_img_rect)


def draw_other_hands(game_screen, players_order):

    """Draws cards of other (non-active) players."""

    for ind, player in enumerate(players_order):
        count = len(player.hand)
        hand_width_px = 70 + 20 * (count - 1)

        start_px = int(game_screen.screen_rect.centery - hand_width_px / 2)  # to place whole car dset left/right-center
        other_hand_image = pygame.transform.rotate(game_screen.back_img, 90)
        other_hand_image_rect = other_hand_image.get_rect()
        for i in range(count):
            other_hand_image_rect.top = int(start_px + i * 20)  # each card stacked one on another with a little shift
            if ind == 1:
                other_hand_image_rect.right = game_screen.screen_rect.right
                degree = 90
            else:
                other_hand_image_rect.left = 0
                degree = -90
            game_screen.screen.blit(other_hand_image, other_hand_image_rect)
        draw_name(game_screen.screen_rect, game_screen.screen, player, degree)
        if player.one_card_flag:
            draw_hint(other_hand_image_rect, degree, game_screen.screen)


def draw_hint(other_hand_image_rect, degree, screen):

    """A dialog cloud with word "One!" to indicate that player has only one card left"""

    hint = pygame.image.load('Cards_70x105/ONE.png')
    hint_img = pygame.transform.rotate(hint, degree)
    hint_img_rect = hint_img.get_rect()

    if degree == -90:  # draw for right- or left-side player
        hint_img_rect.left = other_hand_image_rect.right
        hint_img_rect.centery = other_hand_image_rect.centery + 25
    else:
        hint_img_rect.right = other_hand_image_rect.left
        hint_img_rect.centery = other_hand_image_rect.centery - 25
    screen.blit(hint_img, hint_img_rect)


def draw_hands(players, game_screen):

    """Determines active player, right- and left-side players and
        delegates drawing to appropriate functions"""

    act_ind = None  # index of an active player
    for ind, player in enumerate(players):
        if player.active_flag:
            act_ind = ind
            draw_active_hand(game_screen, player)
    players_order = players[act_ind + 1:] + players[:act_ind]
    draw_other_hands(game_screen, players_order)


def draw_arrow(right_arrow, flags, screen_rect, screen):

    """ Draws an arrow to show which player goes next"""

    if not flags.reverse_flag:
        right_arrow = pygame.transform.rotate(right_arrow, 180)
    arrow_rect = right_arrow.get_rect()
    arrow_rect.centerx = screen_rect.centerx
    arrow_rect.bottom = screen_rect.bottom - 140
    screen.blit(right_arrow, arrow_rect)


def draw_queen_cards(queen_cards, screen_rect, screen):

    """Draws shaded screen with special cards to choose when a player uses queen card"""

    draw_shade_surf(screen_rect, screen)
    for card in queen_cards:
        screen.blit(card.image, card.rect)


def draw_shade_surf(screen_rect, screen):

    """Draws special surface during queen turn"""

    shade_surface = pygame.Surface([1200, 800])
    shade_color = (200, 200, 200)
    shade_surface.fill(shade_color)
    shade_surface.set_alpha(120)
    screen.blit(shade_surface, screen_rect)


def draw_loose_score(screen_rect, screen, flags):

    """A score to lose in top right corner of the screen"""

    flags.loose_score_rect.right = screen_rect.right - 15
    flags.loose_score_rect.top = 15
    screen.blit(flags.loose_score_img, flags.loose_score_rect)


def draw_everything(players, used_deck,
                    active_deck, flags, queen_cards, game_screen):

    """Main drawing function. Delegate tasks to other functions"""

    game_screen.screen.fill(game_screen.bg_color)
    draw_hands(players, game_screen)
    draw_used_deck(used_deck, game_screen.screen_rect, game_screen.screen)
    draw_active_deck(game_screen.back_img, game_screen.screen_rect, game_screen.screen, active_deck)
    draw_arrow(game_screen.right_arrow, flags, game_screen.screen_rect, game_screen.screen)
    draw_loose_score(game_screen.screen_rect, game_screen.screen, flags)

    if flags.queen_choose_flag:
        draw_queen_cards(queen_cards, game_screen.screen_rect, game_screen.screen)
        if not flags.first_turn_flag:  # at first turn you can`t cancel your choice
            game_screen.cancel_button.draw_button()

    pygame.display.flip()


def draw_end_game_screen(players, flags, game_screen):
    game_screen.screen.fill(game_screen.bg_color)

    """Main drawing function for an end-game screen. Delegates sub-tasks to other functions"""

    draw_result_points(players, game_screen.screen_rect, game_screen.screen, flags.losers)
    draw_loose_score(game_screen.screen_rect, game_screen.screen, flags)

    game_screen.play_again_button.draw_button()
    game_screen.quit_button.draw_button()
    pygame.display.flip()


def draw_end_round_screen(screen_rect, screen, players):

    """Displays score information of a round"""

    draw_shade_surf(screen_rect, screen)
    draw_result_points(players, screen_rect, screen)
    pygame.display.flip()


def draw_text_line(font, text, text_color, x, y, screen):

    """Draws a simple text line. Used by many other functions of the game"""

    text_img = font.render(text, True, text_color)
    text_rect = text_img.get_rect()
    text_rect.left = x
    text_rect.centery = y
    screen.blit(text_img, text_rect)


def draw_result_points(players, screen_rect, screen, losers=None):

    """Displaying results of a round and players who lost this time"""

    if losers is None:
        losers = []
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

    if losers:

        losers_str = f'LOSERS: {", ".join(player.name for player in losers)}'
        text_len = len(losers_str)
        if text_len % 2:  # to center text better
            go_text = 'GAME OVER'
        else:
            go_text = 'GAME  OVER'
        game_over_str = f'{go_text:^{text_len}}'

        draw_text_line(font, game_over_str, text_color, x, y + 80, screen)
        draw_text_line(font, losers_str, text_color, x, y + 120, screen)