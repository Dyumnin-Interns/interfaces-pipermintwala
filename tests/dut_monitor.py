from cocotb_bus.monitors import BusMonitor
from cocotb.triggers import FallingEdge, ReadOnly


class IO_Monitor(BusMonitor):
    _signals = ["rdy", "en", "value"]

    async def _monitor_recv(self):
        fallingedge = FallingEdge(self.clock)
        rdonly = ReadOnly()
        phases = {0: "Idle", 1: "Rdy", 3: "Txn"}
        prev = "Idle"
        while True:
            await fallingedge
            await rdonly
            txn = (self.bus.en.value << 1) | self.bus.rdy.value
            self._recv({"previous": prev, "current": phases[txn]})
            prev = phases[txn]
