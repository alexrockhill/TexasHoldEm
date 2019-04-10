import numpy as np
import time
from itertools import combinations


class Suit:

    def __init__(self, name):
        self.name = name
        self.color = 'red' if name in ['Hearts', 'Diamonds'] else 'black'

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name < other.name  # Alphabetical for consistent ordering

    def __hash__(self):
        return hash(self.name)


class Name:

    name_dict = {'Ace': 14, 'King': 13, 'Queen': 12, 'Jack': 11}

    def __init__(self, name):
        self.name = str(name)
        self.number = self.name_dict[name] if name in self.name_dict else int(name)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return self.number == other.number

    def __lt__(self, other):
        return self.number < other.number

    def __hash__(self):
        return hash(self.__repr__())


class Card:

    def __init__(self, name, suit):
        self.name = Name(name)
        self.suit = Suit(suit)
        self.display = None

    def __repr__(self):
        return '%s of %s' % (self.name, self.suit)

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return self.name == other.name and self.suit == other.suit

    def __lt__(self, other):
        if self.name == other.name:
            return self.suit < other.suit
        else:
            return self.name < other.name

    def __hash__(self):
        return hash(self.__repr__())


class Hand:

    number_dict = {14: 'Ace', 13: 'King', 12: 'Queen', 11: 'Jack'}

    def __init__(self, cards):
        if len(cards) != Deck.hand_n:
            raise ValueError('Wrong number of cards')
        self.cards = sorted(cards)[::-1]
        self.suits = {}
        self.numbers = {}
        for card in cards:
            if card.suit.name in self.suits:
                self.suits[card.suit.name] += 1
            else:
                self.suits[card.suit.name] = 1
            if card.name.number in self.numbers:
                self.numbers[card.name.number] += 1
            else:
                self.numbers[card.name.number] = 1
        self.score = self._score()

    def __repr__(self):
        return (', '.join([card.__repr__()
                           for card in self.cards]))

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return all([this_card == other_card for this_card, other_card in
                    zip(self.cards, other.cards)])

    def __lt__(self, other):
        for s0, s1 in zip(self.score[::-1], other.score[::-1]):
            if s0 == s1:
                continue
            else:
                return s0 < s1
        return False

    def __hash__(self):
        return hash(self.__repr__())

    def _score(self):
        return (self.high_card(), self.pair(), self.two_pair(), self.three(), self.straight(), self.flush(),
                self.full_house(), self.four(), self.straight() * self.flush())

    def flush(self):
        return (max(self.numbers.keys()) if
                max(self.suits.values()) == Deck.hand_n else 0)

    def straight(self):
        return (self.cards[0].name.number if
                all([self.cards[i].name.number - 1 == self.cards[i + 1].name.number
                     for i in range(Deck.hand_n - 1)]) else 0)

    def four(self):
        return (max(self.numbers, key=self.numbers.get)
                if max(self.numbers.values()) == 4 else 0)

    def full_house(self):
        return (Deck.n_names * max(self.numbers, key=self.numbers.get) +
                min(self.numbers, key=self.numbers.get)
                if max(self.numbers.values()) == 3 and min(self.numbers.values()) == 2 else 0)

    def three(self):
        return max(self.numbers, key=self.numbers.get) if max(self.numbers.values()) == 3 else 0

    def two_pair(self):
        one_pair = 0
        for k, v in self.numbers.items():
            if v == 2:
                if one_pair > 0:
                    if one_pair > k:
                        return Deck.n_names * one_pair + k
                    else:
                        return Deck.n_names * k + one_pair
                else:
                    one_pair = k
        return 0

    def pair(self):
        for k, v in self.numbers.items():
            if v == 2:
                return k
        return 0

    def high_card(self):
        return sum([(Deck.n_names ** (Deck.hand_n - i)) * card.name.number for
                    i, card in enumerate(self.cards)])

    def number_to_name(self, number):
        if number <= Deck.n_names + 1:
            return self.number_dict[number] if number in self.number_dict else number
        else:
            name0 = self.number_to_name(number // Deck.n_names)
            name1 = self.number_to_name(number % Deck.n_names)
            return name0, name1

    def get_text(self):
        straight, flush, four, three, pair = self.straight(), self.flush(), self.four(), self.three(), self.pair()
        full_house = self.full_house()
        two_pair = self.two_pair()
        if straight and flush:
            return '%s high straight flush' % self.number_to_name(straight)
        elif four:
            return 'Four %ss' % self.number_to_name(four)
        elif full_house:
            return 'Full house {}s full of {}s'.format(*self.number_to_name(full_house))
        elif flush:
            return 'Flush, %s high' % self.number_to_name(flush)
        elif straight:
            return 'Straight %s high' % self.number_to_name(straight)
        elif three:
            return 'Three %ss' % self.number_to_name(three)
        elif two_pair:
            return 'Two pair {}s and {}s'.format(*self.number_to_name(two_pair))
        elif pair:
            return 'Pair of %ss' % self.number_to_name(pair)
        else:
            return 'High card %s' % self.number_to_name(max(self.numbers))


class Deck:

    suits = ['Hearts', 'Clubs', 'Spades', 'Diamonds']
    names = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
    n_names = 13
    N = 52
    hand_n = 5
    deal_n = 2

    def __init__(self, mc_delta=0.01):
        np.random.seed(int(int(1e5 * time.time()) % 1e5))
        self.mc_delta = mc_delta
        self.cards = set([Card(name, suit) for suit in self.suits for name in self.names])

    def random_cards(self, n):
        n_combos = int(fac(len(self.cards)) / (fac(n) * fac(len(self.cards) - n)))
        index = np.random.randint(n_combos)
        for i, v in enumerate(combinations(self.cards, n)):
            if i == index:
                self.cards = self.cards.difference(set(v))
                return v
        return

    def score_holdem(self, deal, table_cards=None, n_other_players=1, other_deals=None):
        if table_cards is None:
            table_cards = tuple()

        def get_mc_delta(old, this):
            new = np.add(old, this)
            return new, 1 if not old.sum() else sum(abs(new / new.sum() - old / old.sum()))

        this_cards = self.cards.difference(deal).difference(set(table_cards))
        for other_deal in [] if other_deals is None else other_deals:
            this_cards = this_cards.difference(set(other_deal))
        mc_delta = 1
        result = np.array([0, 0, 0])  # wins, losses, draws
        while mc_delta > self.mc_delta or (not result.all() and result.sum() < 1/self.mc_delta):
            this_result = self.mc(deal, table_cards, this_cards, n=n_other_players, other_deals=other_deals)
            result, mc_delta = get_mc_delta(result, this_result)
        return result / result.sum()

    def mc(self, deal, table_cards, cards, n=None, other_deals=None):
        if other_deals is None:
            other_deals = np.random.choice(list(cards), self.deal_n*n)
            cards = cards.difference(other_deals)
            other_deals = [tuple(other_deals[i:i+2]) for i in 2*np.arange(n)]
        next_table_cards = tuple(np.random.choice(list(cards), self.hand_n - len(table_cards)))
        other_hands = [self.get_best_hand(other_deal + table_cards + next_table_cards)
                       for other_deal in other_deals]
        this_hand = self.get_best_hand(deal + table_cards + next_table_cards)
        loss = any([other_hand > this_hand for other_hand in other_hands])
        win = all([this_hand > other_hand for other_hand in other_hands])
        return np.array([win, loss, (not win and not loss)])

    def get_best_hand(self, cards):
        return max([Hand(c) for c in combinations(cards, self.hand_n)])


class Player:

    names = ['Tacko', 'Kirby', 'Nicki', 'Matt', 'Walker', 'Alex', 'Ian', 'Zion',
             'Alik', 'Darin', 'Nick', 'Ranger', 'Ginger', 'Francis', 'Marcello',
             'Fabio', 'Rick', 'Bradley', 'Sasquatch']

    def __init__(self, name=None, cash=500, ai=None):
        self.name = np.random.choice(self.names) if name is None else name
        self.ai = ai
        self.cash = cash
        self.has_folded = False
        self.bet = 0
        self.deal = None
        self.predicted = None
        self.actual = None

    def fold(self):
        self.has_folded = True

    def set_deal(self, deal):
        self.has_folded = False
        self.bet = 0
        self.deal = deal

    def make_bet(self, amount):
        self.cash -= amount
        self.bet += amount
        return amount

    def zero_bet(self):
        self.bet = 0


class Game:

    def __init__(self, players, small_blind=1, big_blind=5,  gui=None):
        self.players = players
        self.n_players = len(players)
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.gui = gui
        self.hands = 0
        self.turn = 0
        self.dealer = 0
        self.table_cards = self.pot = self.deck = self.current_human = self.raise_player = None

    def new_game(self):
        self.hands += 1
        self.pot = 0
        self.turn = self.dealer
        self.table_cards = tuple()
        self.deck = Deck()
        for player in self.players:
            if player.cash > 0:
                player.set_deal(self.deck.random_cards(2))
            else:
                player.set_deal(None)
            if player.ai:
                player.ai.new_game(player.deal)
        self.set_current_human()
        self.update_percentages()
        if self.gui is not None:
            self.gui.draw_new_game()
        self.blinds()
        if self.players[self.turn].ai:
            self.get_ai_response()

    def blinds(self):
        self.next_player()
        self.pot += self.players[self.turn].make_bet(min([self.players[self.turn].cash, self.small_blind]))
        self.next_player()
        self.pot += self.players[self.turn].make_bet(min([self.players[self.turn].cash, self.big_blind]))
        self.raise_player = self.turn
        self.next_player()
        self.send_to_gui('update_turn')
        if self.hands % self.n_players == 0 and self.hands > 0:
            self.small_blind *= 2
            self.big_blind *= 2

    def set_current_human(self):
        if any([not player.ai for player in self.players]):
            self.current_human = self.turn
            while self.players[self.current_human].ai:
                self.current_human = (self.current_human + 1) % self.n_players

    def send_to_gui(self, func, *args):
        if self.gui is None:
            if func == 'update_game_text' or func == 'hand_over':
                print(args[0])
                if func == 'hand_over':
                    print(', '.join(['%s: %s' % (player.name, player.cash) for player in self.players]))
            elif func == 'draw_winner':
                print('%s wins!' % args[0].name)
        else:
            getattr(self.gui, func)(*args)

    def get_bet(self):
        return max([player.bet for player in self.players])

    def fold(self):
        player = self.players[self.turn]
        self.send_to_gui('update_game_text', '%s folds' % player.name)
        player.fold()
        self.update_percentages()
        self.send_to_gui('update_fold')
        for player in self.players:
            if player.ai:
                player.ai.update_turn(player.name, 'fold')
        self.increment_turn()

    def checkcall(self):
        amount = self.get_bet() - self.players[self.turn].bet
        if amount < self.players[self.turn].cash or amount == 0:
            self.send_to_gui('update_game_text', '%s %s' % (self.players[self.turn].name,
                                                            'calls' if amount > 0 else 'checks'))
        self.make_bet(amount)

    def make_bet(self, amount=None):
        if amount is None:
            amount = self.gui.get_bet()
        player = self.players[self.turn]
        if amount > player.cash:
            amount = player.cash
        if amount + player.bet > self.get_bet() or amount == player.cash:
            if amount + player.bet > self.get_bet():
                self.raise_player = self.turn
            if amount > 0:
                if amount == player.cash:
                    self.send_to_gui('update_game_text', '%s all in %i' % (player.name, amount))
                else:
                    self.send_to_gui('update_game_text', '%s raises %i' % (player.name, amount))
        elif amount + player.bet < self.get_bet():
            if player.ai:
                self.send_to_gui('update_game_text', '%s ai failed; bet too low, folding' % player.name)
                player.fold()
            elif self.gui is not None:
                self.send_to_gui('set_bet_entry')
                return
        self.pot += player.make_bet(amount)
        for player in self.players:
            if player.ai:
                player.ai.update_turn(player.name, ('bet', amount))
        self.increment_turn()

    def increment_turn(self):
        if self.raise_player is None and not self.players[self.turn].has_folded:
            self.raise_player = self.turn
        self.next_player()
        winner = self.check_all_fold()
        if winner is None:
            if self.check_all_call():
                if len(self.table_cards) == Deck.hand_n:
                    self.hand_over()
                else:
                    self.next_table_cards()
                    self.next_turn()
            else:
                self.next_turn()
        else:
            self.hand_over(winner)

    def next_turn(self):
        self.send_to_gui('update_turn')
        if self.players[self.turn].cash == 0:  # all in
            self.checkcall()
        if self.players[self.turn].ai:
            self.get_ai_response()

    def next_player(self):
        self.turn = (self.turn + 1) % self.n_players
        while self.players[self.turn].has_folded or self.players[self.turn].deal is None:
            self.turn = (self.turn + 1) % self.n_players

    def get_ai_response(self):
        player = self.players[self.turn]
        response = player.ai.make_decision(player.predicted)
        if response == 'fold':
            self.fold()
        elif response in ['check', 'call']:
            self.checkcall()
        elif len(response) == 2 and response[0] == 'bet':
            if response[1] > 0:
                self.make_bet(response[1])
            else:
                self.checkcall()
        else:
            print('unrecognized response %s, folding' % response)
            self.fold()

    def update_percentages(self):
        for player in self.players:
            if not player.has_folded and player.deal is not None:
                if player.ai or (self.gui is not None and self.gui.show_predicted):
                    player.predicted = self.deck.score_holdem(player.deal, self.table_cards,
                                                              n_other_players=self.n_players-1)
                if not player.ai and self.gui is not None and self.gui.show_actual:
                    other_deals = [p.deal for p in self.players if p is not player and p.deal is not None]
                    player.actual = self.deck.score_holdem(player.deal, self.table_cards, other_deals=other_deals)

    def hand_over(self, winner=None):
        if winner is None:
            winner, winning_hand = self.get_winner()
            winner_text = '%s %s' % (winning_hand.get_text(), winner.name)
        else:
            winner_text = 'Everyone else folded, %s wins' % winner.name
        winner.cash += self.pot
        self.send_to_gui('hand_over', winner_text)
        self.dealer = (self.dealer + 1) % self.n_players
        while not self.players[self.dealer].cash:
            self.dealer = (self.dealer + 1) % self.n_players
        info = {'winner': {winner.name: winner.deal},
                'losers': {player.name: player.deal for player in self.players if player is not winner},
                'pot': self.pot, 'folded': [player for player in self.players if player.has_folded]}
        for player in self.players:
            if player.ai:
                player.ai.update_result(info)
        if sum([player.cash > 0 for player in self.players]) > 1:
            self.new_game()
        else:
            self.send_to_gui('draw_winner', winner)

    def check_all_call(self):
        current_bet = self.get_bet()
        return (all([player.bet == current_bet or player.cash == 0
                     for player in self.players if not player.has_folded and player.deal is not None]) and
                self.turn == self.raise_player)

    def check_all_fold(self):
        players_in = [player for player in self.players if not player.has_folded and player.deal is not None]
        if len(players_in) == 1:
            return players_in[0]
        return None

    def get_winner(self):
        players_in = [player for player in self.players if player.deal is not None]
        hands_in = {player: self.deck.get_best_hand(player.deal + self.table_cards) for player in players_in}
        winner = max(hands_in, key=hands_in.get)
        return winner, hands_in[winner]

    def next_table_cards(self):
        self.raise_player = None
        if len(self.table_cards) == 0:
            new_cards = self.deck.random_cards(n=3)
            self.send_to_gui('update_game_text', 'The flop is %s' % ', '.join([c.__repr__() for c in new_cards]))
            self.table_cards += new_cards
        elif len(self.table_cards) < 5:
            new_cards = self.deck.random_cards(n=1)
            self.send_to_gui('update_game_text', 'The %s is %s' % ('turn' if len(self.table_cards) == 3 else 'river',
                                                                   ', '.join([c.__repr__() for c in new_cards])))
            self.table_cards += new_cards
        self.update_percentages()
        for player in self.players:
            player.zero_bet()
            if player.ai:
                player.ai.update_table_cards(self.table_cards)
        self.send_to_gui('draw_table_cards')


def fac(x):
    if x <= 0:
        return 1
    else:
        return fac(x - 1) * x
