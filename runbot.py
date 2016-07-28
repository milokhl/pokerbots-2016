# coding: utf-8


import argparse
import socket
import helperbot as B
from datetime import datetime
startTime = datetime.now()


#USED TO CHECK IF BOARD HAS CHANGED

BOARDLENGTH = 0
BOT_WIN_PROB = 0
LOOK_AHEAD = 0
ALREADY_RAISED = False #this is used to keep us from entering raise wars

#USED IN OPTIMIZING BOT_WIN_PROB
BOARDS_ALREADY_CHECKED = []

#USED TO COUNT OPP CHECK
global Check_Counter
Check_Counter = 0 

####################################################################
    #THE REAL POKERBOT
####################################################################
    
#instead of dealing with cards as strings (6h or Kd for example), we make them into card objects with value and suit
class Card(object):
    def __init__(self, card):
        """
        Takes a card in the form of a string, ("6h") and makes a card object with value and suit
        """
        #using a dictionary to assign the card an int value
        #NOTE: Ace can be high or low - we will need to account for this somehow
        card_value_dict = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J':11, 'Q':12, 'K':13, 'A':14}
        self.value = card_value_dict[card[0]]
        self.suit = card[1]
    
    def __cmp__(self, other):
        """
        This function is used for things like the sorted() function and comparing card objects
        """
        if self.value < other.value:
            return -1
        if self.value > other.value:
            return 1
        if self.value == other.value:
            return 0
    
    def __repr__(self):
        """
        This tells python how to handle printing out a card object.
        """
        card_name_dict = {1: 'Ace', 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 'Jack', 12: 'Queen', 13: 'King', 14: 'Ace'}
        card_name = card_name_dict[self.value]
        
        display_name = str(card_name) + '_' + str(self.suit)
        return display_name


def BOT_SaveNewHandInfo(new_hand_packet):
    """
    Every time a NEWHAND packet class is received, this function is called.
    It stores the most recent NEWHAND packet and makes it available globally.
    All of the information from the packet is stored in HANDINFO
    """
    global HANDINFO #making HANDINFO a global variable
    HANDINFO = new_hand_packet
    """
        Attributes of HANDINFO that can be used:
        http://mitpokerbots.com/docs/grammar.html
        
        HANDINFO.hand_num = an int indicating the hand # being played
        HANDINFO.button = True/False, indicating whether or not we are on the button
        HANDINFO.hand = a list of card strings (these are converted to card objects below)
        HANDINFO.my_bank = an integer indicating your cumulative change in bankroll
        HANDINFO.opp_bank = an integer indicating the opponent player’s cumulative change in bankroll
        HANDINFO.time_bank = indicates the time remaining for the match (we start with 10 sec)
    """

def BOT_BuildHand(HANDINFO):
    """
    Builds a hand of 4 card objects using HANDINFO.hand
    Stores that hand in a global variable called HAND
    """
    global HAND
    
    HAND = []
    for card_str in HANDINFO.hand: #for each card string, add an equivalent card object to HAND
        HAND.append(Card(card_str))

def BOT_SaveGetActionInfo(get_action_packet):
    """
    Every time a GETACTION packet class is received, this function is called.
    It stores the most up-to-date GETACTION info in a variable called ACTIONINFO
    """
    global ACTIONINFO
    ACTIONINFO = get_action_packet
    """
        Attributes of ACTIONINFO that can be used:
        http://mitpokerbots.com/docs/grammar.html
        
        ACTIONINFO.potSize = an integer indicating the number of chips currently in the pot
        ACTIONINFO.numBoardCards = an integer indicating the number of cards currently shown on the board (0-5)
        ACTIONINFO.BoardCards = list of cards on the board (strings) 
        ACTIONINFO.numLastActions = integer indicating how many PerformedActions there have been
        ACTIONINFO.lastActions = contain each of the actions up to and including the last action that you performed on the current hand
        ACTIONINFO.numLegalActions = an integer indicating the number of LegalActions you can perform
        ACTIONINFO.legalActions = contains all the possible actions that you may respond with
        ACTIONINFO.timeBank = time left for the hand
    """

def BOT_BuildBoard(ACTIONINFO):
    """
    Updates a variable called BOARD (a list all the cards on the table)
    """
    global BOARD
    BOARD = []
    for card_str in ACTIONINFO.BoardCards: #for each card string, add an equivalent card object to BOARD
        BOARD.append(Card(card_str))

FULL_DECK = B.build_full_deck()


#PARSING CLASSES: this will store each piece of information from a packet as a class attribute
class NEWHAND:
    """
    Used to parse the data from a NEWHAND packet
    See: http://mitpokerbots.com/docs/grammar.html
    """
    def __init__(self, data):
        self.type = data.split()[0]
        self.hand_num = data.split()[1]
        self.button = data.split()[2]
        self.hand = [data.split()[3], data.split()[4], data.split()[5], data.split()[6]]
        self.my_bank = data.split()[7]
        self.opp_bank = data.split()[8]
        self.time_bank = data.split()[9]
            
class GETACTION:
    """
    Used to parse the data from a GETACTION packet
    For packet sections of variable length, uses for loops
    See: http://mitpokerbots.com/docs/grammar.html
    """
    def __init__(self, data):
        self.type = data.split()[0]
        self.potSize = data.split()[1]
        self.numBoardCards = int(data.split()[2])
        
        parse_index = 3
        BoardCards = []
        for i in range(self.numBoardCards):
            BoardCards.append(data.split()[(parse_index)])
            parse_index+=1
        self.BoardCards = BoardCards

        #print "Parse Index for numLast Actions:", parse_index
        self.numLastActions = int(data.split()[parse_index])
        parse_index += 1
        
        lastActions = []
        for i in range(self.numLastActions):
            lastActions.append(data.split()[parse_index])
            parse_index +=1
        self.lastActions = lastActions

        #print "Parse Index for num Legal Actions:", parse_index
        self.numLegalActions = int(data.split()[parse_index])

        legalActions = []
        for i in range(self.numLegalActions):
            parse_index += 1
            legalActions.append(data.split()[parse_index])
        
        self.legalActions = legalActions


def DETERMINE_ACTION_PREFLOP(ACTIONINFO, HANDINFO):
    
    hand_value = B.determine_hand_value(HAND)
    print 'HAND VALUE IS:', hand_value
    
    RAISE_THRESHOLD = 5
    BEST_HAND = 13
    
    if hand_value >= RAISE_THRESHOLD:
        print "HIT RAISE THRESHOLD"
        for action in ACTIONINFO.legalActions:
            if 'RAISE' in action:
                index1 = action.index(":")
                raise_limits = action[(index1+1):]
                index2 = raise_limits.index(":")
                min_raise = int(raise_limits[:index2])
                max_raise = int(raise_limits[index2+1:])
                raise_range = max_raise-min_raise
                
                raise_amount = int(min_raise + ((hand_value / BEST_HAND) * raise_range))
                return 'RAISE:' + str(raise_amount) + '\n'
        
        if 'CALL' in ACTIONINFO.legalActions:
            return 'CALL\n'    
        else:
            return 'CHECK\n'
    
    if hand_value < RAISE_THRESHOLD and hand_value >= 0:

        if 'CHECK' in ACTIONINFO.legalActions:
            return 'CHECK\n'
        elif 'CALL' in ACTIONINFO.legalActions:
            return 'CALL\n'

    if hand_value < 0 and HANDINFO.button == 'true':
        return 'FOLD\n'
    
    if hand_value < 0 and HANDINFO.button == 'false':
        if 'CHECK' in ACTIONINFO.legalActions:
            return 'CHECK\n'
        else:
            return 'FOLD\n'

def DETERMINE_ACTION(ACTIONINFO, HANDINFO, BOT_WIN_PROB, Bot_look_ahead):
    """
    Takes in current info and winning probability, and makes a decision.
    """
    RAISE_PERCENT = 80.0
    CALLCHECK_PERCENT = 60.0
    LOOK_AHEAD_HIGH = 20.0
    LOOK_AHEAD_CALL = 15.0
    
    #BELOW CALLCHECK PERCENT, we always checkfold

    Check_Test = False
    global Check_Counter
    
    for item in ACTIONINFO.lastActions:
        if "CHECK" in item and "IHTFG" not in item:                                 
            Check_Counter += 1
            Check_Test = True
    for item in ACTIONINFO.lastActions:
        if "BET" in item:
            Check_Test = False
            break
    if Check_Test == False:
        Check_Counter = 0
    
    
    if BOT_WIN_PROB >= RAISE_PERCENT or Bot_look_ahead >= LOOK_AHEAD_HIGH or Check_Counter >= 2:
        for action in ACTIONINFO.legalActions:
           
            if 'RAISE' in action:

                min_bet = int(action.split(':')[1])
                max_bet = int(action.split(':')[2])
                #determine how much the opponent bet before us
                for opp_action in ACTIONINFO.lastActions:
                    if 'BET' in opp_action:
                        opp_bet = int(opp_action.split(':')[1])
                        
                if BOT_WIN_PROB >= 98 and len(BOARD) == 5:
                    action = 'RAISE:'+str(max_bet - 1)+'\n'
                elif BOT_WIN_PROB >= 90:
                    if len(BOARD) == 5:
                        our_bet = int(.75 * max_bet)
                        action = 'RAISE:'+str(our_bet)+'\n'
                    if len(BOARD) < 5:
                        our_bet = int(.4 * max_bet)
                        if our_bet < min_bet:
                            our_bet = min_bet
                        action = 'RAISE:'+str(our_bet)+'\n'
                elif BOT_WIN_PROB >= 84: 
                    if len(BOARD) == 5:
                        our_bet = int(.5 * max_bet)
                        action = 'RAISE:'+str(our_bet)+'\n'
                    elif len(BOARD) < 5:
                        our_bet = int(.25 * max_bet)
                        action = 'RAISE:'+str(our_bet)+'\n'
                    else:
                        action = 'RAISE:'+str(max_bet)+'\n'
                elif BOT_WIN_PROB >= 80 or Bot_look_ahead >= LOOK_AHEAD_HIGH:
                    our_bet = (.3 * max_bet)                    
                    action = 'RAISE:'+str(our_bet)+'\n'
                elif Check_Counter >= 2:
                        action = 'RAISE:'+str(min_bet)+'\n'
                    
            elif 'BET' in action:
            
                min_bet = int(action.split(':')[1])
                max_bet = int(action.split(':')[2])
                
                for opp_action in ACTIONINFO.lastActions:
                    if 'RAISE' in opp_action:
                        opp_raise = int(opp_action.split(':')[1])
                if BOT_WIN_PROB >= 98 and len(BOARD) == 5:
                    action = 'BET:'+str(max_bet - 1)+'\n'
                elif BOT_WIN_PROB >= 90:
                    if len(BOARD) == 5:
                        our_bet = int(.9 * max_bet)
                        action = 'BET:'+str(our_bet)+'\n'
                    else:
                        action = 'BET:'+str(max_bet)+'\n'
                    if len(BOARD) < 5:
                        our_bet = int(.4 * max_bet)
                        if our_bet < min_bet:
                            our_bet = min_bet                        
                        action = 'BET:'+str(our_bet)+'\n'
                elif BOT_WIN_PROB > 84:
                    if len(BOARD) == 5:
                        our_bet = int(.7 * max_bet)
                        action = 'BET:'+str(our_bet)+'\n'
                    if len(BOARD) < 5:
                        our_bet = int(.3 * max_bet)
                        if our_bet < min_bet:
                            our_bet = min_bet
                        action = 'BET:'+str(our_bet)+'\n'
                elif BOT_WIN_PROB >= 80 or Bot_look_ahead >= LOOK_AHEAD_HIGH:
                    our_bet = int(.4 * max_bet)
                    if our_bet < min_bet:
                            our_bet = min_bet                    
                    action = 'BET:'+str(our_bet)+'\n'
                elif Check_Counter >= 2:
                    action = 'BET:'+str(min_bet)+'\n'
    
    elif BOT_WIN_PROB >= CALLCHECK_PERCENT or Bot_look_ahead >= LOOK_AHEAD_CALL:
        print ACTIONINFO.lastActions
        if 'RAISE' in ACTIONINFO.lastActions[-1]:
            opp_raise = int(ACTIONINFO.lastActions[-1].split(':')[1])
            if opp_raise > 30 and Bot_look_ahead < 20:
                action = 'FOLD\n'
                
        elif 'BET' in ACTIONINFO.lastActions[-1]:
            opp_bet = int(ACTIONINFO.lastActions[-1].split(':')[1])
            if opp_bet > 30 and Bot_look_ahead < 20:
                action = 'FOLD\n'
        
        if 'CHECK' in ACTIONINFO.legalActions:
            action = 'CHECK\n'
        elif 'CALL' in ACTIONINFO.legalActions:
            action = 'CALL\n'
        else:
            action = 'FOLD\n'
    
    else:
        if 'CHECK' in ACTIONINFO.legalActions:
            action = 'CHECK\n'
        else:
            action = 'FOLD\n'
    
    return action

#Using this dictionary to do two card to four card conversion tests
conv_dict = {}
class Player:
    def run(self, input_socket):
        # Get a file-object for reading packets from the socket.
        # Using this ensures that you get exactly one packet per read.

        f_in = input_socket.makefile()
        while True:
            # Block until the engine sends us a packet.
            data = f_in.readline().strip()
            # If data is None, connection has closed.
            if not data:
                print "Gameover, engine disconnected."
                break
        
            print data
            # Here is where you should implement code to parse the packets from
            # the engine and act on it. We are just printing it instead.
            #print data


            packet_type  = data.split()[0] #determines the type of the packet in order to parse
            #Here, a "send_packet" is generated by creating an instance of a class corresponding to the packet type

            if packet_type == 'NEWHAND':
                newhand = NEWHAND(data)
                BOT_SaveNewHandInfo(newhand) #this calls a global function called BOT_SaveNewHandInfo
                BOT_BuildHand(HANDINFO)  #which stores the new hand packet outside of this run() loop
                
                
            if packet_type == 'GETACTION':
                getaction = GETACTION(data)
                BOT_SaveGetActionInfo(getaction)
                BOT_BuildBoard(ACTIONINFO)
                
                #PREFLOP
                if len(BOARD) == 0: #this means we are in preflop mode
                    action = DETERMINE_ACTION_PREFLOP(ACTIONINFO,HANDINFO)
                    BOARDLENGTH = 0 
                    LOOK_AHEAD = 0 #RESET THE LOOK AHEAD 
                    ALREADY_RAISED = False
                
                #POSTFLOP
                elif len(BOARD) > 0:
                    
                    if len(BOARD) != BOARDLENGTH: #the number of cards on the board has changed
                        ALREADY_RAISED = False #if a card has been dealt, make the raise counter false so that our bot has the option to raise again
                        
                        global BOARDLENGTH
                        BOARDLENGTH = len(BOARD)
            
                        BOT_WIN_PROB = B.BOT_WIN_PROB(HAND, BOARD) #update the bot win prob
                        
                        if BOARDLENGTH != 5: #no need to update look ahead after the river
                            LOOK_AHEAD = B.BOT_LOOK_AHEAD(HAND,BOARD) #update the look ahead
        
                    action = DETERMINE_ACTION(ACTIONINFO,HANDINFO, BOT_WIN_PROB, LOOK_AHEAD)
                
                if '\n' not in action:
                    action += '\n'
                
                if 'RAISE' in action:
                    ALREADY_RAISED = True
                    
                print "HAND:", HAND
                print "BOARD:", BOARD
                print "Sending Action:", action
                s.send(action) #SENDING OUR ACTION TO THE ENGINE
            
            if packet_type == "REQUESTKEYVALUES":
                # At the end, the engine will allow your bot save key/value pairs.
                # Send FINISH to indicate you're done.
                s.send("FINISH\n")
        # Clean up the socket.
        s.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A Pokerbot.', add_help=False, prog='pokerbot')
    parser.add_argument('-h', dest='host', type=str, default='localhost', help='Host to connect to, defaults to localhost')
    parser.add_argument('port', metavar='PORT', type=int, help='Port on host to connect to')
    args = parser.parse_args()

    # Create a socket connection to the engine.
    print 'Connecting to %s:%d' % (args.host, args.port)
    try:
        s = socket.create_connection((args.host, args.port))
    except socket.error as e:
        print 'Error connecting! Aborting'
        exit()

    bot = Player()
    bot.run(s)
    


