import argparse
import csv
from collections import defaultdict
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from python_scripts.experiments.common import pearson_correlation, to_float, to_int


def load_rows(csv_path: Path) -> list[dict]:
    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def family_summary(rows: list[dict]) -> dict[str, dict]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["family"]].append(row)

    summary = {}
    for family, family_rows in grouped.items():
        ok_rows = [row for row in family_rows if row["status"] == "ok"]
        macs = [to_float(row["macs"]) for row in ok_rows if to_float(row["macs"]) is not None]
        mcu = [to_float(row["mcu_avg_us"]) for row in ok_rows if to_float(row["mcu_avg_us"]) is not None]
        workstation = [
            to_float(row["workstation_avg_us"])
            for row in ok_rows
            if to_float(row["workstation_avg_us"]) is not None
        ]

        summary[family] = {
            "total_rows": len(family_rows),
            "ok_rows": len(ok_rows),
            "failed_rows": len(family_rows) - len(ok_rows),
            "macs_vs_mcu_r": pearson_correlation(macs, mcu) if len(macs) == len(mcu) else None,
            "workstation_vs_mcu_r": (
                pearson_correlation(workstation, mcu)
                if len(workstation) == len(mcu)
                else None
            ),
        }
    return summary


def overall_summary(rows: list[dict]) -> dict:
    ok_rows = [row for row in rows if row["status"] == "ok"]
    macs = [to_float(row["macs"]) for row in ok_rows if to_float(row["macs"]) is not None]
    mcu = [to_float(row["mcu_avg_us"]) for row in ok_rows if to_float(row["mcu_avg_us"]) is not None]
    workstation = [
        to_float(row["workstation_avg_us"])
        for row in ok_rows
        if to_float(row["workstation_avg_us"]) is not None
    ]
    arena_estimated = [
        to_float(row["arena_estimated"])
        for row in ok_rows
        if to_float(row["arena_estimated"]) is not None
    ]
    arena_final = [
        to_float(row["arena_final"])
        for row in ok_rows
        if to_float(row["arena_final"]) is not None
    ]

    return {
        "total_rows": len(rows),
        "ok_rows": len(ok_rows),
        "failed_rows": len(rows) - len(ok_rows),
        "macs_vs_mcu_r": pearson_correlation(macs, mcu) if len(macs) == len(mcu) else None,
        "workstation_vs_mcu_r": (
            pearson_correlation(workstation, mcu) if len(workstation) == len(mcu) else None
        ),
        "arena_estimated_vs_final_r": (
            pearson_correlation(arena_estimated, arena_final)
            if len(arena_estimated) == len(arena_final)
            else None
        ),
    }


def format_metric(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.4f}"


def write_markdown_report(csv_path: Path, output_md: Path, rows: list[dict]) -> None:
    overall = overall_summary(rows)
    family = family_summary(rows)
    failed_rows = [row for row in rows if row["status"] != "ok"]

    lines = []
    lines.append("# Relatorio de Benchmark Suite")
    lines.append("")
    lines.append(f"- CSV analisado: `{csv_path}`")
    lines.append(f"- total de linhas: `{overall['total_rows']}`")
    lines.append(f"- sucessos: `{overall['ok_rows']}`")
    lines.append(f"- falhas: `{overall['failed_rows']}`")
    lines.append("")
    lines.append("## Correlacoes gerais")
    lines.append("")
    lines.append("| Comparacao | r de Pearson |")
    lines.append("| --- | ---: |")
    lines.append(f"| MACs vs MCU avg us | {format_metric(overall['macs_vs_mcu_r'])} |")
    lines.append(
        f"| Workstation avg us vs MCU avg us | {format_metric(overall['workstation_vs_mcu_r'])} |",
    )
    lines.append(
        f"| Arena estimada vs arena final | {format_metric(overall['arena_estimated_vs_final_r'])} |",
    )
    lines.append("")
    lines.append("## Correlacoes por familia")
    lines.append("")
    lines.append("| Familia | Linhas | Sucessos | Falhas | MACs vs MCU r | Workstation vs MCU r |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for family_name in sorted(family):
        data = family[family_name]
        lines.append(
            "| "
            + f"{family_name} | {data['total_rows']} | {data['ok_rows']} | {data['failed_rows']} | "
            + f"{format_metric(data['macs_vs_mcu_r'])} | {format_metric(data['workstation_vs_mcu_r'])} |",
        )

    lines.append("")
    lines.append("## Amostras coletadas")
    lines.append("")
    lines.append("| Familia | Nome | Arena final | MACs | Workstation avg us | MCU avg us | Attempts | Status |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |")
    for row in rows:
        lines.append(
            "| "
            + f"{row['family']} | {row['name']} | {row['arena_final'] or 'n/a'} | {row['macs'] or 'n/a'} | "
            + f"{row['workstation_avg_us'] or 'n/a'} | {row['mcu_avg_us'] or 'n/a'} | {row['attempts'] or 'n/a'} | {row['status']} |",
        )

    if failed_rows:
        lines.append("")
        lines.append("## Falhas")
        lines.append("")
        lines.append("| Familia | Nome | Error |")
        lines.append("| --- | --- | --- |")
        for row in failed_rows:
            lines.append(f"| {row['family']} | {row['name']} | {row['error']} |")

    lines.append("")
    lines.append("## Observacoes")
    lines.append("")
    lines.append(
        "- Correlacao de Pearson so faz sentido com pelo menos dois pontos validos e variacao real entre eles.",
    )
    lines.append(
        "- Se o suite tiver apenas um modelo, os campos de correlacao ficam como `n/a` por definicao.",
    )
    lines.append(
        "- Para chegar mais perto do artigo, adicione varias variacoes por familia ao manifesto e rerode a coleta.",
    )

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze the CSV produced by run_benchmark_suite.py and write a Markdown report.",
    )
    parser.add_argument("input_csv", help="CSV generated by the benchmark suite runner")
    parser.add_argument("output_md", help="Markdown report path")
    args = parser.parse_args()

    csv_path = Path(args.input_csv).resolve()
    output_md = Path(args.output_md).resolve()
    rows = load_rows(csv_path)
    if not rows:
        raise ValueError(f"No rows were found in {csv_path}")

    write_markdown_report(csv_path, output_md, rows)
    print(f"Report written to {output_md}")


if __name__ == "__main__":
    main()
