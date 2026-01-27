# Coding Standards

## General Python
*   **Style Guide**: PEP 8 compliance.
*   **Type Hinting**: Required for all function signatures (e.g., `def my_func(a: int) -> str:`).
*   **Docstrings**: Google Style docstrings for all modules, classes, and functions.

## Taipy Specifics
*   **Callbacks**: Name callbacks clearly, e.g., `on_submit_action`, `on_change_input`.
*   **State**: Minimize global state usage; use Taipy's `state` object effectively within callbacks.
*   **Layout**: Use `tgb` (Taipy GUI Builder) syntax for Python-based UI definition over Markdown where complex logic is involved, though Markdown is acceptable for static content.

## Configuration (Dynaconf)
*   **Access**: Always access config via `settings.key` (from `config.py`), never hardcode values.
*   **Secrets**: Never commit secrets. Use `.secrets.toml` or Environment Variables.

## Error Handling
*   **Exceptions**: Use specific exception blocks (avoid bare `except:`).
*   **Logging**: Use Python's `logging` module. Do not use `print` statements in production code.

## Testing
*   **Framework**: `pytest`.
*   **Coverage**: Aim for high coverage on Business Logic (`database.py`, `auth.py`). UI testing is secondary.
