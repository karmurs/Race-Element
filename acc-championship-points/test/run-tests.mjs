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
  computeChampionship, formatLapTime, formatTotalTime };`)();

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
test("sessionType 10 → 레이스(R)로 판별", () => {
  assert.equal(race.type, "R");
  assert.equal(core.prettyTrack(race.trackRaw), "Monza");
});
test("leaderBoardLines 배열 순서 = 완주 순위", () => {
  assert.deepEqual(race.lines.map(l => l.raceNumber), [20, 30, 4, 7]);
  assert.deepEqual(race.lines.map(l => l.name), ["이태희", "장혁", "쏭", "김민수"]);
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
  assert.equal(by["김민수"], 7); // 4위
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

console.log(`\n${passed}개 테스트 모두 통과 ✅`);
