#!/usr/bin/env python3
# ============================================================
# ACC 라이브 브리지 — ACC Broadcasting UDP API → localhost HTTP
#
# 게임이 방송하는 실시간 데이터(순위/랩타임/트랙)를 받아서
# index.html이 읽을 수 있게 http://127.0.0.1:8927/state 로 제공한다.
#
# 사용법:
#   1) 문서\Assetto Corsa Competizione\Config\broadcasting.json 을 열어
#      {"udpListenerPort": 9000, "connectionPassword": "asd", ...} 로 설정
#      (파일 수정 후 게임 재시작)
#   2) python live-bridge.py   (옵션: --password asd --acc-port 9000 --http-port 8927)
#   3) index.html 의 "라이브 연결" 버튼 클릭
#
# 표준 라이브러리만 사용 — 설치할 패키지 없음 (Python 3.8+)
# ============================================================
import argparse
import json
import socket
import struct
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ---------- ksBroadcastingNetwork 프로토콜 ----------
PROTOCOL_VERSION = 4

OUT_REGISTER = 1
OUT_UNREGISTER = 9
OUT_REQUEST_ENTRY_LIST = 10
OUT_REQUEST_TRACK_DATA = 11

IN_REGISTRATION_RESULT = 1
IN_REALTIME_UPDATE = 2
IN_REALTIME_CAR_UPDATE = 3
IN_ENTRY_LIST = 4
IN_TRACK_DATA = 5
IN_ENTRY_LIST_CAR = 6
IN_BROADCASTING_EVENT = 7

SESSION_TYPES = {0: "연습", 4: "퀄리파잉", 9: "슈퍼폴", 10: "레이스", 11: "핫랩"}
PHASES = {0: "-", 1: "시작 중", 2: "포메이션 전", 3: "포메이션 랩",
          4: "세션 전", 5: "진행 중", 6: "세션 종료", 7: "세션 후", 8: "결과 화면"}
INVALID_MS = 2147483647


class Reader:
    def __init__(self, data):
        self.d = data
        self.p = 0

    def take(self, n):
        v = self.d[self.p:self.p + n]
        if len(v) < n:
            raise EOFError("메시지가 잘렸습니다")
        self.p += n
        return v

    def u8(self): return self.take(1)[0]
    def i8(self): return struct.unpack("<b", self.take(1))[0]
    def u16(self): return struct.unpack("<H", self.take(2))[0]
    def i32(self): return struct.unpack("<i", self.take(4))[0]
    def f32(self): return struct.unpack("<f", self.take(4))[0]

    def s(self):
        n = self.u16()
        return self.take(n).decode("utf-8", "replace")

    def lap(self):
        ms = self.i32()
        self.u16(); self.u16()              # carIndex, driverIndex
        for _ in range(self.u8()):          # splits
            self.i32()
        self.u8(); self.u8(); self.u8(); self.u8()  # invalid/validForBest/out/in
        return None if ms <= 0 or ms >= INVALID_MS else ms


def w_str(s):
    b = s.encode("utf-8")
    return struct.pack("<H", len(b)) + b


def register_msg(password, update_ms):
    return (bytes([OUT_REGISTER, PROTOCOL_VERSION])
            + w_str("ACC Championship Points")
            + w_str(password)
            + struct.pack("<i", update_ms)
            + w_str(""))


class Bridge:
    def __init__(self, acc_host, acc_port, password, update_ms):
        self.addr = (acc_host, acc_port)
        self.password = password
        self.update_ms = update_ms
        self.sock = None
        self.conn_id = None
        self.lock = threading.Lock()
        self.cars = {}        # carIndex -> entry/실시간 정보
        self.session = {"connected": False, "track": "", "sessionType": "",
                        "phase": "", "timeRemainMs": None, "updatedAt": 0}
        self._last_entry_req = 0.0
        self._last_rx = 0.0

    # ---------- 수신 처리 ----------
    def handle(self, data):
        r = Reader(data)
        t = r.u8()
        if t == IN_REGISTRATION_RESULT:
            self.conn_id = r.i32()
            ok, readonly = r.u8(), r.u8()
            err = r.s()
            if ok:
                print(f"[브리지] ACC 연결 성공 (connectionId={self.conn_id})")
                with self.lock:
                    self.session["connected"] = True
                self.request(OUT_REQUEST_ENTRY_LIST)
                self.request(OUT_REQUEST_TRACK_DATA)
            else:
                print(f"[브리지] 등록 실패: {err} — broadcasting.json의 비밀번호를 확인하세요")
        elif t == IN_REALTIME_UPDATE:
            r.u16(); r.u16()                      # eventIndex, sessionIndex
            stype, phase = r.u8(), r.u8()
            stime, sendtime = r.f32(), r.f32()
            with self.lock:
                self.session["sessionType"] = SESSION_TYPES.get(stype, f"세션 {stype}")
                self.session["phase"] = PHASES.get(phase, str(phase))
                self.session["timeRemainMs"] = max(0, int(sendtime - stime))
                self.session["updatedAt"] = time.time()
        elif t == IN_REALTIME_CAR_UPDATE:
            idx = r.u16()
            r.u16(); r.u8(); r.i8()               # driverIndex, driverCount, gear
            r.f32(); r.f32(); r.f32(); r.u8()     # 좌표/방향/위치종류
            kmh = r.u16()
            pos = r.u16()
            r.u16(); r.u16(); r.f32()             # cupPos, trackPos, spline
            laps = r.u16()
            delta = r.i32()
            best, last = r.lap(), r.lap()
            with self.lock:
                car = self.cars.get(idx)
                if car is None:
                    # 엔트리 정보가 아직 없는 차 → 엔트리 리스트 재요청 (1초 스로틀)
                    if time.time() - self._last_entry_req > 1.0:
                        self._last_entry_req = time.time()
                        self.request(OUT_REQUEST_ENTRY_LIST)
                    car = self.cars.setdefault(idx, {})
                car.update(position=pos, laps=laps, kmh=kmh, delta=delta,
                           bestLap=best, lastLap=last)
        elif t == IN_ENTRY_LIST:
            r.i32()
            count = r.u16()
            known = {r.u16() for _ in range(count)}
            with self.lock:
                for idx in list(self.cars):       # 사라진 차 제거
                    if idx not in known:
                        del self.cars[idx]
        elif t == IN_ENTRY_LIST_CAR:
            idx = r.u16()
            model = r.u8()
            team = r.s()
            num = r.i32()
            cup = r.u8()
            r.u8()                                 # currentDriverIndex
            drivers = []
            for _ in range(r.u8()):
                first, lastn, short = r.s(), r.s(), r.s()
                r.u8(); r.u16()                    # category, nationality
                drivers.append({"firstName": first, "lastName": lastn, "shortName": short})
            with self.lock:
                self.cars.setdefault(idx, {}).update(
                    raceNumber=num, carModel=model, cupCategory=cup,
                    teamName=team, drivers=drivers)
        elif t == IN_TRACK_DATA:
            r.i32()
            track = r.s()
            with self.lock:
                self.session["track"] = track
            print(f"[브리지] 트랙: {track}")

    def request(self, msg_type):
        if self.conn_id is not None and self.sock:
            self.sock.sendto(bytes([msg_type]) + struct.pack("<i", self.conn_id), self.addr)

    # ---------- 연결 루프 ----------
    def run(self):
        while True:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock.settimeout(3.0)
                self.sock.sendto(register_msg(self.password, self.update_ms), self.addr)
                print(f"[브리지] ACC({self.addr[0]}:{self.addr[1]})에 등록 요청…")
                self._last_rx = time.time()
                while True:
                    try:
                        data, _ = self.sock.recvfrom(65535)
                        self._last_rx = time.time()
                        try:
                            self.handle(data)
                        except EOFError:
                            pass
                    except socket.timeout:
                        if time.time() - self._last_rx > 6.0:
                            raise ConnectionError("응답 없음")
            except Exception as e:
                with self.lock:
                    self.session["connected"] = False
                    self.cars.clear()
                self.conn_id = None
                print(f"[브리지] 연결 끊김({e}) — 5초 후 재시도 (게임이 켜져 있는지, "
                      f"broadcasting.json 설정을 확인하세요)")
                try:
                    self.sock.close()
                except Exception:
                    pass
                time.sleep(5)

    # ---------- HTTP 응답용 스냅샷 ----------
    def snapshot(self):
        with self.lock:
            cars = [dict(c) for c in self.cars.values() if c.get("raceNumber") is not None]
            sess = dict(self.session)
        cars.sort(key=lambda c: c.get("position") or 9999)
        sess["cars"] = cars
        return sess


def serve_http(bridge, port):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.split("?")[0] != "/state":
                self.send_response(404)
                self.end_headers()
                return
            body = json.dumps(bridge.snapshot(), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass

    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"[브리지] 앱 연결 대기: http://127.0.0.1:{port}/state")
    httpd.serve_forever()


def main():
    ap = argparse.ArgumentParser(description="ACC 라이브 브리지")
    ap.add_argument("--acc-host", default="127.0.0.1")
    ap.add_argument("--acc-port", type=int, default=9000,
                    help="broadcasting.json의 udpListenerPort (기본 9000)")
    ap.add_argument("--password", default="asd",
                    help="broadcasting.json의 connectionPassword (기본 asd)")
    ap.add_argument("--http-port", type=int, default=8927)
    ap.add_argument("--update-ms", type=int, default=250)
    args = ap.parse_args()

    bridge = Bridge(args.acc_host, args.acc_port, args.password, args.update_ms)
    threading.Thread(target=bridge.run, daemon=True).start()
    try:
        serve_http(bridge, args.http_port)
    except KeyboardInterrupt:
        print("\n[브리지] 종료")


if __name__ == "__main__":
    main()
