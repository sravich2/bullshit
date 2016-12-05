import PodSixNet.Channel
import PodSixNet.Server
from time import sleep
from card import Card, CardValue
import random

class ClientChannel(PodSixNet.Channel.Channel):

	def Network(self, data):
		print data

	def Network_bet(self, data):
		
		self._server.place_bet(data["bet"], data["game_id"])

	def Network_bullshit(self, data):

		self._server.call_bullshit(data["player_num"], data["game_id"])
		winner = self._server.game_over(data["game_id"]) 
		if winner is not None:
			self._server.end_game(data["game_id"], winner)
		else:
			self._server.start_round(data["game_id"])
 
class Server(PodSixNet.Server.Server):

	def game_over(self, game_id):

		game = [game for game in self.games if game_id == game.game_id][0]
		return game.game_over()

	def call_bullshit(self, player_num, game_id):

		game = [game for game in self.games if game_id == game.game_id][0]
		winner, count = game.call_bullshit(player_num)
		game.last_winner = winner

		game.player0.Send(
			{
				"action": "round_over",
				"winner": winner,
				"count": count,
			}
		)
		game.player1.Send(
			{
				"action": "round_over",
				"winner": winner,
				"count": count,
			}
		)

	def start_round(self, game_id):

		game = [game for game in self.games if game_id == game.game_id][0]
		game.start_round()

		game.player0.Send(
				{
					"action": "startround",
					"cards": game.player0_cards,
					"turn": game.turn,
				}
			)
		game.player1.Send(
			{
				"action": "startround",
				"cards": game.player1_cards,
				"turn": game.turn,
			}
		)

	def end_game(self, game_id, winner):

		game = [game for game in self.games if game_id == game.game_id][0]
		game.player0.Send(
				{
					"action": "endgame",
					"winner": winner,
				}
			)
		game.player1.Send(
			{
				"action": "endgame",
				"winner": winner,
			}
		)

	def place_bet(self, bet, game_id):

		game = [game for game in self.games if game_id == game.game_id][0]
		game.place_bet(bet)
		game.player0.Send(
			{
				"action": "bet_placed",
				"turn": 1 if game.turn == 0 else 0,
				"bet": game.bet,
			}
		)
		game.player1.Send(
			{
				"action": "bet_placed",
				"turn": 1 if game.turn == 1 else 0,
				"bet": game.bet,
			}
		)

	def __init__(self, *args, **kwargs):

		PodSixNet.Server.Server.__init__(self, *args, **kwargs)
		self.games = []
		self.queue = None
		self.currentIndex = 0

	channelClass = ClientChannel
 
	def Connected(self, channel, addr):
		
		print 'new connection:', channel

		if self.queue is None:

			self.currentIndex += 1
			channel.game_id = self.currentIndex
			self.queue = SGame(channel, self.currentIndex)

		else:
			channel.game_id = self.currentIndex
			self.queue.player1 = channel
			self.queue.player0.Send(
				{
					"action": "startgame",
					"player_num": 0, 
					"game_id": self.queue.game_id,
					"cards": self.queue.player0_cards,
				}
			)
			self.queue.player1.Send(
				{
					"action": "startgame",
					"player_num": 1, 
					"game_id": self.queue.game_id,
					"cards": self.queue.player1_cards,
				}
			)
			self.games.append(self.queue)
			self.queue = None


class SGame:

	def __init__(self, player0, currentIndex):

		self.all_cards = Card.get_all_cards()
		self.turn = 0
		self.player0_num_cards = 5
		self.player1_num_cards = 5

		round_cards = self.deal_cards(self.player0_num_cards + self.player1_num_cards)

		self.player0_cards = round_cards[:self.player0_num_cards]
		self.player1_cards = round_cards[self.player0_num_cards:]

		self.player0 = player0
		self.player1 = None

		self.game_id = currentIndex
		self.bet = None
		self.last_winner = None

	def game_over(self):

		if self.player0_num_cards == 0:
			return 1
		elif self.player1_num_cards == 0:
			return 0
		else:
			return None

	def start_round(self):

		self.turn = self.last_winner
		round_cards = self.deal_cards(self.player0_num_cards + self.player1_num_cards)

		self.player0_cards = round_cards[:self.player0_num_cards]
		self.player1_cards = round_cards[self.player0_num_cards:]

	def deal_cards(self, count):

		return random.sample(range(len(self.all_cards)), count)

	def place_bet(self, bet):

		self.bet = bet
		self.turn = (self.turn + 1) % 2

	def call_bullshit(self, player_num):

		round_cards = [self.all_cards[ind] for ind in (self.player0_cards + self.player1_cards)]
		count = 0
		face_card_values = [11, 12, 13]
		for card in round_cards:
			if any(CardValue(card_val).name in card for card_val in face_card_values):
				count += 1	
			elif self.bet[1] == 1:
				if CardValue(self.bet[1]).name in card:
					count += 1
			else:
				if str(self.bet[1]) in card:
					count += 1

		if count < self.bet[0]:
			winner = player_num
		else:
			winner = (player_num + 1) % 2

		if winner == 0:
			self.player1_num_cards -= 1
			if self.player1_num_cards == 0:
				self.game_over()
		else:
			self.player0_num_cards -= 1
			if self.player0_num_cards == 0:
				self.game_over()

		self.bet = None
		return winner, count

print "STARTING SERVER ON LOCALHOST"
# try:
address=raw_input("Host:Port (localhost:8000): ")
if not address:
    host, port="localhost", 8000
else:
    host,port=address.split(":")
server = Server(localaddr=(host, int(port)))
while True:
	server.Pump()
	sleep(0.01)