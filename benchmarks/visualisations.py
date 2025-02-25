"""Visualisations for benchmark data."""

import time

import matplotlib.pyplot as plt
from bench_utils import warmed_timeit
from components import (
    LexPhase,
    ParsePhase,
    PatternRewritePhase,
    PrintPhase,
    VerifyPhase,
)

LEXER = LexPhase()
PARSER = ParsePhase()
PATTERN_REWRITER = PatternRewritePhase()
VERIFIER = VerifyPhase()
PRINTER = PrintPhase()


def draw_comparison_chart() -> None:
    """Compare the pipeline phase times for a workload."""
    plt.style.use("default")
    plt.rcParams.update(
        {
            "grid.alpha": 0.7,
            "grid.linestyle": "--",
            "figure.dpi": 100,
            "font.family": "Menlo",
        }
    )
    plt.title("Pipeline phase times for constant folding 100 items")

    phase_functions = {
        "Lexing": LEXER.time_constant_100,
        "Lexing + Parsing": PARSER.time_constant_100,
        "Rewriting": PATTERN_REWRITER.time_constant_100,
        "Verifying": VERIFIER.time_constant_100,
        "Printing": PRINTER.time_constant_100_input,
    }

    raw_phase_times = {
        name: warmed_timeit(func) for name, func in phase_functions.items()
    }
    print(raw_phase_times)
    phase_means = {
        "Lexing": raw_phase_times["Lexing"][0],
        "Parsing": raw_phase_times["Lexing + Parsing"][0]
        - raw_phase_times["Lexing"][0],
        "Rewriting": raw_phase_times["Rewriting"][0],
        "Verifying": raw_phase_times["Verifying"][0],
        "Printing": raw_phase_times["Printing"][0],
    }
    phase_medians = {
        "Lexing": raw_phase_times["Lexing"][1],
        "Parsing": raw_phase_times["Lexing + Parsing"][1]
        - raw_phase_times["Lexing"][1],
        "Rewriting": raw_phase_times["Rewriting"][1],
        "Verifying": raw_phase_times["Verifying"][1],
        "Printing": raw_phase_times["Printing"][1],
    }
    phase_errors = {
        "Lexing": raw_phase_times["Lexing"][2],
        "Parsing": raw_phase_times["Lexing + Parsing"][2]
        + raw_phase_times["Lexing"][2],
        "Rewriting": raw_phase_times["Rewriting"][2],
        "Verifying": raw_phase_times["Verifying"][2],
        "Printing": raw_phase_times["Printing"][2],
    }

    for name in phase_means:
        if name in phase_errors:
            print(
                f"{name}: {phase_means[name]:.3g} ± {phase_errors[name]:.3g}s (median {phase_medians[name]:.3g})"
            )
    print(f"Total: {sum(phase_means.values()):.3g} ± {sum(phase_errors.values()):.3g}s")

    plt.bar(
        phase_means.keys(),
        phase_means.values(),
        yerr=[phase_errors[name] for name in phase_means],
        error_kw={"capsize": 5},
        label="mean",
    )
    plt.scatter(
        phase_medians.keys(),
        phase_medians.values(),
        label="median",
    )
    plt.xlabel("Pipeline phase", fontweight="bold")
    plt.ylabel("Time [s]", fontweight="bold")
    plt.grid(axis="y")
    plt.legend()
    plt.savefig(f"/Users/edjg/Desktop/ubenchmarks/out{int(time.time())}.pdf", dpi=300)
    plt.show()


if __name__ == "__main__":
    draw_comparison_chart()
