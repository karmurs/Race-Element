# -*- coding: utf-8 -*-
"""
오버레이(게임 화면에 그려지는 HUD) 라벨 한글화.
지정한 파일에서 '정확히 일치하는 따옴표 문자열'만 교체하므로 코드 식별자는 안전하다.
"""
import sys, os

EDITS = {
    "Race_Element.HUD.ACC/Overlays/Driving/AverageLaptime/AverageLaptime.cs": [
        ('"fastest lap time:      "', '"최고 랩타임:        "'),
        ('"fastest "', '"최고 "'),
        ('" lap average: "', '" 랩 평균: "'),
        ('"average"', '"평균"'),
    ],
}

def main(root="."):
    total = 0
    for rel, pairs in EDITS.items():
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            print("skip (not found):", rel)
            continue
        s = open(p, encoding="utf-8").read()
        n = 0
        for old, new in pairs:
            c = s.count(old)
            if c:
                s = s.replace(old, new)
                n += c
        open(p, "w", encoding="utf-8").write(s)
        total += n
        print("[overlays_ko] %s: %d replaced" % (rel, n))
    print("[overlays_ko] total %d replaced" % total)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
