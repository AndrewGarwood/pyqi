"""
*`@file`* `_utils`
"""
from typing import Protocol

class HasDunderName(Protocol):
    @property
    def __name__(self) -> str: ...

def export_symbols(*items: HasDunderName, ) -> tuple[str, ...]:
    """ 
    *`@returns`* `tuple(x.__name__ for x in items)` 
    ```
    __all__ = [
        *export_symbols(cls0, cls1, fn0, fn1),
        "const0"
    ]
    ```
    `.vscode/settings.json` (if no want warning)
    ```
    {
        "python.analysis.diagnosticSeverityOverrides": {
            "reportUnsupportedDunderAll": "none"
        } # or "information"
    }
    ```
    """
    return tuple(x.__name__ for x in items)

def export(*items: HasDunderName | str, ) -> list[str]:
    """ 
    *`@returns`* `list(x if isinstance(x, str) else x.__name__ for x in items)` 
    ```
    __all__ = export(cls0, cls1, fn0, fn1, "const0")
    ```
    `.vscode/settings.json` (if no want warning)
    ```
    {
        "python.analysis.diagnosticSeverityOverrides": {
            "reportUnsupportedDunderAll": "none"
        }  # or "information"
    }
    ```
    """
    return list(x if isinstance(x, str) else x.__name__ for x in items)