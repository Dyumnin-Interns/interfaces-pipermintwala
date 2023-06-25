import cocotb
from cocotb.result import TestFailure
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db
from cocotb.triggers import RisingEdge, Timer
import os
from dut_init import dut_init
from dut_drivers import InputDriver, OutputDriver
from dut_monitor import IO_Monitor


def sb_fn(actual_value):
    global expected_value
    print(f"\n\n{expected_value,actual_value}\n\n")
    try:
        assert actual_value == expected_value.pop(0)
    except:
        raise TestFailure("Scoreboard Matching failed")


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
    # Test using len port

    await dut_init(dut)
    lenDrv = InputDriver(dut, "len", dut.CLK)
    inDrv = InputDriver(dut, "din", dut.CLK)
    OutputDriver(dut, "dout", dut.CLK, sb_fn)
    IO_Monitor(dut, "din", dut.CLK, callback=din_prot_cover)
    global expected_value
    expected_value = []
    v = [1, 4, 6, 33, 150, 20, 20, 3, 5, 8]
    expected_value.append(sum(v))
    await lenDrv._driver_send(len(v))
    for i in v:
        await inDrv._driver_send(i)
        din_cover(i)

    # Test using cfg port

    await dut_init(dut)
    await Timer(10, "ns")
    dut.cfg_en.value = 1
    dut.cfg_op.value = 1  # Write operation
    dut.cfg_address.value = 4
    dut.cfg_data_in.value = 0x00000001  # Enable s/w override
    dut.cfg_address.value = 8
    v = [1, 4, 2, 33, 90, 20, 20, 31, 20, 8]
    expected_value.append(sum(v))
    dut.cfg_data_in.value = len(v)  # Set Len Value

    for i in v:
        await inDrv._driver_send(i)
        din_cover(i)
    coverage_db.report_coverage(cocotb.log.info, bins=True)
    coverage_file = os.path.join(os.getenv("RESULT_PATH", "./"), "coverage.xml")
    coverage_db.export_to_xml(filename=coverage_file)
