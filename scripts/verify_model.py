import argparse
import json
import os
import sys

import requests


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8000")
    ap.add_argument("--expected", default="samples/expected.json")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    base = args.url.rstrip("/")
    folder = os.path.dirname(args.expected)
    with open(args.expected, encoding="utf-8") as f:
        expected = json.load(f)

    details = []
    for name, want in expected.items():
        with open(os.path.join(folder, name), "rb") as f:
            r = requests.post(
                base + "/predict",
                files={"file": (name, f, "audio/wav")},
                timeout=30,
            )
        r.raise_for_status()
        body = r.json()
        ok = body["label"] == want
        details.append({
            "file": name,
            "expected": want,
            "predicted": body["label"],
            "confidence": body["confidence"],
            "ok": ok,
        })
        mark = "OK  " if ok else "FAIL"
        print(f"{mark} {name}: очікувано {want}, отримано {body['label']} "
              f"({body['confidence']})")

    passed = sum(d["ok"] for d in details)
    result = {"passed": passed, "total": len(details), "details": details}
    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Пройдено {passed}/{len(details)}")
    sys.exit(0 if passed == len(details) else 1)


if __name__ == "__main__":
    main()