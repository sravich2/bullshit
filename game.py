# https://www.raywenderlich.com/38732/multiplayer-game-programming-for-teens-with-python
import pygame
import pygbutton
from card import Card
from bet import Bet
import random
from time import sleep
from PodSixNet.Connection import ConnectionListener, connection

class Game(ConnectionListener):

	def Network_endgame(self, data):

		self.player_won = True if data["winner"] == self.player_num else False
		self.screen.blit(self.gameover if not self.player_won else self.winningscreen, (0,0))
		while True:
			  for event in pygame.event.get():
				  if event.type == pygame.QUIT:
					  exit()
			  pygame.display.flip()

	def Network_startgame(self, data):

		self.running = True
		self.player_num = data["player_num"]
		self.game_id = data["game_id"]
		self.cards = data["cards"]

	def Network_startround(self, data):

		self.running = True
		self.cards = data["cards"]
		self.turn = 1 if data["turn"] == self.player_num else 0

	def Network_round_over(self, data):

		self.game_bet = None
		myfont = pygame.font.SysFont(None, 32)
		count_label = myfont.render("There were " + str(data["count"]), 1, (255,255,255))
		self.screen.blit(count_label, (175, 250))
	  	pygame.display.flip()
	  	sleep(3)
		
	def Network_bet_placed(self, data):

		self.turn = data["turn"]
		self.game_bet = Bet(data["bet"][0], data["bet"][1])

	def game_over(self, count):
		
		self.screen.blit(self.gameover if not self.player_won else self.winningscreen, (0,0))
		while True:
			  for event in pygame.event.get():
				  if event.type == pygame.QUIT:
					  exit()
			  pygame.display.flip()

	def init_graphics(self):

		self.card_imgs = []
		for card in self.all_cards:
			card_img = pygame.image.load("res/" + card + ".png")
			card_img = pygame.transform.scale(card_img, (100, 144))
			self.card_imgs.append(card_img)

		self.redindicator = pygame.image.load("res/redindicator.png")
		self.greenindicator = pygame.image.load("res/greenindicator.png")
		self.winningscreen = pygame.image.load("res/youwin.png")
		self.gameover = pygame.image.load("res/gameover.png")
		self.score_panel = pygame.image.load("res/score_panel.png")
		self.bg = pygame.image.load("res/bg.jpg")

	def draw_cards(self):

		self.screen.blit(self.bg, [0, 0])		
		x, y = 100, 100

		for card_ind in self.cards:
			self.screen.blit(self.card_imgs[card_ind], [x, y])
			x += 20

	def draw_hud(self):
		
		self.screen.blit(self.score_panel, [0, 389])
		#create font
		myfont = pygame.font.SysFont(None, 32)
		 
		turn_label = myfont.render("Turn", 1, (255,255,255))
		self.screen.blit(turn_label, (10, 400))

		if self.turn:
			self.screen.blit(self.greenindicator, (18, 430))
		else:
			self.screen.blit(self.redindicator, (18, 430))

		if self.game_bet is not None:
			bet_label = myfont.render(self.game_bet.__repr__(), 1, (255,255,255))
			self.screen.blit(bet_label, (150, 450))

		self.bs_button.draw(self.screen)

		self.count_inc_button.draw(self.screen)
		count_label = myfont.render(str(self.count_bet), 1, (255,255,255))
		self.screen.blit(count_label, (280, 397))
		self.count_dec_button.draw(self.screen)

		self.val_inc_button.draw(self.screen)
		val_label = myfont.render(str(self.val_bet), 1, (255,255,255))
		self.screen.blit(val_label, (280, 447))
		self.val_dec_button.draw(self.screen)

		self.bet_button.draw(self.screen)

	def __init__(self):

		pygame.init()
		pygame.font.init()
		width, height = 389, 489

		self.count_bet = 0
		self.val_bet = 1

		self.screen = pygame.display.set_mode((width, height))
		self.bs_button = pygbutton.PygButton((150, 400, 80, 30), 'Bullshit!')
		self.count_inc_button = pygbutton.PygButton((250, 400, 20, 20), '+')
		self.count_dec_button = pygbutton.PygButton((300, 400, 20, 20), '-')
		self.val_inc_button = pygbutton.PygButton((250, 450, 20, 20), '+')
		self.val_dec_button = pygbutton.PygButton((300, 450, 20, 20), '-')
		self.bet_button = pygbutton.PygButton((330, 420, 50, 30), 'Bet')

		self.all_cards = Card.get_all_cards()
		pygame.display.set_caption("Bullshit")

		self.clock = pygame.time.Clock()

		self.init_graphics()

		self.game_id = None
		self.player_num = None

		self.turn = True
		self.player_won = False
		self.game_bet = None

		address=raw_input("Address of Server: ")
		try:
		    if not address:
		        host, port="localhost", 8000
		    else:
		        host,port=address.split(":")
		    self.Connect((host, int(port)))
		except:
		    print "Error Connecting to Server"
		    print "Usage:", "host:port"
		    print "e.g.", "localhost:31425"
		    exit()
		print "Bullshit client started"

		self.running = False
		while not self.running:
			self.Pump()
			connection.Pump()
			sleep(0.01)
		#determine attributes from player #
		if self.player_num == 0:
			self.turn = True
		else:
			self.turn = False

	def update(self):

		connection.Pump()
		self.Pump()
		# 60fps
		self.clock.tick(60)

		# Clear screen
		self.screen.fill(0)

		self.draw_cards()
		self.draw_hud()

		for event in pygame.event.get():

			if event.type == pygame.QUIT:
				exit()

			if 'click' in self.bs_button.handleEvent(event) and self.game_bet is not None:
				self.Send(
					{
						"action": "bullshit", 
						"game_id": self.game_id, 
						"player_num": self.player_num,
					}
				)

			if 'click' in self.count_inc_button.handleEvent(event) and self.turn:
				self.count_bet += 1
			if 'click' in self.count_dec_button.handleEvent(event) and self.turn:
				if self.count_bet - 1 >= 0:
					self.count_bet -= 1

			if 'click' in self.val_inc_button.handleEvent(event) and self.turn:
				if self.val_bet + 1 >= 1 and self.val_bet + 1 <= 10:
					self.val_bet += 1
			if 'click' in self.val_dec_button.handleEvent(event) and self.turn:
				if self.val_bet - 1 >= 1 and self.val_bet - 1 <= 10:
					self.val_bet -= 1

			if 'click' in self.bet_button.handleEvent(event) and self.turn:
				new_bet = Bet(self.count_bet, self.val_bet)
				if self.game_bet is None or new_bet.bet_valid(self.game_bet):
					self.Send(
						{
							"action": "bet",
							"game_id": self.game_id,
							"player_num": self.player_num,
							"bet": (self.count_bet, self.val_bet),
						}
					)

		# Update screen
		pygame.display.flip()

game = Game()
while True:
	game.update()	
