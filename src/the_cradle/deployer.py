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

from colorlight_i9 import Colorlight_I9_V7_2_Platform
from blinky import *
from blinky_gpio import *
from chaser_gpio import *
from amaranth import Elaboratable
from amaranth.build import Platform
from typing import List

class Deployer():
    def __init__(self, endpoint:Platform, payload:Elaboratable):
        self.endpoint = endpoint
        self.payload = payload

    def run(self):
        print(f"========================[ START OF Deployment ]============================")
        self.endpoint.build(self.payload, do_program = True)
        print(f"-- -- -- -- -- -- -- -- [ END OF Deployment ] -- -- -- -- -- -- -- --")
