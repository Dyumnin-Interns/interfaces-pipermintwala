from typing import Any, Optional
import cocotb
from cocotb.triggers import RisingEdge, Timer, NextTimeStep, ReadOnly
from cocotb_bus.drivers import BusDriver
import random


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
    inDrv = DUTDriver(dut, dut.CLK)
    # inDrv2 = InputDriver(dut, "data_in", dut.CLK)

    await Timer(10, "ns")

    for i in range(4):
        await inDrv.send_data(i + 1)

    dut.dout_rdy == 1, "Data output not ready after accumulation"
    assert dut.dout_value == 10, "Incorrect accumulated value"


# class InputDriver(BusDriver):
#     _signals = ["din_rdy", "din_en", "din_value"]

#     def __init__(self, dut, name, clk):
#         BusDriver.__init__(self, dut, name, clk)
#         self.bus.din_en = 0
#         self.clk = clk

#     async def _driver_send(self, value, sync=True):
#         await RisingEdge(self.clk)
#         if self.bus.din_rdy != 1:
#             await RisingEdge(self.bus.din_rdy)
#         self.bus.din_en.value = 1
#         self.bus.din_value = value
#         await ReadOnly()
#         await RisingEdge(self.clk)
#         self.bus.din_en.value = 0
#         await NextTimeStep()


class DUTDriver:
    def __init__(self, dut, clock):
        self.dut = dut
        self.clock = clock

    async def send_data(self, value):
        while not int(self.dut.din_rdy):
            await RisingEdge(self.clock)
            await ReadOnly()
        self.dut.din_en.value = 1
        self.dut.din_value.value = value
        await ReadOnly()
        await RisingEdge(self.clock)
        self.dut.din_en.value = 0
        await NextTimeStep()
