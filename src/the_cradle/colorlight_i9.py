import os
import subprocess

from amaranth.build import *
from amaranth.vendor.lattice_ecp5 import *
from amaranth_boards.resources import *  # from .resources import *


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
    ]

    # no connectors for now
    connectors = [
        # 'P[2..6] connectors, 2x15 pins ; pins are listed row by row ; meaning first 2x6 pmod is from pin 1 to 12, second 2x6 pmod is from pin 18
        Connector(
            "p",
            2,
            "- - - - K18  L2 T18 C18 R17 R18 M17 P17 " #first pmod
            "U18 T17 - - P18 U17 " 
            "- - - - N18 N17 L20 M18 K20 L18 G20 J20" # second pmod
        ),
    ]

    @property
    def required_tools(self):
        return super().required_tools + ["openFPGALoader"]

    def toolchain_prepare(self, fragment, name, **kwargs):
        overrides = dict(ecppack_opts="--compress")
        overrides.update(kwargs)
        return super().toolchain_prepare(fragment, name, **overrides)

    def toolchain_program(self, products, name):
        tool = os.environ.get("OPENFPGALOADER", "openFPGALoader")
        with products.extract("{}.bit".format(name)) as bitstream_filename:
            subprocess.check_call([tool, "-c", "cmsisdap", "-m", bitstream_filename])
