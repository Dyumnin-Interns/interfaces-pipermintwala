import cocotb
from cocotb.triggers import RisingEdge, Timer, NextTimeStep, ReadOnly
from cocotb_bus.drivers import BusDriver
from cocotb.result import TestError
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db
import random

# specifying the expected value


def sb_fn(actual_value):
    global expected_value
    assert actual_value == expected_value, "Scoreboard Matching Failed"


# @CoverPoint("top.din", xf=lambda x, y: x, bins=[0, 255])  # noqa F405
# @CoverPoint("top.len", xf=lambda x, y: y, bins=[0, 255])  # noqa F405
# @CoverCross("top.cross.xy", items=["top.din", "top.len"])
# def ab_cover(din):
#     pass


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

    # inDrv = DUTDriver(dut, dut.CLK)
    lenDrv = InputDriver(dut, "len", dut.CLK)
    inDrv = InputDriver(dut, "din", dut.CLK)
    OutputDriver(dut, "dout", dut.CLK, sb_fn)

    lenValue = 23

    await lenDrv._driver_send(lenValue)

    global expected_value
    expected_value = (lenValue * (lenValue + 1)) / 2
    print(expected_value)
    for i in range(lenValue):
        await inDrv._driver_send(i + 1)
        await ReadOnly()


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
            await ReadOnly()
            if self.bus.rdy.value != 1:
                await RisingEdge(self.bus.rdy)
            self.bus.en.value = 1
            await ReadOnly()
            # self.bus.data = value
            self.callback(self.bus.value.value.integer)

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
