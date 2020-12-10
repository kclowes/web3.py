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
                    "foo": (Foo,),
                }),
            }),
        }),
    }
    w3 = Web3(EthereumTesterProvider(), modules={})
    attach_modules(w3, mods)
    assert w3.foo.bar.baa.does_something() == 'passed'
    assert w3.foo.bar.baa.baz.does_something_else() == 'something else'
    assert w3.foo.bar.baa.foo.foo_fn() == 'foo_fn'


def test_attach_modules_with_wrong_module_format():
    mods = {
        "foo": (Foo, Bar, Baz)
    }
    w3 = Web3(EthereumTesterProvider, modules={})
    with pytest.raises(ValidationError, match="Module definitions can only have 1 or 2 elements"):
        attach_modules(w3, mods)


def test_attach_modules_with_existing_modules():
    mods = {
        "foo": (Foo,),
    }
    w3 = Web3(EthereumTesterProvider, modules=mods)
    with pytest.raises(AttributeError,
                       match="The web3 object already has an attribute with that name"):
        attach_modules(w3, mods)
