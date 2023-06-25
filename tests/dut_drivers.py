import random
from cocotb.triggers import RisingEdge, ReadOnly, NextTimeStep
from cocotb_bus.drivers import BusDriver


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
            for i in range(random.randint(0, 20)):
                await RisingEdge(self.clk)
            await ReadOnly()
            if self.bus.rdy.value != 1:
                await RisingEdge(self.bus.rdy)
            self.bus.en.value = 1
            await ReadOnly()
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
        for i in range(random.randint(0, 20)):
            await RisingEdge(self.clk)
        if self.bus.rdy != 1:
            await RisingEdge(self.bus.rdy)
        self.bus.en.value = 1
        self.bus.value.value = value
        await ReadOnly()
        await RisingEdge(self.clk)
        self.bus.en.value = 0
        await NextTimeStep()
