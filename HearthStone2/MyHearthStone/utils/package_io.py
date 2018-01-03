#! /usr/bin/python
# -*- coding: utf-8 -*-

"""I/O utilities for package data (project built-in or user extension)."""

import sys
import os
from locale import getdefaultlocale
from importlib import import_module
import json

from .constants import get_package_paths, C
from .message import error, warning, msg_block
from ..game.game_entity import SetDataMeta
from ..game.card import Card
from ..game.hero import Hero

__author__ = 'fyabc'


_AllCards = None
_AllHeroes = None
_AllGameData = None


def _load_module_variables(root_package_path, package_name):
    """Load all variables in a Python module file.

    :param root_package_path: The path of the module.
    :param package_name: The name of the module.
    :return: All variables in this module.
    """

    _origin_sys_path = sys.path.copy()

    full_package_name = os.path.join(root_package_path, package_name)

    try:
        sys.path.append(root_package_path)

        module_vars = vars(import_module(package_name))

    except ImportError:
        error('Error when loading package {}'.format(full_package_name))
        module_vars = None
    finally:
        sys.path = _origin_sys_path

    return module_vars


class _GameData:
    """The game data object, may be useful in future (load card images, etc.).

    Game data contains some packages and resources.
    A package is a Python file, contains some cards and heroes.
    """

    ResourcePathName = 'resources'
    ImagesPathName = 'images'
    SoundsPathName = 'sounds'
    ValuesPathName = 'values'

    def __init__(self, path):
        self.path = path
        self._package_vars = None

    @property
    def resource_path(self):
        return os.path.join(self.path, self.ResourcePathName)

    @property
    def vars_list(self):
        if self._package_vars is None:
            self._load_package_vars()
        return self._package_vars

    def _load_package_vars(self):
        self._package_vars = []
        for filename in os.listdir(self.path):
            package_name, ext = os.path.splitext(filename)
            if ext == '.py':
                module_vars = _load_module_variables(self.path, package_name)
                if module_vars is not None:
                    self._package_vars.append(module_vars)

    def load_strings(self, cards_dict: dict, heroes_dict: dict):
        """Load strings of name and description (specific locale) of cards and heroes."""

        my_locale = C.Locale
        if my_locale is None:
            my_locale = getdefaultlocale()[0]

        values_filename = os.path.join(self.path, self.ResourcePathName, self.ValuesPathName, my_locale + '.json')
        if not os.path.exists(values_filename):
            warning('Locale "{}" not found, use default locale "{}".'.format(my_locale, C.DefaultLocale))
            my_locale = C.DefaultLocale
            values_filename = os.path.join(self.path, self.ResourcePathName, self.ValuesPathName, my_locale + '.json')

            if not os.path.exists(values_filename):
                warning('Default locale not found, do not load strings.')
                return

        try:
            with open(values_filename, 'r', encoding='utf-8') as f:
                values_dict = json.load(f)
            values_cards = values_dict['Cards']
            values_heroes = values_dict['Heroes']
            for k, v in values_cards.items():
                assert isinstance(v, list)
                assert len(v) == 2
                assert isinstance(v[0], str)
                assert isinstance(v[1], str)

                var = cards_dict.get(int(k), None)
                if var is not None:
                    data = getattr(var, '_data')
                    data['name'] = v[0]
                    data['description'] = v[1]
            for k, v in values_heroes.items():
                assert isinstance(v, list)
                assert len(v) == 2
                assert isinstance(v[0], str)
                assert isinstance(v[1], str)

                var = heroes_dict.get(int(k), None)
                if var is not None:
                    data = getattr(var, '_data')
                    data['name'] = v[0]
                    data['description'] = v[1]
        except (json.JSONDecodeError, ValueError, AssertionError) as e:
            error('Error when loading locale of game data in "{}"'.format(self.path))
            return


def _load_packages():
    """Load package data."""

    AllCards = {}
    AllHeroes = {}
    AllGameData = []

    with msg_block('Loading cards and heroes'):
        for package_path in get_package_paths():
            AllGameData.append(_GameData(package_path))

            for vars_ in AllGameData[-1].vars_list:
                for var in vars_.values():
                    if isinstance(var, SetDataMeta) and issubclass(var, Card):
                        data = var.data

                        card_id = data.get('id', None)
                        if card_id is None:
                            continue

                        if card_id in AllCards:
                            if AllCards[card_id] == var:
                                continue
                            warning('The card id {} already exists, overwrite it'.format(card_id))

                        AllCards[card_id] = var
                    elif isinstance(var, SetDataMeta) and issubclass(var, Hero):
                        data = var.data

                        hero_id = data.get('id', None)
                        if hero_id is None:
                            continue

                        if hero_id in AllHeroes:
                            if AllHeroes[hero_id] == var:
                                continue
                            warning('The hero id {} already exists, overwrite it'.format(hero_id))

                        AllHeroes[hero_id] = var

            AllGameData[-1].load_strings(AllCards, AllHeroes)

    return AllCards, AllHeroes, AllGameData


def all_cards():
    """Get dict of all cards.

    If cards not loaded, it will load cards automatically.

    :return: Dict of all cards.
    """

    global _AllCards, _AllHeroes, _AllGameData
    if _AllCards is None:
        _AllCards, _AllHeroes, _AllGameData = _load_packages()
    return _AllCards


def all_heroes():
    """Get dict of all heroes.

    If heroes not loaded, it will load heroes automatically.

    :return: Dict of all heroes.
    """

    global _AllCards, _AllHeroes, _AllGameData
    if _AllHeroes is None:
        _AllCards, _AllHeroes, _AllGameData = _load_packages()
    return _AllHeroes


def search_by_name(name):
    """Search card by name, return the FIRST card with same name.

    :param name: card name
    :return: card id
    """

    data = all_cards()

    for i, e in data.items():
        if e.data['name'] == name:
            return i

    return None


__all__ = [
    'all_cards',
    'all_heroes',
    'search_by_name',
]
