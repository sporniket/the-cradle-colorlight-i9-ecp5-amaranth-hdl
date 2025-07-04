"""
---
(c) 2022~2025 David SPORN
---
This is part of Sporniket's "The Cradle for MuseLab's Colorlight i9" project.

Sporniket's "The Cradle for MuseLab's Colorlight i9" project is free software: you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your option)
any later version.

Sporniket's "The Cradle for MuseLab's Colorlight i9" project is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.

See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with Sporniket's "The Cradle for MuseLab's Colorlight i9" project.
If not, see <https://www.gnu.org/licenses/>. 
---
"""

### builtin deps
from typing import List  # , Dict, Tuple, Optional

### amaranth -- main deps
from amaranth.hdl import Elaboratable, Module
from amaranth.build import Platform

### project deps
from amaranth_stuff.modules import SlowBeat


class Blinky(Elaboratable):
    """A one second cycle, 50% duty blinking led driver

    Striped down version of the amaranth-board 'blinky'."""

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        led = platform.request("led", 0)
        m.submodules.beat = beat = SlowBeat(1)

        m.d.comb += led.o.eq(beat.beat_p)

        return m
