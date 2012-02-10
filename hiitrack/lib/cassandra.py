#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cassandra methods for dealing with hashed keys.
"""

from ..lib.hash import pack_hash
from twisted.internet.defer import inlineCallbacks, returnValue
import struct
import time
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from ..lib.profiler import profile
from collections import defaultdict

CLIENT = None
HIGH_ID = chr(255) * 16
RELATION_INSERT_BUFFER = defaultdict(dict)
COUNTER_INSERT_BUFFER = defaultdict(dict)


def pack_timestamp():
    """
    Return a packed byte string representing a timestamp.
    """
    return struct.pack(">1d", time.time())


def cols_to_dict(columns, prefix=None):
    """
    Convert a Cassandra row into a dictionary.
    """
    if prefix:
        prefix_length = len(prefix)
        return OrderedDict([
            (x.column.name[prefix_length:], x.column.value)
                for x in columns])
    else:
        return OrderedDict([(x.column.name, x.column.value)
            for x in columns])


def counter_cols_to_dict(columns, prefix=None):
    """
    Convert a Cassandra row into a dictionary.
    """
    if prefix:
        prefix_length = len(prefix)
        return OrderedDict([
            (x.counter_column.name[prefix_length:], x.counter_column.value)
                for x in columns])
    else:
        return OrderedDict([(x.counter_column.name, x.counter_column.value)
            for x in columns])


@profile
def set_user(key, column, value, consistency=None):
    """
    Sets a key and column in the user column family.
    """
    return CLIENT.insert(
        key=key,
        column_family="user",
        consistency=consistency,
        column=column,
        value=value)


@profile
@inlineCallbacks
def get_user(key, column, consistency=None):
    """
    Gets a key and column in the user column family.
    """
    result = yield CLIENT.get(
        key=key,
        column_family="user",
        consistency=consistency,
        column=column)
    returnValue(result.column.value)


@profile
def delete_user(key, consistency=None):
    """
    Deletes a key and column in the user column family.
    """
    return CLIENT.remove(
        key=key,
        column_family="user",
        consistency=consistency)


@profile
@inlineCallbacks
def get_relation(
        key,
        column=None,
        column_id=None,
        prefix=None,
        consistency=None):
    """
    Get a row, column, or slice from the relation column family.
    """
    if column_id:
        result = yield CLIENT.get(
            key=pack_hash(key),
            column_family="relation",
            consistency=consistency,
            column=column_id)
        returnValue(result.column.value)
    elif column:
        result = yield CLIENT.get(
            key=pack_hash(key),
            column_family="relation",
            consistency=consistency,
            column=pack_hash(column))
        returnValue(result.column.value)
    else:
        if prefix:
            start = prefix
            finish = prefix + HIGH_ID
        else:
            start = ''
            finish = ''
        result = yield CLIENT.get_slice(
            key=pack_hash(key),
            column_family="relation",
            start=start,
            finish=finish,
            consistency=consistency)
        returnValue(cols_to_dict(result, prefix=prefix))


@profile
def insert_relation(key, column, value, consistency=None):
    """
    Insert a column into the relation column family using a hashed
    column tuple.
    """
    key = pack_hash(key)
    column_id = pack_hash(column)
    return _insert_relation(key, column_id, value, consistency)


@profile
def insert_relation_by_id(key, column_id, value, consistency=None):
    """
    Insert a column into the relation column family using a column ID.
    """
    key = pack_hash(key)
    return _insert_relation(key, column_id, value, consistency)


def _insert_relation(key, column_id, value, consistency):
    return CLIENT.insert(
        key=key,
        column_family="relation",
        consistency=consistency,
        column=column_id,
        value=value)


@profile
def delete_relation(key, column=None, column_id=None, consistency=None):
    """
    Delete a row or column from the relation CF.
    """
    if column_id:
        return CLIENT.remove(
            key=pack_hash(key),
            column_family="relation",
            column=column_id,
            consistency=consistency)
    elif column:
        return CLIENT.remove(
            key=pack_hash(key),
            column_family="relation",
            column=pack_hash(column),
            consistency=consistency)
    else:
        return CLIENT.remove(
            key=pack_hash(key),
            column_family="relation",
            consistency=consistency)


@profile
@inlineCallbacks
def get_counter(key, consistency=None, prefix=None):
    """
    Get all columns from a row of counters.
    """
    if prefix:
        start = prefix
        finish = prefix + HIGH_ID
    else:
        start = ''
        finish = ''
    result = yield CLIENT.get_slice(
        key=pack_hash(key),
        column_family="counter",
        consistency=consistency,
        start=start,
        finish=finish,
        count=10000)
    returnValue(counter_cols_to_dict(result, prefix=prefix))


@profile
def increment_counter(
        key,
        column=None,
        consistency=None,
        column_id=None,
        value=1):
    """
    Increment a counter specified by a hashed column tuple or a column_id.
    """
    if column_id:
        return CLIENT.add(
            key=pack_hash(key),
            column_family="counter",
            consistency=consistency,
            column=column_id,
            value=value)
    elif column:
        return CLIENT.add(
            key=pack_hash(key),
            column_family="counter",
            consistency=consistency,
            column=pack_hash(column),
            value=value)
    else:
        raise TypeError("column composite key or column_id is required.")


@profile
def delete_counter(key, column=None, column_id=None, consistency=None):
    """
    Delete a row or column from the counter CF.
    """
    if column_id:
        return CLIENT.remove_counter(
            key=pack_hash(key),
            column_family="counter",
            column=column_id,
            consistency=consistency)
    elif column:
        return CLIENT.remove_counter(
            key=pack_hash(key),
            column_family="counter",
            column=pack_hash(column),
            consistency=consistency)
    else:
        return CLIENT.remove_counter(
            key=pack_hash(key),
            column_family="counter",
            consistency=consistency)
