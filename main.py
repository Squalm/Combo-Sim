"""
Fishelbrand pauper deck simulator
---------------------------------
Copyright (c) Squalm 2023

Scope:  
Optimise a fishelbrand deck by goldfishing it and making small changes.
"""

import random
import itertools
import numpy
from copy import deepcopy
from colorama import Fore, Style
from tqdm import tqdm

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
# weather      = 214
wraith       = 233
# epicure      = 234

cardLookupDict = {
    1: 'plains',
    2: 'island',
    3: 'swamp',
    4: 'mountain',
    5: 'forest',
    11: 'spring',
    12: 'skerry',
    13: 'vent',
    101: 'star',
    102: 'petal',
    111: 'offering',
    112: 'ritual',
    113: 'manamorphose',
    121: 'brainspoil',
    122: 'energytap',
    123: 'looting',
    124: 'kaervek',
    125: 'ponder',
    126: 'preordain',
    127: 'knowledge',
    128: 'visions',
    131: 'gurmangler',
    132: 'attendants',
    203: 'sphere',
    233: 'wraith'
}

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

deckBase = [
    star, star, star, star,
    petal, petal,
    offering, offering, offering,
    ritual, ritual, ritual,
    manamorphose, manamorphose, manamorphose,
    energytap, energytap, energytap,
    kaervek,
    ponder, ponder, ponder,
    preordain, preordain, preordain, preordain,   
    knowledge, knowledge, knowledge, knowledge,
    gurmangler, gurmangler,
    attendants, attendants, attendants,
    spring, spring, spring, spring,
    island,
    skerry, skerry, skerry, skerry,
    vent, vent, vent,
] # 47 cards

deckOptions = [
    petal,
    offering,
    ritual,
    manamorphose,
    energytap,
    ponder,
    gurmangler, gurmangler,
    attendants,
    forest,
    mountain,
    swamp,
    sphere, sphere, sphere,
    wraith, wraith, wraith, wraith,
    brainspoil, brainspoil,
    visions, visions,
    looting, looting,
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
        self.tapped = []

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
        self.filtering = [star, sphere, manamorphose, petal]

        if self.verbose:
            print("# NEW GAME")
            print(Style.DIM + "mulliganing..." + Style.RESET_ALL)

        self.mulligan()

    def state(self, full = False) -> None:
        if self.verbose:
            print(Style.RESET_ALL + Style.DIM + "Tu " + Style.RESET_ALL + Fore.CYAN + f"{self.turn} " +
                Style.RESET_ALL + Style.DIM + "Ha " + Style.RESET_ALL + Fore.CYAN + f"{len(self.hand)} " +
                Style.RESET_ALL + Style.DIM + "Ba " + Style.RESET_ALL + Fore.CYAN + f"{len(self.battlefield)} " +
                Style.RESET_ALL + Style.DIM + "Gr " + Style.RESET_ALL + Fore.CYAN + f"{len(self.graveyard)} " +
                Style.RESET_ALL + Style.DIM + "Li " + Style.RESET_ALL + Fore.CYAN + f"{len(self.library)} " + 
                Style.RESET_ALL + Style.DIM + "St " + Style.RESET_ALL + Fore.CYAN + f"{self.storm}" + 
                Style.RESET_ALL + Style.DIM + " : " + Style.RESET_ALL + 
                Fore.YELLOW + f"{self.floating[0]} " + Fore.BLUE + f"{self.floating[1]} " + Fore.MAGENTA + f"{self.floating[2]} " + 
                Fore.RED + f"{self.floating[3]} " + Fore.GREEN + f"{self.floating[4]} " + Fore.WHITE + f"{self.floating[5]}" + Style.RESET_ALL)
            if full:
                print(Style.RESET_ALL + Style.DIM + "  hand   " + Style.RESET_ALL + Fore.CYAN + str(self.lookUpNames(self.hand)))
                print(Style.RESET_ALL + Style.DIM + "  field  " + Style.RESET_ALL + Fore.CYAN + str(self.lookUpNames(self.battlefield)))
                print(Style.RESET_ALL + Style.DIM + "  tapped " + Style.RESET_ALL + Fore.CYAN + str(self.lookUpNames(self.tapped)) + Style.RESET_ALL)
                print(Style.RESET_ALL + Style.DIM + "  yard   " + Style.RESET_ALL + Fore.CYAN + str(self.lookUpNames(self.graveyard)) + Style.RESET_ALL)
            
    def stateTurn(self) -> None:
        if self.verbose:
            print(f"\n# TURN {self.turn}")

    def lookUpNames(self, l: list) -> list:
        """Returns the english names of cards with ids in the list `l`."""
        return [cardLookupDict.get(i, str(i)) for i in l]

    def win(self, bywhat) -> None:
        if self.verbose:
            print(f"WON BY {bywhat}!")

    def lose(self) -> None:
        if self.verbose:
            self.state()
            print("LOST :(")

    def draw(self, n: int) -> None:
        """Draw `n` cards."""

        if self.verbose:
            drawn = self.library[0:n]
            print(Style.RESET_ALL + Style.DIM + "draws " + Style.RESET_ALL + Fore.CYAN + str(self.lookUpNames(drawn)) + Style.RESET_ALL)

        for _ in range (0, n):
            if len(self.library) == 0:
                self.lose()
                break
            self.hand.append(self.library.pop(0))

    def scry(self, n: int) -> None:
        """Scrys `n` cards."""
        if len(self.library) < n:
            self.lose()
        peek = self.library[0:n]

        bottom = []
        top = []

        bad = self.tappedLands
        good = [kaervek]

        wantCreatures = self.numberOf(self.creatures, self.hand) <= 0
        wantFiltering = self.numberOf(self.filtering, self.hand) + self.numberOf(self.filtering, self.battlefield) <= 2
        wantDraw = self.numberOf(self.easydraw, self.hand) <= 1
        wantKnowledge = self.numberOf([knowledge, brainspoil], self.hand) <= 0 and sum(self.floating) > 5
        wantLand = self.numberOf(self.untappedLands, self.hand) + self.numberOf(self.untappedLands, self.tapped) <= 0

        for card in peek:
            if card in good:
                top.append(card)
            elif card in bad:
                bottom.append(card)

            elif (wantCreatures and card in self.creatures) or (wantFiltering and card in self.creatures) or (wantDraw and card in self.easydraw) or (wantKnowledge and card in [knowledge, brainspoil]) or (wantLand and card in self.untappedLands):
                top.append(card)
            
            else:
                bottom.append(card)
            
        for card in bottom:
            library.append(card)
        for card in top:
            library.insert(0, card)

        if self.verbose:
            print(Style.RESET_ALL + Style.DIM + "scrys " + Style.RESET_ALL + Fore.CYAN + f"{self.lookUpNames(top)} top, {self.lookUpNames(bottom)} bottom" + Style.RESET_ALL)

    def discard(self, n: int) -> None:
        """Discards `n` card from hand."""
        if self.verbose:
            print(Style.RESET_ALL + Style.DIM + "discards " + Style.RESET_ALL + Fore.CYAN + str(n) + Style.RESET_ALL)
        for _ in range(0, n):
            # check for lands in hand
            handLands = [card for card in self.hand if card in self.lands]
            handCreatures = [card for card in self.hand if card in self.creatures]
            if len(handLands) > 0:
                self.graveyard.append(self.hand.pop(self.hand.index(handLands[0])))
            elif len(handCreatures) > 1:
                self.graveyard.append(self.hand.pop(self.hand.index(handCreatures[0])))
            elif len(self.hand) > 0:
                self.graveyard.append(self.hand.pop(0))
                
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
                self.state(True)  

            if self.turn != 1:
                self.draw(1)

            if self.numberOf(self.lands, self.hand) > 0:
               self.playLand()

            # Play stars and spheres on turn 3
            if self.turn == 3:
                self.tapLands()
                if self.numberOf([star, sphere], self.hand) > 0:
                    self.playStars()
            
            self.state()

        self.turn = 4
        self.clearForNewTurn()

        self.stateTurn()
        self.state(True)
        self.draw(1)

    def go(self) -> bool:
        """Attempts to combo off and returns a bool based on whether it won."""
        
        # First make mana
        self.tapSacLands()

        playedALand = False

        # Loop forever until we win or can't play anything.
        while True:

            playedSomething = False

            if len(self.library) == 0:
                self.lose()
                return False

            # Make obvious plays
            for i in range(0, len(self.hand)):

                if playedSomething:
                    self.state()
                    break
                
                # Kaervek's touch to win the game
                if self.hand[i] == kaervek:
                    if self.floating[R] >= 1 and sum(self.floating) >= 21:
                        self.spend(20, 0, 0, 0, 1, 0)
                        self.playNonPermanent(i)
                        self.state()
                        self.win(kaervek)
                        playedSomething = True
                        return True

                # Petals
                elif self.hand[i] == petal:
                    self.playPermanent(i)
                    playedSomething = True
                
                # Rituals
                elif self.hand[i] == ritual:
                    if self.floating[B] >= 1:

                        # effect
                        self.floating[B] += 2 # -1 +3
                        
                        self.playNonPermanent(i)
                        playedSomething = True

                elif self.hand[i] == wraith:
                    # cycle wraith
                    self.storm -= 1
                    self.playNonPermanent(i)

                    self.draw(1)

                    playedSomething = True

                # Try to play an untapped land if we haven't already
                elif (not playedALand) and self.hand[i] in self.untappedLands:
                    playedSomething = self.playKindOfLand(self.untappedLands)

                    self.tapBasics()
                
                
            # Now that we've made all the obvious plays,
            # here're the rest of our priorities:
            #    1. PLAY DELVE CREATURE
            #    2. GENERATE MANA
            #    3. DRAW CARDS
            #    4. DIG
            
            if not playedSomething:

                # Delve for creature
                if len(self.graveyard) >= 7 and attendants in self.hand and (self.floating[B] >= 1):
                    i = self.hand.index(attendants)

                    self.spend(max(0, 7-len(self.graveyard)),0,0,1)
                    self.delve(min(7, len(self.graveyard)))

                    self.playPermanent(i)
                    playedSomething = True
                            
                elif len(self.graveyard) >= 6 and gurmangler in self.hand and self.floating[B] >= 1:
                    i = self.hand.index(gurmangler)

                    self.spend(max(0, 6-len(self.graveyard)),0,0,1)
                    self.delve(min(6, len(self.graveyard)))

                    self.playPermanent(i)
                    playedSomething = True

                # Make mana
                elif petal in self.battlefield:
                    i = self.battlefield.index(petal)

                    self.make(1)
                    self.sac(i)

                    playedSomething = True
                
                elif energytap in self.hand and self.floating[U] >= 1 and self.maxCMCon(self.battlefield) >= 7:
                    spell = self.hand.index(energytap)
                    creature = self.battlefield.index(attendants) if attendants in self.battlefield else self.battlefield.index(gurmangler)

                    self.spend(0, 0, 1)
                    self.floating[colorless] += self.maxCMCon(self.battlefield)
                    
                    self.tap(creature)
                    self.playNonPermanent(spell)

                    playedSomething = True
                
                elif offering in self.hand and self.floating[B] >= 1 and (self.maxCMCon(self.battlefield) >= 7 or self.maxCMCon(self.tapped) >= 7):
                    spell = self.hand.index(offering)
                    creature = -1
                    tapped = False

                    if attendants in self.tapped:
                        creature = self.tapped.index(attendants)
                        tapped = True
                    elif gurmangler in self.tapped:
                        creature = self.tapped.index(gurmangler)
                        tapped = True
                    elif attendants in self.battlefield:
                        creature = self.battlefield.index(attendants)
                    elif gurmangler in self.battlefield:
                        creature = self.battlefield.index(gurmangler)

                    if tapped:
                        self.spend(0, 0, 0, 1)
                        self.make(self.maxCMCon(self.tapped), False, False, True, True, False)

                        self.sac(creature, True)
                        self.statePlayFromHand(spell)
                        self.playNonPermanent(spell)
                    else:
                        self.spend(0, 0, 0, 1)
                        self.make(self.maxCMCon(self.battlefield), False, False, True, True, False)
                    
                        self.sac(creature)
                        self.playNonPermanent(spell)

                    playedSomething = True

                # Filter mana
                elif star in self.battlefield and sum(self.floating) >= 1:
                    i = self.battlefield.index(star)

                    self.spend(1)
                    self.make(1)
                    self.sac(i)
                    self.draw(1)

                    playedSomething = True

                elif sphere in self.battlefield and sum(self.floating) >= 1:
                    i = self.battlefield.index(sphere)

                    self.spend(1)
                    self.make(1)
                    self.draw(1)
                    self.sac(i)

                    playedSomething = True

                elif star in self.hand and sum(self.floating) >= 2:
                    i = self.hand.index(star)

                    self.spend(1)
                    self.playPermanent(i)

                    playedSomething = True

                elif sphere in self.hand and sum(self.floating) >= 2:
                    i = self.hand.index(sphere)

                    self.spend(1)
                    self.playPermanent(i)

                    playedSomething = True
                
                elif manamorphose in self.hand and self.floating[R] >= 1 and sum(self.floating) >= 2:
                    i = self.hand.index(manamorphose)

                    self.spend(1, 0, 0, 0, 1)
                    self.make(2)
                    self.draw(1)

                    self.playNonPermanent(i)

                    playedSomething = True

                # Draw cards
                elif (knowledge in self.hand) and (sum(self.floating) >= 7 and self.floating[B] >= 1) and (self.numberOf(self.creatures, self.battlefield) + self.numberOf(self.creatures, self.tapped) >= 1):
                    i = self.hand.index(knowledge)

                    self.spend(4, 0, 1)
                    self.playNonPermanent(i)
                    # effect
                    cmc = max(self.maxCMCon(self.battlefield), self.maxCMCon(self.tapped))
                    self.draw(cmc)

                    playedSomething = True

                elif brainspoil in self.hand and self.floating[B] >= 2 and self.floating[U] >= 1 and sum(self.floating) >= 10 and self.library.count(knowledge) > 0:
                    i = self.hand.index(brainspoil)
                    # account for increase of storm (it shouldn't increase)
                    self.storm -= 1
                    self.playNonPermanent(i)

                    self.spend(1, 0, 0, 2)

                    self.library.pop(self.library.index(knowledge))
                    self.hand.append(knowledge)
                    random.shuffle(self.library)

                    playedSomething = True

                # Dig for cards
                elif ponder in self.hand and self.floating[U] >= 1:
                    i = self.hand.index(ponder)

                    # approximate ponder as scry 2
                    self.spend(0,0,1)
                    self.playNonPermanent(i)

                    self.scry(2)
                    self.draw(1)


                    playedSomething = True
                
                elif preordain in self.hand and self.floating[U] >= 1:
                    i = self.hand.index(preordain)

                    # approximate ponder as scry 2
                    self.spend(0,0,1)
                    self.playNonPermanent(i)

                    self.scry(2)
                    self.draw(1)

                    playedSomething = True

                elif looting in self.hand and self.floating[R] >= 1:
                    i = self.hand.index(looting)

                    self.spend(0,0,0,0,1)
                    self.playNonPermanent(i)

                    self.draw(2)
                    self.discard(2)

                elif visions in self.hand and self.floating[U] >= 1:
                    i = self.hand.index(visions)

                    # approximate ponder as scry 2
                    self.spend(0,0,1)
                    self.playNonPermanent(i)

                    self.draw(1)
                    self.scry(2)

                    playedSomething = True


                self.state(True)
            
            # if we don't play anything from our hand, lose!
            if not playedSomething:
                self.lose()
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

                    if self.hand[i] in self.untappedLands:
                        self.battlefield.append(self.hand.pop(i))
                    else:
                        self.tapped.append(self.hand.pop(i))

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
        for _ in range(4):
            for i in range(0, len(self.battlefield)):
                if self.battlefield[i] in self.tappedLands:

                    if self.battlefield[i] == spring:
                        self.floating[1] += 1
                        self.tap(i)
                        break
                    elif self.battlefield[i] == vent:
                        self.floating[2] += 1
                        self.tap(i)
                        break
            
        
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
                        self.floating[W] += 1
                        self.floating[B] += 1
                        self.sac(i)
                        break
                    elif self.battlefield[i] == skerry:
                        self.floating[U] += 2
                        self.sac(i)
                        break
                    elif self.battlefield[i] == vent:
                        self.floating[U] += 1
                        self.floating[R] += 1
                        self.sac(i)
                        break
        
        self.state()

    def tapBasics(self) -> None:
        for card in self.battlefield:
            if card in self.untappedLands:

                y = False
                if card == plains:
                    self.floating[0] += 1
                    y = True
                elif card == island:
                    self.floating[1] += 1
                    y = True
                elif card == swamp:
                    self.floating[2] += 1
                    y = True
                elif card == mountain:
                    self.floating[3] += 1
                    y = True
                elif card == forest:
                    self.floating[4] += 1
                    y = True

                if y:
                    self.tapped.append(self.battlefield.pop(self.battlefield.index(card)))

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
        """Resets for new turn."""
        self.floating = [0, 0, 0, 0, 0, 0]
        self.storm = 0
        for _ in range(0, len(self.tapped)):
            self.battlefield.append(self.tapped.pop(0))
    
    def sac(self, i: int, tapped = False) -> None:
        """Sacs element i from the battlefield and adds it to the graveyard."""
        if not tapped:
            if self.verbose:
                print(Style.RESET_ALL + Style.DIM + "sacs " + Style.RESET_ALL + Fore.CYAN + cardLookupDict[self.battlefield[i]] + Style.RESET_ALL)
            self.graveyard.append(self.battlefield.pop(i))
        else:
            if self.verbose:
                print(Style.RESET_ALL + Style.DIM + "sacs " + Style.RESET_ALL + Fore.CYAN + cardLookupDict[self.tapped[i]] + Style.RESET_ALL)
            self.graveyard.append(self.tapped.pop(i))

    def tap(self, i: int) -> None:
        if self.verbose:
            print(Style.RESET_ALL + Style.DIM + "taps " + Style.RESET_ALL + Fore.CYAN + cardLookupDict[self.battlefield[i]] + Style.RESET_ALL)
        self.tapped.append(self.battlefield.pop(i))

    def delve(self, n: int) -> None:
        """Exile cards from graveyard when delving for creatures."""
        if self.verbose:
            print(Style.RESET_ALL + Style.DIM + "delves " + Style.RESET_ALL + Fore.CYAN + str(n) + Style.RESET_ALL)
        for _ in range(0,n):
            self.graveyard.pop(0)

    def playPermanent(self, i: int) -> None:
        """Plays element i from the hand and adds it to the battlefield."""
        if self.verbose:
            print(Style.RESET_ALL + Style.DIM + "plays " + Style.RESET_ALL + Fore.CYAN + cardLookupDict[self.hand[i]] +
                  Style.RESET_ALL + Style.DIM + " -> field " + Style.RESET_ALL + Fore.CYAN + str(self.lookUpNames(self.battlefield)) + Style.RESET_ALL)
        self.battlefield.append(self.hand.pop(i))
        self.storm += 1

    def playNonPermanent(self, i: int) -> None:
        if self.verbose:
            print(Style.RESET_ALL + Style.DIM + "plays " + Style.RESET_ALL + Fore.CYAN + cardLookupDict[self.hand[i]] +
                  Style.RESET_ALL + Style.DIM + " -> yard " + Style.RESET_ALL + Fore.CYAN + str(self.lookUpNames(self.graveyard)) + Style.RESET_ALL)
        self.graveyard.append(self.hand.pop(i))
        self.storm += 1

    def spend(self, c = 0, w = 0, u = 0, b = 0, r = 0, g = 0) -> None:
        """Spends as much mana as passed in.
        
        args: `colourless, W,U,B,R,G`"""

        self.floating[W] -= w
        self.floating[U] -= u
        self.floating[B] -= b
        self.floating[R] -= r
        self.floating[G] -= g

        while c > 0:
            if sum(self.floating) <= 0:
                print("tried to pay for something but ran out of mana!")
                break
        
            if self.floating[colorless] > 0:
                self.floating[colorless] -= 1
                c -= 1
            elif self.floating[W] > 0:
                self.floating[W] -= 1
                c -= 1
            elif sum(self.floating) - sum(self.floating[U:R]) > 0: # Just the floating W,R,G
                self.floating[max([W,R,G], key=lambda i: self.floating[i])] -= 1
                c -= 1
            elif self.floating[U] > 0:
                self.floating[U] -= 1
                c -= 1
            else:
                self.floating[B] -= 1
                c -= 1

    def make(self, amount = 0, w = False, u = True, b = True, r = True, g = False) -> None:
        """Makes as much mana as passed in from the colours specified.
        
        args: `amount, W,U,B,R,G`"""

        available = []
        if w: available.append(W)
        if u: available.append(U)
        if b: available.append(B)
        if r: available.append(R)
        if g: available.append(G)

        for _ in range(0, amount):
            self.floating[min(available, key=lambda i: self.floating[i])] += 1

    def maxCMCon(self, place: list) -> int:

        cmc = 0
        for permanent in place:
            if permanent == gurmangler and cmc < 7:
                cmc = 7
            elif permanent == attendants and cmc < 8:
                cmc = 8
            elif permanent == star and cmc < 1:
                cmc = 1
            elif permanent == sphere and cmc < 1:
                cmc = 1

        return cmc

    def statePlayFromHand(self, i: int) -> None:
        """If verbose, makes a pretty statement about a play."""
        if self.verbose:
            print(Style.RESET_ALL + Style.DIM + "plays " + Style.RESET_ALL + Fore.CYAN + cardLookupDict[self.hand[i]] + 
                  Style.RESET_ALL + Style.DIM + " -> field " + Style.RESET_ALL + Fore.CYAN + str(self.lookUpNames(self.battlefield)) + Style.RESET_ALL)


def allDecks(deckBase: list, deckOptions: list, deckSize=60) -> list:
    """Return a list of all possible decks using a constant base and list of options.
    
    List returned has no duplicates."""
    cardCounts = {}
    for card in deckBase:
        cardCounts[card] = cardCounts.get(card, 0) + 1

    toAdd = deckSize - len(deckBase)
    # Generate all possible combinations of cards
    all_possible_decks = []
    for comb in itertools.combinations(deckOptions, toAdd):
        all_possible_decks.append(tuple(deckBase) + comb)

    return list(set(all_possible_decks)) # enforce uniqueness

# Decks are by default tuples, but are passed to games as lists
# TODO: avoid gobbling memory!
toCheck = allDecks(deckBase, deckOptions)

# Get everything ready to spit out a csv
def prettyDecklist(deck: list) -> str:
    """Returns a string of the counts of different cards ready to be put into the CSV."""
    counts = {}
    for card in cardLookupDict:
        counts[card] = 0
    for card in deck:
        counts[card] += 1
    
    out = ""
    for card in counts:
        out += str(counts[card]) + ","
    return out

# top of CSV
out = open('results.csv', 'w')
out.write(", ".join([cardLookupDict[name] for name in cardLookupDict]) + ",\n")
out.close()

# Do the calcs
for chunk in numpy.array_split(numpy.array(toCheck),1000):

    out = open('results.csv', 'a')
    
    wins = {}
    for deck in tqdm(chunk):
        won = 0
        for _ in range(0,10000):
            t = game(list(deck))
            t.firstTurns()
            won += t.go()
        wins[tuple(deck)] = won

    # The fact that the orders are the same so this works is slightly tenuous.
    for deck in wins:
        out.write(prettyDecklist(deck) + str(wins[deck]) + ",\n")
    out.close()

    print(max(wins, key= lambda x: x[1]))
