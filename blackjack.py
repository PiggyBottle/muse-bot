import random

class Game():
    def __init__(self):
        self.players = []
        self.deck = generate_deck()
        self.playernames = []
        self.turnorder = []
    def add_player(self, playername, money):
        self.players.append(Player(playername, money))
        self.playernames.append(playername)
        self.turnorder.append(playername)
    def start_game(self):
        self.players.append(Dealer())
        self.turnorder.append('dealer')
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
    def player_hand(self, name):
        for a in self.players:
            if name == a.name:
                return a.show_hand()
    def main(self, name, command):
        for a in self.players:
            if a.name == name:
                if command.startswith('$hit'):
                    return a.hit(self.deck.pop())
                elif command.startswith('$stand'):
                    return (False, True)
    def dealer_draw(self):
        while self.players[len(self.players)-1].check_value(self.players[len(self.players)-1].hand[0]) < 17:
            self.players[len(self.players)-1].hand[0].append(self.deck.pop())
        self.dealer_hand_value = self.players[len(self.players)-1].check_value(self.players[len(self.players)-1].hand[0])
        print(self.dealer_hand_value)
        if self.dealer_hand_value > 21:
            self.dealer_bust = True
        else:
            self.dealer_bust = False
        for a in self.players[0:len(self.players)-1]:
            if self.dealer_bust == True:
                if a.check_value(a.hand[0]) == 21:
                    a.money += (a.bet * 3)
                    a.bet = 0
                elif a.bet != 0:
                    a.money += (a.bet * 2)
                    a.bet = 0
            elif self.dealer_hand_value == 21:
                if a.check_value(a.hand[0]) == 21:
                    a.money += a.bet
                    a.bet = 0
                else:
                    a.bet = 0
            else:
                if a.check_value(a.hand[0]) == 21:
                    a.money += (a.bet * 3)
                    a.bet = 0
                elif a.check_value(a.hand[0]) > self.dealer_hand_value:
                    a.money += (a.bet * 2)
                    a.bet = 0
                elif a.check_value(a.hand[0]) == self.dealer_hand_value:
                    a.money += a.bet
                    a.bet = 0
                else:
                    a.bet = 0
        return self.players[len(self.players)-1].show_hand()
    def generate_savedata(self):
        savedata = {}
        for a in self.players[0:len(self.players)-1]:
            savedata[a.name] = a.money
        return savedata
    def restart_game(self):
        self.deck = generate_deck()
        temp = []
        self.playernames = []
        self.betsremaining = []
        self.turnorder = []
        for a in self.players:
            if a.name == 'dealer':
                pass
            elif a.money == 0:
                pass
            else:
                a.hand = []
                self.betsremaining.append(a.name)
                self.playernames.append(a.name)
                temp.append(a)
                self.turnorder.append(a.name)
        self.players = []
        for a in temp:
            self.players.append(a)


class Player():
    def __init__(self, name, money):
        self.name = name
        self.money = money
        self.hand = []
        self.bet = 0
    def show_hand(self):
        if len(self.hand) == 1:
            return str(self.hand[0]).strip("][").replace("'","")
    def hit(self, card):
        self.hand[0].append(card)
        if self.check_value(self.hand[0]) < 22:
            bust_and_nextturn = (False, False)
        else:
            self.bet = 0
            bust_and_nextturn = (True, True)
        return bust_and_nextturn
    def check_value(self, hand):
        value = 0
        aces = 0
        for a in hand:
            #Elements with length 3 are definitely ten in value
            if len(a) == 3 or a[0] == 'J' or a[0] == 'Q' or a[0] == 'K':
                value += 10
            elif len(a) == 2:
                try:
                    #testing if single digit
                    value += int(a[0])
                except:
                    #card is an ace
                    aces += 1
        if aces == 0:
            return value
        else:
            #generates list of possibilities
            options = [value]
            while len(options) < 2**aces:
                temp = []
                for a in options:
                    temp.append(a)
                options = []
                for a in temp:
                    for b in [1,11]:
                        options.append(a+b)
            #filter those that are bust
            final = []
            for a in options:
                if a < 22:
                    final.append(a)
            #account for situation where all options are bust
            if len(final) < 1:
                return 22
            return max(final)
            



class Dealer(Player):
    def __init__(self):
        self.name = 'dealer'
        self.hand = []
    


def generate_deck():
    deck = []
    suits = ['♣','♦','♥','♠']
    numbers = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']

    for a in numbers:
        for b in suits:
            deck.append(a+b)

    random.shuffle(deck)
    return deck

