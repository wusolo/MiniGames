#! /usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'fyabc'


def order_of_play(objects):
    """Sort objects by the order of play.

    :param objects: Entities or events or triggers.
    :return: List of objects, sorted by order of play.
    """

    return sorted(objects, key=lambda o: o.oop)


def error_and_stop(game, event, msg):
    """Show an error message and stop the event.

    :param game:
    :param event:
    :param msg:
    :return:
    """

    game.error_stub(msg)
    event.disable()
    game.stop_subsequent_phases()


class Zone:
    """An enumeration class, contains zones of the card."""

    Invalid = 0
    Deck = 1
    Hand = 2
    Play = 3
    Secret = 4
    Graveyard = 5
    SetAside = 6
    Weapon = 7

    Str2Idx = {
        'Invalid': Invalid,
        'Deck': Deck,
        'Hand': Hand,
        'Play': Play,
        'Secret': Secret,
        'Graveyard': Graveyard,
        'SetAside': SetAside,
        'Weapon': Weapon,
    }

    Idx2Str = {v: k for k, v in Str2Idx.items()}


class Condition:
    """The class of conditions to get random cards or select cards."""

    pass


__all__ = [
    'order_of_play',
    'error_and_stop',
    'Zone',
    'Condition',
]
