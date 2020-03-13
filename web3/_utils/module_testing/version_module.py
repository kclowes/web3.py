from typing import (
    TYPE_CHECKING,
)

from eth_utils import (
    is_integer,
)

if TYPE_CHECKING:
    from web3 import Web3  # noqa: F401


class VersionModuleTest:
    def test_eth_protocolVersion(self, web3: "Web3") -> None:
        protocol_version = web3.eth.protocolVersion

        assert is_integer(protocol_version)
