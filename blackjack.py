import random

class Game():
    def __init__(self):
        self.players = []
        self.deck = generate_deck()
        self.playernames = []
    def add_player(self, playername, money):
        self.players.append(Player(playername, money))
        self.playernames.append(playername)
    def start_game(self):
        self.players.append(Dealer())
        list = []
        for a in self.players:
            list.append(self.deck.pop())
            list.append(self.deck.pop())
            a.hand.append(list)
            list = []
    def addbet(self, name, bet):
        #returns True if succeeded, False if not enough money
        for a in self.players:
            if name == a.name:
                if bet > a.money:
                    return False
                else:
                    a.bet += bet
                    a.money -= bet
                    return True



class Player():
    def __init__(self, name, money):
        self.name = name
        self.money = money
        self.hand = []
        self.bet = 0
    def show_hand(self):
        if len(self.hand) == 1:
            return str(self.hand[0]).strip("][").replace("'","")
class Dealer(Player):
    def __init__(self):
        self.name = 'dealer'
        self.hand = []


def generate_deck():
    deck = []
    suits = ['♣','♦','♥','♠']
    numbers = ['1','2','3','4','5','6','7','8','9','10','J','Q','K','A']

    for a in numbers:
        for b in suits:
            deck.append(a+b)

    random.shuffle(deck)
    return deck

