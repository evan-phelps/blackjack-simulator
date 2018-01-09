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
        valid_options = [ValidMoves.STAY]
        if min(hand_player.scores)<21:
            valid_options.append(ValidMoves.HIT)
        return valid_options
    
    def get_dealer_play(self, hand):
        scores = [score for score in hand.scores if score <=21]
        if len(scores) == 0:
            return ValidMoves.STAY
        for score in reversed(scores):
            if score > 16:
                return ValidMoves.STAY
            elif score <= 16:
                return ValidMoves.HIT
        raise InvalidMoveError('Dealer unable to choose! If you see this '
                                + 'error, then your RuleSet class does not '
                                + 'account for all possible hand states.')


class StrategyDefault(Strategy):
    
    def advise_bet(self, hand):
        return 0
    
    def advise_play(self, hand):
        for score in reversed(hand.scores):
            if score > 16:
                return RuleSet.ValidMoves.STAY
            elif score <= 16:
                return RuleSet.ValidMoves.HIT
        raise InvalidMoveError('Player unable to choose! If you see this '
                                + 'error, then your Strategy class does not '
                                + 'account for all possible hand states.')
