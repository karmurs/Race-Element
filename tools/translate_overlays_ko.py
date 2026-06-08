# -*- coding: utf-8 -*-
"""
오버레이(게임 화면에 그려지는 HUD) 라벨 한글화.
- 특정 파일의 정확한 따옴표 문자열만 교체(EDITS)
- 모든 오버레이의 .AddLine("라벨", ...) / .Draw(g, "라벨", ...) 의 '라벨' 인자만 교체(LABELS)
두 방식 모두 '표시용 라벨'만 건드리고 코드 식별자/로직 문자열은 손대지 않는다.
약어(ABS, RPM, TC1...)와 디버그용 라벨은 일부러 영어로 둔다.
"""
import re, os, glob, sys

EDITS = {
    "Race_Element.HUD.ACC/Overlays/Driving/AverageLaptime/AverageLaptime.cs": [
        ('"fastest lap time:      "', '"최고 랩타임:        "'),
        ('"fastest "', '"최고 "'),
        ('" lap average: "', '" 랩 평균: "'),
        ('"average"', '"평균"'),
    ],
}

LABELS = {
    "Air": "기온", "Avg": "평균", "Car": "차량", "Clock": "시계", "Condition": "상태",
    "Drivers/Laps": "드라이버/랩", "Expected Pos": "예상 순위", "Fastest": "최고",
    "Fastest Lap": "최고 랩", "Flag": "플래그", "Fuel": "연료", "Fuel Time": "연료 시간",
    "Fuel-End": "연료 소진", "Grip": "그립", "Laps": "랩", "Laps Left": "남은 랩",
    "Location": "위치", "Map": "맵", "Max": "최대", "Median": "중간값", "Min": "최소",
    "Model": "모델", "Multiplier": "배율", "Phase": "단계", "Pit": "피트",
    "Pit Closing": "피트 마감", "Pit Open In": "피트 오픈까지", "Position": "순위",
    "Power": "파워", "Redline": "레드라인", "Replay Bar %": "리플레이 바 %",
    "Replay Bar open?": "리플레이 바 열림?", "Replay Paused": "리플레이 일시정지",
    "Replay Speed": "리플레이 속도", "Replay Time": "리플레이 시간",
    "Save replay before": "리플레이 저장 시점", "Sectors": "섹터", "Session": "세션",
    "Session End": "세션 종료", "Session Length": "세션 길이", "Session Time": "세션 시간",
    "Set": "세트", "Stint": "스틴트", "Stint Fuel": "스틴트 연료", "Stint Time": "스틴트 시간",
    "Throttle": "스로틀", "Time": "시간", "Track": "트랙", "Type": "종류", "Wind": "바람",
}

OVERLAY_DIRS = [
    "Race_Element.HUD.ACC/Overlays",
    "Race Element.HUD.Common/Overlays",
]

count_edits = 0
count_labels = 0

def _label_sub(m):
    global count_labels
    if m.group(2) in LABELS:
        count_labels += 1
        return m.group(1) + LABELS[m.group(2)] + m.group(3)
    return m.group(0)

def main(root="."):
    global count_edits
    for rel, pairs in EDITS.items():
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            print("skip (not found):", rel); continue
        s = open(p, encoding="utf-8").read(); n = 0
        for old, new in pairs:
            c = s.count(old)
            if c:
                s = s.replace(old, new); n += c
        open(p, "w", encoding="utf-8").write(s)
        count_edits += n
        print("[overlays_ko] EDITS %s: %d" % (rel, n))

    addline_re = re.compile(r'(\.AddLine\(\s*")([^"]*)(")')
    draw_re = re.compile(r'(\.Draw\(\s*g\s*,\s*")([^"]*)(")')
    files = []
    for d in OVERLAY_DIRS:
        files += glob.glob(os.path.join(root, d, "**", "*.cs"), recursive=True)
    for f in files:
        s = open(f, encoding="utf-8", errors="replace").read()
        s2 = draw_re.sub(_label_sub, addline_re.sub(_label_sub, s))
        if s2 != s:
            open(f, "w", encoding="utf-8").write(s2)

    print("[overlays_ko] EDITS total %d, LABEL replacements %d (checked %d files)"
          % (count_edits, count_labels, len(files)))
    return 0

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
