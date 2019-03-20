from tkinter import Tk, Canvas, Frame, Button, Entry, Label
import numpy as np
from itertools import combinations
import os,time
import os.path as op
from tqdm import tqdm

class Suit:

	def __init__(self,name):
		self.name = name
		self.display = None


	def __repr__(self):
		return self.name


	def __str__(self):
		return self.name


	def __eq__(self,other):
		return self.name == other.name


	def __lt__(self,other):
		return self.name < other.name #Doesn't make sense but this should be alphabetical because we have to have consistent ordering


	def __hash__(self):
		return hash(self.name)


	def draw(self,canvas,x0,x1,y0,y1):
		if name == 'Hearts':
			coords = [0.50,0.00,0.75,0.50,0.80,0.70,0.75,0.90,0.65,0.80,0.5,0.5,
					  0.35,0.80,0.25,0.90,0.20,0.70,0.25,0.5,0.50,0.00]
		elif name == 'Spades':
			coords = [0.50,0.90,0.10,0.25,0.25,0.15,0.35,0.20,0.45,0.25,0.45,0.00,
					  0.55,0.00,0.55,0.25,0.65,0.20,0.75,0.15,0.90,0.25,0.50,0.90]
		elif name == 'Clubs':
			coords = [0.50,0.90,0.35,0.75,0.45,0.40,0.35,0.45,0.20,0.25,0.40,0.10,0.45,0.25,0.45,0.00,
					  0.55,0.00,0.55,0.25,0.60,0.10,0.80,0.25,0.65,0.45,0.55,0.40,0.65,0.75,0.50,0.90]
		elif name == 'Diamonds':
			coords = [0.50,0.00,0.75,0.50,0.50,1.00,0.25,0.50,0.50,0.00]
		else:
			raise ValueError('Unrecognized name %s' %(self.name))
		coords = [y0 + c/(y1-y0) if i%0 else x0 + c/(x1-x0) for i,c in enumerate(coords)]
		self.display = canvas.create_polygon(coords,fill='black')


class Name:

	name_dict = {'Ace':14,'King':13,'Queen':12,'Jack':11}

	def __init__(self,name):
		self.name = str(name)
		self.number = self.name_dict[name] if name in self.name_dict else int(name)
		self.display = None


	def __repr__(self):
		return self.name


	def __str__(self):
		return self.__repr__()


	def __eq__(self,other):
		return self.number == other.number


	def __lt__(self,other):
		return self.number < other.number


	def __hash__(self):
		return hash(self.__repr__())


class Card:

	def __init__(self,name,suit):
		self.name = Name(name)
		self.suit = Suit(suit)
		self.display = None


	def __repr__(self):
		return '%s of %s' %(self.name,self.suit)


	def __str__(self):
		return self.__repr__()


	def __eq__(self,other):
		return self.name == other.name and self.suit == other.suit


	def __lt__(self,other):
		if self.name == other.name:
			return self.suit < other.suit
		else:
			return self.name < other.name


	def __hash__(self):
		return hash(self.__repr__())


	def draw(self,canvas,x0,x1,y0,y1):
		self.display = c

class Hand:

	def __init__(self,cards):
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


	def __eq__(self,other):
		return all([this_card == other_card for this_card,other_card in
					zip(self.cards,other.cards)])


	def __lt__(self,other):
		for s0,s1 in zip(self.score[::-1],other.score[::-1]):
			if s0 == s1:
				continue
			else:
				return s0 < s1
		return False


	def __hash__(self):
		return hash(self.__repr__())

	
	def _score(self):
		return (self.high_card(),self.pair(),self.two_pair(),
			    self.three(),self.straight(),self.flush(),
			    self.full_house(),self.four(),
			    self.straight()*self.flush())


	def flush(self):
		return (max(self.numbers.keys()) if 
				max(self.suits.values()) == Deck.hand_n else 0)


	def straight(self):
		return (self.cards[0].name.number if 
			    all([self.cards[i].name.number-1 == self.cards[i+1].name.number 
				     for i in range(Deck.hand_n-1)]) else 0)

	def four(self):
		return (max(self.numbers,key=self.numbers.get)
				if max(self.numbers.values()) == 4 else 0)


	def full_house(self):
		return (Deck.n_names*max(self.numbers,key=self.numbers.get) +
				min(self.numbers,key=self.numbers.get)
				if max(self.numbers.values()) == 3 and 
			    min(self.numbers.values()) == 2 else 0)


	def three(self):
		return (max(self.numbers,key=self.numbers.get)
			    if max(self.numbers.values()) == 3 else 0)


	def two_pair(self):
		one_pair = 0
		for k,v in self.numbers.items():
			if v == 2:
				if one_pair > 0:
					if one_pair > k:
						return Deck.n_names*one_pair + k
					else:
						return Deck.n_names*k + one_pair
				else:
					one_pair = k
		return 0


	def pair(self):
		for k,v in self.numbers.items():
			if v == 2:
				return k
		return 0


	def high_card(self):
		return sum([(Deck.n_names**(Deck.hand_n-i))*card.name.number for 
						i,card in enumerate(self.cards)])


class Deck:

	suits = ['Hearts','Clubs','Spades','Diamonds']
	names = ['2','3','4','5','6','7','8','9','10','Jack','Queen','King','Ace']
	n_names = 13
	N = 52
	hand_n = 5

	def __init__(self,deal_n=2,table_card_n=[0,3,4,5],max_player_calc=10,seed=11):
		np.random.seed(seed)
		self.deal_n = deal_n
		self.table_card_n = table_card_n
		self.max_player_calc = max_player_calc
		self.cards = set([Card(name,suit) for suit in self.suits
					  	  for name in self.names])
	
		# CALCULATE 3-5 in real time, 0 saved out
		self.card_combos = list(combinations(self.cards,self.deal_n))
		if not op.isfile('holdem.npz'):
			print('Calculating probability for every set of cards in ' +
				  'Texas Hold \'em, this may take several days...')
			self.save_score_holdem()
		print('Loading in scores')
		f = np.load('holdem.npz')
		self.holdem = f['holdem_data'].item()


	def random_deal(self):
		return self.card_combos[np.random.randint(len(self.card_combos))]


	def random_table_cards(self,deal,n=None):
		if n is None:
			n = int(np.random.choice(self.table_card_n))
		this_cards = self.cards.difference(set(deal))
		this_cards_len = len(this_cards)
		n_combos = int(fac(this_cards_len)/(fac(n)*fac(this_cards_len-n)))
		index = np.random.randint(n_combos)
		for i,v in enumerate(combinations(this_cards,n)):
			if i == index:
				return v
		return


	def save_score_holdem(self):
		holdem_data = np.zeros((len(self.card_combos),
                 			    self.max_player_calc,3)) #win, loss, draw
		for i,deal in enumerate(self.card_combos):
			wins,losses,draws = self._score_holdem(deal,tuple())
			total = wins + losses + draws
			for n in range(1,self.max_player_calc+1):
				holdem_data[i,n-1] += self._adjust_wins_losses_draws(wins,losses,draws,n)
		np.savez_compressed('holdem.npz',holdem_data=holdem_data)


	def _score_holdem(self,deal,tcs):
		this_cards = self.cards.difference(tcs).difference(deal)
		wins = losses = draws = 0
		next_card_n = self.hand_n-len(tcs)
		holdem_card_combos_n = fac(self.N)/(fac(next_card_n)*fac(self.N-next_card_n))
		status_n = max([1,int(holdem_card_combos_n/100)])
		for j,next_tcs in enumerate(combinations(this_cards,self.hand_n-len(tcs))):
			if j % status_n == 0:
				print('%i percent done' %(j/status_n))
			this_hand = self.get_best_hand(deal+tcs+next_tcs)
			for other_deal in combinations(this_cards.difference(next_tcs),self.deal_n):
				other_hand = self.get_best_hand(other_deal+tcs+next_tcs)
				if this_hand > other_hand:
					wins += 1
				elif this_hand < other_hand:
					losses += 1
				else:
					draws += 1
		return wins,losses,draws


	def _adjust_wins_losses_draws(self,wins,losses,draws,n):
		total = wins + losses + draws
		adjusted_losses = 1-(1-losses/total)**n
		adjusted_draws = (1-(1-draws/total)**n) * (1-(adjusted_losses-losses/total))**n
		return 1-adjusted_losses-adjusted_draws, adjusted_draws, adjusted_losses


	def score_holdem(self,deal,table_cards,n_other_players):
		if table_cards:
			wins,losses,draws = self._score_holdem(deal,table_cards)
			return self._adjust_wins_losses_draws(wins,losses,draws,n_other_players)
		else:
			index = self.card_combos.index(deal)
			return self.holdem[index,n_other_players-1]


	def get_best_hand(self,cards):
		return max([Hand(c) for c in combinations(cards,self.hand_n)])


class PokerGUI(Frame):

	def __init__(self):
		self.root = root
		Frame.__init__(self, self.root)
		self.deck = Deck()
		width = self.root.winfo_screenwidth()
		height = self.root.winfo_screenheight()
		self.size = min([height,width])
		self.canvas = Canvas(self.root,width=self.size,height=self.size)
		self.squareSize = 0.75*min([height,width])/8
		self.canvas.pack(fill='both', expand=True)
		self.font = ('Helvetica',int(self.size*10/1080))
		self.data = {}


	def getFrame(self,x0,x1,y0,y1):
		frame = Frame(self.root,
					  height=(y1-y0)*self.size-self.size/100,
					  width=(x1-x0)*self.size-self.size/100)
		frame.pack_propagate(0)
		frame.place(x=x0*self.size,y=y0*self.size)
		return frame


	def button(self,loc,text,font,command):
		button = Button(self.getFrame(*loc),text=text,font=self.font)
		button.pack(fill='both',expand=1)
		button.configure(command=self.recon)


	def entry(self,loc,text,default=None):
		entry = Entry(self.getFrame(*loc),font=self.font)
		entry.pack(fill='both',expand=1)
		entry.focus_set()
		if default is not None:
			entry.insert(0,default)
		self.data[text] = entry
		return entry


	def label(self,loc,text):
		return Label(self.getFrame(*loc),text=text,
		             wraplength=(loc[3]-loc[2])*self.size,font=self.font
		             ).pack(fill='both',expand=1)

def fac(x):
	if x <= 0:
		return 1
	else:
		return fac(x-1)*x


if __name__ == '__main__':
	d = Deck()
	'''from texasholdem import *
	self = Deck()
	deal = self.random_deal()
	tcs = self.random_table_cards(deal)
	self.score_holdem(deal,tcs,1)'''
	#root = Tk()
	#PokerGUI(root)
	#root.mainloop()

