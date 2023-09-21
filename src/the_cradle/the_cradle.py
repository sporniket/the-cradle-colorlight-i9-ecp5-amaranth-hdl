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
from amaranth.build import Platform, Resource, Pins, Attrs

### project deps
from .blinky import Blinky
from .ecp5 import PllInstance
from amaranth_stuff.modules import (
    Sequencer,
    SlowBeat,
    ShiftRegisterSendLsbFirst,
    DviTmdsEncoder,
    RippleCounter,
    SlowRippleCounter,
)

from .vid_settings_640x480_59Hz94 import (
    # from .vid_settings_720x576_50Hz import (
    mainPllParameters,
    mainPllClockMap,
    pixelSequence,
    scanlineSequence,
)


class TheCradle(Elaboratable):
    def __init__(self):
        pass

    def setupGpios(self, platform: Platform):
        """Demonstrate how to setup some pins of the platform

        Args:
            platform (Platform): the platform to update.
        """

        for gpioIndex, targetPinIndex in enumerate(
            (5, 7, 9, 11, 13, 17, 23, 25, 27, 29)
        ):
            # retrieve the targeted pin
            pin_name = platform.connectors["p", 2].mapping[str(targetPinIndex)]
            print(f"pin name = {pin_name}")

            # setup pin as resource
            res = Resource("my_gpio", gpioIndex, Pins(pin_name, dir="o"))
            res.attrs.update(Attrs(IO_TYPE="LVCMOS33", DRIVE="4"))

            # append resource into platform
            platform.add_resources([res])

    def createClockDomain(
        self, m: Module, name: str, sourceClock, sourceReset=None, *, isLocal=True
    ) -> ClockDomain:
        result = ClockDomain(name, local=isLocal)
        m.d.comb += result.clk.eq(sourceClock)
        if sourceReset is not None:
            m.d.comb += result.rst.eq(sourceReset)
        m.domains += result
        return result

    def elaborate(self, platform: Platform) -> Module:
        self.setupGpios(platform)
        m = Module()

        ## Setup blinky : shows that the fpga is running
        m.submodules.blinky = blinky = Blinky()

        ### Main pll and clocks
        m.submodules.mainPll = mainPll = PllInstance(mainPllParameters)

        for dmn in mainPllClockMap:
            print(
                f"generating clock domain '{dmn}' using 'clkout{mainPllClockMap[dmn]}'..."
            )
            self.createClockDomain(
                m, dmn, mainPll.ports()[mainPllClockMap[dmn] + 1], isLocal=False
            )

        ### Setup probe blinkies
        # m.submodules.blinky0 = Blinky("my_gpio", 0)  # Witness

        ## Ripple counters setup
        # reference : default clock
        m.submodules.rc0 = rc0 = RippleCounter(8)
        m.submodules.rc1 = rc1 = SlowRippleCounter(8)
        m.submodules.rc2 = rc2 = SlowRippleCounter(8)
        m.submodules.rc3 = rc3 = SlowRippleCounter(8)
        m.d.comb += [
            rc1.beat.eq(rc0.value[7]),
            rc2.beat.eq(rc1.value[7]),
            rc3.beat.eq(rc2.value[7]),
        ]

        toProbe = "dviLink"
        # toProbe = "theCradle"
        # toProbe = "pixel"
        # toProbe = "cpuBase"
        m.submodules.rc4 = rc4 = DomainRenamer(toProbe)(RippleCounter(8))
        m.submodules.rc5 = rc5 = DomainRenamer(toProbe)(SlowRippleCounter(8))
        m.submodules.rc6 = rc6 = DomainRenamer(toProbe)(SlowRippleCounter(8))
        m.submodules.rc7 = rc7 = DomainRenamer(toProbe)(SlowRippleCounter(8))
        m.d.comb += [
            rc5.beat.eq(rc4.value[7]),
            rc6.beat.eq(rc5.value[7]),
            rc7.beat.eq(rc6.value[7]),
        ]

        # link to leds
        gpio = platform.request("my_gpio", 0)
        m.d.comb += gpio.eq(rc0.value[7])
        gpio = platform.request("my_gpio", 2)
        m.d.comb += gpio.eq(rc1.value[7])
        gpio = platform.request("my_gpio", 4)
        m.d.comb += gpio.eq(rc2.value[7])
        gpio = platform.request("my_gpio", 6)
        m.d.comb += gpio.eq(rc3.value[7])

        gpio = platform.request("my_gpio", 1)
        m.d.comb += gpio.eq(rc4.value[7])
        gpio = platform.request("my_gpio", 3)
        m.d.comb += gpio.eq(rc5.value[7])
        gpio = platform.request("my_gpio", 5)
        m.d.comb += gpio.eq(rc6.value[7])
        gpio = platform.request("my_gpio", 7)
        m.d.comb += gpio.eq(rc7.value[7])

        # direct output, to scope the signals
        gpio = platform.request("my_gpio", 8)
        m.d.comb += gpio.eq(mainPll.clkout2)

        gpio = platform.request("my_gpio", 9)
        m.d.comb += gpio.eq(mainPll.clkout3)

        # m.submodules.blinky0 = DomainRenamer("dviLink")(Blinky("my_gpio", 0))
        # m.submodules.blinky1 = DomainRenamer("theCradle")(Blinky("my_gpio", 1))
        # m.submodules.blinky2 = DomainRenamer("pixel")(Blinky("my_gpio", 2))
        # m.submodules.blinky3 = DomainRenamer("cpuBase")(Blinky("my_gpio", 3))

        ### Pixel sequencer -> hsync clock
        m.submodules.pixelSequencer = pixelSequencer = DomainRenamer("pixel")(
            Sequencer(pixelSequence)
        )
        hsync = Signal()
        m.d.comb += hsync.eq(pixelSequencer.steps[0])
        henable = pixelSequencer.steps[2]

        self.createClockDomain(m, "hsync", hsync)

        ### Scanline sequencer -> vsync clock + video display enable
        m.submodules.scanlineSequencer = scanlineSequencer = DomainRenamer("hsync")(
            Sequencer(scanlineSequence)
        )
        vsync = Signal()
        m.d.comb += vsync.eq(scanlineSequencer.steps[0])
        venable = scanlineSequencer.steps[2]

        vde = Signal()
        m.d.comb += vde.eq(venable & henable)

        hsyncActive = Signal()  # Hsync pulse only for lines with displayable area
        m.d.comb += hsyncActive.eq(venable & hsync)

        self.createClockDomain(m, "vsync", vsync)

        self.createClockDomain(m, "hsyncActive", hsyncActive, vsync)

        ### The pixel source
        videoSource = videoSolidBlink = Signal(
            24
        )  # v[0:8] = blue, v[8:16] = green, v[16:24] = blue
        red, green, blue = Signal(8), Signal(8), Signal(8)
        m.d.comb += [
            blue.eq(videoSource[0:8]),
            green.eq(videoSource[8:16]),
            red.eq(videoSource[16:24]),
        ]

        m.submodules.beat = beat = SlowBeat(1)
        m.d.comb += videoSolidBlink.eq(Mux(beat.beat_p, 0x0055AA, 0xAA9955))

        ### The dvi link
        ctl0, ctl1, ctl2, ctl3 = Signal(), Signal(), Signal(), Signal()
        m.d.comb += [
            ctl0.eq(0),
            ctl1.eq(0),
            ctl2.eq(0),
            ctl3.eq(0),
        ]
        m.submodules.blueTmds, m.submodules.greenTmds, m.submodules.redTmds = (
            blueTmds,
            greenTmds,
            redTmds,
        ) = (
            DomainRenamer("pixel")(DviTmdsEncoder(blue, vde, hsync, vsync)),
            DomainRenamer("pixel")(DviTmdsEncoder(green, vde, ctl0, ctl1)),
            DomainRenamer("pixel")(DviTmdsEncoder(red, vde, ctl2, ctl3)),
        )

        channelClockSource = Signal(10)
        # m.d.comb += channelClockSource.eq(0b1111100000)
        m.d.comb += channelClockSource.eq(0b0000011111)
        (
            m.submodules.channel0,
            m.submodules.channel1,
            m.submodules.channel2,
            m.submodules.channelClock,
        ) = (channel0, channel1, channel2, channelClock) = (
            DomainRenamer("dviLink")(ShiftRegisterSendLsbFirst(blueTmds.ports()[-1])),
            DomainRenamer("dviLink")(ShiftRegisterSendLsbFirst(greenTmds.ports()[-1])),
            DomainRenamer("dviLink")(ShiftRegisterSendLsbFirst(redTmds.ports()[-1])),
            DomainRenamer("dviLink")(ShiftRegisterSendLsbFirst(channelClockSource)),
        )

        hdmiMain = platform.request("hdmi", 0)
        m.d.comb += [
            hdmiMain.c0_p.eq(channel0.dataOut),
            hdmiMain.c0_n.eq(channel0.dataOutInverted),
            hdmiMain.c1_p.eq(channel1.dataOut),
            hdmiMain.c1_n.eq(channel1.dataOutInverted),
            hdmiMain.c2_p.eq(channel2.dataOut),
            hdmiMain.c2_n.eq(channel2.dataOutInverted),
            hdmiMain.c3_p.eq(channelClock.dataOut),
            hdmiMain.c3_n.eq(channelClock.dataOutInverted),
        ]

        ### What you should get at this point
        #
        # * A blinking onboard led, 1Hz
        # * Through a display plugged into the HDMI port, a pattern (either solid blue-ish, or a checkered pattern, or colored gradient tiles)
        #
        ###

        return m
