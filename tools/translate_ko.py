# -*- coding: utf-8 -*-
"""
Race Element 한글 패치 스크립트
빌드 직전에 실행되어 XAML(UI) 안의 영어 문자열을 한국어로 치환한다.
바인딩({Binding ...})과 코드 식별자는 건드리지 않는다.
"""
import re, glob, sys, os

TR = {
    "Add": "추가", "Cars": "차량", "Data": "데이터", "Edit": "편집", "Game": "게임",
    "Info": "정보", "Play": "재생", "Save": "저장", "Tags": "태그", "Close": "닫기",
    "Drive": "주행", "Games": "게임", "Guide": "가이드", "Hours": "시간", "Local": "로컬",
    "Reset": "초기화", "Teams": "팀", "Tools": "도구", "- Data": "- 데이터", "- HUD": "- HUD",
    "- Tools": "- 도구", "- Setups": "- 셋업", "- Liveries": "- 리버리", "Browse": "찾아보기",
    "Camera": "카메라", "Cancel": "취소", "Guides": "가이드", "Import": "가져오기", "Setups": "셋업",
    "Add tag": "태그 추가", "Add tags": "태그 추가", "Compare": "비교", "Current": "현재",
    "Laptime": "랩타임", "License": "라이선스", "Minutes": "분", "Pitwall": "피트월",
    "Refresh": "새로고침", "Setup 1": "셋업 1", "Setup 2": "셋업 2", "Sponsor": "후원",
    "Browser:": "브라우저:", "Creator:": "생성기:", "Hardware": "하드웨어", "Liveries": "리버리",
    "Position": "위치", "Settings": "설정", "Car Model": "차량 모델", "Changelog": "변경 내역",
    "Exporter:": "내보내기:", "Importer:": "가져오기:", "Password:": "비밀번호:",
    "Race Data": "주행 데이터", "Scroll Me": "스크롤하세요", "Software:": "소프트웨어:",
    "Streaming": "스트리밍", "Open Setup": "셋업 열기", "Server IP:": "서버 IP:",
    "Serverlist": "서버 목록", "Team Name*": "팀 이름*", "Add new Tag": "새 태그 추가",
    "Add new tag": "새 태그 추가", "Car Number*": "차량 번호*", "Copy Spline": "스플라인 복사",
    "Driver Name": "드라이버 이름", "Include DDS": "DDS 포함", "Instruction": "안내",
    "Nationality": "국적", "Contributors": "기여자", "Display Name": "표시 이름",
    "Fuel Per Lap": "랩당 연료", "Select a car": "차량 선택", "Server Port:": "서버 포트:",
    "Configuration": "구성", "DDS Generator": "DDS 생성기", "Export as zip": "zip으로 내보내기",
    "- View setups.": "- 셋업 보기.", "Race Weekends:": "레이스 위켄드:", "Select a track": "트랙 선택",
    "Setup Importer": "셋업 가져오기", "Fuel Calculator": "연료 계산기", "Import Liveries": "리버리 가져오기",
    "Show fps widget": "FPS 위젯 표시", "Test Connection": "연결 테스트", "Export Skin Pack": "스킨 팩 내보내기",
    "Fuel calculator:": "연료 계산기:", "Start generating": "생성 시작", "Unlisted Servers": "비공개 서버",
    "Add Tag to livery": "리버리에 태그 추가", "Create New Livery": "새 리버리 만들기",
    "Imported liveries": "가져온 리버리", "Lap and Fuel Data": "랩 및 연료 데이터",
    "Update to 0.1.7.6": "0.1.7.6 업데이트", "Enable Setup Hider": "셋업 숨김 사용",
    "Generate DDS Files": "DDS 파일 생성", "Opens the Info Tab": "정보 탭 열기",
    "Show rating widget": "레이팅 위젯 표시", "Custom Livery Name*": "커스텀 리버리 이름*",
    "Load data from Game": "게임에서 데이터 불러오기", "Support Development": "개발 지원",
    "Race Element Website": "Race Element 웹사이트", "Customizable Overlays": "커스터마이즈 가능한 오버레이",
    "Recorded session data": "기록된 세션 데이터", "Reset Livery Settings": "리버리 설정 초기화",
    "Setup Hider Activated": "셋업 숨김 활성화됨", "Supported wheelbases:": "지원 휠베이스:",
    "Reset Helicam settings": "헬리캠 설정 초기화", "Yes, Delete the livery": "예, 리버리 삭제",
    "- Generate dds_1 files.": "- dds_1 파일 생성.", "Add new unlisted server": "새 비공개 서버 추가",
    "Adjust the helicam FOV.": "헬리캠 FOV 조절.", "Enable auto save replay": "리플레이 자동 저장 사용",
    "Open Race Element Folder": "Race Element 폴더 열기", "Show server stats widget": "서버 통계 위젯 표시",
    "Adjust the helicam distance.": "헬리캠 거리 조절.", "Automatic Steering Hard Lock": "자동 스티어링 하드 락",
    "View and Compare your Setups": "셋업 보기 및 비교", "Telemetry: Extended Data Herz": "텔레메트리: 확장 데이터 Hz",
    "- Start your creative journey.": "- 창작 여정을 시작하세요.", "Filter HUDs based on category.": "카테고리별로 HUD 필터링.",
    "Select items in the above list": "위 목록에서 항목 선택", "Automatic Replay Save Activated": "자동 리플레이 저장 활성화됨",
    "Fill out details for new livery": "새 리버리 정보를 입력하세요", "Guides/Tutorials on the website": "웹사이트의 가이드/튜토리얼",
    "- Right click skins to tag them.": "- 스킨을 우클릭하여 태그를 지정하세요.", "ACC Steering locks, Lock to Lock": "ACC 스티어링 락 (락 투 락)",
    "Automatic Steering Lock Activated": "자동 스티어링 락 활성화됨", "Provides Solutions for Simulators": "시뮬레이터를 위한 솔루션 제공",
    "DDS(DirectDraw Surface) Generator:": "DDS(DirectDraw Surface) 생성기:", "- Supported archives: 7z, rar, zip.": "- 지원 압축 형식: 7z, rar, zip.",
    "Discord - (Guides/Help/Suggestions)": "Discord - (가이드/도움말/제안)", "Enable Automatic Steering Hard Lock": "자동 스티어링 하드 락 사용",
    "Check whether wheelbase is supported": "휠베이스 지원 여부 확인", "Create custom livery file and folder": "커스텀 리버리 파일 및 폴더 생성",
    "Minimize Race Element to system tray": "Race Element를 시스템 트레이로 최소화", "- Right click skins to open json file.": "- 스킨을 우클릭하여 json 파일을 여세요.",
    "Apply Settings (Restarts Race Element)": "설정 적용 (Race Element 재시작)", "Centers the HUD on the primary monitor": "기본 모니터 중앙에 HUD 배치",
    "OBS: Version 28 or higher is required.": "OBS: 버전 28 이상이 필요합니다.", "Telemetry: Record Extended Data (BETA)": "텔레메트리: 확장 데이터 기록 (BETA)",
    "Adjust the helicam target max distance.": "헬리캠 타깃 최대 거리 조절.", "DDS Generator: generate 4K dds_1 files.": "DDS 생성기: 4K dds_1 파일 생성.",
    "- Right click skins to add to skin pack.": "- 스킨을 우클릭하여 스킨 팩에 추가하세요.", "Adjust settings for the in-game ACC HUD.": "게임 내 ACC HUD 설정 조절.",
    "Displays or Hides the in-game fps widget.": "게임 내 FPS 위젯을 표시하거나 숨깁니다.", "Add any Source to your Active Scene called:": "활성 장면에 다음 이름의 소스를 추가하세요:",
    "- Right click skins to browse livery folder.": "- 스킨을 우클릭하여 리버리 폴더를 여세요.", "Are you sure you want to delete this livery?": "이 리버리를 삭제하시겠습니까?",
    "- Right click cars/teams to add to skin pack.": "- 차량/팀을 우클릭하여 스킨 팩에 추가하세요.", "- Select multiple archives to import at once.": "- 여러 압축 파일을 선택해 한 번에 가져오세요.",
    "Adjust the helicam target interpolation time.": "헬리캠 타깃 보간 시간 조절.", "Right click setups in the browser to add them": "브라우저에서 셋업을 우클릭하여 추가하세요",
    "Start Race Element before you join a session.": "세션에 참가하기 전에 Race Element를 실행하세요.", "- Scrolling the sliders will change their value.": "- 슬라이더를 스크롤하면 값이 변경됩니다.",
    "Automatically switch to supported running games.": "실행 중인 지원 게임으로 자동 전환합니다.", "In ACC, set the steering rotation in-game to 10.": "ACC에서 게임 내 스티어링 회전을 10으로 설정하세요.",
    "View, Create, Import and Export Custom Liveries.": "커스텀 리버리 보기, 생성, 가져오기 및 내보내기.", "- Select a Race Weekend and go to the Current tab.": "- 레이스 위켄드를 선택한 뒤 현재 탭으로 이동하세요.",
    "Adjust the amount of cars targeted by the helicam.": "헬리캠이 추적하는 차량 수를 조절합니다.", "This allows you to modify livery settings for acc.": "ACC의 리버리 설정을 변경할 수 있습니다.",
    "- Right click skins to delete (or press Delete key).": "- 스킨을 우클릭하여 삭제하세요 (또는 Delete 키).", "Allow ACC to generate DDS files with higher quality.": "ACC가 더 높은 품질의 DDS 파일을 생성하도록 허용합니다.",
    "- Once you add 1 skin to skin pack a new panel opens.": "- 스킨 팩에 스킨을 1개 추가하면 새 패널이 열립니다.", "Migrate ACC HUD settings(pre 2.0) to Race Element 2.0": "ACC HUD 설정(2.0 이전)을 Race Element 2.0으로 이전",
    "- Button is visible in viewer when dds_1 do not exist.": "- dds_1 파일이 없을 때 뷰어에 버튼이 표시됩니다.", "- Mouse Middle Click or Ctrl + Home: Toggle move mode.": "- 마우스 가운데 클릭 또는 Ctrl + Home: 이동 모드 전환.",
    "Settings for Race Element, Hardware, Streaming and ACC": "Race Element, 하드웨어, 스트리밍 및 ACC 설정", "Warning: the livery files will be deleted permanently!": "경고: 리버리 파일이 영구적으로 삭제됩니다!",
    "- Open car/track directories quickly by right clicking.": "- 우클릭으로 차량/트랙 폴더를 빠르게 엽니다.", "Select a different game. This might take a few seconds.": "다른 게임을 선택하세요. 몇 초 걸릴 수 있습니다.",
    "Create all the files and folders for a new custom livery": "새 커스텀 리버리를 위한 모든 파일과 폴더를 생성합니다", "Streamlabs: Use most recent version, only works locally.": "Streamlabs: 최신 버전을 사용하세요. 로컬에서만 작동합니다.",
    "This will be used for the name of the custom skin folder": "커스텀 스킨 폴더 이름으로 사용됩니다", "- Compare setups, right click in the browser to add them.": "- 셋업을 비교하려면 브라우저에서 우클릭하여 추가하세요.",
    "- Right click the setup browser tab to refresh the setups.": "- 셋업 브라우저 탭을 우클릭하여 셋업을 새로고침하세요.", "When disabled the exporter will not include the dds files.": "비활성화하면 내보내기에 dds 파일이 포함되지 않습니다.",
    "- Click items in the exporter to remove them from the pack.": "- 내보내기에서 항목을 클릭하면 팩에서 제거됩니다.", "This allows you to modify external camera settings for acc.": "ACC의 외부 카메라 설정을 변경할 수 있습니다.",
    "- HUDs will become visible as soon as the engine is running.": "- 엔진이 작동하면 HUD가 표시됩니다.", "This will check and generate DDS files for all liveries above.": "위의 모든 리버리에 대해 DDS 파일을 확인하고 생성합니다.",
    "- Click the Create livery button to create a new Custom Livery.": "- 리버리 생성 버튼을 클릭하여 새 커스텀 리버리를 만드세요.", "- Drag and Drop setup json files on top of the app to import them.": "- 셋업 json 파일을 앱 위로 드래그 앤 드롭하여 가져오세요.",
    "- Race weekend databases are saved in %appdata%/Race Element/Data.": "- 레이스 위켄드 데이터베이스는 %appdata%/Race Element/Data에 저장됩니다.", "During DDS generation, finishes the current livery and then stops.": "DDS 생성 중 현재 리버리를 마친 뒤 중지합니다.",
    "Generate the _1 dds files so the game doesn't have to do it for you.": "게임이 직접 생성하지 않도록 _1 dds 파일을 생성합니다.", "- Fill out the required fields and the selected livery will be ready.": "- 필수 항목을 입력하면 선택한 리버리가 준비됩니다.",
    "- Mouse Right Click: (De)Activate HUD. (you can also click the title)": "- 마우스 우클릭: HUD 활성화/비활성화. (제목을 클릭해도 됩니다)", "Toggle Movement mode | Mouse: Scroll Click | Keyboard: Control + Home": "이동 모드 전환 | 마우스: 스크롤 클릭 | 키보드: Control + Home",
    "- Reload the Local race weekends list by re-opening the Telemetry tab.": "- 텔레메트리 탭을 다시 열어 로컬 레이스 위켄드 목록을 새로고침하세요.", "- Bulk generate dds_1 files, click the button below the livery browser.": "- dds_1 파일을 일괄 생성하려면 리버리 브라우저 아래 버튼을 클릭하세요.",
    "Race Element will automatically set the correct rotation for every car.": "Race Element가 모든 차량의 올바른 회전값을 자동으로 설정합니다.", "Allow ACC to generate DDS files (Disable when working on custom liveries)": "ACC가 DDS 파일을 생성하도록 허용 (커스텀 리버리 작업 시 비활성화)",
    "Displays or Hides the in-game rating widget in the right top of the screen.": "화면 우측 상단의 게임 내 레이팅 위젯을 표시하거나 숨깁니다.", "- Drag and drop .rwdb(Race weekend databases) ontop of the app to view them.": "- .rwdb(레이스 위켄드 데이터베이스)를 앱 위로 드래그 앤 드롭하여 확인하세요.",
    "- Import archives, supports multi-select and archives with multiple liveries.": "- 압축 파일 가져오기, 다중 선택과 여러 리버리가 든 압축을 지원합니다.", "- When the game is in Fullscreen mode, hit F11 twice to display the overlays.": "- 게임이 전체화면 모드일 때 F11을 두 번 눌러 오버레이를 표시하세요.",
    "- Activate the HUDs you want to see, activated HUDs will be green in the list.": "- 보고 싶은 HUD를 활성화하세요. 활성화된 HUD는 목록에서 녹색으로 표시됩니다.", "- Displays each session of a Race Weekend recorded when Race Element is running.": "- Race Element 실행 중 기록된 레이스 위켄드의 각 세션을 표시합니다.",
    "This is a preview, the scaling will become visible once you Activate the overlay.": "미리보기입니다. 오버레이를 활성화하면 실제 크기가 적용됩니다.", "Displays or Hides the in-game server stats widget in the right bottom of the screen.": "화면 우측 하단의 게임 내 서버 통계 위젯을 표시하거나 숨깁니다.",
    "Reset either the HUD position or the HUD Configuration for the currently viewed HUD.": "현재 보고 있는 HUD의 위치 또는 구성을 초기화합니다.", "- Export with or without dds_1 files.": "- dds_1 파일 포함 여부를 선택해 내보냅니다.",
    "- Exports as zip.": "- zip으로 내보냅니다.", "This allows you to save and activate unlisted server ips for lan discovery in the game.": "게임 내 LAN 검색을 위해 비공개 서버 IP를 저장하고 활성화할 수 있습니다.",
    "Click the correct track and the setup will automatically be copied in the correct folder.": "올바른 트랙을 클릭하면 셋업이 해당 폴더에 자동으로 복사됩니다.", "If you are in a session, your best lap time and fuel per lap will be automatically filled in.": "세션 중이면 최고 랩타임과 랩당 연료가 자동으로 입력됩니다.",
    "- Right click the laptime table to copy the lap data to clipboard in CSV format (comma seperated).": "- 랩타임 표를 우클릭하면 랩 데이터를 CSV 형식(쉼표 구분)으로 클립보드에 복사합니다.", "- Drag and Drop proper .zip/7.zip/.rar skin packs or single liveries on top of the app to import them.": "- 올바른 .zip/7.zip/.rar 스킨 팩 또는 단일 리버리를 앱 위로 드래그 앤 드롭하여 가져오세요.",
    "Recommended is to generate dds _1 files for driving with Race Element in the Liveries tab in the main menu.": "Race Element로 주행할 때는 메인 메뉴의 리버리 탭에서 dds _1 파일을 생성하는 것을 권장합니다.", "If any of the supported games is running and Race Element isn't set to this game, it will automatically switch for you.": "지원되는 게임이 실행 중이고 Race Element가 해당 게임으로 설정되어 있지 않으면 자동으로 전환합니다.",
    "- Simple fuel calculator, enter duration, fuel per lap and lap-time. Has button to load these from your active in-game session.": "- 간단한 연료 계산기입니다. 주행 시간, 랩당 연료, 랩타임을 입력하세요. 게임 세션에서 값을 불러오는 버튼이 있습니다.", "- When you open the Setups tab during a session, the correct car and track combo leaf in the tree will automatically be opened.": "- 세션 중 셋업 탭을 열면 해당 차량과 트랙 조합 항목이 트리에서 자동으로 열립니다.",
    "Add a Source in your Scene called SetupHider. ACC Mananger will automatically show and hide this based on the setup menu visibility.": "장면에 SetupHider라는 소스를 추가하세요. ACC 매니저가 셋업 메뉴 표시 여부에 따라 자동으로 표시/숨김 처리합니다.", "Toggles Always Visible. By default HUDs become visible once the engine is running( unless a HUD Setting creates different behavior).": "항상 표시를 전환합니다. 기본적으로 HUD는 엔진이 작동하면 표시됩니다(HUD 설정이 다른 동작을 만들지 않는 한).",
    "Usually dds_1 files are downscaled to 2K, this forces it to be 4k. Useful if you want to make screenshots of your custom livery whilst driving.": "일반적으로 dds_1 파일은 2K로 축소되지만, 이 옵션은 4K로 강제합니다. 주행 중 커스텀 리버리 스크린샷을 찍고 싶을 때 유용합니다.", "If you updated the app from version 1.X to 2 or higher, you will need to migrate the HUD settings for ACC. This Button automatically does it for you and restarts the app.": "앱을 1.X에서 2 이상으로 업데이트한 경우 ACC HUD 설정을 이전해야 합니다. 이 버튼이 자동으로 처리하고 앱을 재시작합니다.",
    "ACC usually when a custom livery doesn't contain the dds files for either showroom or race lobby starts generating them, this option disables it so you can use the showroom to check out your custom livery whilst working on it.": "ACC는 보통 커스텀 리버리에 쇼룸이나 레이스 로비용 dds 파일이 없으면 생성을 시작하는데, 이 옵션은 그것을 비활성화하여 작업 중에도 쇼룸에서 커스텀 리버리를 확인할 수 있게 합니다.",
}

ATTRS = ("Text", "Content", "Header", "ToolTip", "Title", "Watermark", "Description")
count = 0

def _swap(val):
    core = val.strip()
    if core in TR:
        lead = val[:len(val) - len(val.lstrip())]
        trail = val[len(val.rstrip()):]
        return lead + TR[core] + trail
    return None

def repl_attr(m):
    global count
    new = _swap(m.group(2))
    if new is not None:
        count += 1
        return m.group(1) + new + m.group(3)
    return m.group(0)

def repl_inner(m):
    global count
    new = _swap(m.group(2))
    if new is not None:
        count += 1
        return m.group(1) + new + m.group(3)
    return m.group(0)

def main(root):
    files = glob.glob(os.path.join(root, "**", "*.xaml"), recursive=True)
    attr_re = re.compile(r'(\b(?:' + '|'.join(ATTRS) + r')=")([^"{}]*)(")')
    inner_re = re.compile(r'(>)([^<>{}]+)(<)')
    for f in files:
        s = open(f, encoding="utf-8").read()
        s2 = inner_re.sub(repl_inner, attr_re.sub(repl_attr, s))
        if s2 != s:
            open(f, "w", encoding="utf-8").write(s2)
    # 한글 글리프가 없는 Conthrax 폰트에 한글 폴백(맑은 고딕)을 추가
    app = os.path.join(root, "App.xaml")
    if os.path.exists(app):
        a = open(app, encoding="utf-8").read()
        old = "./Fonts/#Conthrax Sb</FontFamily>"
        new = "./Fonts/#Conthrax Sb, Malgun Gothic, Malgun Gothic Semilight</FontFamily>"
        if old in a and "Malgun Gothic" not in a:
            open(app, "w", encoding="utf-8").write(a.replace(old, new))
            print("[translate_ko] App.xaml: Conthrax 폰트에 한글 폴백 추가")

    print("[translate_ko] %d strings replaced (checked %d xaml files)" % (count, len(files)))
    return 0

if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    sys.exit(main(root))
