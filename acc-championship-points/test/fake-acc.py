#!/usr/bin/env python3
# live-bridge.py 테스트용 가짜 ACC 방송 서버.
# ksBroadcastingNetwork 인바운드 메시지를 실제 포맷대로 만들어 보낸다.
# 실행: python test/fake-acc.py [포트]
import socket
import struct
import sys
import threading
import time

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9000


def s(v):
    b = v.encode("utf-8")
    return struct.pack("<H", len(b)) + b


def lap(ms):
    # laptime i32, carIndex u16, driverIndex u16, splitCount u8(=3)+splits, 유효성 4바이트
    return (struct.pack("<iHHB", ms, 0, 0, 3) + struct.pack("<iii", ms // 3, ms // 3, ms // 3)
            + bytes([0, 1, 0, 0]))


def registration_result():
    return bytes([1]) + struct.pack("<i", 7) + bytes([1, 0]) + s("")


def entry_list():
    return bytes([4]) + struct.pack("<i", 7) + struct.pack("<H", 2) + struct.pack("<HH", 0, 1)


def entry_car(idx, num, model, team, last, short):
    return (bytes([6]) + struct.pack("<H", idx) + bytes([model]) + s(team)
            + struct.pack("<i", num) + bytes([0, 0, 1])
            + s("") + s(last) + s(short) + bytes([0]) + struct.pack("<H", 0))


def track_data():
    return bytes([5]) + struct.pack("<i", 7) + s("Misano") + struct.pack("<ii", 5, 4226)


def realtime_update():
    return (bytes([2]) + struct.pack("<HH", 0, 2) + bytes([10, 5])
            + struct.pack("<ff", 600000.0, 1200000.0))


def car_update(idx, pos, laps, best, last):
    return (bytes([3]) + struct.pack("<HHBb", idx, 0, 1, 3)
            + struct.pack("<fffB", 0.0, 0.0, 0.0, 0) + struct.pack("<HHHH", 180, pos, pos, pos)
            + struct.pack("<f", 0.5) + struct.pack("<Hi", laps, 1234)
            + lap(best) + lap(last) + lap(last))


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", PORT))
    print(f"[fake-acc] 대기 중: udp://127.0.0.1:{PORT}", flush=True)
    client = [None]

    def stream():
        while True:
            time.sleep(0.2)
            if client[0]:
                sock.sendto(realtime_update(), client[0])
                sock.sendto(car_update(0, 1, 9, 89307, 89925), client[0])
                sock.sendto(car_update(1, 2, 9, 90555, 90600), client[0])

    threading.Thread(target=stream, daemon=True).start()
    while True:
        data, addr = sock.recvfrom(65535)
        t = data[0]
        if t == 1:  # 등록
            client[0] = addr
            sock.sendto(registration_result(), addr)
            print("[fake-acc] 클라이언트 등록됨", flush=True)
        elif t == 10:  # 엔트리 리스트
            sock.sendto(entry_list(), addr)
            sock.sendto(entry_car(0, 20, 16, "이태희", "태희", "TeaHee"), addr)
            sock.sendto(entry_car(1, 30, 19, "장혁", "장혁", "Bapps"), addr)
        elif t == 11:  # 트랙 데이터
            sock.sendto(track_data(), addr)


if __name__ == "__main__":
    main()
