import numpy as np
import time


class TexasHoldemAI:

    name = 'default'
    table_card_names = {0: 'pre-flop', 3: 'flop', 4: 'turn', 5: 'river'}

    def __init__(self, name, cash, players):
        np.random.seed(int(int(1e5 * time.time()) % 1e5))
        self.name = name
        self.players = players
        self.cashes = {player: cash for player in players}
        self.deal = self.pot = self.table_cards = None
        self.bluff_likelihood = np.random.random()
        self.big_bet_likelihood = np.random.random()
        self.check_threshold = 0.5
        self.big_bet = False
        self.bluffing = False
        self.current_bets = {}
        self.data = {}
        self.hands = 0

    def reset(self):
        self.bluffing = np.random.random() < self.bluff_likelihood
        self.big_bet = np.random.random < self.big_bet_likelihood

    def new_game(self, deal):
        self.deal = deal
        self.pot = 0
        self.table_cards = tuple()
        self.data[self.hands] = {'deal': self.deal}
        for player in self.players:
            self.data[self.hands][player] = {}

    def make_decision(self, predicted):
        w, l, d = predicted
        cash = self.cashes[self.name]
        this_bet = max(self.current_bets.values()) if self.current_bets else 0
        big_stack = (self.cashes[self.name] >
                     max([cash for player, cash in self.cashes.items() if player != self.name]) * 2)
        go_for_it = w > (self.check_threshold + this_bet/max([1, self.cashes[self.name]]))
        if go_for_it or self.bluffing or big_stack:
            if self.big_bet:
                amount = int(max([this_bet, cash / np.random.randint(2, 7)]))
            elif self.bluffing:
                amount = int(max([this_bet, cash / np.random.randint(4, 8)]))
            elif big_stack:
                amount = int(max([this_bet, cash / np.random.randint(15, 25)]))
            else:
                amount = int(max([this_bet, cash / np.random.randint(15, 25)]))
            self.pot += amount
            self.cashes[self.name] -= amount
            self.data[self.hands][self.name][self.table_card_names[len(self.table_cards)]] = amount
            return ['bet', amount]
        elif l > 0.9:
            self.data[self.hands][self.name][self.table_card_names[len(self.table_cards)]] = 'fold'
            return 'fold'
        else:
            self.data[self.hands][self.name][self.table_card_names[len(self.table_cards)]] = this_bet
            return 'call'

    def update_result(self, info):
        winner, deal = list(info['winner'].items())[0]
        self.data[self.hands][winner]['deal'] = deal
        self.data[self.hands]['winner'] = winner
        self.data[self.hands]['losers'] = []
        for loser, deal in info['losers'].items():
            self.data[self.hands][loser]['deal'] = deal
            self.data[self.hands]['losers'].append(loser)
        self.data[self.hands]['pot'] = info['pot']
        self.data[self.hands]['folded'] = info['folded']
        self.hands += 1

    def update_turn(self, name, response):  # store info about other players for learning
        if len(response) == 2 and response[0] == 'bet':
            amount = response[1]
            self.current_bets[name] = amount
            self.cashes[name] -= amount
            self.pot += amount
            self.data[self.hands][name][self.table_card_names[len(self.table_cards)]] = amount
        elif response == 'fold':
            self.data[self.hands][name][self.table_card_names[len(self.table_cards)]] = 'fold'
        else:
            print('Unrecognized response %s' % response)

    def update_table_cards(self, table_cards):
        self.table_cards = table_cards
        self.data[self.hands][self.table_card_names[len(table_cards)]] = \
            table_cards if len(table_cards) == 3 else table_cards[-1]
        self.current_bets = {}
