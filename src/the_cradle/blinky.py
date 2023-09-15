### main deps
from amaranth import *
from amaranth.build import Platform
from typing import List, Dict, Tuple, Optional

### local deps
from slowbeat import SlowBeat

__all__ = ["Blinky"]

class Blinky(Elaboratable):
    """A one second cycle, 50% duty blinking led driver
    
    Striped down version of the amaranth-board 'blinky'."""

    def elaborate(self, platform):
        m = Module()
        
        led = platform.request("led",0)
        m.submodules.beat = beat = SlowBeat(1)

        m.d.comb += led.eq(beat.beat_p)
        
        return m
