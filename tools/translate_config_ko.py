# -*- coding: utf-8 -*-
"""
설정 화면(HUD 옵션/그룹/선택지/On·Off/설명문) 한글화.
- 라벨/그룹/선택지: 단어 단위 사전(WORDS)으로 변환 -> 모든 오버레이에 자동 적용
- 설명문: 문장 사전(DESC)으로 변환 (없으면 영어 그대로 = 안 깨짐)
방식: 라벨을 만드는 코드 몇 곳에 KoMap.Label()/KoMap.Desc() 호출만 끼워넣는다.
변수명/저장 키는 손대지 않으므로 저장된 설정이 안전하다.
"""
import os, re, sys, io, json

WORDS = {
 "On":"켜짐","Off":"꺼짐","and":"및","Of":"of","For":"용","In":"in","At":"at","With":"with","Is":"표시","Now":"현재",
 "Color":"색","Colors":"색상","colors":"색상","Opacity":"투명도","Background":"배경","Back":"뒤","Ground":"바탕",
 "Border":"테두리","Outline":"외곽선","Text":"텍스트","Font":"폰트","Size":"크기","Width":"너비","Height":"높이",
 "Thickness":"두께","Scale":"배율","Spacing":"간격","Offset":"오프셋","Margin":"여백","Padding":"여백",
 "Shape":"모양","Roundness":"둥글기","Layout":"배치","Orientation":"방향","Direction":"방향","Position":"위치",
 "Location":"위치","Alignment":"정렬","Visibility":"표시","Visible":"표시","Hide":"숨김","Show":"표시","Display":"표시",
 "Enable":"사용","Enabled":"사용","Active":"활성","Auto":"자동","Always":"항상","Default":"기본","Custom":"사용자",
 "Header":"머리글","Table":"표","Rows":"행","Columns":"열","Row":"행","Column":"열","Cell":"칸",
 "Speed":"속도","Brake":"브레이크","Brakes":"브레이크","Braking":"브레이킹","Throttle":"스로틀","Clutch":"클러치",
 "Steering":"조향","Wheel":"휠","Gear":"기어","Fuel":"연료","Tyre":"타이어","Tyres":"타이어","Pressure":"압력",
 "Pressures":"압력","Temp":"온도","Temps":"온도","Temperature":"온도","Damage":"손상","Engine":"엔진","Rpm":"RPM",
 "Redline":"레드라인","Upshift":"업시프트","Shift":"시프트","Bar":"바","Bars":"바","Indicator":"인디케이터",
 "Radar":"레이더","Map":"맵","Circle":"서클","Track":"트랙","Lap":"랩","Laps":"랩","Sector":"섹터","Sectors":"섹터",
 "Delta":"델타","Time":"시간","Timing":"타이밍","Clock":"시계","Date":"날짜","Day":"요일","Session":"세션",
 "Race":"레이스","Races":"레이스","Qualifying":"퀄리파잉","Practice":"연습","Driver":"드라이버","Drivers":"드라이버",
 "Car":"차량","Cars":"차량","Model":"모델","Number":"번호","Name":"이름","Names":"이름","Position":"순위",
 "Ahead":"앞차","Behind":"뒤차","Opponents":"상대","Gap":"간격","Distance":"거리","Leader":"선두","Class":"클래스",
 "Rating":"레이팅","Ratings":"레이팅","Info":"정보","Information":"정보","Additional":"추가","Extra":"추가",
 "Extras":"추가","General":"일반","Other":"기타","Others":"기타","Settings":"설정","Options":"옵션","Option":"옵션",
 "Format":"형식","Mode":"모드","Type":"종류","Source":"소스","Data":"데이터","Value":"값","Range":"범위",
 "Min":"최소","Max":"최대","Minimum":"최소","Median":"중간값","Average":"평균","Averages":"평균","Total":"합계",
 "Count":"개수","Amount":"수량","Percentage":"퍼센트","Percent":"퍼센트","Percentages":"퍼센트","Ratio":"비율",
 "Factor":"계수","Multiplier":"배율","Level":"레벨","Strength":"강도","Threshold":"임계값","thresholds":"임계값",
 "Smoothing":"부드럽게","Smooth":"부드럽게","Animation":"애니메이션","Effect":"효과","Flash":"깜박임","Fill":"채움",
 "Line":"선","Lines":"선","Marker":"마커","Crosshair":"십자선","Logo":"로고","Avatar":"아바타","Image":"이미지",
 "Preview":"미리보기","Render":"렌더","Rendering":"렌더링","Quality":"품질","Refresh":"새로고침","Rate":"빈도",
 "Frequency":"빈도","Interval":"간격","interval":"간격","Buffer":"버퍼","Decimals":"소수점","Digit":"자리",
 "Digits":"자리","Units":"단위","Energy":"에너지","Power":"파워","Load":"부하","Force":"힘","Angle":"각도",
 "Acceleration":"가속도","Slip":"슬립","Traction":"트랙션","Control":"컨트롤","Controls":"컨트롤","Input":"입력",
 "Inputs":"입력","Output":"출력","Wind":"바람","Water":"수온","Exhaust":"배기","Pit":"피트","Pitstop":"피트스톱",
 "Limiter":"리미터","Stint":"스틴트","Refuel":"급유","Repair":"수리","Finish":"피니시","Start":"시작","Stop":"정지",
 "Behavior":"동작","Behaviour":"동작","Window":"창","Overlay":"오버레이","Panel":"패널","View":"보기","Dock":"도킹",
 "Undock":"도킹 해제","Chart":"차트","Trace":"트레이스","History":"기록","Live":"실시간","Profile":"프로필",
 "Links":"링크","Tag":"태그","Order":"순서","Target":"목표","Best":"최고","Fastest":"최고","Last":"마지막",
 "Current":"현재","Previous":"이전","First":"첫","Valid":"유효","Invalid":"무효","Estimated":"예상","Potential":"잠재",
 "Prediction":"예측","prediction":"예측","Warnings":"경고","Connection":"연결","Port":"포트","Token":"토큰",
 "User":"사용자","Credentials":"인증정보","Subscription":"구독","Url":"URL","Path":"경로","Save":"저장",
 "Test":"테스트","Tasks":"작업","Bench":"벤치","Seed":"시드","Light":"조명","Dark":"어두움","Darkmode":"다크모드",
 "Main":"메인","Big":"큰","Long":"긴","Short":"짧은","High":"높음","Low":"낮음","Normal":"보통","Medium":"중간",
 "Full":"전체","Solid":"단색","Fixed":"고정","Initial":"초기","Wet":"웻","Dry":"드라이","Compound":"컴파운드",
 "Suspension":"서스펜션","Front":"앞","Rear":"뒤","Center":"중앙","Family":"종류","Style":"스타일","Glow":"글로우",
 "Shadow":"그림자","Heading":"헤딩","Rotation":"회전","Dimension":"크기","Shape":"모양","Animation":"애니메이션",
 "Spotter":"스포터","Proximity":"근접","Member":"멤버","Members":"멤버","Group":"그룹","Grouping":"그룹","Field":"필드",
 "Period":"주기","Milliseconds":"밀리초","Second":"초","Length":"길이","Life":"수명","Difference":"차이","Loss":"손실",
 "Major":"주요","Minor":"보조","Split":"구간","Lapped":"랩차","Pitted":"피트","Running":"진행","Improving":"개선",
 "Multiclass":"멀티클래스","Multi":"멀티","Division":"디비전","Spectator":"관전","Admin":"관리자","Event":"이벤트",
 "Results":"결과","Progress":"진행","Created":"생성","Updated":"갱신","Viewing":"보기","Index":"인덱스",
 "Indicator":"표시기","Element":"요소","Elements":"요소","Bits":"비트","Brush":"브러시","Ring":"링","Star":"별",
 "Amplitude":"진폭","Complexity":"복잡도","Iterations":"반복","Physics":"피직스","Corner":"코너","Cube":"큐브",
 "Aileron":"에일러론","Elevator":"엘리베이터","Rudder":"러더","Flight":"비행","Helicopter":"헬리콥터",
 "Earth":"지구","Air":"공기","Ambient":"대기","Global":"글로벌","Flag":"플래그","Speech":"음성","Commands":"명령",
 "Responses":"응답","Bot":"봇","Chat":"채팅","Twitch":"트위치","Steam":"스팀","Platform":"플랫폼","Pad":"패드",
 "Joystick":"조이스틱","Joy":"조이","Stick":"스틱","Haptics":"햅틱","Feedback":"피드백","Strength":"강도",
 "Roundness":"둥글기","Setup":"셋업","Weight":"무게","Range":"범위","Difference":"차이","Title":"제목",
 "Cars":"차량","Behind":"뒤차","Counter":"카운터","Total":"합계","Show":"표시","Hide":"숨김",
}

OVERLAY_DIRS = ["Race_Element.HUD.ACC", "Race Element.HUD.Common"]

def cs_escape(s):
    # \n 은 이미 소스에서 \n(역슬래시+n) 형태 -> C# 문자열에서 그대로 개행으로 컴파일됨
    return s.replace('\\', '\\\\').replace('\\\\n', '\\n').replace('"', '\\"')

def build_desc():
    # DESC는 별도 파일에서 로드(번역 사전). 없으면 빈 dict.
    p = os.path.join(os.path.dirname(__file__), "desc_ko.json")
    if os.path.exists(p):
        return json.load(open(p, encoding="utf-8"))
    return {}

def gen_komap(root, desc):
    def lit(s):
        # 소스의 \n(두 글자)을 C# 리터럴에서 개행으로 만들기 위해 그대로 둠
        return '"' + s.replace('\\', '\\\\').replace('\\\\n','\\n').replace('"','\\"') + '"'
    lines = []
    lines.append("// 자동 생성: 한글 라벨/설명 변환 테이블")
    lines.append("using System.Collections.Generic;")
    lines.append("")
    lines.append("internal static class KoMap")
    lines.append("{")
    lines.append("    private static readonly Dictionary<string,string> WORDS = new()")
    lines.append("    {")
    for k,v in WORDS.items():
        lines.append("        [%s] = %s," % (lit(k), lit(v)))
    lines.append("    };")
    lines.append("    private static readonly Dictionary<string,string> DESC = new()")
    lines.append("    {")
    for k,v in desc.items():
        lines.append("        [%s] = %s," % (lit(k), lit(v)))
    lines.append("    };")
    lines.append("""    public static string Label(string s)
    {
        if (string.IsNullOrEmpty(s)) return s;
        var parts = s.Split(' ');
        for (int i = 0; i < parts.Length; i++)
            if (WORDS.TryGetValue(parts[i], out var k)) parts[i] = k;
        return string.Join(" ", parts);
    }
    public static string Desc(string s)
    {
        if (s != null && DESC.TryGetValue(s, out var k)) return k;
        return s;
    }
}""")
    out = os.path.join(root, "Race_Element", "KoMap.cs")
    open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return out, len(WORDS), len(desc)

PATCHES = [
    ("Race_Element/Controls/HUD/Controls/ControlFactory.cs",
     'Content = string.Concat(label.Select(x => Char.IsUpper(x) ? " " + x : x.ToString())).TrimStart(\' \'),',
     'Content = KoMap.Label(string.Concat(label.Select(x => Char.IsUpper(x) ? " " + x : x.ToString())).TrimStart(\' \')),'),
    ("Race_Element/Controls/HUD/Controls/ValueControls/EnumValueControl.cs",
     'Content = string.Concat(_names[i].Select(x => char.IsUpper(x) ? " " + x : x.ToString())).TrimStart(\' \'),',
     'Content = KoMap.Label(string.Concat(_names[i].Select(x => char.IsUpper(x) ? " " + x : x.ToString())).TrimStart(\' \')),'),
    ("Race_Element/Controls/HUD/Controls/ValueControls/BooleanValueControl.cs",
     '_label.Content = bool.Parse(_field.Value.ToString()) ? "On" : "Off";',
     '_label.Content = bool.Parse(_field.Value.ToString()) ? KoMap.Label("On") : KoMap.Label("Off");'),
    ("Race_Element/Controls/HUD/HudOptions.xaml.cs",
     'Content = $" {cga.Title}",',
     'Content = $" {KoMap.Label(cga.Title)}",'),
    ("Race_Element/Controls/HUD/HudOptions.xaml.cs",
     'Text = overlayAttribute.Description,',
     'Text = KoMap.Desc(overlayAttribute.Description),'),
    ("Race_Element/Controls/HUD/HudOptions.xaml.cs",
     'ToolTip = $"{cga.Description}",',
     'ToolTip = $"{KoMap.Desc(cga.Description)}",'),
]

def main(root="."):
    desc = build_desc()
    out, nw, nd = gen_komap(root, desc)
    print("[config_ko] KoMap.cs 생성: 단어 %d, 설명 %d" % (nw, nd))
    patched = 0
    for rel, old, new in PATCHES:
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            print("  skip(없음):", rel); continue
        s = open(p, encoding="utf-8").read()
        if new in s:
            patched += 1; continue
        if old in s:
            s = s.replace(old, new, 1)
            open(p, "w", encoding="utf-8").write(s)
            patched += 1
            print("  patched:", rel)
        else:
            print("  !! 대상 못 찾음:", rel, "::", old[:50])
    print("[config_ko] 패치 %d/%d" % (patched, len(PATCHES)))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
