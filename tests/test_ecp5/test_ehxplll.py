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

### amaranth -- test deps
from amaranth.asserts import *  # AnyConst, AnySeq, Assert, Assume, Cover, Past, Stable, Rose, Fell, Initial

### other deps
from the_cradle import TheCradle
from ecp5 import Ehxplll

baseParameters = {
    "p_PLLRST_ENA": "DISABLED",
    "p_INTFB_WAKE": "DISABLED",
    "p_STDBY_ENABLE": "DISABLED",
    "p_DPHASE_SOURCE": "DISABLED",
    "p_OUTDIVIDER_MUXA": "DIVA",
    "p_OUTDIVIDER_MUXB": "DIVB",
    "p_OUTDIVIDER_MUXC": "DIVC",
    "p_OUTDIVIDER_MUXD": "DIVD",
    "p_CLKI_DIV": 5,
    "p_CLKOP_ENABLE": "ENABLED",
    "p_CLKOP_DIV": 2,
    "p_CLKOP_CPHASE": 1,
    "p_CLKOP_FPHASE": 0,
    "p_CLKOS_ENABLE": "ENABLED",
    "p_CLKOS_DIV": 5,
    "p_CLKOS_CPHASE": 1,
    "p_CLKOS_FPHASE": 0,
    "p_CLKOS2_ENABLE": "ENABLED",
    "p_CLKOS2_DIV": 20,
    "p_CLKOS2_CPHASE": 1,
    "p_CLKOS2_FPHASE": 0,
    "p_CLKOS3_ENABLE": "ENABLED",
    "p_CLKOS3_DIV": 17,
    "p_CLKOS3_CPHASE": 1,
    "p_CLKOS3_FPHASE": 0,
    "p_FEEDBK_PATH": "CLKOP",
    "p_CLKFB_DIV": 54,
    "i_RST": 0,
    "i_STDBY": 0,
    "i_PHASESEL0": 0,
    "i_PHASESEL1": 0,
    "i_PHASEDIR": 1,
    "i_PHASESTEP": 1,
    "i_PHASELOADREG": 1,
    "i_PLLWAKESYNC": 0,
    "i_ENCLKOP": 0,
}


def test_Ehxplll_instance_should_have_expected_properties():
    # prepare

    # execute
    pll = Ehxplll(baseParameters)
    pll._MustUse__silence = True  # this is a pure python test

    # verify
    ## managed signals
    assert isinstance(pll.clkin, ClockSignal) and pll.clkin.domain == "sync"
    assert isinstance(pll.clkout0, Signal) and pll.clkout0.width == 1
    assert isinstance(pll.clkout1, Signal) and pll.clkout1.width == 1
    assert isinstance(pll.clkout2, Signal) and pll.clkout2.width == 1
    assert isinstance(pll.clkout3, Signal) and pll.clkout3.width == 1
    assert isinstance(pll.locked, Signal) and pll.locked.width == 1

    ## instanciation parameters
    expectedParams = baseParameters | {
        "i_CLKI": pll.clkin,
        "i_CLKFB": pll.clkout0,
        "o_CLKOP": pll.clkout0,
        "o_CLKOS": pll.clkout1,
        "o_CLKOS2": pll.clkout2,
        "o_CLKOS3": pll.clkout3,
        "o_LOCK": pll.locked,
    }
    assert len(pll.params) == len(expectedParams)
    for k, v in expectedParams.items():
        assert k in pll.params
        assert pll.params[k] is v

    ## referenced ports
    expectedPorts = [
        pll.clkin,
        pll.clkout0,
        pll.clkout1,
        pll.clkout2,
        pll.clkout3,
        pll.locked,
    ]
    actualPorts = pll.ports()
    assert len(expectedPorts) == len(actualPorts)
    for i in range(0, len(expectedPorts)):
        assert actualPorts[i] is expectedPorts[i]

    ## referenced output ports
    expectedOutputClockPorts = [
        pll.clkout0,
        pll.clkout1,
        pll.clkout2,
        pll.clkout3,
    ]
    actualOutputClockPorts = pll.outputClockPorts()
    assert len(expectedOutputClockPorts) == len(actualOutputClockPorts)
    for i in range(0, len(expectedOutputClockPorts)):
        assert actualOutputClockPorts[i] is expectedOutputClockPorts[i]


def test_Ehxplll_instance_should_use_the_explicitely_designated_clock_domain():
    # prepare

    # execute
    pll = Ehxplll(baseParameters, domain="foo")
    pll._MustUse__silence = True  # this is a pure python test

    # verify
    assert pll.clkin.domain == "foo"


def test_Ehxplll_instance_should_handle_feedback():
    # prepare

    ## when using output clock
    for fbParams, fbProp in [
        ("CLKOP", "clkout0"),
        ("CLKOS", "clkout1"),
        ("CLKOS2", "clkout2"),
        ("CLKOS3", "clkout3"),
    ]:
        # execute
        pll = Ehxplll(baseParameters, feedback=fbParams)
        pll._MustUse__silence = True  # this is a pure python test

        # verify
        assert pll.params["p_FEEDBK_PATH"] == fbParams
        assert pll.params["i_CLKFB"] is getattr(pll, fbProp)
        assert not hasattr(pll, "intfb")

    ## when using internal path
    for fbParams, fbProp in [
        ("INT_OP", "intfb"),
        ("INT_OS", "intfb"),
        ("INT_OS2", "intfb"),
        ("INT_OS3", "intfb"),
    ]:
        # execute
        pll = Ehxplll(baseParameters, feedback=fbParams)
        pll._MustUse__silence = True  # this is a pure python test

        # verify
        assert pll.params["p_FEEDBK_PATH"] == fbParams
        assert pll.params["i_CLKFB"] is getattr(pll, fbProp)
        assert pll.params["o_CLKINTFB"] is getattr(pll, fbProp)

    ## when using user clock
    for fbParams, fbProp in [
        ("USERCLOCK", "userFeedback"),
    ]:
        # execute
        feedback = Signal()
        feedback._MustUse__silence = True  # this is a pure python test
        pll = Ehxplll(baseParameters, feedback=fbParams, userFeedback=feedback)
        pll._MustUse__silence = True  # this is a pure python test

        # verify
        assert pll.params["p_FEEDBK_PATH"] == fbParams
        assert pll.params["i_CLKFB"] is getattr(pll, fbProp)
