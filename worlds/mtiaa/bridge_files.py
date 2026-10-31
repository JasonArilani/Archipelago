"""Seed-bound bridge protocol for My Teacher Is an Alien Archipelago."""
import hashlib
import os
from pathlib import Path
from typing import Dict, Optional

# The shipped TEACHER.EXE still emits original gameplay event IDs.
# Translate those IDs to the reorganized Archipelago location IDs.
# Do NOT change the game executable's event IDs.
GAME_EVENT_TO_AP_LOCATION = {
    # School Periods
    1048: 1001,  # Monday - Started Period 1
    1049: 1002,  # Monday - Started Period 2
    1050: 1003,  # Monday - Started Period 3
    1051: 1004,  # Monday - Started Period 4
    1052: 1005,  # Monday - Started Period 5
    1053: 1006,  # Tuesday - Started Period 1
    1054: 1007,  # Tuesday - Started Period 2
    1055: 1008,  # Tuesday - Started Period 3
    1056: 1009,  # Tuesday - Started Period 4
    1057: 1010,  # Tuesday - Started Period 5
    1058: 1011,  # Wednesday - Started Period 1
    1059: 1012,  # Wednesday - Started Period 2
    1060: 1013,  # Wednesday - Started Period 3
    1061: 1014,  # Wednesday - Started Period 4
    1062: 1015,  # Wednesday - Started Period 5
    1063: 1016,  # Thursday - Started Period 1
    1064: 1017,  # Thursday - Started Period 2
    1065: 1018,  # Thursday - Started Period 3
    1066: 1019,  # Thursday - Started Period 4
    1067: 1020,  # Thursday - Started Period 5
    # Classrooms
    1002: 1021,  # Mr. Daniels' Classroom - Magnet
    1068: 1022,  # Mr. Daniels' Classroom - Peter Completed Roach Experiment
    1069: 1023,  # Ms. Marsh's Classroom - Duncan Set Off Fire Alarm
    1004: 1024,  # Mr. Tucker's Classroom - Tuning Fork
    1070: 1025,  # Mr. Tucker's Classroom - Susan Completed Investigation
    # Hallways
    1020: 1026,  # Hall - Found Alien Device
    1071: 1027,  # Hall - Survived Orville's Stink Bombs
    1017: 1028,  # Hall - Susan Obtained Business Card
    # Locker Rooms
    1001: 1029,  # Girls Locker Room - Susan's Cassette Recorder
    1003: 1030,  # Boys Locker Room - Peter's Radio
    1038: 1031,  # Boys Locker Room - Witnessed Mike's Kidnapping
    # Office and Library
    1012: 1032,  # Office - Thermos
    1014: 1033,  # Office - Maintenance Key
    1015: 1034,  # Library - Obtained Computer Password
    # Computers
    1021: 1035,  # Computer - Unlocked Alien Hunter Website
    1030: 1036,  # Computer - Viewed Artifacts Page
    1005: 1037,  # Computer - Learned Disrupt Speech Test Recipe
    1009: 1038,  # Computer - Learned Taste Test Recipe
    1013: 1039,  # Computer - Learned Water Test
    1011: 1040,  # Computer - Learned Awful Sound Test Recipe
    1010: 1041,  # Computer - Downloaded Awful Sound
    # Maintenance, Kitchen, and Teacher Lounge
    1006: 1042,  # Maintenance Room - Dust Bunnies
    1007: 1043,  # Maintenance Room - Moth Balls
    1008: 1044,  # Kitchen - Blunder Bread
    1016: 1045,  # Teacher's Lounge - Kidnapping List
    # Duct System
    1022: 1046,  # Ducts - Enter the Duct System
    1024: 1047,  # Ducts - Removed Teacher's Lounge Vent
    1025: 1048,  # Ducts - Cleared Rats
    1037: 1049,  # Ducts - Susan Witnessed Alien Mask Removal
    # Alien Device and Police Station
    1029: 1050,  # Alien Device - Viewed Spaceship Maps
    1032: 1051,  # Police Station - Spoke to Police Officer
    # Teacher Investigations
    1072: 1052,  # School - Performed Disrupt Speech Test
    1073: 1053,  # School - Performed Taste Test
    1074: 1054,  # School - Performed Awful Sound Test
    1075: 1055,  # School - Performed Water Test
    1034: 1056,  # School - Ruled Out Mr. Tucker
    1035: 1057,  # School - Ruled Out Ms. Marsh
    1036: 1058,  # School - Ruled Out Mr. Daniels
    1033: 1059,  # School - Identified Alien Teacher
    # Spaceship
    1023: 1060,  # Spaceship - Enter the Spaceship
    1018: 1061,  # Spaceship - Ray Gun and Glasses
    1019: 1062,  # Spaceship - Alien Translator
    1026: 1063,  # Spaceship - Completed Left Bridge Puzzle
    1027: 1064,  # Spaceship - Completed Right Bridge Puzzle
    1028: 1065,  # Spaceship - Defeated Slime Boss
    1031: 1066,  # Spaceship - Discovered Hidden Nook
    1076: 1067,  # Spaceship - Solved Left Forcefield
    1077: 1068,  # Spaceship - Solved Middle Forcefield
    1078: 1069,  # Spaceship - Solved Right Forcefield
    # Student Rescues
    1039: 1070,  # Rescued Linsey Carter
    1040: 1071,  # Rescued Mike Foran
    1041: 1072,  # Rescued Wendy Sanders
    1042: 1073,  # Rescued Jack McCall
    1043: 1074,  # Rescued Stacy Benoit
    1044: 1075,  # Rescued Orville Plumber
    # Endings
    1079: 1076,  # Complete Any Ending
    1083: 1077,  # Complete Any Full Ending
    1045: 1078,  # Complete Peter's Ending
    1080: 1079,  # Complete Peter's Full Ending
    1046: 1080,  # Complete Duncan's Ending
    1081: 1081,  # Complete Duncan's Full Ending
    1047: 1082,  # Complete Susan's Ending
    1082: 1083,  # Complete Susan's Full Ending
}
FILLER_ITEMS = {2025}
GAME_ITEMS: Dict[int, int] = {
    # Physical Items and Evidence
    2001: 7,  # Magnet
    2002: 8,  # Tuning Fork
    2003: 2,  # Radio
    2004: 5,  # Cassette Recorder
    2005: 9,  # Dust Bunnies
    2006: 6,  # Moth Balls
    2007: 4,  # Blunder Bread
    2008: 10,  # Thermos
    2009: 3,  # Maintenance Key
    2010: 14,  # Computer Password
    2011: 21,  # Kidnapping List
    2012: 12,  # Business Card
    2013: 11,  # Ray Gun and Glasses
    2014: 1,  # Alien Translator
    2015: 30,  # Alien Device
    # Test Knowledge and Downloads
    2016: 22,  # Disrupt Speech Test Recipe
    2017: 23,  # Taste Test Recipe
    2018: 17,  # Awful Sound Download
    2019: 24,  # Awful Sound Test Recipe
    2020: 25,  # Water Test Knowledge
    # Character Unlocks
    2021: 26,  # Peter Unlock
    2022: 27,  # Susan Unlock
    2023: 28,  # Duncan Unlock
    # Period Unlocks
    2024: 29,  # Progressive Period
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
            ap_location = GAME_EVENT_TO_AP_LOCATION.get(location)
            if ap_location is not None:
                checks.add(ap_location)
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
