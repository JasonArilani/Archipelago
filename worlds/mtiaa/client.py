"""My Teacher Is an Alien Archipelago client.

Handles per-slot item delivery, event checks, and gameplay goal reporting.
"""
import asyncio
import json
import logging
import time
from pathlib import Path

from CommonClient import gui_enabled, server_loop

# Universal Tracker can share this client's connection and add a Tracker tab.
# When it is not installed, MTIAA continues to use the ordinary AP client.
try:
    from worlds.tracker.TrackerClient import TrackerGameContext as BaseMTIAAContext
except ImportError:
    from CommonClient import CommonContext as BaseMTIAAContext
    TRACKER_AVAILABLE = False
else:
    TRACKER_AVAILABLE = True
from NetUtils import ClientStatus
from .world import LOCATIONS, ALL_ENDING_LOCATIONS, REGULAR_ENDINGS, FULL_ENDINGS
from .bridge_files import (GAME_ITEMS, FILLER_ITEMS, world_token, write_world_binding,
                           read_applied, read_events_since, write_grant_if_free)

log = logging.getLogger('MTIAA')
CONFIG_FILE = Path.home() / 'mtiaa_ap_client.json'
EXAMPLE_CONFIG = {
    'bridge_dir': 'C:\\Games\\MTIAA-AP\\CDDATA\\DATA\\apbridge'
}


def read_config():
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(json.dumps(EXAMPLE_CONFIG, indent=2) + '\n', encoding='utf-8')
        raise RuntimeError(f'Created sample {CONFIG_FILE}; edit it and relaunch')
    cfg = json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
    if not isinstance(cfg.get('bridge_dir'), str) or not cfg['bridge_dir'].strip():
        raise ValueError('Invalid client config: bridge_dir')
    return cfg


class MTIAAContext(BaseMTIAAContext):
    game = 'My Teacher Is an Alien'
    items_handling = 0b111
    want_slot_data = True

    def __init__(self, config):
        super().__init__(None, None)
        self.auth = None
        self.username = None
        self.bridge_dir = Path(config['bridge_dir']).expanduser()
        if not self.bridge_dir.is_dir():
            raise RuntimeError(f'Bridge folder not found: {self.bridge_dir}')
        self._events = self.bridge_dir / 'events.log'
        self._applied = self.bridge_dir / 'applied.log'
        self._event_offset = 0
        self._seen_checks = set()
        self._epoch = None
        self._pending = None
        self._pending_since = 0.0
        self._goal_sent = False
        self._world = None
        self._starting_mask = 1
        self._goal = 0
        self._full_ending = False
        self._seed = None
        self._server_connected = False
        self._items_ready = False
        log.warning('MTIAA: connect client before starting AP game; '
                    'restart the game when switching seeds. No manual log deletion.')

    async def connect(self, address=None):
        if address:
            self.auth = None
            self.username = None
        await super().connect(address)


    def _clear_tracker_connection(self):
        """Clear disconnected UT state while remaining an AP *game* client.

        TrackerGameContext.disconnect() normally performs this cleanup only
        when the connection has a ``Tracker`` tag. MTIAA must omit that tag,
        so we perform the necessary cleanup ourselves instead.
        """
        self._server_connected = False
        self._items_ready = False
        self._seed = None
        if not TRACKER_AVAILABLE:
            return

        # Clear the UI before disposing of the old generated tracker world.
        self.set_page('Connect to a slot to start tracking!')
        for field, value in (
            ('tracker_total_locs_label', 'Locations: 0/0'),
            ('tracker_logic_locs_label', 'In Logic: 0'),
            ('tracker_glitched_locs_label', 'Glitched: 0'),
            ('tracker_hinted_locs_label', 'Hinted: 0'),
            ('tracker_go_mode_label', 'Go Mode: No'),
        ):
            label = getattr(self, field, None)
            if label is not None:
                label.text = value
        if self.ui is not None:
            if hasattr(self.ui, 'show_map'):
                self.ui.show_map = False
            if hasattr(self.ui, 'show_items'):
                self.ui.show_items = False
        self.tracker_core.disconnect()
        self.tracker_world = None
        self.local_items.clear()

    async def disconnect(self, allow_autoreconnect=False):
        # User-initiated disconnect, including connect-to-different-room.
        self._clear_tracker_connection()
        await super().disconnect(allow_autoreconnect)

    async def connection_closed(self):
        # Also handles the room/server closing unexpectedly. Must not mark
        # the user as intentionally disconnected, so auto-reconnect still works.
        try:
            await super().connection_closed()
        finally:
            self._clear_tracker_connection()

    async def server_auth(self, password_requested=False):
        await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd, args):
        # Universal Tracker needs each packet to update its tracked items,
        # checked locations, and available checks.  The normal context's
        # handler remains in place when Tracker is not installed.
        super().on_package(cmd, args)
        if cmd == 'RoomInfo':
            self._server_connected = False
            self._items_ready = False
            self._seed = args.get('seed_name')
        if cmd == 'Connected':
            seed = self._seed or getattr(self, 'seed_name', None) or args.get('seed_name')
            team = args.get('team', getattr(self, 'team', None))
            slot = args.get('slot', getattr(self, 'slot', None))
            if not seed or team is None or slot is None:
                log.error('No verified seed/team/slot. Bridge stays disabled.')
                return
            token = world_token(str(seed), int(team), int(slot))
            slot_data = args.get('slot_data') or {}
            mask = slot_data.get('starting_mask', 1)
            if mask not in (1, 2, 4, 7):
                log.error('Invalid starting-character mask in slot_data: %r', mask)
                return
            goal = slot_data.get('goal', 0)
            full_ending = slot_data.get('full_ending', False)
            if type(goal) is not int or goal not in range(5):
                log.error('Invalid ending goal: %r', goal)
                return
            self._goal = goal
            self._full_ending = bool(full_ending)
            changed = write_world_binding(self.bridge_dir, token, mask)
            self._starting_mask = mask
            if token != self._world:
                self._world = token
                self._event_offset = 0
                self._seen_checks.clear()
                self._epoch = None
                self._pending = None
                self._pending_since = 0.0
                self._goal_sent = False
            self._server_connected = True
            self._items_ready = False
            log.info('Connected: seed=%s team=%s slot=%s world=%s', seed, team, slot, token)
            if changed:
                log.warning('New seed binding written. Start/restart TEACHER.EXE now. '
                            'Old checks in logs will be ignored automatically.')
        if cmd == 'ReceivedItems':
            self._items_ready = True
            log.info('ReceivedItems now has %d items', len(self.items_received))


def ending_check_ids(goal, full):
    """New AP IDs, selected by name to avoid hardcoded ID dependencies."""
    if goal == 0:
        return {LOCATIONS["Complete Any Full Ending" if full else "Complete Any Ending"]}
    if goal == 4:
        names = FULL_ENDINGS.values() if full else REGULAR_ENDINGS.values()
        return {LOCATIONS[name] for name in names}
    character = {1: "Peter", 2: "Susan", 3: "Duncan"}[goal]
    return {LOCATIONS[(FULL_ENDINGS if full else REGULAR_ENDINGS)[character]]}


def active_ending_ids(goal, full):
    """All ending locations present in this goal configuration."""
    if goal == 0:
        names = ["Complete Any Ending"]
        if full:
            names.append("Complete Any Full Ending")
    elif goal == 4:
        names = list(REGULAR_ENDINGS.values())
        if full:
            names.extend(FULL_ENDINGS.values())
    else:
        character = {1: "Peter", 2: "Susan", 3: "Duncan"}[goal]
        names = [REGULAR_ENDINGS[character]]
        if full:
            names.append(FULL_ENDINGS[character])
    return {LOCATIONS[name] for name in names}


def outstanding_receipts(ctx):
    applied = read_applied(ctx._applied, ctx._world, ctx._epoch)
    missing = []
    for index, item in enumerate(ctx.items_received):
        if item.item in FILLER_ITEMS:
            continue
        game_item = GAME_ITEMS.get(item.item)
        if game_item is None:
            log.warning('Unsupported item %s at index %d', item.item, index)
            continue
        if applied.get(index + 1) != game_item:
            missing.append(index)
    return missing


async def bridge_watcher(ctx):
    while not ctx.exit_event.is_set():
        try:
            if ctx._server_connected and ctx._world is not None:
                offset, checks, epoch, changed = read_events_since(ctx._events, ctx._event_offset, ctx._world)
                ctx._event_offset = offset
                active_checks = set(LOCATIONS.values()) - {LOCATIONS[name] for name in ALL_ENDING_LOCATIONS}
                active_checks.update(active_ending_ids(ctx._goal, ctx._full_ending))
                ctx._seen_checks.update(checks & active_checks)
                if changed and epoch != ctx._epoch:
                    ctx._epoch = epoch
                    ctx._pending = None
                    ctx._pending_since = 0.0
                    if epoch is None:
                        log.info('Game started or is loading; grant delivery paused.')
                    else:
                        log.info('Game ready: session=%s generation=%s', *epoch)
                if ctx.slot is not None and ctx._seen_checks:
                    await ctx.check_locations(ctx._seen_checks)
                if ctx.slot is not None and ctx._epoch is not None and ctx._items_ready:
                    receipts = read_applied(ctx._applied, ctx._world, ctx._epoch)
                    if ctx._pending is not None and receipts.get(ctx._pending + 1) == GAME_ITEMS.get(ctx.items_received[ctx._pending].item):
                        ctx._pending = None
                        ctx._pending_since = 0.0
                    elif (ctx._pending is not None and time.monotonic() - ctx._pending_since > 6
                          and not (ctx.bridge_dir / 'inbox.txt').exists()):
                        log.warning('No receipt for item index %d; retrying', ctx._pending)
                        ctx._pending = None
                    if ctx._pending is None:
                        missing = outstanding_receipts(ctx)
                        if missing:
                            index = missing[0]
                            item = ctx.items_received[index].item
                            if write_grant_if_free(ctx.bridge_dir, ctx._world, ctx._epoch, item, index + 1):
                                ctx._pending = index
                                ctx._pending_since = time.monotonic()
                                log.info('Deliver item index %d game item %d', index, GAME_ITEMS[item])
                    required = ending_check_ids(ctx._goal, ctx._full_ending)
                    checked = getattr(ctx, 'checked_locations', set())
                    if (not ctx._goal_sent and required.issubset(checked)):
                        ctx._goal_sent = True
                        ctx.finished_game = True
                        await ctx.send_msgs([{'cmd': 'StatusUpdate', 'status': ClientStatus.CLIENT_GOAL}])
        except (OSError, ValueError, IndexError) as error:
            log.warning('Bridge I/O: %s', error)
        await asyncio.sleep(0.5)


async def main(config):
    ctx = MTIAAContext(config)
    watcher = asyncio.create_task(bridge_watcher(ctx), name='MTIAA bridge watcher')
    ctx.server_task = asyncio.create_task(server_loop(ctx), name='AP server connection')
    if TRACKER_AVAILABLE:
        # Start Universal Tracker's logic generator inside this game client.
        # We must connect as an AP game client, never a tracker-only client.
        ctx.run_generator()
        ctx.tags.discard('Tracker')
    if gui_enabled:
        ctx.run_gui()
    else:
        ctx.run_cli()
    try:
        await ctx.exit_event.wait()
    finally:
        watcher.cancel()
        await asyncio.gather(watcher, return_exceptions=True)
        await ctx.shutdown()


def run_client(*args):
    from Utils import init_logging
    init_logging('MTIAAClient', exception_logger='Client')
    asyncio.run(main(read_config()))
