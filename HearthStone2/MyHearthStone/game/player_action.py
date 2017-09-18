#! /usr/bin/python
# -*- coding: utf-8 -*-

from .events import standard

__author__ = 'fyabc'


class PlayerAction:
    """"""

    def __init__(self, game):
        self.game = game

    def phases(self):
        """Extract phases from this player action."""

        raise NotImplementedError('implemented by subclasses')

    @classmethod
    def try_to_run(cls, game, *args, **kwargs):
        """Try to run the player action.
        It will search entities according to indices
        and validate conditions.

        :param game: The game instance.
        :param args: Contains zones and indices.
        :param kwargs: Other optional keywords.
        :return: The instance of this player action, None if failed.
        """

        return cls(game, *args, **kwargs)


class TurnEnd(PlayerAction):
    """"""

    def __init__(self, game, player_id=None):
        super().__init__(game)
        self.player_id = game.current_player if player_id is None else player_id

    def phases(self):
        return [
            standard.EndOfTurn(self.game), 'check_win',
            standard.BeginOfTurn(self.game), 'check_win',
            standard.DrawCard(self.game, None), 'check_win',
        ]


class Concede(PlayerAction):
    """May be useless?"""

    def __init__(self, game, player_id=None):
        super().__init__(game)
        self.player_id = game.current_player if player_id is None else player_id

    def phases(self):
        return [
            standard.HeroDeath(self.game, self.game.heroes[self.player_id]), 'check_win',
        ]


class PlaySpell(PlayerAction):
    """"""

    def __init__(self, game, spell, target, player_id=None):
        super().__init__(game)
        self.spell = spell
        self.target = target
        self.player_id = game.current_player if player_id is None else player_id

    def phases(self):
        return [
            standard.OnPlaySpell(self.game, self.spell, self.target, self.player_id),
            standard.SpellBenderPhase(self.game, self.spell, self.target, self.player_id),
            standard.SpellText(self.game, self.spell, self.target, self.player_id),
            standard.AfterSpell(self.game, self.spell, self.target, self.player_id),
            'check_win',
        ]


class PlayWeapon(PlayerAction):
    """"""

    def __init__(self, game, weapon, target, player_id=None):
        super().__init__(game)
        self.weapon = weapon
        self.target = target
        self.player_id = game.current_player if player_id is None else player_id

    def phases(self):
        return []


class PlayMinion(PlayerAction):
    """"""

    def __init__(self, game, minion, loc, target, player_id=None):
        super().__init__(game)
        self.minion = minion
        self.loc = loc
        self.target = target
        self.player_id = game.current_player if player_id is None else player_id

    def phases(self):
        return [
            standard.OnPlayMinion(self.game, self.minion, self.loc, self.target, self.player_id),
            standard.BattlecryPhase(self.game, self.minion, self.loc, self.target, self.player_id),
            standard.AfterPlayMinion(self.game, self.minion, self.player_id),
            standard.AfterSummon(self.game, self.minion, self.player_id),
            'check_win',
        ]


class ToAttack(PlayerAction):
    """"""

    def __init__(self, game, attacker, defender):
        super().__init__(game)
        self.attacker = attacker
        self.defender = defender

    def phases(self):
        return []


class UseHeroPower(PlayerAction):
    """"""

    def __init__(self, game, target, player_id):
        super().__init__(game)
        self.target = target
        self.player_id = game.current_player if player_id is None else player_id

    def phases(self):
        return []
