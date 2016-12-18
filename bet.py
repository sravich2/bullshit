from card import CardValue

class Bet:

	def __init__(self, count, val):

		self.count = count
		self.val = val

	def bet_valid(self, prev_bet):

		return (
			self.count >= 0 and 
			1 <= self.val <= 10 and 
			(self.count > prev_bet.count or (self.val > prev_bet.val and self.count == prev_bet.count))
		)

	def __repr__(self):

		return str(self.count) + " x " + str(self.val)