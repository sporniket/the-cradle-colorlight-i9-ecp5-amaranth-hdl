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
# Video mode : qHD -- 960*540 pixels at 50Hz

SETTINGS__QUART_HD = {
    ## pll parameters to get the frequencies [290, 29, 116, 58]MHz
    ## ecppll -i 25 -o 290 --clkout1 29 --clkout2 116 --clkout3 58 -f foo.txt
    "mainPllParameters": {
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
        "p_CLKOS_DIV": 20,
        "p_CLKOS_CPHASE": 1,
        "p_CLKOS_FPHASE": 0,
        "p_CLKOS2_ENABLE": "ENABLED",
        "p_CLKOS2_DIV": 5,
        "p_CLKOS2_CPHASE": 1,
        "p_CLKOS2_FPHASE": 0,
        "p_CLKOS3_ENABLE": "ENABLED",
        "p_CLKOS3_DIV": 10,
        "p_CLKOS3_CPHASE": 1,
        "p_CLKOS3_FPHASE": 0,
        "p_FEEDBK_PATH": "CLKOP",
        "p_CLKFB_DIV": 58,
        "i_RST": 0,
        "i_STDBY": 0,
        "i_PHASESEL0": 0,
        "i_PHASESEL1": 0,
        "i_PHASEDIR": 1,
        "i_PHASESTEP": 1,
        "i_PHASELOADREG": 1,
        "i_PLLWAKESYNC": 0,
        "i_ENCLKOP": 0,
    },
    "mainPllClockMap": {"dviLink": 0, "theCradle": 2, "pixel": 1, "cpuBase": 3},
    ## Video timings for 960x540@50Hz -- CVT-RBv2
    ## sequence of pixels in a single scan line [sync, back porch, active, front porch]
    "pixelSequence": [32, 40, 960, 8],  # total = 1040
    ## sequence of scanlines in a video screen [sync, back porch, active, front porch]
    "scanlineSequence": [8, 6, 540, 1],  # total = 555
}
