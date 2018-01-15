# Blackjack Strategy Simulator

[Note that not all rules have been implemented yet (e.g., insurance).]

The Blackjack Strategy Simulator is meant to provide a simple framework for testing different blackjack player strategies under various rulesets.  The simulator is divided into three main conceptual components: (1) the *core* gameplay mechanism in `blackjack.py`, (2) the Strategy and RuleSet specifications, and (3) monitoring/analysis code that operates on serialized output (initially files) from the core gameplay mechanism.  The gameplay mechanism allows the invoker to specify how many rounds to play and returns the net results of the game for all players.  It can, also, print round-by-round results to a file, if provided by the invoker of `Game.play`, which, for example, could be useful for testing the effect of number of cards played on card-counting strategies.

# How to simulate a strategy
An example Strategy/RuleSet implementation is defined in `blackjack_sim1.py`.  The example demonstrates the basic recipe for creating a simulation:
1. Import the core mechanism, `from blackjack import *`.
1. Extend the `RuleSet` and `Strategy` classes to your specifications.  `Strategy` requires implementations for `advise_bet` and `advise_play`; `RuleSet requires implementations for `get_player_options`, `get_dealer_play`, and optionally `calculate_payout`.
1. create/configure/run the `Game` in `__main__`.

# How to analyze a strategy
It's easiest to analyze the simulation results with a manual *batch* mentality.  For example, you would save your simulation results to files, and then use a Notebook to inspect and analyze the results.  In your simulation file (e.g., `blackjack_sim1.py`), you might have something like this:
```
# RuleSet specification
...
...
# Strategy specifications
...
...
# main entry point
if __name__ == '__main__':
    # set up the game...
    ...
    ...
    # execute the game
    with open('sim1_1000_rounds.csv', 'w') as fout:
        print(game.play(1000, fout))
```
This would output a game summary and give you a round-by-round result file, `sim1_1000_rounds.csv`, for consumption.  You could also set up and execute many games in the loop (changing `open`'s `w` argument to `a`) and at the command line redirect the program output to another summary-of-all-games file:  `python multigame_sim.py > multigame_sim.csv`.  This would result in two result files -- one for round-level results and another for game-level results.

The round-level results are in the form of comma-separated values:
1. round number
1. ruleset class name
1. number of decks in shoe
1. fraction of shoe to use before reshuffling
1. fraction of shoe already dealt
1. net round winnings for each player (number of columns equal to number of players in game)
1. net game winnings for each player (number of columns equal to number of players in game)
1. profit per dollar for each player (number of columns equal to number of players in game)
Some of the values in the round-level results could be calculated from others but are explicitly written for convenience and for *sanity checks*.

The game-level results consist only of the final profit per dollar for each player, which is returned by `Game.play`.