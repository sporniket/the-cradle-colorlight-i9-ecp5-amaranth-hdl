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
import argparse

### amaranth -- main deps
from amaranth.hdl import Elaboratable
from amaranth.build import Platform

### project deps
from .colorlight_i9 import Colorlight_I9_V7_2_Platform
from .the_cradle import TheCradle
from .settings import SETTINGS__PAL, SETTINGS__QUART_HD, SETTINGS__VGA


SETTINGS_MAP = {
    "vga":SETTINGS__VGA,
    "pal":SETTINGS__PAL,
    "quart_hd":SETTINGS__QUART_HD
}


class Builder:
    def __init__(self, endpoint: Platform, payload: Elaboratable):
        self.endpoint = endpoint
        self.payload = payload

    def build(self):
        print(f"========================[ START OF Build ]============================")
        print(
            """
The file 'build/top.bit' will be the bitstream to upload to the ECP5. 
The file 'build/top.tim' will contains nextpnr logs

To deploy on the colorlight :
* with openFPGALoader : openFPGALoader -c cmsisdap -m build/top.bit
* with ecpdap : ecpdap program build/top.bit -f10M (? to be tested)

-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

        """
        )
        self.endpoint.build(self.payload, do_program=False)
        print(f"-- -- -- -- -- -- -- -- [ END OF Build ] -- -- -- -- -- -- -- --")


def _createArgParser():
    parser = argparse.ArgumentParser(prog="The Cradle builder",description="Build, and optionnally program the cradle")
    parser.add_argument("preset", nargs="?",default="vga", choices=["vga","pal","quart_hd"])
    return parser

if __name__ == "__main__":
    args = _createArgParser().parse_args()
    Builder(Colorlight_I9_V7_2_Platform(), TheCradle(settings=SETTINGS_MAP[args.preset])).build()
