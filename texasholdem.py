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
		self.name = name
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
		for s0,s1 in zip(self.score,other.score):
			if s0 != s1:
				return False
		return True

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
	table_card_n = 5
	pocket_n = 2
	max_player_calc = 10

	def __init__(self,seed=11):
		np.random.seed(seed)
		self.cards = set([Card(name,suit) for suit in self.suits
					  	  for name in self.names])
		if not op.isfile('hand_records.npz'):
			print('Calculating all hands and saving relative records, ' +
				  'this may take several minutes...')
			self.save_all_hands_records()
		print('Loading in hand records')
		f = np.load('hand_records.npz')
		self.hand_records = f['hand_records'].item()
		self.ranked_hands = f['ranked_hands']
		if not op.isfile('holdem.npz'):
			print('Calculating probability for every situation in ' +
				  'Texas Hold \'em, this may take several hours...')
			self.score_all()
		print('Loading in scores')
		self.scores = np.load('holdem.npz')['scores']

	def random_hand(self):
		return Hand(np.random.choice(self.cards,size=self.hand_n,replace=False))

	def all_hands(self):
		return [Hand(c) for c in combinations(self.cards,self.hand_n)]

	def save_all_hands_records(self):
		print('Getting all combinations of hands')
		all_hands = self.all_hands()
		total_n = len(all_hands)
		print('Ranking scores')
		ranked_hands = sorted(all_hands)
		print('Finding win loss draw records')
		j = 0
		hand_records = {}
		for i in tqdm(range(1,total_n+1)):
			if i == total_n or ranked_hands[i] != ranked_hands[i-1]:
				same = (i-j)
				for hand in ranked_hands[j:i]:
					hand_records[hand] = ((0,j),(i,total_n),(j,i)) #wins,losses,draws
				j = i
		print('Saving for next time')
		np.savez_compressed('hand_records.npz',hand_records=hand_records,
							ranked_hands=ranked_hands)


	def score_all(self):
		scores = {}
		n_hands = fac(self.N)/(fac(self.pocket_n)*fac(self.N-self.pocket_n))
		start_time = time.time()
		for i,cards in enumerate(combinations(self.cards,self.pocket_n)):
			print('%i/%i %s %s\t' %(i,n_hands,cards,time.time()-start_time))
			s_cards = set(cards)
			scores[cards] = {}
			for tc_n in range(self.table_card_n+1):
				for down_table_cards in combinations(
						self.cards.difference(cards),tc_n):
					s_down_table_cards = set(down_table_cards)
					scores[cards][down_table_cards] = \
								self.get_win_loss_draw_prob(s_cards,
									s_down_table_cards)
		np.savez_compressed('holdem.npz',scores=scores)
		

	def get_win_loss_draw_prob(self,cards,down_table_cards):
		wins = losses = draws = 0
		for possible_table_cards in combinations(self.cards.difference(
												 cards.union(down_table_cards)),
												 self.table_card_n-len(down_table_cards)):
			possible_table_cards = set(possible_table_cards)
			this_hand = self.get_best_hand(cards,down_table_cards.union(possible_table_cards))
			worse,better,same = (self.ranked_hands[i:j] for (i,j) in self.hand_records[this_hand])
			table_cards = cards.union(down_table_cards).union(possible_table_cards)
			for counter,hands in zip((wins,losses,draws),(worse,better,same)):
				self.remove_impossible(hands,table_cards)
				counter += len(hands)
		win_loss_draw_prob = {}
		total = wins + losses + draws
		for j,n_other_players in enumerate(range(1,self.max_player_calc+1)):
			draw_perc = 1 - (1-draws/total)**n_other_players
			loss_perc = 1 - (1-losses/total)**n_other_players #estimate: every player has roughly one shot to get a better hand
			win_perc = 1 - draw_perc - loss_perc
			win_loss_draw_prob[n_other_players] = (win_perc,draw_perc,loss_perc)
		
	def remove_impossible(self,hands,table_cards):
		remove_indices = []
		for i,hand in enumerate(hands):
			if any([card in table_cards for card in hand.cards]):
				remove_indices.append(i)
		hands = np.delete(hands,remove_indices)

	def n_mutually_exclusive(self,hands,n_other_players):
		if n_other_players == 1: # save some unnecessary computation
			return len(hands)
		n = 0
		for these_hands in combinations(hands,n_other_players):
			these_hands = set(these_hands)
			if not any([card in these_hands.difference(set([hand]))
					    for card in hand.cards for hand in these_hands]):
				n += 1
		return n

	def get_best_hand(self,cards,table_cards):
		return max([Hand(c) for c in combinations(cards.union(table_cards),
												  self.hand_n)])


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
	#root = Tk()
	#PokerGUI(root)
	#root.mainloop()


		
