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
    game = Game(RuleSetBase())
    game.add_player(1, StrategyDefault)
    game.add_player(2, StrategyDefault)
    game.add_player(3, StrategyDefault)
    game.add_player(4, StrategyDefault)
    game.add_player(5, StrategyDefault)
    game.add_player(6, StrategyDefault)
    with open('1000_rounds.csv', 'w') as fout:
        print(game.play(1000, fout))