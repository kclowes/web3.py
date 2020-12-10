from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Optional,
    Sequence,
    TypeVar,
)

from web3.exceptions import (
    ValidationError,
)

T = TypeVar("T")

if TYPE_CHECKING:
    from web3 import Web3  # noqa: F401


def attach_modules(
    parent_module: T,
    module_definitions: Dict[str, Sequence[Any]],
    web3: Optional[T] = None
) -> None:
    for module_name, module_info in module_definitions.items():
        module_class = module_info[0]

        if hasattr(parent_module, module_name):
            raise AttributeError(
                f"Cannot set {parent_module} module named '{module_name}'.  The web3 object "
                "already has an attribute with that name"
            )

        if web3 is None:
            setattr(parent_module, module_name, module_class(parent_module))
            web3 = parent_module
        else:
            setattr(parent_module, module_name, module_class(web3))

        if len(module_info) == 2:
            submodule_definitions = module_info[1]
            module = getattr(parent_module, module_name)
            attach_modules(module, submodule_definitions, web3)
        elif len(module_info) != 1:
            raise ValidationError("Module definitions can only have 1 or 2 elements.")
