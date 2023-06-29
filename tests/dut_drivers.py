import random
from cocotb.triggers import RisingEdge, ReadOnly, NextTimeStep, FallingEdge, Timer
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


class ConfigDriver(BusDriver):
    _signals = ["rdy", "en", "address", "op", "data_out", "data_in"]

    def __init__(self, dut, name, clk):
        BusDriver.__init__(self, dut, name, clk)
        self.clk = clk

    async def _write_reg(self, address, data):
        await RisingEdge(self.clk)
        self.bus.en.value = 1
        self.bus.address.value = address
        self.bus.op.value = 1  # Write operation
        self.bus.data_in.value = data
        await ReadOnly()
        await RisingEdge(self.clk)
        self.bus.op.value = 0
        await ReadOnly()
        await RisingEdge(self.clk)
        self.bus.en.value = 0
        await NextTimeStep()

    async def _driver_send(
        self,
        config,
        sync=True,
    ):
        for i in range(random.randint(0, 20)):
            await RisingEdge(self.clk)
        if self.bus.rdy != 1:
            await RisingEdge(self.bus.rdy)
        overwrite = config.get("sw_overwrite", 0)
        await self._write_reg(4, overwrite)
        pause = config.get("pause", 0)
        if pause:
            pause = 2
            await self._write_reg(4, pause)
        lenValue = config.get("lenValue", 0)
        await self._write_reg(8, lenValue)
