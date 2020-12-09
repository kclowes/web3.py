import pytest

from web3._utils.module import (
    attach_modules,
)
from web3 import Web3
from web3.exceptions import (
    ValidationError,
)
# from web3.geth import (
#     Geth,
# )
from web3.module import (
    ModuleV2,
)
# from web3.parity import (
#     Parity,
#     ParityPersonal,
# )
from web3.providers.eth_tester import (
    EthereumTesterProvider,
)


class Foo(ModuleV2):
    def foo_fn(self):
        return 'foo_fn'


class Bar(ModuleV2):
    pass


class Baa(ModuleV2):
    def does_something(self):
        return 'passed'


class Baz(ModuleV2):
    def does_something_else(self):
        return 'something else'
# modules = {
#     "eth": (Eth,),
#     "net": (Net,),
#     "version": (Version,),
#     "parity": (Parity, {
#         "personal": (ParityPersonal,),
#     }),
#     "geth": (Geth, {
#         "admin": (GethAdmin,),
#         "miner": (GethMiner,),
#         "personal": (GethPersonal,),
#         "txpool": (GethTxPool,),
#     }),
#     "testing": (Testing,),
# }


def test_attach_modules():
    mods = {
        "foo": (Foo, {
            "bar": (Bar, {
                "baa": (Baa, {
                    "baz": (Baz,),
                }),
            }),
        }),
    }
    w3 = Web3(EthereumTesterProvider, modules={})
    attach_modules(w3, mods)
    assert w3.foo.bar.baa.does_something() == 'passed'
    assert w3.foo.bar.baa.baz.does_something_else() == 'something else'
