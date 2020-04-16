from typing import (
    Callable,
    List,
    Optional,
    Tuple,
    Union,
)

from eth_typing import (
    Address,
    ChecksumAddress,
    Hash32,
    HexStr,
)
from eth_utils import (
    is_checksum_address,
)
from eth_utils.toolz import (
    assoc,
)

from web3._utils import (
    shh,
)
from web3._utils.compat import (
    Literal,
)
from web3._utils.personal import (
    ecRecover,
    importRawKey,
    listAccounts,
    newAccount,
    sendTransaction,
    sign,
    signTypedData,
    unlockAccount,
)
from web3._utils.rpc_abi import (
    RPC,
)
from web3.method import (
    Method,
    default_root_munger,
)
from web3.module import (
    ModuleV2,
)
from web3.types import (
    ENS,
    BlockIdentifier,
    EnodeURI,
    ParityBlockTrace,
    ParityFilterParams,
    ParityFilterTrace,
    ParityMode,
    ParityNetPeers,
    ParityTraceMode,
    TxParams,
    _Hash32,
)


class ParityShh(ModuleV2):
    """
    https://wiki.parity.io/JSONRPC-shh-module
    """
    info = shh.info
    new_key_pair = shh.new_key_pair
    add_private_key = shh.add_private_key
    new_sym_key = shh.new_sym_key
    add_sym_key = shh.add_sym_key
    get_public_key = shh.get_public_key
    get_private_key = shh.get_private_key
    get_sym_key = shh.get_sym_key
    post = shh.post
    new_message_filter = shh.new_message_filter
    delete_message_filter = shh.delete_message_filter
    get_filter_messages = shh.get_filter_messages
    delete_key = shh.delete_key
    subscribe = shh.subscribe
    unsubscribe = shh.unsubscribe
    # Deprecated
    newKeyPair = shh.new_key_pair
    addPrivateKey = shh.add_private_key
    newSymKey = shh.new_sym_key
    addSymKey = shh.add_sym_key
    getPublicKey = shh.get_public_key
    getPrivateKey = shh.get_private_key
    getSymKey = shh.get_sym_key
    newMessageFilter = shh.new_message_filter
    deleteMessageFilter = shh.delete_message_filter
    getFilterMessages = shh.get_filter_messages
    deleteKey = shh.delete_key


class ParityPersonal(ModuleV2):
    """
    https://wiki.parity.io/JSONRPC-personal-module
    """
    ecRecover = ecRecover
    importRawKey = importRawKey
    listAccounts = listAccounts
    newAccount = newAccount
    sendTransaction = sendTransaction
    sign = sign
    signTypedData = signTypedData
    unlockAccount = unlockAccount


class Parity(ModuleV2):
    """
    https://paritytech.github.io/wiki/JSONRPC-parity-module
    """
    defaultBlock: Literal["latest"] = "latest"  # noqa: E704
    shh: ParityShh
    personal: ParityPersonal

    enode: Method[Callable[[], str]] = Method(
        RPC.parity_enode,
        mungers=None,
    )

    def list_storage_keys_munger(
        self,
        address: Union[Address, ChecksumAddress, ENS, Hash32],
        quantity: int,
        hash_: Hash32,
        block_identifier: Optional[BlockIdentifier]=None,
    ) -> Tuple[Union[Address, ChecksumAddress, ENS, Hash32], int, Hash32, BlockIdentifier]:
        if block_identifier is None:
            block_identifier = self.defaultBlock
        return (address, quantity, hash_, block_identifier)

    listStorageKeys: Method[Callable[..., List[str]]] = Method(
        RPC.parity_listStorageKeys,
        mungers=[list_storage_keys_munger],
    )

    netPeers: Method[Callable[[], ParityNetPeers]] = Method(
        RPC.parity_netPeers,
        mungers=None
    )

    addReservedPeer: Method[Callable[[EnodeURI], bool]] = Method(
        RPC.parity_addReservedPeer,
        mungers=[default_root_munger],
    )

    def trace_replay_transaction_munger(
        self, block_identifier: _Hash32, mode: ParityTraceMode=['trace']
    ) -> Tuple[Union[BlockIdentifier, _Hash32], ParityTraceMode]:
        return (block_identifier, mode)

    traceReplayTransaction: Method[Callable[..., ParityBlockTrace]] = Method(
        RPC.trace_replayTransaction,
        mungers=[trace_replay_transaction_munger],
    )

    def trace_replay_block_transactions_munger(
        self, block_identifier: BlockIdentifier, mode: ParityTraceMode=['trace']
    ) -> Tuple[BlockIdentifier, ParityTraceMode]:
        return (block_identifier, mode)

    traceReplayBlockTransactions: Method[Callable[..., List[ParityBlockTrace]]] = Method(
        RPC.trace_replayBlockTransactions,
        mungers=[trace_replay_block_transactions_munger]
    )

    traceBlock: Method[Callable[[BlockIdentifier], List[ParityBlockTrace]]] = Method(
        RPC.trace_block,
        mungers=[default_root_munger],
    )

    traceFilter: Method[Callable[[ParityFilterParams], List[ParityFilterTrace]]] = Method(
        RPC.trace_filter,
        mungers=[default_root_munger],
    )

    traceTransaction: Method[Callable[[BlockIdentifier], List[ParityBlockTrace]]] = Method(
        RPC.trace_transaction,
        mungers=[default_root_munger],
    )

    def trace_call_munger(
        self,
        transaction: TxParams,
        mode: ParityTraceMode=['trace'],
        block_identifier: Optional[BlockIdentifier]=None
    ) -> Tuple[TxParams, ParityTraceMode, BlockIdentifier]:
        if 'from' not in transaction and is_checksum_address(self.web3.eth.defaultAccount):
            transaction = assoc(transaction, 'from', self.web3.eth.defaultAccount)

        # TODO: move to middleware
        if block_identifier is None:
            block_identifier = self.defaultBlock

        return (transaction, mode, block_identifier)

    traceCall: Method[Callable[..., ParityBlockTrace]] = Method(
        RPC.trace_call,
        mungers=[trace_call_munger],
    )

    def trace_transactions_munger(
        self, raw_transaction: HexStr, mode: ParityTraceMode=['trace']
    ) -> Tuple[HexStr, ParityTraceMode]:
        return (raw_transaction, mode)

    traceRawTransaction: Method[Callable[..., ParityBlockTrace]] = Method(
        RPC.trace_rawTransaction,
        mungers=[trace_transactions_munger],
    )

    setMode: Method[Callable[[ParityMode], bool]] = Method(
        RPC.parity_setMode,
        mungers=[default_root_munger],
    )

    mode: Method[Callable[[], ParityMode]] = Method(
        RPC.parity_mode,
        mungers=None
    )
