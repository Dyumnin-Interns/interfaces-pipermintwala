from cocotb.triggers import RisingEdge


async def dut_init(dut):
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
