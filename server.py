import getopt
import random
import sys

import PodSixNet.Channel
import PodSixNet.Server

from card import Card, CardValue
from time import sleep


class ClientChannel(PodSixNet.Channel.Channel):

	def Network(self, data):

		print data

	def Network_bet(self, data):
		
		self._server.place_bet(data["bet"], data["game_id"])

	def Network_bullshit(self, data):

		self._server.call_bullshit(data["player_num"], data["game_id"])
		winner = self._server.get_winner(data["game_id"]) 
		if winner is None:
			self._server.start_round(data["game_id"])
		else:
			self._server.end_game(data["game_id"], winner)

	def Network_close(self, data):

		self._server.close(data["game_id"], data["player_num"])
 

class Server(PodSixNet.Server.Server):

	channelClass = ClientChannel
	
	def __init__(self, *args, **kwargs):

		PodSixNet.Server.Server.__init__(self, *args, **kwargs)
		self.games = {}
		self.queue = None
		self.currentIndex = 0
	
	def Connected(self, channel, addr):
		
		print 'new connection:', channel

		if self.queue is None:
			self.currentIndex += 1
			channel.game_id = self.currentIndex
			self.queue = SGame(channel, self.currentIndex)
		else:
			channel.game_id = self.currentIndex
			self.queue.players.append(channel)
			self.queue.num_players += 1
			self.games[channel.game_id] = self.queue
			self.queue = None

			self.start_game(channel.game_id)

	def start_game(self, game_id):

		game = self.games[game_id]
		start_game_msg = lambda player: {
			"action": "startgame",
			"player_num": player, 
			"game_id": game.game_id,
		}
		game.start_game()
		self._msg_all_players(game, start_game_msg)
		self.start_round(game.game_id)

	def start_round(self, game_id):

		game = self.games[game_id]
		game.start_round()
		round_start_msg = lambda player: {
			"action": "startround",
			"cards": game.player_cards[player],
			"turn": game.turn,
			"opponent_count": game.player_num_cards[_other_player(player)],
		}
		self._msg_all_players(game, round_start_msg)

	def place_bet(self, bet, game_id):

		game = self.games[game_id]
		game.place_bet(bet)
		bet_msg = lambda player: {
			"action": "bet_placed",
			"turn": game.turn == player,
			"bet": game.bet,
		}		
		self._msg_all_players(game, bet_msg)

	def call_bullshit(self, player_num, game_id):

		game = self.games[game_id]
		winner, count, satisfiers = game.call_bullshit(player_num)
		game.last_winner = winner

		round_end_msg = lambda player: {
			"action": "round_over",
			"winner": winner,
			"count": count,
			"opponent_cards": game.player_cards[_other_player(player)],
			"satisfiers": satisfiers,
		}
		self._msg_all_players(game, round_end_msg)

	def end_game(self, game_id, winner):

		game = self.games[game_id]
		endgame_msg = lambda player: {
			"action": "endgame",
			"winner": winner,
		}
		self._msg_all_players(game, endgame_msg)

	def close(self, game_id, player_num):

		game = self.games[game_id]
		close_msg = lambda player: {
			"action":"close",
			"player_num": player_num,
		}
		self._msg_all_players(game, close_msg)

	def get_winner(self, game_id):

		game = self.games[game_id]
		return game.get_winner()

	def _msg_all_players(self, game, msg):

		for player_num, player in enumerate(game.players):
			player.Send(msg(player=player_num))


class SGame:

	MAX_PLAYERS = 2
	NUM_CARDS = 5

	def __init__(self, player0, currentIndex):

		self.all_cards = Card.get_all_cards()
		self.game_id = currentIndex
		self.bet = None
		self.last_winner = None
		
		self.num_players = 1
		self.players = [player0]

	def start_game(self):

		self.turn = 0
		self.player_num_cards = [self.NUM_CARDS] * self.num_players
		self.player_cards = [None] * self.num_players

	def start_round(self):

		self.turn = self.last_winner or 0
		round_cards = self.deal_cards()

	def deal_cards(self):

		total_cards_count = sum(self.player_num_cards)
		round_cards = random.sample(range(len(self.all_cards)), total_cards_count)
		for player_num in range(len(self.players)):
			self.player_cards[player_num] = round_cards[:self.player_num_cards[player_num]]
			round_cards = round_cards[self.player_num_cards[player_num]:]

	def place_bet(self, bet):

		self.bet = bet
		self.turn = _other_player(self.turn)

	def call_bullshit(self, player_num):

		count = 0
		face_card_values = [CardValue.jack, CardValue.queen, CardValue.king]

		satisfiers = [[], []]
		for player in range(self.num_players):
			player_round_cards = [self.all_cards[ind] for ind in self.player_cards[player]]
			for i, card in enumerate(player_round_cards):
				if any(face_card_val == card.val for face_card_val in face_card_values):
					count += 1
					satisfiers[player].append(i)

				elif CardValue.joker == card.val:
					count -= 1 
					satisfiers[player].append(i)

				elif self.bet[1] == card.val.value:
					count += 1
					satisfiers[player].append(i)

		round_winner = player_num if count < self.bet[0] else _other_player(player_num)
		self.player_num_cards[_other_player(round_winner)] -= 1
		self.bet = None
		return round_winner, count, satisfiers

	def get_winner(self):

		try:
			return _other_player(self.player_num_cards.index(0))
		except:
			return None

def _other_player(player_num):

	return (player_num + 1) % 2

host, port = "localhost", "8000"
try:
	opts, args = getopt.getopt(sys.argv[1:], "h:")
	for opt, arg in opts:
		if opt == '-h':
			host, port = arg.split(":") 

	print "STARTING SERVER ON {}:{}".format(host, port)
	server = Server(localaddr=(host, int(port)))
	while True:
		server.Pump()
		sleep(0.01)

except:
	print("Usage: python server.py -h [host]:[port]")
	exit()