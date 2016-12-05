from enum import Enum

class Suit(Enum):

	spades = 1
	diamonds = 2
	clubs = 3
	hearts = 4

class CardValue(Enum):

	ace = 1
	two = 2
	three = 3
	four = 4
	five = 5
	six = 6
	seven = 7
	eight = 8
	nine = 9
	ten = 10
	jack = 11
	queen = 12
	king = 13

# TODO: Joker
class Card:

	def __init__(self, val, suit):

		self.val = val
		self.suit = suit

	def __repr__(self):

		if self.val.value <= 10 and self.val.value >= 2:
			return str(self.val.value) + "_of_" + str(self.suit.name)

		return str(self.val.name) + "_of_" + str(self.suit.name)

	# Returns string representations of all cards
	@staticmethod
	def get_all_cards():

		return [Card(card_val, suit).__repr__() for card_val in CardValue for suit in Suit]