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
    joker = 14


class Card:

    def __init__(self, val, suit):

        self.val = val
        self.suit = suit

    def __repr__(self):

        if 2 <= self.val.value <= 10:
            return str(self.val.value) + "_of_" + str(self.suit.name)
        elif self.val == CardValue.joker:
            joker_color = 'black' if self.suit == Suit.spades else 'red'
            return "{0}_joker".format(joker_color)

        return str(self.val.name) + "_of_" + str(self.suit.name)

    # Returns string representations of all cards
    @staticmethod
    def get_all_cards(with_jokers=True):

        deck = [
            Card(card_val, suit) for card_val in CardValue for suit in Suit
            if card_val != CardValue.joker
        ]
        if with_jokers:
            joker_cards = Card(CardValue.joker, Suit.spades), Card(CardValue.joker, Suit.diamonds)
            deck += joker_cards
        return deck

