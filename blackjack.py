import random
import money

class Game():
    def __init__(self, dict, dpl):
        self.channel = dict['channel']  #to make sure commands from that channel are registered.
        self.state = 'just_started'
        self.dpl = dpl
        self.players = {}
        self.dealer = Dealer()
        self.turnorder = []
        self.endgame_processing_order = []  #This list remains untouched until endgame when scores are tabulated
        self.bets_remaining = []
        self.add_player(dict)   #Adds the person who initiated the game
    def lower_keys(self):   #generates a list of player names in .lower()
        keys = []
        for a in self.players.keys():
            keys.append(a.lower())
        return keys
    def generate_deck(self, number):
        deck = []
        suits = ['♣','♦','♥','♠']
        numbers = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        for a in numbers:
            for b in suits:
                deck.append(a+b)
        deck = [a+b for a in numbers for b in suits for c in range(number)]
        random.shuffle(deck)
        return deck
    def generate_bets_remaining(self):
        bets = []
        for a in self.turnorder:
            bets.append(a)
        return bets
    def set_bet(self, dict): #Used during the betting phase
        try:
            bet = int(dict['message'])
        except:
            return
        if bet > self.players[dict['name']].money:
            dict['message'] = 'You don\'t have enough money!'
            return dict
        elif bet < 1:
            dict['message'] = 'Error: Invalid number.'
            return dict
        else:
            self.players[dict['name']].bet = bet
            self.players[dict['name']].money -= bet
            del self.bets_remaining[self.bets_remaining.index(dict['name'])]
            if len(self.bets_remaining) < 1:
                self.state = 'main'
                dict['message'] = self.start_game(dict)
                return dict
    def deal_cards(self):   #For use at start of game
        for a in self.players.keys():
            list = []
            list.append(self.deck.pop())
            list.append(self.deck.pop())
            self.players[a].hand.append(list)
        list = []
        list.append(self.deck.pop())
        list.append(self.deck.pop())
        self.dealer.hand.append(list)
    def start_game(self, dict):
        if len(self.lower_keys()) <= 4:
            self.deck = self.generate_deck(1)
        elif len(self.lower_keys()) in range(5,9):
            self.deck = self.generate_deck(2)
        else:
            self.deck = self.generate_deck(8)
        self.deal_cards()
        buffer = ''
        for a in self.turnorder:
            buffer += self.players[a].name + ' (%d): ' %(self.players[a].active_hand_value()) + self.players[a].print_hand() + '\r\n%s %s :' %(dict['type'], dict['channel'])
        buffer += self.dealer.name + ': ' + self.dealer.peek() + '\r\n%s %s :$hit, $doubledown, $split, $stand or $quit.' %(dict['type'], dict['channel'])
        return buffer
    def add_player(self, dict):
        a = money.Money(self.dpl)
        #Be careful, the name is NOT in .lower()!
        name = dict['name']
        amount = a.check(name)
        #A person who is broke cannot join
        if amount < 1:
            dict['message'] = 'Error, player has no money!'
            return dict
        #A person who has already joined cannot join again.
        elif not name.lower() in self.lower_keys():
            self.players[name] = Player(name, amount)
            self.turnorder.append(name)
            self.endgame_processing_order.append(name)
    def dealer_draw(self):
        while self.dealer.active_hand_value() < 17:
            self.dealer.hand[0].append(self.deck.pop())
        if self.dealer.active_hand_value() > 21:
            self.dealer.bust = True
    def hit(self, dict):
        if dict['message'].startswith('$doubledown'):
            must_stand = True
        else:
            must_stand = False
        name = dict['name']
        player = self.players[name]
        player.hand[player.active_hand_number - 1].append(self.deck.pop())
        hand_value = player.active_hand_value()
        buffer = '%s (%d): %s' %(name, hand_value, player.print_hand())
        if hand_value > 21:
            buffer += '\r\n%s %s :Busted!\r\n%s %s :' %(dict['type'], dict['channel'], dict['type'], dict['channel'])
            dict['message'] = buffer
            return self.stand(dict)
        elif must_stand:
            buffer += '\r\n%s %s :' %(dict['type'], dict['channel'])
            dict['message'] = buffer
            return self.stand(dict)
        else:
            dict['message'] = buffer
            return dict
    def doubledown(self, dict):
        name = dict['name']
        player = self.players[name]
        if player.active_hand_number == 1:
            bet = player.bet
        elif player.active_hand_number == 2:
            bet = player.bet2
        if player.money < bet:
            dict['message'] = 'You don\'t have enough money!'
            return dict
        else:
            player.money -= bet
            if player.active_hand_number == 1:
                player.bet = player.bet * 2
            elif player.active_hand_number == 2:
                player.bet2 = player.bet2 * 2
            return self.hit(dict)
    def split(self, dict):
        name = dict['name']
        player = self.players[name]
        tens = ['1', 'J', 'Q', 'K']
        if player.splitted:
            dict['message'] = 'Error: You can only split once!'
            return dict
        elif player.money < player.bet:
            dict['message'] = 'You don\'t have enough money!'
            return dict
        elif not len(player.hand[0]) == 2:
            dict['message'] = 'Error: You can only split on your first turn!'
            return dict
        elif (not player.hand[0][0][0] == player.hand[0][1][0]) and not (player.hand[0][0][0] in tens and player.hand[0][1][0] in tens):
            dict['message'] = 'Error: You can only split when both card values are the same!'
            return dict
        else:
            bet = player.bet
            player.splitted = True
            self.turnorder.insert(0, name)
            player.money -= bet
            player.bet2 = bet
            list = [player.hand[0][1]]
            player.hand.append(list)
            del player.hand[0][1]
            buffer = ''
            for i,a in enumerate(player.hand):
                player.hand[i].append(self.deck.pop())
                buffer += '%s (%d): %s\r\n%s %s :' %(name, player.active_hand_value(), player.print_hand(), dict['type'], dict['channel'])
                if i == 0:
                    player.active_hand_number = 2
                else:
                    player.active_hand_number = 1
            buffer += 'Hand has been split. $hit, $doubledown or $stand.'
            dict['message'] = buffer
            return dict
    def stand(self, dict):
        if not dict['message'].startswith('$stand'):    #suggests that this method was called by a $hit or $doubledown
            buffer = dict['message']
        else:
            buffer = ''
        if self.players[self.turnorder[0]].splitted: #To switch splitted player's hand
            hand_number = self.players[self.turnorder[0]].active_hand_number
            if hand_number == 1:
                self.players[self.turnorder[0]].active_hand_number = 2
            else:
                self.players[self.turnorder[0]].active_hand_number = 1
        del self.turnorder[0]
        if len(self.turnorder) > 0:
            name = self.turnorder[0]
            player = self.players[name]
            hand_value = player.active_hand_value()
            buffer += '%s\'s turn!\r\n%s %s :%s (%d): %s' %(name, dict['type'], dict['channel'], name, hand_value, player.print_hand())
            dict['message'] = buffer
            return dict
        else:   #Remember to insert 'endgame' function.
            dict['message'] = buffer
            return self.end_game(dict)
    def end_game(self, dict):
        nextline = '\r\n%s %s :' %(dict['type'], dict['channel'])
        buffer = dict['message']
        self.dealer_draw()
        buffer += 'All players have played!' + nextline
        for a in self.endgame_processing_order:
            self.process_score(self.players[a])
            buffer += '%s (%d): %s' %(a, self.players[a].active_hand_value(), self.players[a].print_hand()) + nextline
            if self.players[a].splitted:
                self.players[a].active_hand_number = 2
                buffer += '%s (%d): %s' %(a, self.players[a].active_hand_value(), self.players[a].print_hand()) + nextline
        buffer += '%s (%d): %s' %('Dealer', self.dealer.active_hand_value(), self.dealer.print_hand()) + nextline
        buffer += 'Here\'s the amount of money you have left:' + nextline
        a = money.Money(self.dpl)
        for b in self.endgame_processing_order:
            buffer += '%s: %d' %(b, self.players[b].money) + nextline
            a.set(b, self.players[b].money)
        list = self.endgame_processing_order
        self.endgame_processing_order = []
        self.players = {}
        self.turn_order = []
        self.state = 'join_phase'
        self.dealer = Dealer()
        for b in list:
            amount = a.check(b.lower())
            if amount > 0:
                self.players[b] = Player(b, amount)
                self.turnorder.append(b)
                self.endgame_processing_order.append(b)
        buffer += 'Players who are broke have been kicked. Press $join, $start or $quit.'
        dict['message'] = buffer
        return dict
    def process_score(self, player):
        if player.splitted:
            list = range(2)
        else:
            list = range(1)
        for i,a in enumerate(list):
            #If bust, money definitely lost
            if player.active_hand_value() > 21:
                if i == 0:
                    player.bet = 0
                else:
                    player.bet2 = 0
            elif self.dealer.active_hand_value() == player.active_hand_value():
                #Also includes scenario where both dealer and player has blackjack.
                if i == 0:
                    player.money += player.bet
                    player.bet = 0
                else:
                    player.money += player.bet2
                    player.bet2 = 0
            elif player.active_hand_value() == 21:
                if i == 0:
                    player.money += 3 * player.bet
                    player.bet = 0
                else:
                    player.money += 3 * player.bet2
                    player.bet2 = 0
            elif player.active_hand_value() > self.dealer.active_hand_value() or self.dealer.bust:
                if i == 0:
                    player.money += 2 * player.bet
                    player.bet = 0
                else:
                    player.money += 2 * player.bet2
                    player.bet2 = 0
            elif player.active_hand_value() < self.dealer.active_hand_value():
                if i == 0:
                    player.bet = 0
                else:
                    player.bet2 = 0
            if len(list) > 1 and player.active_hand_number == 1:
                player.active_hand_number = 2
            elif len(list) > 1 and player.active_hand_number == 2:
                player.active_hand_number = 1
    def execute(self, dict):
        #Making sure only messages sent from the initiating channel are registered
        if not dict['channel'] == self.channel:
            return
        name = dict['name']
        command = dict['message']
        if self.state == 'just_started':
            self.state = 'join_phase'
            dict['message'] = '%s has started a game of blackjack! Feel free to $join! Once ready, press $start.' %(name)
            return dict
        elif self.state == 'join_phase' and command.startswith('$join'):
            return self.add_player(dict)
        #From here on, it only allows messages from in-game players.
        elif not name.lower() in self.lower_keys():
            return
        elif self.state == 'join_phase' and command.startswith('$start'):
            self.state = 'betting_phase'
            self.bets_remaining = self.generate_bets_remaining()
            dict['message'] = 'Players: ' + str(self.turnorder).strip('][').replace("\'", "") + '\r\n%s %s :Input your bets in integer numbers' %(dict['type'], self.channel)
            return dict
        elif self.state == 'betting_phase' and name in self.bets_remaining:
            return self.set_bet(dict)
        elif self.state == 'endgame' and command.startswith('$continue'):
            pass    #under construction
        elif len(self.turnorder) < 1:
            return
        elif self.state == 'main' and name == self.turnorder[0]:
            if command.startswith('$hit'):
                return self.hit(dict)
            elif command.startswith('$stand'):
                return self.stand(dict)
            elif command.startswith('$doubledown'):
                return self.doubledown(dict)
            elif command.startswith('$split'):
                return self.split(dict)
        





class Player():
    def __init__(self, name, money):
        self.name = name
        self.money = money
        self.hand = []
        self.bet = 0
        self.active_hand_number = 1 #For double-down
        self.double_downed = False
        self.splitted = False
    def hand_number(self):  #To clarify which hand the splitted player is playing
        if not self.splitted:
            return ''
        else:
            return ' (Hand number: %d)' %(self.active_hand_number)
    def print_hand(self):
        return str(self.hand[self.active_hand_number - 1]).strip('][').replace("\'", "") + self.hand_number()
    def active_hand_value(self):
        hand = self.hand[self.active_hand_number - 1]
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
            temp = []
            for a in options:
                if a < 22:
                    final.append(a)
                temp.append(a)  #Appends into temporary regardless, so that there is something in it in the event of a bust.
            if len(final) < 1:
                return min(temp)
            return max(final)

class Dealer(Player):
    def __init__(self):
        self.name = 'Dealer'
        self.hand = []
        self.active_hand_number = 1
        self.bust = False
        self.splitted = False
    def peek(self):
        return str(self.hand[self.active_hand_number - 1][0]).strip('][').replace("\'", "")
