#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Evan Phelps <ephelps@omegaas.com>
#
# Distributed under terms of the MIT license.
###############################################################################

'''This module implements a blackjack simulator for testing the effectiveness
of player strategies.
'''

import itertools
import functools
import random

class Card:
    '''Card represents a playing card in Blackjack and is responsible for
    knowing all of its potential values.  Valid suits are not enforced.
    '''
    _val_map = {'A': [1, 11], 'J': [10], 'Q': [10], 'K': [10]}
    _val_map.update({str(n): [n] for n in range(2, 11)})

    def __init__(self, rank, suit):
        self._rank = rank
        self._suit = suit
        # Even though only Ace can have more than one value, all Cards will
        # return lists so that invokers don't need to treat the return values
        # differently.
        self._values = Card._val_map[rank]

    @property
    def values(self):
        return self._values
    
    @property
    def card_rep(self):
        return self._rank + self._suit
    
    def __repr__(self):
        values = ','.join([str(s) for s in self.values])
        return '%s%s (%s)' % (self._rank, self._suit, values)
        
    def __str__(self):
        '''Returns a color-coded string representation of Card.  The color
        coding is injected for red cards only if the Card was created with a
        suit value equal to a unicode representation of a heart or diamond.
        '''
        (clr0, clr1) = ('', '')
        if self._suit in ['\u2665', '\u2666']:     # heart or diamond
            (clr0, clr1) = ('\x1b[31m','\x1b[0m')  # red markup decorators
        return clr0 + self.card_rep + clr1


class Shoe:
    '''Shoe is an arbitrary number of decks of Cards that get shuffled together.
    Cards are dealt from the Shoe.  If a specified fraction of the Shoe has been
    dealt, then when the Shoe is next checked by a dealer,the Cards will be
    replaced and reshuffled.
    '''
    def __init__(self, num_decks, depth_threshold):
        self._ndecks = num_decks
        self._shoe_size = num_decks * 52
        self._depth_threshold = depth_threshold
        self._shuffle()

    @property
    def max_cards(self):
        return self._shoe_size

    @property
    def num_cards(self):
        return len(self._cards)
        
    def check_reshuffle(self):
        if 1 - self.num_cards/self.max_cards >= self._depth_threshold:
            print('RESHUFFLING!')
            self._shuffle()
            
    def deal_one(self):
        if len(self._cards) == 0:
            self.check_reshuffle()
        return self._cards.pop()
    
    def _shuffle(self):
        '''Creates _ndecks of Cards and shuffles.'''
        ranks = ['A'] + [str(n) for n in range(2, 11)] + ['J', 'Q', 'K']
        suits = ['\u2660', '\u2665', '\u2666', '\u2663']
        decks = [itertools.product(ranks, suits) for ideck in range(self._ndecks)]
        cards = functools.reduce(lambda x, y: x + y,
                                 [list(deck) for deck in decks])

        self._cards = [Card(rank, suit) for (rank, suit) in cards]
        random.shuffle(self._cards)

    def __repr__(self):
        shoe_repr = 'decks=%d, reshuffle at %.2f.' % (self._ndecks,
                                                      self._depth_threshold)
        she_repr += ' %d/%d' % (len(self._cards), self._shoe_size)
        return shoe_repr


class Hand:
    '''Hand is a Blackjack hand of Card objects and is responsible for reporting
    all of its possible scores.  Hand includes all properties that are required
    to determine payouts other than the payout ratios associated with the house
    rules.
    '''
    def __init__(self, seat_split=(0,0), bet=0):
        self._cards = []
        self._hole = None
        self._bet = bet
        self._is_insured = False
        self._seat = seat_split[0]
        self._split = seat_split[1]
        self.__key = hash( (self._seat, self._split) )
    
    @property
    def seat_id(self):
        return self._seat
    
    @property
    def split_id(self):
        return self._split

    @property
    def bet(self):
        return self._bet
    
    @property
    def cards(self):
        return ','.join([card.card for card in self._cards])
    
    @property
    def num_cards(self):
        return len(self._cards)
    
    @property
    def is_blackjack(self):
        return self.num_cards == 2 and self.best_score == 21

    @property
    def scores(self):
        '''Returns all possible scores (more than 1 if hand contains aces).'''
        card_vals = [card.values for card in self._cards]
        sums = [sum(list(vals_list))
                for vals_list in itertools.product(*card_vals)]
        # sums = filter(lambda x: x <= 21, sums)
        return sorted(set(sums))

    @property
    def best_score(self):
        if len(self.scores) == 0:
            return 0
        inplay = [s for s in self.scores if s<=21]
        if len(inplay) == 0:
            return min(self.scores)
        return max([s for s in self.scores if s<=21])
    
    def unhole(self):
        if self._hole is not None:
            self._cards.append(self._hole)
            self._hole = None

    def add_card(self, card, ishole=False):
        if ishole:
            self._hole = card
        else:
            self._cards.append(card)
            
    def split(self, card1, card2):
        '''Perform a Split and return newly split hand.'''
        assert self.num_cards == 2
        assert self._cards[0] == self._cards[1]
        hand = Hand((self.seat_id, self.split_id), self.bet)
        hand.add_card(self._cards.pop())
        self.add_card(card1)
        hand.add_card(card2)
        return hand
            
    def __str__(self):
        visible = [str(card) for card in self._cards]
        holes = [] if self._hole is None else ['??']
        cards = visible + holes
        return 'Seat/Split: %d/%d \t %d \t %s' % (self._seat,
                                                  self._split,
                                                  self.best_score,
                                                  ' '.join(cards))


###############################################################################
# py.test tests

def test_Card():
    ace_of_spades = Card('A', 'S')
    assert str(ace_of_spades) == 'AS'
    assert ace_of_spades.values == [1, 11]
    
    queen_of_hearts = Card('Q', 'H')
    assert str(queen_of_hearts) == 'QH'
    assert queen_of_hearts.values == [10]
    
    eight_of_clubs = Card('8', 'C')
    assert str(eight_of_clubs) == '8C'
    assert eight_of_clubs.values == [8]


def test_Shoe():
    shoe = Shoe(1, 0.75)
    assert shoe.max_cards == 52
    cards =  list([shoe.deal_one() for i in range(52)])
    assert len(cards) == 52
    assert shoe.num_cards == 0
    card = shoe.deal_one()
    assert shoe.num_cards == 51
    
    for i in range(37):
        card = shoe.deal_one()
        shoe.check_reshuffle()
    assert shoe.num_cards == 14
    card = shoe.deal_one()
    assert shoe.num_cards == 13
    shoe.check_reshuffle()
    assert shoe.num_cards == 52


def test_Hand():
    hand = Hand()
    assert hand.bet == 0
    assert hand.seat_id == 0
    assert hand.split_id == 0
    assert hand.cards == ''
    assert hand.num_cards == 0
    assert hand.is_blackjack is not True
    assert hand.scores == [0]
    assert hand.best_score == 0
    
    hand.add_card(Card('A', 'S'))
    hand.add_card(Card('J', 'S'))
    assert hand.num_cards == 2
    assert hand.is_blackjack is True
    assert 11 in hand.scores
    assert 21 in hand.scores
    assert hand.best_score == 21