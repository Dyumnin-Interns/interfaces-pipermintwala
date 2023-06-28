import cocotb
from cocotb.result import TestFailure
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db
from cocotb.triggers import Timer
import os
from dut_init import dut_init, dut_rst
from dut_drivers import InputDriver, OutputDriver, ConfigDriver
from dut_monitor import IO_Monitor
import random


def sb_fn(actual_value):
    global expected_value
    print(f"\n\n{expected_value,actual_value}\n\n")
    assert actual_value == expected_value.pop(0), "Scoreboard Matching failed"


@CoverPoint("top.din", bins=range(256))  # noqa F405
def din_cover(din):
    pass


@CoverPoint(
    "top.prot.din.current",  # noqa F405
    xf=lambda x: x["current"],
    bins=["Idle", "Rdy", "Txn"],
)
@CoverPoint(
    "top.prot.din.previous",  # noqa F405
    xf=lambda x: x["previous"],
    bins=["Idle", "Rdy", "Txn"],
)
@CoverCross(
    "top.cross.din_prot.cross",
    items=["top.prot.din.previous", "top.prot.din.current"],
    ign_bins=[("Rdy", "Idle")],
)
def din_prot_cover(txn):
    pass


@cocotb.test()
async def test_dut(dut):
    await dut_init(dut)
    inDrv = InputDriver(dut, "din", dut.CLK)
    OutputDriver(dut, "dout", dut.CLK, sb_fn)
    IO_Monitor(dut, "din", dut.CLK, callback=din_prot_cover)
    global expected_value
    expected_value = []

    # Test using len port
    v = [[1, 4, 2, 33, 10, 20, 20, 31, 20, 8], [1, 2, 3], [2, 5, 6, 7]]
    lenDrv = InputDriver(dut, "len", dut.CLK)
    for j in v:
        await dut_rst(dut)

        expected_value.append(sum(j))
        await lenDrv._driver_send(len(j))
        for i in j:
            await inDrv._driver_send(i)
            din_cover(i)
    await Timer(10, "ns")

    # Test using cfg port
    await dut_rst(dut)
    v = [1, 4, 6, 33, 12, 20, 20, 3, 5, 8, 2, 2]
    config = {"sw_overwrite": True, "lenValue": len(v), "pause": False}
    await Timer(10, "ns")
    cfgDrv = ConfigDriver(dut, "cfg", dut.CLK)
    await cfgDrv._driver_send(config)
    expected_value.append(sum(v))
    for i in v:
        await inDrv._driver_send(i)
        din_cover(i)
        if i == 2:
            await cfgDrv._driver_send({"sw_overwrite": True, "pause": True})

    await Timer(40, "ns")

    coverage_db.report_coverage(cocotb.log.info, bins=True)
    coverage_file = os.path.join(os.getenv("RESULT_PATH", "./"), "coverage.xml")
    coverage_db.export_to_xml(filename=coverage_file)
