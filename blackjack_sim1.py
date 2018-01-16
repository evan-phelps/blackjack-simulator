#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Evan Phelps <ephelps@omegaas.com>
#
# Distributed under terms of the MIT license.
###############################################################################

'''Implementation of a Blackjack variant and strategy.
'''

from blackjack import *

class RuleSetBase(RuleSet):
    
    def get_player_options(self, hand_player, hand_dealer):
        valid_options = [RuleSet.ValidMoves.STAY]
        if min(hand_player.scores)<21:
            valid_options.append(RuleSet.ValidMoves.HIT)
        return valid_options
    
    def get_dealer_play(self, hand):
        scores = [score for score in hand.scores if score <=21]
        if len(scores) == 0:
            return RuleSet.ValidMoves.STAY
        for score in reversed(scores):
            if score > 16:
                return RuleSet.ValidMoves.STAY
            elif score <= 16:
                return RuleSet.ValidMoves.HIT
        raise InvalidMoveError('Dealer unable to choose! If you see this '
                                + 'error, then your RuleSet class does not '
                                + 'account for all possible hand states.')


class StrategyDefault(Strategy):
    
    def advise_bet(self):
        return 1
    
    def advise_play(self, hand):
        for score in reversed(hand.scores):
            if score > 16:
                return RuleSet.ValidMoves.STAY
            elif score <= 16:
                return RuleSet.ValidMoves.HIT
        raise InvalidMoveError('Player unable to choose! If you see this '
                                + 'error, then your Strategy class does not '
                                + 'account for all possible hand states.')


class StrategyBasicHS(Strategy):
    '''Always hit hard 11 or less.
    Stand on hard 12 against a dealer 4-6, otherwise hit.
    Stand on hard 13-16 against a dealer 2-6, otherwise hit.
    Always stand on hard 17 or more.
    Always hit soft 17 or less.
    Stand on soft 18 except hit against a dealer 9, 10, or A.
    Always stand on soft 19 or more.
    '''
    def advise_bet(self):
        return 1
    
    def advise_play(self, hand):
        dealer_cards_visible = self._hands[0].num_cards
        if dealer_cards_visible > 1:
            n = dealer_cards_visible
            raise InvalidStateError('Dealer hand has %d visible cards ' % n
                                     + 'but should not have more than '
                                     + 'one at this point.')
        upcard = self._hands[0].best_score
        if upcard not in range(2,12):
            raise InvalidStateError('Dealer hand has a score of %d ' % upcard
                                     + 'but should have a value between 2 '
                                     + 'and 11.')
        score = hand.best_score
        soft = hand.is_soft
        hard = not hand.is_soft
        #print(upcard, score, soft)
        
        hit_conditions = (
            hard and score <= 11,
            hard and score == 12 and upcard in [2,3,7,8,9,10,11],
            hard and score in range(13,17) and upcard in [7,8,9,10,11],
            soft and score <= 17,
            soft and score == 18 and upcard in [9, 10, 11]
        )
        
        stay_conditions = (
            hard and score == 12 and upcard in range(4,7),
            hard and score in range(13,17) and upcard in range(2,7),
            hard and score >= 17,
            soft and score == 18 and upcard in range(2,9),
            soft and score >= 19
        )
        
        num_hit_conditions = sum(hit_conditions)
        num_stay_conditions = sum(stay_conditions)
        
        if num_hit_conditions + num_stay_conditions == 1:
            if num_hit_conditions == 1:
                return RuleSet.ValidMoves.HIT
            if num_stay_conditions == 1:
                return RuleSet.ValidMoves.STAY

        raise InvalidMoveError('One and only one condition must be '
                                + 'satisfied!  Check strategy rules.')
        

###############################################################################
# py.test tests

def test_Round():
    # setup game
    shoe = Shoe(6, 0.75)
    hands = []
    rules = RuleSetBase()
    strategy_class = StrategyDefault
    strategy = strategy_class(hands, shoe.num_dealt)
    player1 = Player(2, strategy, shoe.deal_one)
    player2 = Player(6, strategy, shoe.deal_one)
    
    # setup round
    dealer = Dealer(rules, shoe.deal_one)
    hands.append(dealer)
    ## take bets, set hands
    for p in [player1, player2]:
        bet = p.make_bet()
        hand = Hand((p.seat, 0), bet)
        hands.append(hand)
        p.add_hand(hand)
    # deal
    for i in range(2):
        for h in hands[1:]:
            h.add_card(shoe.deal_one())
        dealer.add_card(shoe.deal_one(), i==0)
    
    player1.play_through()
    player2.play_through()
    dealer.play_through()
    
    # look
    print(dealer)
    print(player1)
    print(player2)
    
def test_RuleSetBase():
    assert True
    

def test_StrategyDefault():
    assert True


if __name__ == '__main__':
    for i in range(100):
        game = Game(RuleSetBase())
        game.add_player(1, StrategyBasicHS)
        game.add_player(2, StrategyDefault)
        print(','.join([str(s) for s in game.play(100)]), flush=True)
    #with open('1000_rounds.csv', 'w') as fout:
    #    print(game.play(1000, fout))