from tkinter import Tk, Canvas, Frame, Button, Entry, messagebox
from TexasHoldem import Deck, Player, Game
import numpy as np
import importlib, time


class TexasHoldemGUI(Frame):

    suit_coords = {'Hearts': [0.50, 0.00, 0.75, 0.50, 0.80, 0.70, 0.75, 0.90, 0.65, 0.80, 0.50, 0.50,
                              0.35, 0.80, 0.25, 0.90, 0.20, 0.70, 0.25, 0.50, 0.50, 0.00],
                   'Spades': [0.50, 0.90, 0.10, 0.25, 0.25, 0.15, 0.35, 0.20, 0.45, 0.25, 0.45, 0.00,
                              0.55, 0.00, 0.55, 0.25, 0.65, 0.20, 0.75, 0.15, 0.90, 0.25, 0.50, 0.90],
                   'Clubs': [0.50, 0.90, 0.35, 0.75, 0.45, 0.40, 0.35, 0.45,
                             0.20, 0.25, 0.40, 0.10, 0.45, 0.25, 0.45, 0.00,
                             0.55, 0.00, 0.55, 0.25, 0.60, 0.10, 0.80, 0.25,
                             0.65, 0.45, 0.55, 0.40, 0.65, 0.75, 0.50, 0.90],
                   'Diamonds': [0.50, 0.00, 0.75, 0.50, 0.50, 1.00, 0.25, 0.50, 0.50, 0.00]}

    def __init__(self, tk_root):
        self.root = tk_root
        Frame.__init__(self, self.root)
        self.width = self.root.winfo_screenwidth()*0.75
        self.height = self.root.winfo_screenheight()*0.75
        self.canvas = Canvas(self.root, width=self.width*1.1, height=self.height*1.1,
                             background='green')
        self.canvas.pack(fill='both', expand=True)
        size = min([self.height, self.width])
        self.card_size = [size/10, size/6]
        self.font = ('Helvetica', int(self.width/50))
        self.table_card_canvases = []
        self.fold_button = self.call_check_button = self.bet_button = self.bet_entry = self.pot_text = None
        self.show_predicted = self.show_actual = self.game_text = self.game_text_list = self.game = None
        self.n_human = None

    def start_game(self, n_players=5, cash=500, small_blind=1, big_blind=5,
                   show_predicted=True, show_actual=True, ai_names=None,
                   n_human=1):
        self.show_predicted = show_predicted
        self.show_actual = show_actual
        players = []
        if ai_names is None:
            names = np.random.choice(Player.names, n_players, replace=False)
        else:
            names = np.random.choice(Player.names, n_players - len(ai_names), replace=False) + list(ai_names.keys())
        for name in ai_names if ai_names is not None else []:
            players.append(Player(ai=importlib.import_module(name).TexasHoldemAI(name, cash, names),
                                  name=name, cash=cash))
        for i in range(n_human):
            players.append(Player(ai=False, name=names[i], cash=cash))
        self.n_human = n_human
        for i in range(len(players), n_players):
            players.append(
                Player(ai=importlib.import_module('DefaultTexasHoldemAI').TexasHoldemAI(names[-i], cash, names),
                       name=names[-i], cash=cash))
        self.game = Game(players, small_blind=small_blind, big_blind=big_blind,  gui=self)
        x0, y0, dy = (self.width-self.width/(int(n_players/2)+1))/self.width, 2./3, 1./9
        self.fold_button = self.get_button([x0, 1.0, y0, y0+dy], 'Fold', self.game.fold)
        self.call_check_button = \
            self.get_button([x0, 1.0, y0+dy, y0+2*dy], 'Call\t%s' % self.game.big_blind, self.game.checkcall)
        self.bet_button = self.get_button([x0, x0+(1.0-x0)/2, y0+2*dy, y0+3*dy], 'Bet', self.game.make_bet)
        self.bet_entry = self.get_entry([x0+(1.0-x0)/2, 1.0, y0+2*dy, y0+3*dy])
        self.pot_text = self.canvas.create_text(self.width*3/4, self.height/2, text='Pot\t0', fill='white',
                                                font=self.font)
        self.game_text = self.canvas.create_text(self.width/2, self.height*15/24, text='', fill='white', font=self.font)
        self.game_text_list = ['Game started']
        for i in range(Deck.hand_n):
            card_ratio = [self.card_size[0]/self.width*1.1, self.card_size[1]/self.height]
            table_card_canvas = self.get_canvas(card_ratio[0]*1.1*i + 1/4 - card_ratio[0]/2,
                                                card_ratio[0]*1.1*i + 1/4 + card_ratio[0]/2,
                                                1/2 - card_ratio[1]/2, 1/2 + card_ratio[1]/2,
                                                highlight=False)
            self.table_card_canvases.append(table_card_canvas)
        self.game.new_game()

    def draw_new_game(self):
        self.draw_deck()
        self.draw_players()
        self.player_up()
        self.set_bet_entry()
        self.update_dealer()
        self.root.update()

    def player_up(self):
        for player in self.game.players:
            if not player.has_folded:
                player.canvas.config({'highlightbackground': 'white'})
        self.game.players[self.game.turn].canvas.config({'highlightbackground': 'yellow'})
        self.canvas.itemconfig(self.pot_text, text='Pot\t%i' % self.game.pot)
        for player in self.game.players:
            player.canvas.itemconfig(player.cash_text, text='Cash %s' % player.cash)
            player.canvas.itemconfig(player.bet_text, text='Bet %s' % player.bet)
            if player.predicted is not None and not player.ai:
                w, l, d = player.predicted
                player.canvas.itemconfig(player.predicted_text,
                                         text='Predicted\nWin: %.2f\nLoss: %.2f\nDraw: %.2f' % (w, l, d))
            if player.actual is not None and not player.ai:
                w, l, d = player.actual
                player.canvas.itemconfig(player.actual_text,
                                         text='Actual\nWin: %.2f\nLoss: %.2f\nDraw: %.2f' % (w, l, d))
        self.root.update()

    def update_game_text(self, text):
        self.game_text_list.append(text)
        self.canvas.itemconfig(self.game_text, text=text)

    def hand_over(self, winner_text):
        for player in self.game.players:
            if not player.has_folded:
                self.draw_deal(player, up=True)
        self.root.update()
        self.game_text_list.append(winner_text)
        messagebox.showinfo('Hand Over', winner_text)
        for table_card_canvas in self.table_card_canvases:
            table_card_canvas.delete('all')
            table_card_canvas.config({'highlightbackground': 'green'})
        self.player_up()
        self.root.update()

    def update_turn(self):
        player = self.game.players[self.game.turn]
        if self.n_human > 1 and self.game.current_human == self.game.turn:
            name = self.game.players[self.game.turn].name
            this_game_text = [self.game_text_list[-1]]
            i = 2
            while i < len(self.game_text_list) + 1 and name not in self.game_text_list[-i]:
                this_game_text.append(self.game_text_list[-i])
                i += 1
            messagebox.showinfo('%s\'s turn' % name, '\n'.join(this_game_text[::-1]))
            self.draw_deal(player, up=True)
        elif self.n_human == 1 and self.game.current_human == self.game.turn:
            self.update_game_text('%s\'s turn' % player.name)
            self.draw_deal(player, up=True)
        call_amount = self.game.get_bet() - self.game.players[self.game.turn].bet
        call_check_text = 'Call\t%s' % call_amount if call_amount else 'Check'
        self.call_check_button.config(text=call_check_text)
        self.set_bet_entry()
        self.player_up()
        if not self.game.current_human == self.game.turn:
            time.sleep(0.5)

    def update_fold(self):
        player = self.game.players[self.game.turn]
        self.draw_deal(player, up=False)
        player.canvas.config({'highlightbackground': 'red'})

    def draw_card(self, card, canvas, x0, x1, y0, y1, up=True):
        dx = x1-x0
        dy = y1-y0
        canvas.create_rectangle(x0, y0, x1, y1, fill='white' if up else 'red', outline='white', tag=card.__repr__)
        if up:
            draw_suit(card.suit, canvas, x1 - dx / 2, x1 - dx / 3, y0 + dy / 5, y0 + dy / 3, card.__repr__(),
                      self.suit_coords[card.suit.name])
            draw_suit(card.suit, canvas, x0 + dx / 3, x0 + dx / 2, y1 - dy / 3, y1 - dy / 5, card.__repr__(),
                      self.suit_coords[card.suit.name])
            draw_name(card.name, canvas, x1 - dx / 4, y0 + dy / 4, card.__repr__(), card.suit.color)
            draw_name(card.name, canvas, x0 + dx / 4, y1 - dy / 4, card.__repr__(), card.suit.color)

    def draw_deck(self, delta=0.1):
        x0, x1 = self.width / 10, self.width / 10 + self.card_size[0]
        y0, y1 = self.height / 2 - self.card_size[1] / 2, self.height / 2 + self.card_size[1] / 2
        for i in range(min([5, len(self.game.deck.cards)])):
            self.canvas.create_rectangle(x0+i*(x1-x0)*delta, y0, x1+i*(x1-x0)*delta, y1, fill='red', outline='white')

    def draw_player(self, player, canvas, up=False):
        player.canvas = canvas
        player.height, player.width = float(player.canvas['height']), float(player.canvas['width'])
        player.x_center, player.y_center = player.width/2, player.height/2
        player.font = ('Helvetica', int(player.width/15))
        player.dealer_icon = None
        player.dealer_text = None
        player.canvas.create_text(player.x_center, player.height / 12, text=player.name, fill='white', font=player.font)
        self.draw_deal(player, up=up)
        self.updatables(player)

    def draw_winner(self, player):
        self.canvas.delete('all')
        self.canvas.create_text(self.width/2, self.height/2, text='%s wins!' % player.name)

    def draw_deal(self, player, up=True):
        self.draw_card(player.deal[0], player.canvas,
                       player.x_center-self.card_size[0]-player.width/100, player.x_center-player.width/100,
                       player.y_center+self.card_size[1]/2, player.y_center-self.card_size[1]/2,
                       up=up)
        self.draw_card(player.deal[1], player.canvas,
                       player.x_center+player.width/100,  player.x_center+self.card_size[0]+player.width/100,
                       player.y_center+self.card_size[1]/2, player.y_center-self.card_size[1]/2,
                       up=up)

    def updatables(self, player):
        if player.predicted is not None and not player.ai:
            player.predicted_text = \
                player.canvas.create_text(player.x_center/3, player.height/4, width=player.x_center-self.card_size[0],
                                          text='', fill='white')
        if player.actual is not None and not player.ai:
            player.actual_text = \
                player.canvas.create_text(player.x_center/3, player.height*3/4, width=player.x_center-self.card_size[0],
                                          text='', fill='white')
        player.cash_text = \
            player.canvas.create_text(5*player.x_center/3, player.height/4, width=player.x_center-self.card_size[0],
                                      text='Cash %s' % player.cash, fill='white')
        player.bet_text = \
            player.canvas.create_text(player.x_center, player.height*7/8, width=player.x_center-self.card_size[0],
                                      text='Bet %s' % player.bet, fill='white')
        player.dealer_icon = None
        player.dealer_text = None

    def update_dealer(self):
        for i, player in enumerate(self.game.players):
            if self.game.dealer == i:
                player.dealer_icon = \
                    player.canvas.create_oval(3*player.x_center/2, player.height*3/4+player.width/12,
                                              11*player.x_center/6, player.height*3/4-player.width/12,
                                              fill='red', width=0)
                player.dealer_text = \
                    player.canvas.create_text(5*player.x_center/3, player.height*3/4,
                                              width=player.x_center-self.card_size[0],
                                              text='D', fill='white')
            else:
                if player.dealer_icon is not None:
                    player.canvas.delete(player.dealer_icon)
                    player.dealer_icon = None
                if player.dealer_text is not None:
                    player.canvas.delete(player.dealer_text)
                    player.dealer_text = None

    def draw_players(self):
        def get_player_loc(j, n_players):  # clockwise order
            row = j > np.floor(n_players / 2) - 1
            n = int(np.ceil(n_players / 2)) if row else int(n_players / 2) + 1
            j = j - int(n_players / 2) if row else int(n_players / 2) - j - 1
            return j / n, (j + 1) / n, 0 if row else 2 / 3, 1 / 3 if row else 1
        for i, player in enumerate(self.game.players):
            self.draw_player(player, self.get_canvas(*get_player_loc(i, self.game.n_players)),
                             up=not player.ai and self.game.turn == i)

    def draw_table_cards(self):
        for i, card in enumerate(self.game.table_cards):
            self.table_card_canvases[i].config({'highlightbackground': 'white'})
            self.draw_card(card, self.table_card_canvases[i], 0, self.card_size[0], self.card_size[1], 0)
        self.player_up()
        self.root.update()

    def get_bet(self):
        try:
            amount = int(self.bet_entry.get())
        except Exception as e:
            print(e)
            self.set_bet_entry()
            return
        return amount

    def set_bet_entry(self):
        self.bet_entry.delete(0, 'end')
        self.bet_entry.insert(0, max([2*self.game.big_blind, (2*self.game.get_bet())]))

    def get_canvas(self, x0, x1, y0, y1, highlight=True):
        canvas = Canvas(self.root, borderwidth=1, highlightbackground='white' if highlight else 'green',
                        height=(y1-y0)*self.height-self.height/100,
                        width=(x1-x0)*self.width-self.width/100, background='green')
        canvas.pack_propagate(0)
        canvas.place(x=x0*self.width, y=y0*self.height)
        return canvas

    def get_frame(self, x0, x1, y0, y1):
        frame = Frame(self.canvas, height=(y1-y0)*self.height-self.height/100, width=(x1-x0)*self.width-self.width/100)
        frame.pack_propagate(0)
        frame.place(x=x0*self.width, y=y0*self.height)
        return frame

    def get_button(self, loc, text, command):
        button = Button(self.get_frame(*loc), text=text, font=self.font)
        button.pack(fill='both', expand=1)
        button.configure(command=command)
        return button

    def get_entry(self, loc, default=None):
        entry = Entry(self.get_frame(*loc), font=self.font, justify='center')
        entry.pack(fill='both', expand=1)
        entry.focus_set()
        if default is not None:
            entry.insert(0, default)
        return entry


def draw_name(name, canvas, x0, y0, tag, color):
    canvas.create_text(x0, y0, text=name.name if len(name.name) < 3 else name.name[0], fill=color, tag=tag)


def draw_suit(suit, canvas, x0, x1, y0, y1, tag, coords):
    coords = [y0 + c * (y1 - y0) if i % 2 else x0 + c * (x1 - x0) for i, c in enumerate(coords)]
    canvas.create_polygon(coords, fill=suit.color, tag=tag)


if __name__ == '__main__':
    root = Tk()
    self = TexasHoldemGUI(root)
    self.start_game()
    root.mainloop()
