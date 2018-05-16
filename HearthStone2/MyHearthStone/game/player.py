#! /usr/bin/python
# -*- coding: utf-8 -*-

"""The class of player."""

import itertools
import random

from .game_entity import GameEntity
from ..utils.constants import C
from ..utils.game import Zone
from ..utils.message import info, debug
from ..utils.package_io import all_cards, all_heroes

__author__ = 'fyabc'


class Player(GameEntity):
    DeckMax = C.Game.DeckMax
    HandMax = C.Game.HandMax
    PlayMax = C.Game.PlayMax
    SecretMax = C.Game.SecretMax
    ManaMax = C.Game.ManaMax
    TurnMax = C.Game.TurnMax
    StartCardOffensive, StartCardDefensive = C.Game.StartCard

    CoinCardID = "43"

    def __init__(self, game):
        super().__init__(game)

        # Mana and overloads.
        self.max_mana = 0
        self.temp_mana = 0
        self.used_mana = 0
        self.overload = 0
        self.overload_next = 0

        # Zones.
        self.hero = None
        self.hero_power = None
        self.deck = []
        self.hand = []
        self.play = []
        self.secret = []
        self.weapon = None
        self.graveyard = []

        # Misc.
        self.tire_counter = 0
        self.start_player = None

    def start_game(self, deck, player_id: int, start_player: int):
        info('Deck of player {}: {}'.format(player_id, deck))
        self.player_id = player_id
        self.start_player = start_player

        self._init_mana()

        cards = all_cards()
        heroes = all_heroes()

        self.hero = heroes[deck.klass](self.game, player_id)
        self.deck = [cards[card_id](self.game, player_id) for card_id in deck.card_id_list]
        random.shuffle(self.deck)

        if player_id == start_player:
            self.hand = self.deck[:self.StartCardOffensive]
            self.deck = self.deck[self.StartCardOffensive:]
        else:
            self.hand = self.deck[:self.StartCardDefensive]
            self.deck = self.deck[self.StartCardDefensive:]

        self.tire_counter = 0

    def on_replace_done(self, replace):
        replace = sorted(set(replace))  # Get sorted unique elements
        info('Replace hand {} of player {}'.format(replace, self.player_id))
        replace_index = random.sample(list(range(len(self.deck))), k=len(replace))
        for hand_index, deck_index in zip(replace, replace_index):
            self.deck[deck_index], self.hand[hand_index] = self.hand[hand_index], self.deck[deck_index]
        random.shuffle(self.deck)

        # Add coin into defensive hand
        if self.player_id != self.start_player:
            self.hand.append(all_cards()[self.CoinCardID](self.game, 1 - self.start_player))

        self._init_card_zones()

    def end_game(self):
        # TODO: add more clean here?
        pass

    def _init_card_zones(self):
        """Initialize cards' zones when the game start.

        This will call ``move_map`` to do some other initializing (such as triggers)
        """
        # Need to init hero zone?

        for zone_id in Zone.Idx2Str.keys():
            try:
                zone = self.get_zone(zone_id)
                for card in zone:
                    # Weapon may be None.
                    if card is not None:
                        card.zone = zone_id
            except ValueError:
                pass
        self.hero.zone = Zone.Hero
        if self.weapon is not None:
            self.weapon.zone = Zone.Weapon

    def _init_mana(self):
        self.max_mana = 0
        self.temp_mana = 0
        self.used_mana = 0
        self.overload = 0
        self.overload_next = 0

    def generate(self, to_zone, to_index, entity):
        """Generate an entity into a zone.

        :param to_zone: The target zone.
        :param entity: The entity id to be generated, or the entity object.
        :param to_index: The target index of the entity.
            if it is 'last', means append.
        :return: a tuple of (entity, dict)
            The generated entity (None when failed).
            The dict contains:
                'success': The bool indicate success or not.
                'events': The list contains consequence events.
                'from_index': None.
                'to_index': The final insert index.
        """

        # If the play board is full, do nothing.
        if self.full(to_zone):
            debug('{} full!'.format(Zone.Idx2Str[to_zone]))
            return None, {
                'success': False,
                'events': [],
                'from_index': None,
                'to_index': None,
            }

        if isinstance(entity, int):
            # Convert integer to string for backward compatibility.
            entity = str(entity)
        if isinstance(entity, str):
            entity = self.create_card(entity, player_id=self.player_id)

        index = self.insert_entity(entity, to_zone, to_index)

        return entity, {
            'success': True,
            'events': [],
            'to_index': index,
        }

    def insert_entity(self, entity, to_zone, to_index):
        """Insert an entity.

        :param entity:
        :param to_zone:
        :param to_index:
        :return:
        """
        tz = self.get_zone(to_zone)

        # todo: set oop when moving to play zone.
        # todo: set other things
        # todo: fix the problems of hero, weapons, and other unique zones (how to insert?)

        if to_index == 'last':
            tz.append(entity)
            to_index = len(tz) - 1
        else:
            tz.insert(to_index, entity)
        entity.zone = to_zone
        entity.player_id = self.player_id

        return to_index

    def full(self, zone):
        if zone == Zone.Deck:
            return len(self.deck) >= self.DeckMax
        if zone == Zone.Hand:
            return len(self.hand) >= self.HandMax
        if zone == Zone.Secret:
            return len(self.secret) >= self.SecretMax
        if zone == Zone.Play:
            return len(self.play) >= self.PlayMax
        if zone == Zone.Graveyard:
            return False
        if zone == Zone.Weapon:
            return self.weapon is not None
        if zone == Zone.Hero:
            return self.hero is not None
        if zone == Zone.HeroPower:
            return self.hero_power is not None
        return False

    def get_all_entities(self):
        """Get all entities in the game.

        Contains:
            entities in deck, hand, play, hero, weapon, hero_power, secret;
        Excludes:
            entities in graveyard;
            enchantments;
            ...

        :return: Iterator of all entities.
        """

        return itertools.chain(
            self.deck, self.hand, self.secret, self.play, [self.weapon, self.hero, self.hero_power])

    def get_zone(self, zone):
        if zone == Zone.Deck:
            return self.deck
        if zone == Zone.Hand:
            return self.hand
        if zone == Zone.Secret:
            return self.secret
        if zone == Zone.Play:
            return self.play
        if zone == Zone.Graveyard:
            return self.graveyard
        if zone == Zone.Weapon:
            return [self.weapon]
        if zone == Zone.Hero:
            return [self.hero]
        if zone == Zone.HeroPower:
            return [self.hero_power]
        raise ValueError('Does not have zone {!r}'.format(Zone.Idx2Str.get(zone, zone)))

    def get_entity(self, zone, index=0):
        return self.get_zone(zone)[index]

    def add_mana(self, value: int, action: str):
        """Add mana.

         Mana rules copied from Advanced Rulebook:
            Rule M1: Your current mana is capped at 10 but has no lower limit. Negative current mana is displayed as 0.
            Rule M2: Your maximum mana (number of Mana Crystals) is always at most 10 and at least 0.
            Rule M3: Your current/pending Overloaded Mana Crystals has no upper limit.
            Rule M4: Gaining or losing maximum mana has no effect on your pending/current Overload.
            Rule M8: Kun the Forgotten King gives you 10 temporary mana crystals, but no more than your maximum mana.
        See also:
            Felguard <https://hearthstone.gamepedia.com/Felguard>
            Mana crystals <https://hearthstone.gamepedia.com/Mana#Mana_Crystals>
            Current mana <https://hearthstone.gamepedia.com/Advanced_rulebook#Why_available_mana_can_be_negative>

        :param value: (int) Mana value to be added.
        :param action: (str)
            'T': Add temp mana
            'M': Add (empty) max mana
            'D': Destroy mana
            'B': Both add max mana and temp mana
            'R': Restore mana
            'N': New turn: add a new max mana and restore all mana
        """

        if action == 'N':
            # New turn
            self.max_mana = min(self.ManaMax, value + self.max_mana)
            self.overload = self.overload_next
            self.overload_next = 0
            self.temp_mana = 0
            self.used_mana = self.overload
        elif action == 'T':
            self.temp_mana = min(self.ManaMax, value + self.temp_mana)
        else:
            raise ValueError('Unknown action {!r}'.format(action))

    def spend_mana(self, value):
        """Spend mana."""

        # assert value <= self.displayed_mana()

        if value < self.temp_mana:
            # Also handle the case of `value == 0`.
            self.temp_mana -= value
            return
        value -= self.temp_mana
        self.temp_mana = 0
        self.used_mana += value

    def spend_all_mana(self):
        """Spend all available mana.

        :return: Value of spent mana.
        """

        result = self.displayed_mana()
        self.temp_mana = 0
        self.used_mana = self.max_mana
        return result

    def __repr__(self):
        return super()._repr(player_id=self.player_id)

    def displayed_mana(self):
        """Get displayed current mana value. Negative value will be displayed as 0.

        From Advanced Rulebook:
            'Available mana' does not exist as a tag, but is calculated as RESOURCES + TEMP_RESOURCES - RESOURCES_USED.

        :return: Current mana values for display.
        """
        return max(0, self.max_mana + self.temp_mana - self.used_mana)

    def create_card(self, card_id, **kwargs):
        return all_cards()[card_id](self.game, **kwargs)

    def format_zone(self, zone, verbose=False):
        """Format cards in the zone into string.

        :param zone:
        :param verbose: If True, return str(card), or only return card.name if False. [False]
        :return: String to represent the zone.
        :rtype: str
        """

        if verbose:
            return str(self.get_zone(zone))
        else:
            return str([card.name for card in self.get_zone(zone)])
