"""Seed-bound bridge protocol for My Teacher Is an Alien Archipelago."""
import hashlib
import os
from pathlib import Path
from typing import Dict, Optional

VALID_LOCATIONS = set(range(1001, 1084))
FILLER_ITEMS = {2003}
GAME_ITEMS: Dict[int, int] = {
    2001: 7, 2002: 5, 2004: 2, 2005: 8, 2006: 22,
    2007: 9, 2008: 6, 2009: 4, 2010: 23,
    2011: 17, 2012: 24, 2013: 10, 2014: 25,
    2015: 3, 2016: 14, 2017: 21, 2018: 12, 2019: 11, 2020: 1,
    2021: 27, 2022: 28, 2023: 29, 2024: 26, 2025: 30,  # Virtual character unlocks
}


def world_token(seed_name: str, team: int, slot: int) -> str:
    identity = f'My Teacher Is an Alien\n{seed_name}\n{team}\n{slot}'
    return hashlib.sha256(identity.encode('utf-8')).hexdigest()[:32]


def write_world_binding(directory: Path, token: str, starting_mask: int = 1) -> bool:
    """Write tiny binding.txt on seed changes; never delete historical game logs."""
    if len(token) != 32 or not all(c in '0123456789abcdef' for c in token):
        raise ValueError('Invalid world token')
    if starting_mask not in (1, 2, 4, 7):
        raise ValueError('Invalid seed starting-character mask')
    path = directory / 'binding.txt'
    data = f'{token}\nSTART_MASK {starting_mask}\n'
    previous = path.read_text(encoding='ascii') if path.exists() else None
    if previous == data:
        return False
    temp = directory / 'binding.tmp'
    temp.write_text(data, encoding='ascii')
    os.replace(temp, path)
    # In-flight commands from a different world MUST NOT be processed.
    (directory / 'inbox.txt').unlink(missing_ok=True)
    return True


def read_events_since(path: Path, offset: int, token: str):
    """(offset, checks, epoch_change). epoch_change: NO_EVENT, None, or (session,generation).

    SESSION/LOAD/NEWGAME make the game not-ready; only READY permits item delivery.
    A game started on an old seed cannot emit new-world events without restart.
    """
    NO_EVENT = object()  # Only compared with `is` by a single caller per invocation.
    if not path.exists():
        return 0, set(), NO_EVENT, False
    length = path.stat().st_size
    if length < offset:
        offset = 0
    with path.open('rb') as stream:
        stream.seek(offset)
        data = stream.read()
        end = stream.tell()
    if data and not data.endswith(b'\n'):
        cut = data.rfind(b'\n') + 1
        data = data[:cut]
        end = offset + cut
    checks = set()
    epoch_change = NO_EVENT
    saw = False
    for raw in data.splitlines():
        f = raw.decode('ascii', errors='replace').strip().split()
        if len(f) == 4 and f[0] == 'CHECK' and f[1] == token and f[3].isdigit():
            location = int(f[3])
            if location in VALID_LOCATIONS:
                checks.add(location)
        elif len(f) == 4 and f[0] in ('SESSION', 'LOAD', 'NEWGAME', 'READY') and f[1] == token:
            try:
                generation = int(f[3])
            except ValueError:
                continue
            saw = True
            epoch_change = (f[2], generation) if f[0] == 'READY' else None
    return end, checks, epoch_change, saw


def read_applied(path: Path, token: str, epoch: Optional[tuple]) -> Dict[int, int]:
    if not path.exists() or epoch is None:
        return {}
    session, generation = epoch
    ack = {}
    with path.open('r', encoding='ascii', errors='replace') as stream:
        for line in stream:
            f = line.strip().split()
            if len(f) != 7 or f[0] != 'APPLIED' or f[1] != token or f[2] != session:
                continue
            try:
                gen, sequence, item_id, flag = map(int, f[3:])
            except ValueError:
                continue
            if gen == generation and sequence > 0 and item_id > 0 and flag in (0, 1):
                ack[sequence] = item_id
    return ack


def write_grant_if_free(directory: Path, token: str, epoch: tuple,
                        ap_item_code: int, sequence: int) -> bool:
    item_id = GAME_ITEMS.get(ap_item_code)
    if item_id is None or sequence <= 0 or epoch is None:
        return False
    directory.mkdir(parents=True, exist_ok=True)
    inbox = directory / 'inbox.txt'
    if inbox.exists():
        return False
    staging = directory / 'inbox.ap-writing'
    try:
        with staging.open('x', encoding='ascii', newline='\n') as stream:
            stream.write(f'GRANT {token} {epoch[0]} {epoch[1]} {item_id} {sequence}\n')
    except FileExistsError:
        return False
    try:
        if inbox.exists():
            return False
        os.replace(staging, inbox)
        return True
    finally:
        if staging.exists():
            staging.unlink()
