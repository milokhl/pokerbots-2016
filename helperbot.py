# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 20:16:46 2016

@author: mknowles
"""
import itertools
#from operator import attrgetter
#import time

class Card(object):
    def __init__(self, card_str):
        """
        Takes a card in the form of a string, ("6h") and makes a card object with value and suit
        self.value: 2-14
        self.suit: 'h','s','d','c'
        """
        #using a dictionary to assign the card an int value
        #NOTE: Ace can be high or low - we will need to account for this somehow
        card_value_dict = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, '10': 10, 'J':11, 'Q':12, 'K':13, 'A':14}
        self.value = card_value_dict[card_str[0]]
        self.suit = card_str[1]
        self.string = card_str
    
    def __cmp__(self, other):
        """
        This function is used for things like the sorted() function and comparing card objects.
        NOTE: compares cards only by VALUE
        """
        if self.value < other.value:
            return -1
        if self.value > other.value:
            return 1
        if self.value == other.value:
            return 0
    
    def __eq__(self, other):
        """
        This is used to check if a card is equal to another card.
        NOTE: compares both value AND suit
        """
        if self.value == other.value and self.suit == other.suit:
            return True
        else:
            return False
    
    def __repr__(self):
        """
        This tells python how to handle printing out a card object.
        """
        return self.string

#building a full deck
def build_full_deck():
    FULL_DECK = []
    card_value_list = ['2','3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q','K','A']

    for string in card_value_list:
        for suit in ['h', 's', 'd', 'c']:
            card_str = string + suit
            FULL_DECK.append(Card(card_str))
    return FULL_DECK
    
FULL_DECK = build_full_deck()

def update_deck(hand, board):
    """
    Removes all of the cards that have been dealt from the deck.
    Hand: the 4 cards in a players hand (list of Card objects)
    Table: the 3-5 cards on the table (list of Card objects)
    Returns: a list of all the card objects left in the deck
    """
    new_deck = FULL_DECK[:]
    for card in hand:
        if card in new_deck:
            new_deck.remove(card)
        
    for card in board:
        if card in new_deck:
            new_deck.remove(card)
    return new_deck


def is_straight(cardlist):
    try:
        if len(cardlist) != 5:
            raise "Error: CardList in is_straight does not contain 5 cards."
    except:
        pass
    
    hand_value_list = []
    for card in cardlist:
        if card.value not in hand_value_list:
            hand_value_list.append(card.value)
    
    if len(hand_value_list) != 5:
        return False
    
    if 14 in hand_value_list:
        alt_hand_value_list = hand_value_list[:]
        alt_hand_value_list.remove(14)
        alt_hand_value_list.append(1)

    if min(hand_value_list)+4 == max(hand_value_list):
        return True
    
    else:
        try:
            if min(alt_hand_value_list)+4 == max(alt_hand_value_list):
                return True
        except:
            pass
    
    return False
    
    
def generate_hand_combs_4(hand, board):
    """
    Returns: every possible 4-card combination of 2 hand-cards and 2 board-cards (this is used in several other functions)
    """
    #generate all 4-card combinations of 2 hand-cards and 2 board-cards
    hand_combs = list(itertools.combinations(hand, 2)) #NOTE: itertools.combinations returns each element in the form of a tuple
    board_combs = list(itertools.combinations(board, 2))
    
    play_card_combs = [] #this will end up being a list of lists 
    for i in hand_combs:
        for j in board_combs: #convert the tuple j into a list
            play_card_combs.append(list(i)+list(j)) #play_card_perms contains all of the 4-card combinations
    return play_card_combs

def generate_hand_combs_5(hand,board):
    """
    Returns: every possible 5-card combination of 2 hand-cards and 3 board-cards (this is used in several other functions)
    """
    #generate all 4-card combinations of 2 hand-cards and 3 board-cards
    hand_combs = list(itertools.combinations(hand, 2)) #NOTE: itertools.combinations returns each element in the form of a tuple
    board_combs = list(itertools.combinations(board, 3))
    
    play_card_combs = [] #this will end up being a list of lists 
    for i in hand_combs:
        for j in board_combs:
            play_card_combs.append(list(i) + list(j)) #play_card_perms contains all of the 4-card combinations
    return play_card_combs


def is_flush(cardList):
    suit_list = []
    for card in cardList:
        if card.suit not in suit_list:
            suit_list.append(card.suit)
    
    if len(suit_list)==1:
        return True
    return False

def is_threeofkind(cardList):
    value_list = []
    for card in cardList:
        value_list.append(card.value)
    
    for value in value_list:
        if value_list.count(value) >= 3:
            return (True, value)
    return (False, [])

def is_fullhouse(cardList):
    #because a hand can only have 5 cards, if the hand only has two distinct card values in it, there has to be a full house
    values = []
    for card in cardList:
        if card.value not in values:
            values.append(card.value)
    if len(values) == 2:
        return True
    else:
        return False
    
def is_straight_possible(BOARD):
    value_list = []
    for card in BOARD:
        value_list.append(card.value)
    if len(value_list) < 3:
        return False
    
    combs_three = []
    comb_three = list(itertools.combinations(value_list, 3))
    for comb in comb_three:
        combs_three.append(list(comb))
    
    for comb in combs_three:
        if min(comb) >= max(comb) - 4:
            return True
    return False
    
def is_flush_possible(BOARD, num=3):
    suit_list = []
    for card in BOARD:
        suit_list.append(card.suit)
    
    for suit in suit_list:
        if suit_list.count(suit) >= num:
            return True
    return False


class Holding(object):
    """
    Tells you what you're currently holding
    """
    def __init__(self, hand, board, Flush_Possible = True, Straight_Possible = True):
        self.hand = hand
        self.board = board
        
        play_card_values = []
        for card in hand + board:
            play_card_values.append(card.value)
        self.play_card_values = play_card_values
        
        self.play_card_combs = generate_hand_combs_5(self.hand,self.board)
        self.Flush_Possible = Flush_Possible
        self.Straight_Possible = Straight_Possible
        
    def best_hand(self, stopbeyond = 1):
        """
        Order:
        1.royal flush
        2.straight flush
        3. four of a kind
        4. full house
        5. flush
        6. straight
        7. three of kind
        8. two pair
        9. one pair
        10. high card
        """
        highcard = self.highcard()
        
        best_hand_val = [10,highcard]
        overall_best_hand_val = best_hand_val
        
        for comb in self.play_card_combs:
            #checking pair
            if self.has_pair(comb)['Has'] == True:
                next_pair = 0
                highest_pair = 0
                for key in self.has_pair(comb):
                    if key != 'Has': 
                        if key > highest_pair:
                            next_pair = highest_pair
                            highest_pair = key
                        else:
                            next_pair = key
                #best_hand = {'Pair': highest_pair}
                best_hand_val = [9,highest_pair,highcard]
                if stopbeyond > 9:
                    break
            
                #checking 3 of a kind
                if self.has_threeofkind(comb)['Has'] == True:
                    threeofkind_value = 0
                    for key in self.has_threeofkind(comb):
                        if key != 'Has':
                            threeofkind_value = key
                    best_hand_val = [7,threeofkind_value,highcard]
                    if stopbeyond > 7:
                        break
                    #checking full house
                    if self.has_fullhouse(comb) == True:
                        if threeofkind_value == highest_pair:
                            best_hand_val = [4, threeofkind_value, next_pair]
                        else:
                            best_hand_val = [4, threeofkind_value, highest_pair]
                        if stopbeyond > 4:
                            break
                    #checking four of a kind
                    if self.has_fourofkind(comb)[0] == True:
                        best_hand_val = [3,self.has_fourofkind(comb)[1],highcard]
                      
                #checking twopair
                elif self.has_twopair(comb)['Has'] == True:
                    best_hand_val = [8,highest_pair,next_pair]
                    if stopbeyond > 8:
                        break
                        
            #checking straight
            if self.Straight_Possible == True:
                if self.has_straight(comb) == True:
                    best_hand_val = [6, highcard]
                    if stopbeyond > 6:
                        break
                
            #checking flush
            if self.Flush_Possible == True:
                if self.has_flush(comb) == True:
                    best_hand_val = [5, highcard]
                    if stopbeyond > 5:
                        break
    
                #checking straight flush
                if self.has_straight(comb) == True and self.has_flush(comb) == True:
                    best_hand_val = [2, highcard]
                    if stopbeyond > 2:
                        break
                
                    #checking royal flush
                    if self.has_straight(comb) == True and self.has_flush(comb) == True and 14 in self.play_card_values:
                        best_hand_val = [1,True]
            
            if best_hand_val[0] < overall_best_hand_val[0]:
                overall_best_hand_val = best_hand_val
            elif best_hand_val[0] == overall_best_hand_val[0]:
                if best_hand_val[1] > overall_best_hand_val[1]:
                    overall_best_hand_val = best_hand_val
                elif best_hand_val[1] == overall_best_hand_val[1]:
                    try:
                        if best_hand_val[2] > overall_best_hand_val[2]:
                            overall_best_hand_val = best_hand_val
                    except:
                        pass
                    
        return overall_best_hand_val
        
    
    def has_pair(self, comb):
        """
        Determines whether you already have a pair or not.
        Returns: a dictionary with 'Has' = True/False and Card = True/False for each card in the hand
        """
        return_dict = {'Has': False}
    
        hand_value_list = []
        for hand_card in self.hand:
            hand_value_list.append(hand_card.value)
                
        board_value_list = []
        for board_card in self.board:
            board_value_list.append(board_card.value)
    
        for value in hand_value_list:
            if board_value_list.count(value) >= 1 or hand_value_list.count(value) >= 2:
                return_dict['Has'] = True
                return_dict[value] = True
            
        return return_dict
    
    def has_twopair(self, comb):
        return_dict = {'Has': False}
        has_pair = self.has_pair(comb)
        
        if len(has_pair.keys()) >= 3:
            return_dict['Has'] = True
            for key in has_pair.keys():
                if key != 'Has':
                    return_dict[key] = True
        
        return return_dict
    
    def has_threeofkind(self, comb):
        
        return_dict = {'Has':False}
        comb_values = []
        hand_values = []
        
        for card in self.hand:
            hand_values.append(card.value)
        
        for c in comb:
            comb_values.append(c.value)
        
        for value in comb_values:
            if comb_values.count(value) >= 3 and value in hand_values:
                return_dict['Has'] = True
                return_dict[value] = True
                
        return return_dict
    
    def has_straight(self, comb):
        """
        Determines whether you have a straight or not.
        Returns: true/false
        """
        if is_straight(comb) == True:
            return True
        return False
    
    def has_flush(self, comb):
        """
        Determines whether you have a flush.
        Returns: true/false
        """
        if is_flush(comb) == True:
            return True
        return False
    
    def has_fullhouse(self,comb):
        """
        Determines whether you have a fulll house.
        Returns: true/false
        """
        if is_fullhouse(comb) == True:
            return True     
        
        return False
    
    def has_fourofkind(self,comb):
        return_list = [False, 0]
        
        values = []
        for card in comb:
            values.append(card.value)
        
        for num in values:
            if values.count(num) >=4:
                return_list[1] = num
                return_list[0] = True
        return return_list
                
    def highcard(self):
        """
        Returns the highest card in the hand
        """
        return max(self.play_card_values)

def determine_hand_value(HAND):
    """
    Determines how good a hand is to start with... used only for preflop.
    Returns a value between 0 and 
    """
    hand_value = 0
    
    #CHECKS IF THE HAND HAS ANY PAIRS IN IT
    holding = Holding(HAND, [])
    if holding.has_pair(HAND)['Has'] == True:
        hand_value += 3
        
    if holding.highcard == 14:
        hand_value += 1
    elif holding.highcard == 13:
        hand_value += 0.5
    elif holding.highcard == 12:
        hand_value += 0.25
    
    #CHECKS HOW MANY KINDS OF SUITS ARE IN THE HAND
    suit_list = []
    for card in HAND:
        if card.suit not in suit_list:
            suit_list.append(card.suit)
    if len(suit_list) == 2:
        for suit in suit_list:
            if suit_list.count(suit) == 2:
                hand_value += 5
    if len(suit_list) == 4:
        hand_value -= 2
    
    return hand_value


def BOT_WIN_PROB(HAND,BOARD):
    """
    Takes in the ACTIONINFO, HANDINFO, HAND, AND BOARD
    Determines which of the legal actions to take
    """
    #remove all the known cards from the deck
    remaining_deck = update_deck(HAND,BOARD)
    
    #makes these preliminary determinations to optimize the holding_best() function
    flush_possible = is_flush_possible(BOARD)
    straight_possible = is_straight_possible(BOARD)
    
    #calculate what our BOT is holding
    BOT_holding = Holding(HAND,BOARD, flush_possible, straight_possible)
    #print "BOT HOLDING:", BOT_holding
    BOT_holding_best = BOT_holding.best_hand()
    
    #optmizes the best_hand() function by allowing it to stop computing as soon as a hand i above a certain level
    stopbeyond = BOT_holding_best[0]
    
    #generate all 2 card combs for the opponents hands
    hand_combs = list(itertools.combinations(remaining_deck, 2))
    #generate all 3 card combs for the board
    board_combs = list(itertools.combinations(BOARD, 3))
    
    #turning each comb from a tuple into a list
    board_combs_lists =[]
    for comb in board_combs:
        board_combs_lists.append(list(comb))
    
    hand_combs_lists = []
    for comb in hand_combs:
        hand_combs_lists.append(list(comb))
    
    OPP_WIN_COUNT = 0
    TOTAL_COUNT = 0
    
    for hand in hand_combs_lists:
        TOTAL_COUNT += 1
        for board in board_combs_lists:
            OPP_holding = Holding(hand, board, flush_possible, straight_possible)
            OPP_holding_best = OPP_holding.best_hand()
            
            #compare OPP hand to BOT hand
            if OPP_holding_best[0] < BOT_holding_best[0]:
                OPP_WIN_COUNT += 1
                break
            elif OPP_holding_best[0] == BOT_holding_best[0]:
                if OPP_holding_best[1] > BOT_holding_best[1]:
                    OPP_WIN_COUNT += 1
                    break
                elif OPP_holding_best[1] == BOT_holding_best[1]:
                    try:
                        if OPP_holding_best[2] > BOT_holding_best[2]:
                            OPP_WIN_COUNT += 1
                            break
                    except:
                        pass
                    
    PROB_OPP_WINS = float(OPP_WIN_COUNT) / TOTAL_COUNT * 100
    PROB_BOT_WINS = 100 - PROB_OPP_WINS

    FOURCARD_CONVERSION = 0.0012 * (PROB_BOT_WINS ** 2.4539)
    print "BOT WIN%:", FOURCARD_CONVERSION
    return FOURCARD_CONVERSION

#LOOK AHEAD HELPER FUNCTIONS
def flush_possible2(hand,board): 
    h = 0
    d = 0
    c = 0
    s = 0
    for card in hand:
        if card.suit == 'h':
            h+=1
        elif card.suit == 'd':
            d+=1
        elif card.suit == 'c':
            c+=1
        elif card.suit == 's':
            s+=1
    if h<2 and d<2 and c<2 and s<2:
        return False
    
    suit_list=[]
    for card in board:
        suit_list.append(card.suit)
    
    if h>2:
        if suit_list.count('h') >=2:
            return True
    if d>2:
        if suit_list.count('d') >=2:
            return True
    if c>2:
        if suit_list.count('c') >=2:
            return True
    if s>2:
        if suit_list.count('s') >=2:
            return True
    
    return False

def has_pair(cardlist):
    value_list = []
    for card in cardlist:
        value_list.append(card.value)
    for value in value_list:
        if value_list.count(value) >= 2:
            return True
    return False
  
def straight_draw_possible(hand,board):
    #need to be at least 3 unique values on the board for straight to be possible
    board_value_list = []
    for card in board:
        if card.value not in board_value_list:
            board_value_list.append(card.value)
    if len(board_value_list) < 3:
        return False
    
    hand_value_list = []
    for card in hand:
        hand_value_list.append(card.value)
    if 14 in hand_value_list:
        hand_value_list.append(1)
    
    combs_four = generate_hand_combs_4(hand_value_list,board_value_list)
    
    for comb in combs_four:
        if min(comb) >= max(comb) - 4:
            return True
    return False
  
def BOT_LOOK_AHEAD(hand,board):
    
    #preliminary checks to save time
    board_has_pair = has_pair(board)
    flush_possible = flush_possible2(hand,board)
    straight_possible = is_straight_possible(board)
    
    if board_has_pair==False and flush_possible == False and straight_possible == False:
        
        return 0.0
    
    #remove all the known cards from the deck
    remaining_deck = update_deck(hand,board)
    new_board = board[:]
    
    holding_list = []
    ideal_cards = []
    
    for card in remaining_deck:
        new_board.append(card)
        holding = Holding(hand, new_board, flush_possible, straight_possible)
        best_hand_value = holding.best_hand()
        if best_hand_value[0] <= 6:
            ideal_cards.append(card)
            holding_list.append(best_hand_value)
        new_board.remove(card)
    
    ideal_prob = float(len(ideal_cards)) / len(remaining_deck) * 100
    print "Probability of Improving to Straight or Better:", ideal_prob
    
    return ideal_prob

     
#HAND = [Card('Kh'), Card('Kh'), Card('Ah'), Card('Qh')]
#BOARD = [Card('Kh'), Card('Qh'), Card('Qh')]

#test_hold = Holding(HAND, BOARD)
#print test_hold.best_hand()
