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
from typing import List  # , Dict, Tuple, Optional

### amaranth -- main deps
from amaranth import *
from amaranth.build import Platform

### project deps
from .colorlight_i9 import Colorlight_I9_V7_2_Platform
from .the_cradle import TheCradle


class Deployer:
    def __init__(self, endpoint: Platform, payload: Elaboratable):
        self.endpoint = endpoint
        self.payload = payload

    def deploy(self):
        print(
            f"========================[ START OF Deployment ]============================"
        )
        print(
            """
The file 'build/top.bit' will be created and deployed onto the colorlight.

The actual deployment into the colorlight assume that openFPGALoader is present, otherwise
you will have to do it manually with another tool (like ecpdap).

        """
        )
        self.endpoint.build(self.payload, do_program=True)
        print(f"-- -- -- -- -- -- -- -- [ END OF Deployment ] -- -- -- -- -- -- -- --")


if __name__ == "__main__":
    Deployer(Colorlight_I9_V7_2_Platform(), TheCradle()).deploy()
