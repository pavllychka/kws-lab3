import argparse
import json
import os
import shutil

import requests

CLASSES = ["yes", "no", "up", "down"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--url", default="http://127.0.0.1:8000/predict")
    ap.add_argument("--min-conf", type=float, default=0.99)
    ap.add_argument("--out-dir", default="samples")
    args = ap.parse_args()

    root = os.path.join(args.data_dir, "SpeechCommands", "speech_commands_v0.02")
    with open(os.path.join(root, "testing_list.txt")) as f:
        test = [line.strip() for line in f]

    os.makedirs(args.out_dir, exist_ok=True)
    expected = {}
    for c in CLASSES:
        files = [p for p in test if p.startswith(c + "/")][:80]
        for p in files:
            src = os.path.join(root, p)
            with open(src, "rb") as fh:
                r = requests.post(args.url, files={"file": fh}).json()
            if r["label"] == c and r["confidence"] >= args.min_conf:
                shutil.copy(src, os.path.join(args.out_dir, c + ".wav"))
                expected[c + ".wav"] = c
                print(f"{c}: {p} (впевненість {r['confidence']})")
                break
        else:
            raise SystemExit(f"Не знайшла підходящий зразок для {c}")

    with open(os.path.join(args.out_dir, "expected.json"), "w",
              encoding="utf-8") as f:
        json.dump(expected, f, indent=2)


if __name__ == "__main__":
    main()