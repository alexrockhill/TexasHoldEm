import numpy as np
from importlib import import_module
from TexasHoldem import Card, Hand, Deck, Player, Game


def test_game():
    cash = 10
    ai_name = 'AI.DefaultTexasHoldemAI'
    n_players = 5
    names = np.random.choice(Player.names, n_players, replace=False)
    players = [Player(ai=import_module(ai_name).TexasHoldemAI(names[i], cash, names), name=names[i], cash=cash)
               for i in range(n_players)]
    game = Game(players)
    game.new_game()


def test_deck():
    deal0 = (Card('Ace', 'Spades'), Card(9, 'Hearts'))
    deal1 = (Card(2, 'Diamonds'), Card(4, 'Clubs'))
    table_cards = (Card('Ace', 'Diamonds'), Card(4, 'Spades'), Card('Ace', 'Hearts'),
                   Card(7, 'Clubs'), Card(9, 'Clubs'))
    deck = Deck()
    hand0 = deck.get_best_hand(deal0 + table_cards)
    hand1 = deck.get_best_hand(deal1 + table_cards)
    assert hand0 > hand1
    assert hand0.get_text() == 'Full house Aces full of 9s'
    assert hand1.get_text() == 'Two pair Aces and 4s'
    deck.random_cards(2)


if __name__ == '__main__':
    test_deck()
    test_game()
