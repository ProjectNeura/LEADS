from leads import LEADS as _LEADS, Plugin as _Plugin, SystemLiteral as _SystemLiteral, DTCS as _DTCS, ABS as _ABS, \
    EBI as _EBI, ATBS as _ATBS, set_on_register_context as _set_on_register_context
from leads.types import OnRegister as _OnRegister


def register_plugins(plugins: dict[str, _Plugin] | None = None) -> None:
    if not plugins:
        plugins = {_SystemLiteral.DTCS: _DTCS, _SystemLiteral.ABS: _ABS, _SystemLiteral.EBI: _EBI,
                   _SystemLiteral.ATBS: _ATBS}

    def _on_register_context(chain: _OnRegister[_LEADS]) -> _OnRegister[_LEADS]:
        def _(ctx: _LEADS) -> None:
            chain(ctx)
            for k, p in plugins.items():
                ctx.plugin(k, p)

        return _

    _set_on_register_context(_on_register_context)
