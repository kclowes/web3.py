import pytest

# from web3.parity import (
#     shh,
# )


@pytest.fixture(autouse=True)
def include_parity_shh_module(web3):
    web3.parity.shh.attach(web3, "shh")
