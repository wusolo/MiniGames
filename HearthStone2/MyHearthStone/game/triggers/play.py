#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Standard triggers of play events."""

from ..events import standard
from .trigger import StandardBeforeTrigger
from ...utils.game import error_and_stop, Zone

__author__ = 'fyabc'


class StdOnPlaySpell(StandardBeforeTrigger):
    """Standard trigger of OnPlaySpell."""

    respond = [standard.OnPlaySpell]

    def process(self, event: respond[0]):
        """Process the OnPlaySpell event.

        The card is removed from your hand and enters Play and its Mana cost is paid.
        If it targets, the target is remembered (and its validity is not checked again).
        (If Bloodbloom or Cho'Gall is out, you take damage instead.
        This damage is resolved immediately, e.g. for Floating Watcher.)

        :param event: The event to be processed.
        :return: new event list.
        """

        player_id = event.player_id

        # todo: Add effect of Cho'gall
        if self.game.mana[player_id] < event.spell.cost:
            error_and_stop(self.game, event, 'You do not have enough mana!')
            return []

        if not event.spell.check_target(event.target):
            error_and_stop(self.game, event, 'This is not a valid target!')
            return []

        if event.spell.data['secret']:
            if self.game.full(Zone.Secret, player_id):
                error_and_stop(self.game, event, 'I cannot have more secrets!')
                return []

            for card in self.game.get_zone(Zone.Secret, player_id):
                if card.data['id'] == event.spell.data['id']:
                    error_and_stop(self.game, event, 'I already have this secret!')
                    return []

        # [NOTE]: move it to ``Game.move``?
        event.spell.oop = self.game.inc_oop()
        event.message()

        tz = Zone.Graveyard
        if event.spell.data['secret']:
            tz = Zone.Secret

        self.game.move(player_id, Zone.Hand, event.spell, player_id, tz, 'last')

        return []


class StdSpellBlenderPhase(StandardBeforeTrigger):
    """Standard trigger of SpellBlenderPhase (may be useless?)."""

    respond = [standard.SpellBenderPhase]

    def process(self, event: respond[0]):
        event.message()
        return []


class StdSpellText(StandardBeforeTrigger):
    """Standard trigger of SpellText."""

    respond = [standard.SpellText]

    def process(self, event: respond[0]):
        event.message()
        return event.spell.run(event.target)


class StdAfterSpell(StandardBeforeTrigger):
    """Standard trigger of AfterSpell (may be useless?)."""

    respond = [standard.AfterSpell]

    def process(self, event: respond[0]):
        event.message()
        return []


class StdOnPlayMinion(StandardBeforeTrigger):
    """Standard trigger of OnPlayMinion."""

    respond = [standard.OnPlayMinion]

    def process(self, event: respond[0]):
        """Process the OnPlayMinion event.

        :param event: The event to be processed.
        :return: new event list.
        """

        player_id = event.player_id

        # todo: Add effect of Seadevil Stinger
        if self.game.mana[player_id] < event.minion.cost:
            error_and_stop(self.game, event, 'You do not have enough mana!')
            return []

        if not event.minion.check_target(event.target):
            error_and_stop(self.game, event, 'This is not a valid target!')
            return []

        # todo

        event.message()
        return []


class StdOnBattlecry(StandardBeforeTrigger):
    """Standard trigger of BattlecryPhase."""

    respond = [standard.BattlecryPhase]


class StdAfterPlayMinion(StandardBeforeTrigger):
    """Standard trigger of AfterPlayMinion."""

    respond = [standard.AfterPlayMinion]


class StdAfterSummon(StandardBeforeTrigger):
    """Standard trigger of AfterSummon."""

    respond = [standard.AfterSummon]