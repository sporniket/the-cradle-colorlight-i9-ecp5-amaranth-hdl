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
from typing import List, Dict  # , Tuple, Optional

### amaranth -- main deps
from amaranth import *
from amaranth.build import Platform


class Ehxplll(Elaboratable):
    """Module that instanciate a EHXPLLL using a map of Instance parameters."""

    ALLOWED_FEEDBACK = (
        "CLKOP",
        "CLKOS",
        "CLKOS2",
        "CLKOS3",
        "INT_OP",
        "INT_OS",
        "INT_OS2",
        "INT_OS3",
        "USERCLOCK",
    )

    def __init__(
        self,
        params: Dict,
        *,
        domain: str = "sync",
        feedback: str = "CLKOP",
        userFeedback=None,
    ):
        if feedback not in Ehxplll.ALLOWED_FEEDBACK:
            raise (
                ValueError(
                    f"feedback '{feedback}' MUST be a value among {Ehxplll.ALLOWED_FEEDBACK}"
                )
            )
        # list of I/O signals
        self.clkin = clkin = ClockSignal(domain)
        self.clkout0 = clkout0 = Signal()
        self.clkout1 = clkout1 = Signal()
        self.clkout2 = clkout2 = Signal()
        self.clkout3 = clkout3 = Signal()
        self.locked = locked = Signal()
        # the map of parameters
        self.params = params | {
            "i_CLKI": clkin,
            "i_CLKFB": clkout0,
            "o_CLKOP": clkout0,
            "o_CLKOS": clkout1,
            "o_CLKOS2": clkout2,
            "o_CLKOS3": clkout3,
            "o_LOCK": locked,
        }

        # manage the specification of feedback
        self.params["p_FEEDBK_PATH"] = feedback
        if feedback.startswith("INT_"):
            self.intfb = intfb = Signal()
            self.params["i_CLKFB"] = intfb
            self.params["o_CLKINTFB"] = intfb
        elif feedback == "USERCLOCK":
            if userFeedback is None:
                raise ValueError(
                    f"'userFeedback' MUST be provided (got {userFeedback}) when feedback is USERCLOCK(got {feedback})"
                )
            self.userFeedback = userFeedback
            self.params["i_CLKFB"] = userFeedback
        else:
            self.params["i_CLKFB"] = self.params[f"o_{feedback}"]

    def ports(self) -> List[Signal]:
        return [
            self.clkin,
            self.clkout0,
            self.clkout1,
            self.clkout2,
            self.clkout3,
            self.locked,
        ]

    def outputClockPorts(self) -> List[Signal]:
        return [
            self.clkout0,
            self.clkout1,
            self.clkout2,
            self.clkout3,
        ]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        pll = Instance("EHXPLLL", **self.params)
        m.submodules.pll = pll

        return m
