"""List pyright's sympy-Expr-for-a-multivector errors as file, line, message rows.

Reads the pyright ``--outputjson`` report named on the command line and prints one
tab-separated row per error whose message names ``Expr``, skipping the generated
modules ``g1.py``..``g5.py`` (their errors are a separate cause).
"""

import json
import sys
import typing

GENERATED: frozenset[str] = frozenset(f"g{n}.py" for n in range(1, 6))


def main(report_path: str) -> None:
    """Print the Expr-cause rows from one pyright JSON report.

    Args:
        report_path: path of the pyright ``--outputjson`` file.
    """
    report: dict[str, typing.Any] = json.load(open(report_path))
    diagnostic: dict[str, typing.Any]
    for diagnostic in report["generalDiagnostics"]:
        path: str = diagnostic["file"].removeprefix("/gacalc/")
        message: str = diagnostic["message"].split("\n")[0]
        if (
            diagnostic["severity"] == "error"
            and "Expr" in message
            and path.rsplit("/", 1)[-1] not in GENERATED
        ):
            line: int = diagnostic["range"]["start"]["line"] + 1
            sys.stdout.write(f"{path}\t{line}\t{message}\n")


if __name__ == "__main__":
    main(sys.argv[1])
