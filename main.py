"""
Fishelbrand pauper deck simulator
---------------------------------
Copyright (c) Squalm 2023

Scope:  
Optimise a fishelbrand deck by goldfishing it and making small changes.

==#

# CARDS
#==
Dict: Int -> (type, on cast(cost, mana, draw, other), on T(allowed, cost, mana, draw, other),on T&sac(allowed, cost, mana, draw, other),  )

cost/mana: (W, U, B, R, G, choice(number, W bool, U bool, B bool, R bool, G bool))
"""

import random
from copy import deepcopy
from colorama import Fore, Back, Style

plains   =   1
island   =   2
swamp    =   3
mountain =   4
forest   =   5

spring   =  11
skerry   =  12
vent     =  13

star     = 101
petal    = 102

offering     = 111
ritual       = 112
manamorphose = 113

brainspoil   = 121
energytap    = 122
looting      = 123
kaervek      = 124
ponder       = 125
preordain    = 126
knowledge    = 127
visions      = 128

gurmangler   = 131
attendants   = 132

sphere       = 203
weather      = 214
wraith       = 233
epicure      = 234

W = 0
U = 1
B = 2
R = 3
G = 4
colorless = 5

# Starting deck
default = [
    star, star, star, star,
    petal, petal, petal,
    offering, offering, offering, offering,
    ritual, ritual, ritual, ritual,
    manamorphose, manamorphose, manamorphose, manamorphose,
    brainspoil, brainspoil,
    energytap, energytap, energytap, energytap,
    looting, looting,
    kaervek,
    ponder, ponder, ponder,
    preordain, preordain, preordain, preordain,
    knowledge, knowledge, knowledge, knowledge,
    visions, visions,
    gurmangler, gurmangler, gurmangler,
    attendants, attendants, attendants, attendants,
    spring, spring, spring, spring,
    island,
    skerry, skerry, skerry, skerry,
    vent, vent, vent,
]

library = []
hand = []
graveyard = []
battlefield = []

class game():
    """Start a new goldfishing game with the given deck."""

    def __init__(self, deck: list, verbose = False):
        self.library = deepcopy(deck)
        random.shuffle(self.library)
        self.hand = []
        self.graveyard = []
        self.battlefield = []

        self.floating = [0, 0, 0, 0, 0, 0] # WUBRG colourless
        self.storm = 0
        self.turn = 0
        self.verbose = verbose

        self.lands = [plains, island, swamp, mountain, forest, spring, skerry, vent]
        self.creatures = [gurmangler, attendants, wraith]
        self.artefacts = [star, petal, sphere]
        self.easydraw = [manamorphose, ponder, preordain, star, sphere, looting, visions]
        self.untappedLands = [plains, island, swamp, mountain, forest]
        self.tappedLands = [skerry, vent, spring]
        self.earlyPlays = [star, sphere]

        if self.verbose:
            print("# NEW GAME")
            print(Style.DIM + "mulliganing..." + Style.RESET_ALL)

        self.mulligan()

    def state(self) -> None:
        if self.verbose:
            print(Style.RESET_ALL + Style.DIM + "Tu " + Style.RESET_ALL + Fore.CYAN + f"{self.turn} " +
                Style.RESET_ALL + Style.DIM + "Ha " + Style.RESET_ALL + Fore.CYAN + f"{len(self.hand)} " +
                Style.RESET_ALL + Style.DIM + "Ba " + Style.RESET_ALL + Fore.CYAN + f"{len(self.battlefield)} " +
                Style.RESET_ALL + Style.DIM + "Gr " + Style.RESET_ALL + Fore.CYAN + f"{len(self.graveyard)} " +
                Style.RESET_ALL + Style.DIM + "Li " + Style.RESET_ALL + Fore.CYAN + f"{len(self.library)} " + 
                Style.RESET_ALL + Style.DIM + "St " + Style.RESET_ALL + Fore.CYAN + f"{self.storm}" + 
                Style.RESET_ALL + Style.DIM + " : " + Style.RESET_ALL + 
                Fore.YELLOW + f"{self.floating[0]} " + Fore.BLUE + f"{self.floating[1]} " + Fore.MAGENTA + f"{self.floating[2]} " + 
                Fore.RED + f"{self.floating[3]} " + Fore.GREEN + f"{self.floating[4]} " + Fore.WHITE + f"{self.floating[5]}" + Style.RESET_ALL +
                Style.DIM + f" : {self.hand}" + Style.RESET_ALL)
            
    def stateTurn(self) -> None:
        if self.verbose:
            print(f"\n# TURN {self.turn}")

    def draw(self, n: int) -> None:
        """Draw `n` cards."""

        if self.verbose:
            drawn = self.library[0:n]
            print(Style.RESET_ALL + Style.DIM + "draws " + Style.RESET_ALL + Fore.CYAN + str(drawn) + Style.RESET_ALL)

        for _ in range (0, n):
            self.hand.append(self.library.pop(0))

    def mulligan(self) -> None:
        """Draw hands and mulligan until we have a good enough hand."""

        for n in [7,6,5,4]:
            
            for card in self.hand:
                self.library.append(card)
            
            random.shuffle(self.library)

            # empty hand then draw n
            self.hand = []
            self.draw(n)

            nLands = self.numberOf(self.lands, self.hand)
            nDraw = self.numberOf(self.easydraw, self.hand)
            if (nLands >= 2 and nLands < 5 and nDraw >= 1) or (n <= 5 and nLands >= 2):
                break

    def firstTurns(self) -> None:
        """Play the first 3.5 turns of the game.
        
        Plays the first 3 turns, then increments turn counter and draws a card for turn 4."""

        for i in range(1, 4):
            self.turn = i
            self.clearForNewTurn()

            if self.verbose:
                self.stateTurn()
                self.state()  

            if self.turn != 1:
                self.draw(1)

            # Play stars and spheres on turn 3
            if self.turn == 3:
                self.tapLands()
                if self.numberOf([star, sphere], self.hand) > 0:
                    self.playStars()
                    self.state()

            if self.numberOf(self.lands, self.hand) > 0:
               self.playLand()

        self.turn = 4
        self.clearForNewTurn()

        self.stateTurn()
        self.state()
        self.draw(1)

    def go(self) -> bool:
        """Attempts to combo off and returns a bool based on whether it won."""
        
        # First make mana
        self.tapSacLands()

        playedALand = False

        while True:

            for i in range(0, len(self.hand)):

                playedSomething = False

                # Priority order of plays:
                
                # Petals
                if self.hand[i] == petal:
                    self.playPermanent(i)
                    playedSomething = True
                
                # Rituals
                elif self.hand[i] == ritual:
                    if self.floating[B] >= 1:

                        # effect
                        self.floating[B] += 2 # -1 +3
                        
                        self.playNonPermanent(i)
                        playedSomething = True

                # Try to play an untapped land if we haven't already
                elif not playedALand:
                    if self.hand[i] == plains:
                        self.floating[W] += 1
                    elif self.hand[i] == island:
                        self.floating[U] += 1
                    elif self.hand[i] == swamp:
                        self.floating[B] += 1
                    elif self.hand[i] == mountain:
                        self.floating[R] += 1
                    elif self.hand[i] == forest:
                        self.floating[G] += 1
                    
                    self.statePlayFromHand(i)
                    playedALand = self.playLand()
                    playedSomething = True

                if playedSomething:
                    self.state()
                    break

            break

        return False

    def playLand(self) -> bool:
        """Plays a land.
        
        Turns 0-3: Prefers tapped land.
        Turn 4: Only plays untapped land."""

        if self.turn < 4:
            b = self.playKindOfLand(self.tappedLands)
            if not b:
                b = self.playKindOfLand(self.untappedLands)
            return b
        else:
            return self.playKindOfLand(self.untappedLands)
    
    def playKindOfLand(self, landList) -> bool:
        """Plays the first land in the hand which is in the given list."""
        for i in range(0, len(self.hand)):
                if self.hand[i] in landList:

                    self.statePlayFromHand(i)

                    self.battlefield.append(self.hand.pop(i))
                    return True
        return False

    def playStars(self) -> None:
        """Plays stars and spheres on turn 3."""
        # Loop to make sure we catch them all.
        for _ in range(0, self.numberOf(self.artefacts, self.hand)):
            for i in range(0, len(self.hand)):
                # If we have mana
                if sum(self.floating) > 0:
                    if self.hand[i] == star:
                        self.statePlayFromHand(i)
                        self.battlefield.append(self.hand.pop(i))
                        self.storm += 1
                        # Use the mana
                        for i in range(0, len(self.floating)):
                            if self.floating[i] > 0:
                                self.floating[i] -= 1
                                break
                        break

    def tapLands(self) -> None:
        """Taps all lands for mana (doesn't sac)."""
        self.tapBasics()
        for card in self.battlefield:
            if card in self.tappedLands:

                if card == spring:
                    self.floating[1] += 1
                elif card == vent:
                    self.floating[2] += 1
        
        self.state()

    def tapSacLands(self) -> None:
        """Taps and sacs lands for mana (on turn 4)."""
        self.tapBasics()
        # loop to catch them all
        for _ in range(0, self.numberOf(self.tappedLands, self.battlefield)):
            for i in range(0, len(self.battlefield)):
                if self.battlefield[i] in self.tappedLands:

                    # Check what it is and add appropriate mana.
                    if self.battlefield[i] == spring:
                        self.floating[0] += 1
                        self.floating[2] += 1
                        self.sac(i)
                        break
                    elif self.battlefield[i] == skerry:
                        self.floating[1] += 2
                        self.sac(i)
                        break
                    elif self.battlefield[i] == vent:
                        self.floating[1] += 1
                        self.floating[3] += 1
                        self.sac(i)
                        break
        
        self.state()

    def tapBasics(self) -> None:
        for card in self.battlefield:
            if card in self.untappedLands:

                if card == plains:
                    self.floating[0] += 1
                elif card == island:
                    self.floating[1] += 1
                elif card == swamp:
                    self.floating[2] += 1
                elif card == mountain:
                    self.floating[3] += 1
                elif card == forest:
                    self.floating[4] += 1

    def numberOf(self, seek: list, items: list) -> int:
        """Counts the number of things in `seek` in `items`."""

        number = 0
        for l in seek:
            number += items.count(l)
        
        return number
    
    def numberOfSpells(self) -> int:
        """Shortcut function to return the number of spells in hand."""
        return len(self.hand) - self.numberOf(self.lands, self.hand)
    
    def clearForNewTurn(self) -> None:
        """Clears all floating mana."""
        self.floating = [0, 0, 0, 0, 0, 0]
        self.storm = 0
    
    def sac(self, i: int) -> None:
        """Sacs element i from the battlefield and adds it to the graveyard."""
        if self.verbose:
            print(Style.RESET_ALL + Style.DIM + "sacs " + Style.RESET_ALL + Fore.CYAN + str(self.battlefield[i]) +
                  Style.RESET_ALL + Style.DIM + " -> yard " + Style.RESET_ALL + Fore.CYAN + str(self.graveyard) + Style.RESET_ALL)
        self.graveyard.append(self.battlefield.pop(i))

    def playPermanent(self, i: int) -> None:
        """Plays element i from the hand and adds it to the battlefield."""
        if self.verbose:
            print(Style.RESET_ALL + Style.DIM + "plays " + Style.RESET_ALL + Fore.CYAN + str(self.hand[i]) +
                  Style.RESET_ALL + Style.DIM + " -> field " + Style.RESET_ALL + Fore.CYAN + str(self.battlefield) + Style.RESET_ALL)
        self.battlefield.append(self.hand.pop(i))

    def playNonPermanent(self, i: int) -> None:
        if self.verbose:
            print(Style.RESET_ALL + Style.DIM + "plays " + Style.RESET_ALL + Fore.CYAN + str(self.hand[i]) +
                  Style.RESET_ALL + Style.DIM + " -> yard " + Style.RESET_ALL + Fore.CYAN + str(self.graveyard) + Style.RESET_ALL)
        self.graveyard.append(self.hand.pop(i))

    def statePlayFromHand(self, i: int) -> None:
        """If verbose, makes a pretty statement about a play."""
        if self.verbose:
            print(Style.RESET_ALL + Style.DIM + "plays " + Style.RESET_ALL + Fore.CYAN + str(self.hand[i]) + 
                  Style.RESET_ALL + Style.DIM + " -> field " + Style.RESET_ALL + Fore.CYAN + str(self.battlefield) + Style.RESET_ALL)


t_game = game(default, True)
t_game.firstTurns()
t_game.go()