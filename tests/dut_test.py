from typing import Any, Optional
import cocotb
from cocotb.triggers import RisingEdge, Timer, NextTimeStep, ReadOnly
from cocotb_bus.drivers import BusDriver
from cocotb.result import TestError


def sb_fn(actual_value):
    assert actual_value == 10, "Scoreboard Matching Failed"


@cocotb.test()
async def test_dut(dut):
    # Initialize the DUT inputs
    dut.din_en.value = 0
    dut.len_en.value = 0
    dut.dout_en.value = 0
    dut.cfg_en.value = 0
    dut.din_value.value = 0
    dut.len_value.value = 0
    dut.cfg_address.value = 0
    dut.cfg_op.value = 0
    dut.cfg_data_in.value = 0

    # Reset the DUT
    dut.RST_N.value = 1
    await RisingEdge(dut.CLK)
    dut.RST_N.value = 0
    await RisingEdge(dut.CLK)
    dut.RST_N.value = 1

    # Testing from the len port
    dut.len_en.value = 1
    dut.len_value.value = 4  # Accumulate 4 bytes
    # inDrv = DUTDriver(dut, dut.CLK)

    inDrv2 = InputDriver(dut, "din", dut.CLK)
    OutputDriver(dut, "dout", dut.CLK, sb_fn)

    for i in range(4):
        await inDrv2._driver_send(i + 1)


class OutputDriver(BusDriver):
    _signals = ["rdy", "en", "value"]

    def __init__(self, dut, name, clk, sb_callback):
        BusDriver.__init__(self, dut, name, clk)
        self.bus.en.value = 0
        self.clk = clk
        self.callback = sb_callback
        self.append(0)

    async def _driver_send(self, value, sync=True):
        while True:
            if self.bus.rdy.value != 1:
                await RisingEdge(self.bus.rdy)
            self.bus.en.value = 1
            await ReadOnly()
            # self.bus.data = value
            self.callback(self.bus.value.value)

            await RisingEdge(self.clk)
            await NextTimeStep()


class InputDriver(BusDriver):
    _signals = ["rdy", "en", "value"]

    def __init__(self, dut, name, clk):
        BusDriver.__init__(self, dut, name, clk)
        self.bus.en.value = 0
        self.clk = clk

    async def _driver_send(self, value, sync=True):
        await RisingEdge(self.clk)
        if self.bus.rdy != 1:
            await RisingEdge(self.bus.rdy)
        self.bus.en.value = 1
        self.bus.value.value = value
        await ReadOnly()
        await RisingEdge(self.clk)
        self.bus.en.value = 0
        await NextTimeStep()
