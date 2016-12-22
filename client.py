# https://www.raywenderlich.com/38732/multiplayer-game-programming-for-teens-with-python
import getopt
import random
import sys
from time import sleep

from PodSixNet.Connection import ConnectionListener, connection
import pygame
import pygbutton

from bet import Bet
from card import Card, CardValue

class Game(ConnectionListener):

	def Network_startgame(self, data):

		self.running = True
		self.player_num = data["player_num"]
		self.game_id = data["game_id"]

	def Network_startround(self, data):

		self.cards = data["cards"]
		self.turn = True if data["turn"] == self.player_num else False
		self.opponent_count = data["opponent_count"]

	def Network_round_over(self, data):

		for frame in range(1, 31):
			self.redraw_screen(data["satisfiers"], data["opponent_cards"], frame)

		myfont = pygame.font.SysFont(None, 32)
		count_label = myfont.render((
			("There were " if data["count"] != 1 else "There was ") + 
			str(data["count"]) + 
			" " + 
			(CardValue(self.game_bet.val).name) + 
			("s" if data["count"] != 1 else "")
		), 1, (255,255,255))
		self.screen.blit(count_label, (95, 175))

		self.game_bet = None
	  	sleep(5)
		
	def Network_bet_placed(self, data):

		self.turn = data["turn"]
		self.game_bet = Bet(data["bet"][0], data["bet"][1])

	def Network_endgame(self, data):

		self.player_won = True if data["winner"] == self.player_num else False
		self.end_game()

	def Network_close(self, data):
		
	    print("Player {} disconnected!".format(data["player_num"]))
	    exit()

	def __init__(self):

		pygame.init()
		pygame.font.init()
		pygame.display.set_caption("Bullshit")
		self.clock = pygame.time.Clock()
		self.init_graphics()
		self.width, self.height = 589, 689
		self.count_bet = 0
		self.val_bet = 1

		self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
		
		self.bs_button = pygbutton.PygButton((self.width - 100, self.height - 65, 80, 30), 'Bullshit!')
		self.count_inc_button = pygbutton.PygButton((self.width/2 - 30, self.height - 90, 20, 20), '+')
		self.count_dec_button = pygbutton.PygButton((self.width/2 + 30, self.height - 90, 20, 20), '-')
		self.val_inc_button = pygbutton.PygButton((self.width/2 - 30, self.height - 40, 20, 20), '+')
		self.val_dec_button = pygbutton.PygButton((self.width/2 + 30, self.height - 40, 20, 20), '-')
		self.bet_button = pygbutton.PygButton((self.width/2 + 90, self.height - 70, 50, 30), 'Bet')

		self.game_id = None
		self.player_num = None
		self.player_won = False
		self.game_bet = None
		self.running = False
		self.game_over = False

		host, port = "localhost", "8000"
		try:
			opts, args = getopt.getopt(sys.argv[1:], "h:")
			for opt, arg in opts:
				if opt == '-h':
					host, port = arg.split(":")

			self.Connect((host, int(port)))
			print "Bullshit client started"

			while not self.running:
				self.Pump()
				connection.Pump()
				sleep(0.01)
		except:
			print("Usage: python server.py -h [host]:[port]")
			exit()
			
	def init_graphics(self):

		self.all_cards = Card.get_all_cards()
		self.card_imgs = []
		for card in self.all_cards:
			card_img = pygame.image.load("res/" + card.__repr__() + ".png")
			card_img = pygame.transform.scale(card_img, (100, 144))
			self.card_imgs.append(card_img)
		self.card_back = pygame.image.load("res/back.jpg")
		self.card_back = pygame.transform.scale(self.card_back, (100, 144))

		self.redindicator = pygame.image.load("res/redindicator.png")
		self.greenindicator = pygame.image.load("res/greenindicator.png")
		self.winningscreen = pygame.image.load("res/youwin.png")
		self.gameoverscreen = pygame.image.load("res/gameover.png")
		self.score_panel = pygame.image.load("res/score_panel.png")
		self.bg = pygame.image.load("res/bg.jpg")
		self.card_green_overlay = pygame.image.load("res/card_green_overlay.png")
		self.card_red_overlay = pygame.image.load("res/card_red_overlay.png")

	def update(self):

		connection.Pump()
		self.Pump()
		
		self.clock.tick(60)
		self.redraw_screen()
		
		for event in pygame.event.get():

			if event.type == pygame.QUIT:
				self.Send({
					"action": "close",
					"game_id": self.game_id,
					"player_num": self.player_num,
				})

			elif 'click' in self.bs_button.handleEvent(event) and self.turn and self.game_bet:
				self.Send({
					"action": "bullshit", 
					"game_id": self.game_id, 
					"player_num": self.player_num,
				})

			elif 'click' in self.count_inc_button.handleEvent(event) and self.turn:
				self.count_bet += 1
			elif 'click' in self.count_dec_button.handleEvent(event) and self.turn:
				if self.count_bet - 1 >= 0:
					self.count_bet -= 1

			elif 'click' in self.val_inc_button.handleEvent(event) and self.turn:
				if 1 <= self.val_bet + 1 <= 10:
					self.val_bet += 1
			elif 'click' in self.val_dec_button.handleEvent(event) and self.turn:
				if 1 <= self.val_bet - 1 <= 10:
					self.val_bet -= 1

			elif 'click' in self.bet_button.handleEvent(event) and self.turn:
				new_bet = Bet(self.count_bet, self.val_bet)
				if self.game_bet is None or new_bet.bet_valid(self.game_bet):
					self.Send({
						"action": "bet",
						"game_id": self.game_id,
						"player_num": self.player_num,
						"bet": (self.count_bet, self.val_bet),
					})

			elif event.type == pygame.VIDEORESIZE:
				self.screen = pygame.display.set_mode(event.dict['size'], pygame.RESIZABLE)
				self.width, self.height = event.dict['size']
				self.bs_button.rect = pygame.Rect(self.width - 100, self.height - 65, 80, 30)
				self.count_inc_button.rect = pygame.Rect(self.width/2 - 30, self.height - 90, 20, 20)
				self.count_dec_button.rect = pygame.Rect(self.width/2 + 30, self.height - 90, 20, 20)
				self.val_inc_button.rect = pygame.Rect(self.width/2 - 30, self.height - 40, 20, 20)
				self.val_dec_button.rect = pygame.Rect(self.width/2 + 30, self.height - 40, 20, 20)
				self.bet_button.rect = pygame.Rect(self.width/2 + 90, self.height - 70, 50, 30)

		pygame.display.flip()

	def redraw_screen(self, satisfiers=None, opponent_cards=None, animate_frame=None):

		if not self.game_over:
			self.screen.fill(0)
			self.draw_cards(satisfiers, opponent_cards, animate_frame)
			self.draw_hud()
			pygame.display.flip()

	def draw_cards(self, satisfiers=None, opponent_cards=None, animate_frame=None):

		self.bg = pygame.transform.scale(self.bg, (self.width, self.height))
		self.screen.blit(self.bg, [0, 0])	

		# Draw player's cards
		width_needed = (len(self.cards) - 1) * 20 + 100
		x = (self.width - width_needed)/float(2)
		y = self.height - 274

		for i, card_ind in enumerate(self.cards):
			if satisfiers is not None and i in satisfiers[self.player_num]:
				overlay = self.card_red_overlay if card_ind in [52, 53] else self.card_green_overlay
				self.screen.blit(self.card_imgs[card_ind], [x, y - animate_frame])
				self.screen.blit(overlay, [x, y - animate_frame])
			else:
				self.screen.blit(self.card_imgs[card_ind], [x, y])
			x += 20

		# Draw opponent's cards
		width_needed = (self.opponent_count - 1) * 20 + 100
		x = (self.width - width_needed)/float(2)
		y = 20

		for i in range(self.opponent_count):
			if satisfiers:
				card_ind = opponent_cards[i]
				if i in satisfiers[(self.player_num + 1) % 2]:
					overlay = self.card_red_overlay if card_ind in [52, 53] else self.card_green_overlay
					self.screen.blit(self.card_imgs[card_ind], [x, y + animate_frame])
					self.screen.blit(overlay, [x, y + animate_frame])
				else:
					self.screen.blit(card_img, [x, y])
			else:
				self.screen.blit(self.card_back, [x, y])			
			x += 20

	def draw_hud(self):

		top_of_score_panel = self.height - 100
		self.score_panel = pygame.transform.scale(self.score_panel, (self.width, 100))
		self.screen.blit(self.score_panel, [0, top_of_score_panel])
		myfont = pygame.font.SysFont(None, 32)
		turn_label = myfont.render("Turn", 1, (255,255,255))
		self.screen.blit(turn_label, (10, top_of_score_panel + 11))

		indicator = self.greenindicator if self.turn else self.redindicator
		self.screen.blit(indicator, (18, top_of_score_panel + 41))

		self.bs_button.draw(self.screen)

		self.count_inc_button.draw(self.screen)
		count_label = myfont.render(str(self.count_bet), 1, (255,255,255))
		self.screen.blit(count_label, (self.width/2 - 2 if self.count_bet >= 10 else self.width/2 + 5, self.height - 90))
		self.count_dec_button.draw(self.screen)

		self.val_inc_button.draw(self.screen)
		val_label = myfont.render(str(self.val_bet), 1, (255,255,255))
		self.screen.blit(val_label, (self.width/2 - 2 if self.val_bet >= 10 else self.width/2 + 5 , self.height - 42))
		self.val_dec_button.draw(self.screen)

		self.bet_button.draw(self.screen)

		if self.game_bet is not None:
			myfont = pygame.font.SysFont(None, 50)
			bet_label = myfont.render(self.game_bet.__repr__(), 1, (255,255,255))
			location = (self.width - self.width/6, 20) if self.turn else (self.width - self.width/6, self.height - 100 - 80)
			self.screen.blit(bet_label, location)

	def end_game(self):
		
		self.gameoverscreen = pygame.transform.scale(self.gameoverscreen, (self.width, self.height))
		self.winningscreen = pygame.transform.scale(self.winningscreen, (self.width, self.height))
		self.screen.blit(self.gameoverscreen if not self.player_won else self.winningscreen, [0, 0])
		self.turn = None
		self.game_over = True

game = Game()
while True:
	game.update()