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
import os
import subprocess

### amaranth -- main deps
from amaranth.build import *
from amaranth.vendor import *
from amaranth_boards.resources import *  # from .resources import *


# HDMI mapping,
hdmi_channels = [
    {"p": "G19", "n": "H20"},  # Channel 0
    {"p": "E20", "n": "F19"},  # Channel 1
    {"p": "C20", "n": "D19"},  # Channel 2
    {"p": "J19", "n": "K19"},  # Channel C
]


def HDMIResource(
    *args, channels, conn=None, attrs=None
):  # the colorlight expansion board only connect the output channels.
    io = []
    for i in range(0, 4):
        io += [
            Subsignal(
                f"c{i}_p",
                Pins(channels[i]["p"], dir="o", conn=conn, assert_width=1),
            ),
            Subsignal(
                f"c{i}_n",
                Pins(channels[i]["n"], dir="o", conn=conn, assert_width=1),
            ),
        ]
    if attrs is not None:
        io.append(attrs)
    return Resource.family(*args, default_name="hdmi", ios=io)


class Colorlight_I9_V7_2_Platform(LatticeECP5Platform):
    """See board info at https://github.com/wuxx/Colorlight-FPGA-Projects/blob/master/colorlight_i9_v7.2.md"""

    device = "LFE5U-45F"
    package = "BG381"
    speed = "6"
    default_clk = "clk25"

    resources = [
        Resource(
            "clk25", 0, Pins("P3", dir="i"), Clock(25e6), Attrs(IO_TYPE="LVCMOS33")
        ),
        *LEDResources(
            pins="L2", attrs=Attrs(IO_TYPE="LVCMOS33", DRIVE="4")
        ),  # the sample use LVCMOS25, but this pins is also accessible out of the board
        HDMIResource(
            0, channels=hdmi_channels, attrs=Attrs(IO_TYPE="LVCMOS33", DRIVE="4")
        ),  # See also https://github.com/lawrie/ulx3s_examples/blob/master/video/checkers/ulx3s_v20.lpf#L316-L323
    ]

    # no connectors for now
    connectors = [
        # 'P[2..6] connectors, 2x15 pins ; pins are listed row by row ; meaning first 2x6 pmod is from pin 1 to 12, second 2x6 pmod is from pin 18
        Connector(
            "p",
            2,
            "- - - - K18  L2 T18 C18 R17 R18 M17 P17 "  # first pmod
            "U18 T17 - - P18 U17 "
            "- - - - N18 N17 L20 M18 K20 L18 G20 J20",  # second pmod
        ),
    ]

    def toolchain_prepare(self, fragment, name, **kwargs):
        overrides = dict(ecppack_opts="--compress")
        overrides.update(kwargs)
        return super().toolchain_prepare(fragment, name, **overrides)

    def toolchain_program(self, products, name):
        tool = os.environ.get("OPENFPGALOADER", "openFPGALoader")
        with products.extract("{}.bit".format(name)) as bitstream_filename:
            subprocess.check_call([tool, "-c", "cmsisdap", "-m", bitstream_filename])
