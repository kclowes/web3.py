from eth_account import (
    Account,
)
from eth_utils import (
    apply_to_return_value,
    is_checksum_address,
    is_string,
)
from eth_utils.toolz import (
    assoc,
    merge,
)
from hexbytes import (
    HexBytes,
)

from web3._utils.blocks import (
    select_method_for_block_identifier,
)
from web3._utils.empty import (
    empty,
)
from web3._utils.encoding import (
    to_hex,
)
from web3._utils.filters import (
    BlockFilter,
    LogFilter,
    TransactionFilter,
)
from web3._utils.threads import (
    Timeout,
)
from web3._utils.transactions import (
    assert_valid_transaction_params,
    extract_valid_transaction_params,
    get_buffered_gas_estimate,
    get_required_transaction,
    replace_transaction,
    wait_for_transaction_receipt,
)
from web3.contract import (
    Contract,
)
from web3.exceptions import (
    BlockNotFound,
    TimeExhausted,
    TransactionNotFound,
)
from web3.iban import (
    Iban,
)
from web3.method import (
    Method,
    default_root_munger,
)
from web3.module import (
    ModuleV2,
)


class Eth(ModuleV2):
    account = Account()
    defaultAccount = empty
    defaultBlock = "latest"
    defaultContractFactory = Contract
    iban = Iban
    gasPriceStrategy = None

    def namereg(self):
        raise NotImplementedError()

    def icapNamereg(self):
        raise NotImplementedError()

    get_protocol_version = Method(
        "eth_protocolVersion",
        mungers=None,
    )
    protocolVersion = get_protocol_version

    is_syncing = Method(
        "eth_syncing",
        mungers=None,
    )
    # TODO - Can't call Methods like this
    syncing = is_syncing

    _coinbase = Method(
        "eth_coinbase",
        mungers=None,
    )
    coinbase = _coinbase

    is_mining = Method(
        "eth_mining",
        mungers=None,
    )
    mining = is_mining

    get_hashrate = Method(
        "eth_hashrate",
        mungers=None,
    )
    hashrate = get_hashrate

    get_gas_price = Method(
        "eth_gasPrice",
        mungers=None,
    )
    gasPrice = get_gas_price

    get_accounts = Method(
        "eth_accounts",
        mungers=None,
    )
    accounts = get_accounts

    get_block_number = Method(
        "eth_blockNumber",
        mungers=None,
    )
    blockNumber = get_block_number

    get_chain_id = Method(
        "eth_chainId",
        mungers=None,
    )
    chainId = get_chain_id

    def block_identifier_munger(self, *args, block_identifier=None):
        if block_identifier is None:
            block_identifier = self.defaultBlock
        return [*args, block_identifier]

    getBalance = Method(
        "eth_getBalance",
        mungers=[block_identifier_munger],
    )

    # def account_position_block_id_munger(self, account, position, block_identifier=None):
    #     if block_identifier is None:
    #         block_identifier = self.defaultBlock
    #     return [account, position, block_identifier]

    getStorageAt = Method(
        "eth_getStorageAt",
        mungers=[block_identifier_munger],
    )

    getProof = Method(
        "eth_getProof",
        mungers=[block_identifier_munger],
    )

    getCode = Method(
        "eth_getCode",
        mungers=[block_identifier_munger],
    )

    getBlock = Method(
        select_method_for_block_identifier(
            if_predefined='eth_getBlockByNumber',
            if_hash='eth_getBlockByHash',
            if_number='eth_getBlockByNumber',
        ),
        mungers=[default_root_munger],
    )

    # def getBlock(self, block_identifier, full_transactions=False):
    #     """
    #     `eth_getBlockByHash`
    #     `eth_getBlockByNumber`
    #     """
    #     method = select_method_for_block_identifier(
    #         block_identifier,
    #         if_predefined='eth_getBlockByNumber',
    #         if_hash='eth_getBlockByHash',
    #         if_number='eth_getBlockByNumber',
    #     )

    #     return Method(
    #         method,
    #         mungers=[default_root_munger],
    #     )
    #     # # TODO - move these to error handlers
    #     # if result is None:
    #     #     raise BlockNotFound(f"Block with id: {block_identifier} not found.")
    #     # return result

    def getBlockTransactionCount(self, block_identifier):
        """
        `eth_getBlockTransactionCountByHash`
        `eth_getBlockTransactionCountByNumber`
        """
        method = select_method_for_block_identifier(
            block_identifier,
            if_predefined='eth_getBlockTransactionCountByNumber',
            if_hash='eth_getBlockTransactionCountByHash',
            if_number='eth_getBlockTransactionCountByNumber',
        )
        result = Method(
            method,
            mungers=[default_root_munger],
        )
        if result is None:
            raise BlockNotFound(f"Block with id: {block_identifier} not found.")
        return result

    def getUncleCount(self, block_identifier):
        """
        `eth_getUncleCountByBlockHash`
        `eth_getUncleCountByBlockNumber`
        """
        method = select_method_for_block_identifier(
            block_identifier,
            if_predefined='eth_getUncleCountByBlockNumber',
            if_hash='eth_getUncleCountByBlockHash',
            if_number='eth_getUncleCountByBlockNumber',
        )

        result = Method(
            method,
            mungers=[default_root_munger],
        )
        if result is None:
            raise BlockNotFound(f"Block with id: {block_identifier} not found.")
        return result

    def getUncleByBlock(self, block_identifier, uncle_index):
        """
        `eth_getUncleByBlockHashAndIndex`
        `eth_getUncleByBlockNumberAndIndex`
        """
        method = select_method_for_block_identifier(
            block_identifier,
            if_predefined='eth_getUncleByBlockNumberAndIndex',
            if_hash='eth_getUncleByBlockHashAndIndex',
            if_number='eth_getUncleByBlockNumberAndIndex',
        )
        result = Method(
            method,
            mungers=[default_root_munger]
        )
        if result is None:
            raise BlockNotFound(
                f"Uncle at index: {uncle_index} of block with id: {block_identifier} not found."
            )
        return result

    def getTransaction(self, transaction_hash):
        result = Method(
            "eth_getTransactionByHash",
            mungers=[default_root_munger],
        )
        if result is None:
            raise TransactionNotFound(f"Transaction with hash: {transaction_hash} not found.")
        return result

    def getTransactionFromBlock(self, block_identifier, transaction_index):
        """
        Alias for the method getTransactionByBlock
        Deprecated to maintain naming consistency with the json-rpc API
        """
        raise DeprecationWarning("This method has been deprecated as of EIP 1474.")

    def getTransactionByBlock(self, block_identifier, transaction_index):
        """
        `eth_getTransactionByBlockHashAndIndex`
        `eth_getTransactionByBlockNumberAndIndex`
        """
        method = select_method_for_block_identifier(
            block_identifier,
            if_predefined='eth_getTransactionByBlockNumberAndIndex',
            if_hash='eth_getTransactionByBlockHashAndIndex',
            if_number='eth_getTransactionByBlockNumberAndIndex',
        )
        result = Method(
            method,
            mungers=[default_root_munger],
        )
        if result is None:
            raise TransactionNotFound(
                f"Transaction index: {transaction_index} "
                f"on block id: {block_identifier} not found."
            )
        return result

    def waitForTransactionReceipt(self, transaction_hash, timeout=120, poll_latency=0.1):
        try:
            return wait_for_transaction_receipt(self.web3, transaction_hash, timeout, poll_latency)
        except Timeout:
            raise TimeExhausted(
                "Transaction {} is not in the chain, after {} seconds".format(
                    to_hex(transaction_hash),
                    timeout,
                )
            )

    def getTransactionReceipt(self, transaction_hash):
        result = Method(
            "eth_getTransactionReceipt",
            mungers=[default_root_munger],
        )
        # TODO - move these to error handling?
        if result is None:
            raise TransactionNotFound(f"Transaction with hash: {transaction_hash} not found.")
        return result

    getTransactionCount = Method(
        "eth_getTransactionCount",
        mungers=[block_identifier_munger],
    )

    def replaceTransaction(self, transaction_hash, new_transaction):
        current_transaction = get_required_transaction(self.web3, transaction_hash)
        return replace_transaction(self.web3, current_transaction, new_transaction)

    def modifyTransaction(self, transaction_hash, **transaction_params):
        assert_valid_transaction_params(transaction_params)
        current_transaction = get_required_transaction(self.web3, transaction_hash)
        current_transaction_params = extract_valid_transaction_params(current_transaction)
        new_transaction = merge(current_transaction_params, transaction_params)
        return replace_transaction(self.web3, current_transaction, new_transaction)

    def sendTransaction(self, transaction):
        # TODO: move to middleware
        if 'from' not in transaction and is_checksum_address(self.defaultAccount):
            transaction = assoc(transaction, 'from', self.defaultAccount)

        # TODO: move gas estimation in middleware
        if 'gas' not in transaction:
            transaction = assoc(
                transaction,
                'gas',
                get_buffered_gas_estimate(self.web3, transaction),
            )

        return Method(
            "eth_sendTransaction",
            mungers=[default_root_munger],
        )

    sendRawTransaction = Method(
        "eth_sendRawTransaction",
        mungers=[default_root_munger],
    )
    # def sendRawTransaction(self, raw_transaction):
    #     return self.web3.manager.request_blocking(
    #         "eth_sendRawTransaction",
    #         [raw_transaction],
    #     )

    def sign(self, account, data=None, hexstr=None, text=None):
        message_hex = to_hex(data, hexstr=hexstr, text=text)
        return self.web3.manager.request_blocking(
            "eth_sign", [account, message_hex],
        )

    signTransaction = Method(
        "eth_signTransaction",
        mungers=[default_root_munger],
    )

    signTypedData = Method(
        "eth_signTypedData",
        mungers=[default_root_munger],
    )
    # def signTypedData(self, account, jsonMessage):
    #     return self.web3.manager.request_blocking(
    #         "eth_signTypedData", [account, jsonMessage],
    #     )

    @apply_to_return_value(HexBytes)
    def call(self, transaction, block_identifier=None):
        # TODO: move to middleware
        if 'from' not in transaction and is_checksum_address(self.defaultAccount):
            transaction = assoc(transaction, 'from', self.defaultAccount)

        # TODO: move to middleware
        if block_identifier is None:
            block_identifier = self.defaultBlock
        return self.web3.manager.request_blocking(
            "eth_call",
            [transaction, block_identifier],
        )

    def estimateGas(self, transaction, block_identifier=None):
        # TODO: move to middleware
        if 'from' not in transaction and is_checksum_address(self.defaultAccount):
            transaction = assoc(transaction, 'from', self.defaultAccount)

        if block_identifier is None:
            params = [transaction]
        else:
            params = [transaction, block_identifier]

        return self.web3.manager.request_blocking(
            "eth_estimateGas",
            params,
        )

    def filter(self, filter_params=None, filter_id=None):
        if filter_id and filter_params:
            raise TypeError(
                "Ambiguous invocation: provide either a `filter_params` or a `filter_id` argument. "
                "Both were supplied."
            )
        if is_string(filter_params):
            if filter_params == "latest":
                filter_id = self.web3.manager.request_blocking(
                    "eth_newBlockFilter", [],
                )
                return BlockFilter(self.web3, filter_id)
            elif filter_params == "pending":
                filter_id = self.web3.manager.request_blocking(
                    "eth_newPendingTransactionFilter", [],
                )
                return TransactionFilter(self.web3, filter_id)
            else:
                raise ValueError(
                    "The filter API only accepts the values of `pending` or "
                    "`latest` for string based filters"
                )
        elif isinstance(filter_params, dict):
            _filter_id = self.web3.manager.request_blocking(
                "eth_newFilter",
                [filter_params],
            )
            return LogFilter(self.web3, _filter_id)
        elif filter_id and not filter_params:
            return LogFilter(self.web3, filter_id)
        else:
            raise TypeError("Must provide either filter_params as a string or "
                            "a valid filter object, or a filter_id as a string "
                            "or hex.")

    getFilterChanges = Method(
        "eth_getFilterChanges",
        mungers=[default_root_munger],
    )

    getFilterLogs = Method(
        "eth_getFilterLogs",
        mungers=[default_root_munger],
    )

    getLogs = Method(
        "eth_getLogs",
        mungers=[default_root_munger],
    )

    submitHashrate = Method(
        "eth_submitHashrate",
        mungers=[default_root_munger],
    )

    submitWork = Method(
        "eth_submitWork",
        mungers=[default_root_munger],
    )

    uninstallFilter = Method(
        "eth_uninstallFilter",
        mungers=[default_root_munger],
    )

    def contract(self,
                 address=None,
                 **kwargs):
        ContractFactoryClass = kwargs.pop('ContractFactoryClass', self.defaultContractFactory)

        ContractFactory = ContractFactoryClass.factory(self.web3, **kwargs)

        if address:
            return ContractFactory(address)
        else:
            return ContractFactory

    def setContractFactory(self, contractFactory):
        self.defaultContractFactory = contractFactory

    def getCompilers(self):
        raise DeprecationWarning("This method has been deprecated as of EIP 1474.")

    getWork = Method(
        "eth_getWork",
        mungers=None
    )

    def generateGasPrice(self, transaction_params=None):
        if self.gasPriceStrategy:
            return self.gasPriceStrategy(self.web3, transaction_params)

    def setGasPriceStrategy(self, gas_price_strategy):
        self.gasPriceStrategy = gas_price_strategy
