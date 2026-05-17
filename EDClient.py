import asyncio
import logging
import time

import pymem
import pymem.memory

import Utils
from CommonClient import CommonContext, server_loop
from NetUtils import ClientStatus


PROCESS_NAME = "Dolphin.exe"
GC_RAM_BASE = 0x80000000

CHECK_FLAGS = 0x80725EB0
GOAL_FLAG = 0x80725E52

MEM = {
    "codices": 0x80331748,
    "runes": 0x8033174A,
    "circles": 0x8033174C,
    "scrolls": 0x80331750,
}

LOCATION_FLAGS = {
    0x01: "Anthony - 3 Point Circle",
    0x02: "Anthony - Weak Alignment Rune",
    0x04: "Anthony - Antorbok Rune",
    0x08: "Anthony - Magormor Rune",
    0x10: "Anthony - Weak Alignment Codex",
    0x20: "Anthony - Antorbok Codex",
    0x40: "Anthony - Magormor Codex",
    0x80: "Anthony - Enchant Item Scroll",
}

LOCATION_NAME_TO_ID = {
    "Anthony - 3 Point Circle": 990000,
    "Anthony - Weak Alignment Rune": 990001,
    "Anthony - Antorbok Rune": 990002,
    "Anthony - Magormor Rune": 990003,
    "Anthony - Weak Alignment Codex": 990004,
    "Anthony - Antorbok Codex": 990005,
    "Anthony - Magormor Codex": 990006,
    "Anthony - Enchant Item Scroll": 990007,
}

ITEM_ID_TO_NAME = {
    990100: "3 Point Circle",
    990101: "Weak Alignment Rune",
    990102: "Antorbok Rune",
    990103: "Magormor Rune",
    990104: "Weak Alignment Codex",
    990105: "Antorbok Codex",
    990106: "Magormor Codex",
    990107: "Enchant Item Scroll",
}

ALIGNMENT_ROUTES = {
    "chatturgha": {
        "display": "Chattur'gha",
        "weak_name": "Xel'lotath",
        "weak_rune_bit": 0x0004,
        "weak_codex_bit": 0x0004,
    },
    "ulyaoth": {
        "display": "Ulyaoth",
        "weak_name": "Chattur'gha",
        "weak_rune_bit": 0x0001,
        "weak_codex_bit": 0x0001,
    },
    "xelotath": {
        "display": "Xel'lotath",
        "weak_name": "Ulyaoth",
        "weak_rune_bit": 0x0002,
        "weak_codex_bit": 0x0002,
    },
}


def proc_addr(ram_base, effective_addr):
    return ram_base + (effective_addr - GC_RAM_BASE)


def read_u8(pm, ram_base, effective_addr):
    return pm.read_bytes(proc_addr(ram_base, effective_addr), 1)[0]


def read_u16(pm, ram_base, effective_addr):
    return int.from_bytes(pm.read_bytes(proc_addr(ram_base, effective_addr), 2), "big")


def write_u16(pm, ram_base, effective_addr, value):
    pm.write_bytes(proc_addr(ram_base, effective_addr), value.to_bytes(2, "big"), 2)


def read_u32(pm, ram_base, effective_addr):
    return int.from_bytes(pm.read_bytes(proc_addr(ram_base, effective_addr), 4), "big")


def write_u32(pm, ram_base, effective_addr, value):
    pm.write_bytes(proc_addr(ram_base, effective_addr), value.to_bytes(4, "big"), 4)


def find_ram_base(pm):
    print("Finding Dolphin RAM base...")

    addr = 0
    candidates = []

    while addr < 0x7FFFFFFFFFFF:
        try:
            mbi = pymem.memory.virtual_query(pm.process_handle, addr)
        except Exception:
            addr += 0x10000
            continue

        base = mbi.BaseAddress
        size = mbi.RegionSize
        protect = mbi.Protect
        state = mbi.State

        if state == 0x1000 and protect in (0x04, 0x40) and size >= 0x01800000:
            try:
                codices = read_u16(pm, base, MEM["codices"])
                runes = read_u16(pm, base, MEM["runes"])
                circles = read_u16(pm, base, MEM["circles"])
                flags = read_u8(pm, base, CHECK_FLAGS)

                if codices <= 0x3FFF and runes <= 0x3FFF and circles <= 0x0007:
                    candidates.append((base, size, codices, runes, circles, flags))
            except Exception:
                pass

        next_addr = base + size
        addr = next_addr if next_addr > addr else addr + 0x10000

    exact = [c for c in candidates if c[1] == 0x4000000]

    if exact:
        base, size, codices, runes, circles, flags = exact[0]
    elif candidates:
        base, size, codices, runes, circles, flags = candidates[0]
    else:
        raise RuntimeError("Could not find RAM base.")

    print(
        "Using RAM base:",
        hex(base),
        "size", hex(size),
        f"codices={codices:04X}",
        f"runes={runes:04X}",
        f"circles={circles:04X}",
        f"flags={flags:02X}",
    )

    return base


def normalize_scroll_word(actual_scroll, expected_scroll_owned):
    if expected_scroll_owned:
        if actual_scroll == 0:
            return 0x08000000
        return actual_scroll

    high16 = (actual_scroll >> 16) & 0xFFFF
    low16 = actual_scroll & 0xFFFF

    status_high = high16 & 0xFF00
    circle_y = high16 & 0x00FF

    if actual_scroll == 0x08000000:
        return 0

    if status_high in (0x0C00, 0x0E00):
        if circle_y != 0 and low16 != 0:
            return ((0x0400 | circle_y) << 16) | low16
        return 0

    return actual_scroll


def write_core_state(pm, ram_base, expected):
    write_u16(pm, ram_base, MEM["codices"], expected["codices"])
    write_u16(pm, ram_base, MEM["runes"], expected["runes"])
    write_u16(pm, ram_base, MEM["circles"], expected["circles"])


def police_memory(pm, ram_base, expected):
    codices = read_u16(pm, ram_base, MEM["codices"])
    runes = read_u16(pm, ram_base, MEM["runes"])
    circles = read_u16(pm, ram_base, MEM["circles"])
    scrolls = read_u32(pm, ram_base, MEM["scrolls"])

    if codices != expected["codices"]:
        write_u16(pm, ram_base, MEM["codices"], expected["codices"])

    if runes != expected["runes"]:
        write_u16(pm, ram_base, MEM["runes"], expected["runes"])

    if circles != expected["circles"]:
        write_u16(pm, ram_base, MEM["circles"], expected["circles"])

    normalized_scrolls = normalize_scroll_word(scrolls, expected["enchant_scroll_owned"])
    if normalized_scrolls != scrolls:
        write_u32(pm, ram_base, MEM["scrolls"], normalized_scrolls)


def get_item_write(item_name, route):
    if item_name == "3 Point Circle":
        return "circles", 0x0001

    if item_name == "Weak Alignment Rune":
        return "runes", route["weak_rune_bit"]

    if item_name == "Antorbok Rune":
        return "runes", 0x0100

    if item_name == "Magormor Rune":
        return "runes", 0x0200

    if item_name == "Weak Alignment Codex":
        return "codices", route["weak_codex_bit"]

    if item_name == "Antorbok Codex":
        return "codices", 0x0100

    if item_name == "Magormor Codex":
        return "codices", 0x0200

    if item_name == "Enchant Item Scroll":
        return "scrolls", 0x08000000

    raise KeyError(f"Unknown item name: {item_name}")


def grant_item(pm, ram_base, expected, route, item_name):
    category, bit = get_item_write(item_name, route)

    if category == "scrolls":
        expected["enchant_scroll_owned"] = True
        current = read_u32(pm, ram_base, MEM["scrolls"])
        new = current | bit
        write_u32(pm, ram_base, MEM["scrolls"], new)
        print(f"RECEIVED: {item_name} | scrolls {current:08X}->{new:08X}")
        return

    before = expected[category]
    expected[category] |= bit
    after = expected[category]

    write_core_state(pm, ram_base, expected)
    print(f"RECEIVED: {item_name} | {category} {before:04X}->{after:04X}")


class EternalDarknessContext(CommonContext):
    game = "Eternal Darkness"
    items_handling = 0b111
    want_slot_data = False

    def __init__(self, server_address=None, password=None):
        super().__init__(server_address, password)

        self.route = None
        self.pm = None
        self.ram_base = None

        self.expected = {
            "codices": 0x0000,
            "runes": 0x0000,
            "circles": 0x0000,
            "enchant_scroll_owned": False,
        }

        self.processed_item_count = 0
        self.seen_flags = 0
        self.goal_done = False

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            print("Password required:")
            self.password = await self.console_input()

        await self.get_username()
        await self.send_connect()


async def game_watcher(ctx: EternalDarknessContext):
    while not ctx.exit_event.is_set():
        await asyncio.sleep(0.05)

        if not ctx.slot:
            continue

        if ctx.pm is None:
            try:
                ctx.pm = pymem.Pymem(PROCESS_NAME)
                print("Connected to Dolphin.")
                ctx.ram_base = find_ram_base(ctx.pm)
            except Exception as e:
                # Dolphin may not be open yet. Keep trying quietly.
                await asyncio.sleep(1)
                continue

        try:
            police_memory(ctx.pm, ctx.ram_base, ctx.expected)

            while ctx.processed_item_count < len(ctx.items_received):
                network_item = ctx.items_received[ctx.processed_item_count]
                ctx.processed_item_count += 1

                item_name = ITEM_ID_TO_NAME.get(network_item.item)
                if item_name is None:
                    print(f"Received unknown item id {network_item.item}; ignoring.")
                    continue

                grant_item(ctx.pm, ctx.ram_base, ctx.expected, ctx.route, item_name)
                police_memory(ctx.pm, ctx.ram_base, ctx.expected)

            flags = read_u8(ctx.pm, ctx.ram_base, CHECK_FLAGS)
            new_flags = flags & ~ctx.seen_flags

            if new_flags:
                for mask, location_name in LOCATION_FLAGS.items():
                    if new_flags & mask:
                        location_id = LOCATION_NAME_TO_ID[location_name]
                        sent = await ctx.check_locations([location_id])

                        if sent:
                            print(f"CHECKED: {location_name}")
                        else:
                            print(f"CHECKED locally, already known by AP: {location_name}")

                ctx.seen_flags |= new_flags

            if not ctx.goal_done:
                goal_byte = read_u8(ctx.pm, ctx.ram_base, GOAL_FLAG)
                if goal_byte & 0x01:
                    print("GOAL COMPLETE: Bishop defeated")
                    ctx.goal_done = True
                    ctx.finished_game = True
                    await ctx.send_msgs([{
                        "cmd": "StatusUpdate",
                        "status": ClientStatus.CLIENT_GOAL,
                    }])

        except Exception as e:
            print(f"Memory watcher error: {e}")
            print("Lost Dolphin memory connection. Retrying...")
            ctx.pm = None
            ctx.ram_base = None
            await asyncio.sleep(1)


async def main():
    Utils.init_logging("EternalDarknessClient", exception_logger="Client")

    route_key = input("Route alignment (chatturgha / ulyaoth / xelotath): ").strip().lower()
    if route_key not in ALIGNMENT_ROUTES:
        print("Unknown route. Defaulting to chatturgha.")
        route_key = "chatturgha"

    route = ALIGNMENT_ROUTES[route_key]
    print("Route:", route["display"])
    print("Weak alignment:", route["weak_name"])

    server_address = input("AP server address [localhost:38281]: ").strip()
    if not server_address:
        server_address = "localhost:38281"

    slot_name = input("Slot name [Jason]: ").strip()
    if not slot_name:
        slot_name = "Jason"

    password = input("Password, if any [blank]: ").strip() or None

    ctx = EternalDarknessContext(server_address, password)
    ctx.route = route
    ctx.auth = slot_name

    print("Connecting to AP server...")
    ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
    ctx.watcher_task = asyncio.create_task(game_watcher(ctx), name="game watcher")

    try:
        await ctx.exit_event.wait()
    finally:
        await ctx.shutdown()


if __name__ == "__main__":
    asyncio.run(main())