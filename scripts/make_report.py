import argparse
import json
import os


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", default="metrics")
    ap.add_argument("--artifacts", default="artifacts")
    ap.add_argument("--out", default="metrics/report.md")
    args = ap.parse_args()

    train = load(os.path.join(args.artifacts, "metrics.json"))
    lat = load(os.path.join(args.metrics, "latency.json"))
    ver = load(os.path.join(args.metrics, "verify.json"))

    summary = {
        "commit": os.getenv("GITHUB_SHA", "local")[:7],
        "event": os.getenv("GITHUB_EVENT_NAME", "local"),
        "epochs": train.get("epochs"),
        "accuracy": train.get("accuracy"),
        "model_size_kb": train.get("model_size_kb"),
        "latency_ms": lat.get("latency_ms"),
        "golden_samples": {
            "passed": ver.get("passed"),
            "total": ver.get("total"),
        },
    }

    os.makedirs(args.metrics, exist_ok=True)
    with open(os.path.join(args.metrics, "summary.json"), "w",
              encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    lm = summary["latency_ms"] or {}
    gs = summary["golden_samples"]
    lines = [
        "## Звіт ML-пайплайна",
        "",
        "| Параметр | Значення |",
        "| --- | --- |",
        f"| Коміт | `{summary['commit']}` |",
        f"| Подія | {summary['event']} |",
        f"| Епох | {summary['epochs']} |",
        f"| Accuracy, % | {summary['accuracy']} |",
        f"| Розмір моделі, КБ | {summary['model_size_kb']} |",
        f"| Latency mean / p50 / p95, мс | "
        f"{lm.get('mean')} / {lm.get('p50')} / {lm.get('p95')} |",
        f"| Еталонні зразки | {gs['passed']}/{gs['total']} |",
    ]
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()