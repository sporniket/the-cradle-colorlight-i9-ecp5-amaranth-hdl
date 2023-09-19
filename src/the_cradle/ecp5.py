"""
---
(c) 2022,2023 David SPORN
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
from typing import List, Dict  # , Tuple, Optional

### amaranth -- main deps
from amaranth import *
from amaranth.build import Platform


class PllInstance(Elaboratable):
    """Module that instanciate a EHXPLLL using a map of Instance parameters.
    
    Does only support clkout0 as feedback."""

    def __init__(self, params: Dict):
        # list of I/O signals
        self.clkin = clkin = Signal()
        self.clkout0 = clkout0 = Signal()
        self.clkout1 = clkout1 = Signal()
        self.clkout2 = clkout2 = Signal()
        self.clkout3 = clkout3 = Signal()
        self.locked = locked = Signal()
        # the map of parameters
        self.params = params + {
            "i_CLKI": clkin,
            "i_CLKFB": clkout0,
            "o_CLKOP": clkout0,
            "o_CLKO": clkout,
            "o_CLKO": clkout,
            "o_CLKO": clkout,
            "o_LOCK": locked,
        }

    def ports(self) -> List[Signal]:
        return [
            self.clkin,
            self.clkout0,
            self.clkout1,
            self.clkout2,
            self.clkout3,
            self.locked,
        ]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        pll = Instance("EHXPLLL",**self.params)
        m.submodules.pll += pll

        return m
