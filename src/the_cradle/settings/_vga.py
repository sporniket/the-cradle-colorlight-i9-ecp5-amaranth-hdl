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
# Video mode : VGA -- 640*480 pixels at 59Hz94

SETTINGS__VGA = {
    ## pll parameters to get the frequencies [125, 250, 25, 83]MHz
    "mainPllParameters": {
        "p_PLLRST_ENA": "DISABLED",
        "p_INTFB_WAKE": "DISABLED",
        "p_STDBY_ENABLE": "DISABLED",
        "p_DPHASE_SOURCE": "DISABLED",
        "p_OUTDIVIDER_MUXA": "DIVA",
        "p_OUTDIVIDER_MUXB": "DIVB",
        "p_OUTDIVIDER_MUXC": "DIVC",
        "p_OUTDIVIDER_MUXD": "DIVD",
        "p_CLKI_DIV": 1,
        "p_CLKOP_ENABLE": "ENABLED",
        "p_CLKOP_DIV": 4,
        "p_CLKOP_CPHASE": 3,
        "p_CLKOP_FPHASE": 0,
        "p_CLKOS_ENABLE": "ENABLED",
        "p_CLKOS_DIV": 2,
        "p_CLKOS_CPHASE": 1,
        "p_CLKOS_FPHASE": 0,
        "p_CLKOS2_ENABLE": "ENABLED",
        "p_CLKOS2_DIV": 20,
        "p_CLKOS2_CPHASE": 0,
        # "p_CLKOS2_FPHASE": 0,
        "p_CLKOS3_ENABLE": "ENABLED",
        "p_CLKOS3_DIV": 0,
        "p_CLKOS3_CPHASE": 5,
        # "p_CLKOS3_FPHASE": 0,
        "p_FEEDBK_PATH": "CLKOP",
        "p_CLKFB_DIV": 5,
        ###
        "i_RST": 0,
        "i_STDBY": 0,
        "i_PHASESEL0": 0,
        "i_PHASESEL1": 0,
        "i_PHASEDIR": 0,
        "i_PHASESTEP": 0,
        # "i_PHASELOADREG": 1,
        "i_PLLWAKESYNC": 0,
        "i_ENCLKOP": 0,
        "i_ENCLKOS": 0,
        "i_ENCLKOS2": 0,
        "i_ENCLKOS3": 0,
    },
    "mainPllClockMap": {"dviLink": 1, "theCradle": 0, "pixel": 2, "cpuBase": 3},
    ## Video timings for 640x480@59.94
    ## sequence of pixels in a single scan line [sync, back porch, active, front porch]
    "pixelSequence": [96, 48, 640, 16],  # total = 800
    ## sequence of scanlines in a video screen [sync, back porch, active, front porch]
    "scanlineSequence": [2, 33, 480, 10],  # total = 525
}
