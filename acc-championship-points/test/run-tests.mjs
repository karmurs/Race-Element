// index.html 안의 핵심 로직(__CORE__ 구간)을 추출해 Node에서 검증한다.
// 실행: node test/run-tests.mjs
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const html = readFileSync(join(root, "index.html"), "utf-8");
const m = /\/\*__CORE_START__\*\/([\s\S]*?)\/\*__CORE_END__\*\//.exec(html);
assert.ok(m, "index.html에서 __CORE__ 구간을 찾지 못했습니다");

const core = new Function(`${m[1]}; return {
  DEFAULT_POINTS, PRESETS, decodeResultBuffer, detectSessionType, getTrackName,
  prettyTrack, parseSession, findPoleRaceNumber, findFastestLapRaceNumber,
  computeChampionship, formatLapTime, formatTotalTime, formatGap, carName,
  findQualiFor, makerOf };`)();

let passed = 0;
function test(name, fn) {
  fn();
  passed++;
  console.log(`  ✔ ${name}`);
}

// ---------- 1. UTF-16 LE 디코딩 ----------
const raceBuf = readFileSync(join(root, "samples", "Race.json"));
const raceText = core.decodeResultBuffer(
  raceBuf.buffer.slice(raceBuf.byteOffset, raceBuf.byteOffset + raceBuf.byteLength));

test("UTF-16 LE 파일 디코딩 후 한글 이름이 깨지지 않는다", () => {
  assert.ok(raceText.includes("이태희") && raceText.includes("장혁") && raceText.includes("쏭"));
});

// ---------- 2. 세션 파싱 ----------
const race = core.parseSession(raceText, "Race.json", Date.parse("2026-06-10T21:00:00"));
test("sessionType 10 → 레이스(R)로 판별 (실제 파일엔 트랙 정보 없음)", () => {
  assert.equal(race.type, "R");
  assert.equal(core.prettyTrack(race.trackRaw), "(알 수 없는 트랙)");
});
test("leaderBoardLines 배열 순서 = 완주 순위", () => {
  assert.deepEqual(race.lines.map(l => l.raceNumber), [20, 30, 4, 7, 63]);
  assert.deepEqual(race.lines.map(l => l.name), ["이태희", "장혁", "쏭", "김민수", "Bortolotti"]);
});
test("이름 병합: teamName의 전체 이름 사용, AI는 팀명 유지", () => {
  // 플레이어: teamName '이태희' / lastName '태희' → 표시 이름 '이태희', 팀은 비움
  assert.equal(race.lines[0].name, "이태희");
  assert.equal(race.lines[0].team, "");
  // AI: teamName이 실제 팀명이면 그대로 유지
  assert.equal(race.lines[4].name, "Bortolotti");
  assert.equal(race.lines[4].team, "GRT Grasser Racing Team");
  // "팀명을 드라이버 이름으로 표시" 옵션용 원본 teamName 보존 (오프라인 포맷)
  assert.equal(race.lines[0].entryName, "이태희");
  assert.equal(race.lines[4].entryName, "GRT Grasser Racing Team");
});

const qualiBuf = readFileSync(join(root, "samples", "Qualifying.json"));
const quali = core.parseSession(
  core.decodeResultBuffer(qualiBuf.buffer.slice(qualiBuf.byteOffset, qualiBuf.byteOffset + qualiBuf.byteLength)),
  "Qualifying.json", Date.parse("2026-06-10T20:30:00"));
test("sessionType 4 → 퀄리파잉(Q)로 판별", () => assert.equal(quali.type, "Q"));

// ---------- 3. 요구사항 문서 10번 검증 케이스 ----------
test("기본 포인트(12-10-8-…) 적용: 이태희 12, 장혁 10, 쏭 8", () => {
  const { standings } = core.computeChampionship([race], { points: core.DEFAULT_POINTS });
  const by = Object.fromEntries(standings.map(e => [e.name, e.total]));
  assert.equal(by["이태희"], 12);
  assert.equal(by["장혁"], 10);
  assert.equal(by["쏭"], 8);
  assert.equal(by["김민수"], 7);    // 4위
  assert.equal(by["Bortolotti"], 6); // 5위
  assert.equal(standings[0].name, "이태희");
});

// ---------- 4. 폴 / 패스티스트랩 보너스 ----------
test("폴 보너스: 같은 트랙 퀄리 1위(#30 장혁)에게 +1", () => {
  const pole = core.findPoleRaceNumber(race, [quali]);
  assert.equal(pole, 30);
  const r = { ...race, poleRaceNumber: pole };
  const { standings } = core.computeChampionship([r], { points: core.DEFAULT_POINTS, poleBonus: 1 });
  const by = Object.fromEntries(standings.map(e => [e.name, e.total]));
  assert.equal(by["장혁"], 11);
  assert.equal(by["이태희"], 12);
});

test("패스티스트랩: 유효 베스트랩 최솟값(#30, 2147483647은 무시) +1", () => {
  assert.equal(core.findFastestLapRaceNumber(race), 30);
  const { standings } = core.computeChampionship([race], { points: core.DEFAULT_POINTS, flBonus: 1 });
  const by = Object.fromEntries(standings.map(e => [e.name, e.total]));
  assert.equal(by["장혁"], 11);
});

// ---------- 5. 여러 라운드 합산 (raceNumber 매칭, carId 무시) ----------
function mkRace(track, orderNums, names) {
  return {
    fileName: `${track}.json`, time: 0, trackRaw: track, type: "R",
    lines: orderNums.map((n, i) => ({
      raceNumber: n, name: names[n], team: "", cupCategory: 0,
      lapCount: 10, bestLap: 100000 + i, totalTime: 1000000 + i,
    })),
  };
}
const NAMES = { 20: "이태희", 30: "장혁", 4: "쏭" };

test("2라운드 합산: raceNumber 기준 누적", () => {
  const r1 = mkRace("monza", [20, 30, 4], NAMES);
  const r2 = mkRace("spa", [30, 4, 20], NAMES); // 장혁 우승
  const { standings } = core.computeChampionship([r1, r2], { points: core.DEFAULT_POINTS });
  const by = Object.fromEntries(standings.map(e => [e.name, e.total]));
  assert.equal(by["이태희"], 12 + 8);   // 1위 + 3위
  assert.equal(by["장혁"], 10 + 12);    // 2위 + 1위
  assert.equal(by["쏭"], 8 + 10);       // 3위 + 2위
  assert.equal(standings[0].name, "장혁");
});

test("동점 처리: 총점 같으면 우승수 → 2위수 카운트백", () => {
  // A: 1위+3위 (12+8=20, 우승1), B: 2위+2위 (10+10=20, 우승0)
  const r1 = mkRace("monza", [1, 2, 3], { 1: "A", 2: "B", 3: "C" });
  const r2 = mkRace("spa", [3, 2, 1], { 1: "A", 2: "B", 3: "C" });
  const { standings } = core.computeChampionship([r1, r2], { points: core.DEFAULT_POINTS });
  assert.equal(standings.find(e => e.name === "A").total, standings.find(e => e.name === "B").total);
  assert.ok(standings.findIndex(e => e.name === "A") < standings.findIndex(e => e.name === "B"),
    "우승이 있는 A가 B보다 위여야 함");
});

test("드롭 라운드: 결장(0점) 라운드가 먼저 제외된다", () => {
  const r1 = mkRace("monza", [20, 30], NAMES);
  const r2 = mkRace("spa", [30, 20], NAMES);
  const r3 = mkRace("imola", [30], NAMES); // 이태희 결장
  const { standings } = core.computeChampionship([r1, r2, r3], { points: core.DEFAULT_POINTS, dropCount: 1 });
  const lee = standings.find(e => e.name === "이태희");
  assert.equal(lee.total, 12 + 10); // 결장 라운드(0점)만 드롭
  assert.ok(lee.dropIdx.has(2));
});

// ---------- 6. 서버 덤프 포맷(sessionResult)도 읽힌다 ----------
test("서버 결과 포맷(sessionResult.leaderBoardLines) 호환", () => {
  const server = JSON.stringify({
    sessionType: "R", trackName: "spa",
    sessionResult: { leaderBoardLines: [
      { car: { raceNumber: 9, teamName: "", cupCategory: 0,
               drivers: [{ firstName: "Max", lastName: "Kim", shortName: "KIM" }] },
        timing: { bestLap: 139000, totalTime: 3600000, lapCount: 20 } },
    ]},
  });
  const s = core.parseSession(server, "260610_213000_R.json", 0);
  assert.equal(s.type, "R");
  assert.equal(s.lines[0].raceNumber, 9);
  assert.ok(s.time > 0, "파일명 타임스탬프 파싱");
});

test("랩타임 포맷", () => {
  assert.equal(core.formatLapTime(108123), "1:48.123");
  assert.equal(core.formatLapTime(2147483647), "—");
});

test("트랙 탐색: 고정 키에 없어도 파일 안의 트랙 id를 찾아낸다", () => {
  const j = JSON.stringify({
    sessionDef: { sessionType: 10, options: { weekend: { trackId: "brands_hatch_2020" } } },
    snapShot: { leaderBoardLines: [
      { car: { raceNumber: 1, teamName: "Monza Fans", cupCategory: 0,
               drivers: [{ firstName: "", lastName: "테스트" }] },
        timing: { bestLap: 1, totalTime: 1, lapCount: 1 } },
    ]},
  });
  const s = core.parseSession(j, "Race.json", 0);
  assert.equal(core.prettyTrack(s.trackRaw), "Brands Hatch");
  // 트랙 정보가 전혀 없으면 빈 값 → "(알 수 없는 트랙)" 표시
  const none = core.parseSession(JSON.stringify({
    sessionDef: { sessionType: 10 },
    snapShot: { leaderBoardLines: [
      { car: { raceNumber: 1, drivers: [{ lastName: "x" }] }, timing: { lapCount: 1 } },
    ]},
  }), "Race.json", 0);
  assert.equal(core.prettyTrack(none.trackRaw), "(알 수 없는 트랙)");
});

// ---------- 7. 차량 모델 / 갭 / 랩별 기록 ----------
test("차량 모델 매핑: carModel → 차량 이름", () => {
  assert.equal(race.lines[0].carModel, 16);
  assert.equal(core.carName(16), "Lamborghini Huracán GT3 Evo");
  assert.equal(core.carName(32), "Ferrari 296 GT3");
  assert.equal(core.carName(null), "—");
  assert.equal(core.carName(999), "Car #999");
});

test("1위와의 격차: 같은 랩=시간차, 랩 부족=+N랩", () => {
  const [p1, p2, , p4] = race.lines;
  assert.equal(core.formatGap(p1, p1), "—");
  assert.equal(core.formatGap(p1, p2), "+2.222");      // 1803456 - 1801234
  assert.equal(core.formatGap(p1, p4), "+10랩");       // 14랩 vs 4랩
});

test("랩별 기록: lapTime/flags 포맷을 carId로 드라이버에 연결", () => {
  const lee = race.lines.find(l => l.raceNumber === 20);
  assert.equal(lee.laps.length, 4);
  assert.equal(lee.laps[3].t, 108123);          // 베스트랩
  assert.deepEqual(lee.laps[3].s, [36000, 40123, 32000]); // 섹터
  assert.equal(lee.laps[0].v, true);            // flags 1024(첫 랩) = 유효
  assert.equal(lee.laps[2].v, false);           // flags 1 = 무효
  const kim = race.lines.find(l => l.raceNumber === 7);
  assert.equal(kim.laps.length, 1);
  assert.equal(kim.laps[0].v, false);           // flags 1025 = 무효
});

// ---------- 8. 통계 / 메이커 ----------
test("통계: 보너스가 꺼져 있어도 폴·TOP3·퀄리 기록 집계 (점수엔 미반영)", () => {
  const r = { ...race, poleRaceNumber: 30, qualiPos: { 30: 1, 20: 2, 4: 3 } };
  const { standings } = core.computeChampionship([r, r], { points: core.DEFAULT_POINTS });
  const jang = standings.find(e => e.name === "장혁");
  const lee = standings.find(e => e.name === "이태희");
  assert.equal(jang.total, 20);          // 폴 보너스 점수 없음 (10+10)
  assert.equal(jang.poles, 2);
  assert.equal(jang.qualiBest, 1);
  assert.equal(jang.qualiBestCount, 2);  // 1위 ×2
  assert.equal(lee.podiums, 2);
  assert.equal(lee.qualiBest, 2);
  assert.equal((lee.qualiSum / lee.qualiCount).toFixed(1), "2.0");
  assert.equal(lee.carModel, 16);
});

test("차량 메이커 매핑", () => {
  assert.equal(core.makerOf(32).code, "FER");
  assert.equal(core.makerOf(16).code, "LAM");
  assert.equal(core.makerOf(34).code, "POR");
  assert.equal(core.makerOf(999), null);
});

console.log(`\n${passed}개 테스트 모두 통과 ✅`);
