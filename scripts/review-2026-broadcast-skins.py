"""Read the skin introduction cards in 2026 MSI and Worlds game VODs.

Run with:
  uv run --python 3.13 --with yt-dlp --with rapidocr-onnxruntime \
    --with opencv-python --with openpyxl --with imageio-ffmpeg \
    python scripts/review-2026-broadcast-skins.py

The script only records names that match the player's champion and the event's
patch lookup. Every game gets a review-status.csv row, including games whose
broadcast has no readable skin introduction card.
"""

import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from datetime import datetime, timezone
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
import re
import subprocess
import threading

import cv2
import imageio_ffmpeg
import numpy as np
from openpyxl import load_workbook
from rapidocr_onnxruntime import RapidOCR
import yt_dlp


ROOT = Path(__file__).resolve().parents[1]
DIRECTORIES = {
    "msi": ROOT / "data/msi/2026-all-stages",
    "worlds": ROOT / "data/worlds/2026-main-event",
}
EVIDENCE_FIELDS = ["game_id", "player", "champion_id", "skin", "chroma", "video_time_seconds", "source_url"]
STATUS_FIELDS = ["game_id", "youtube_url", "status", "picks_recorded", "intro_time_seconds", "detail"]
INDEX_FIELDS = ["game_id", "youtube_url", "video_time_seconds", "method", "detail"]
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
THREAD = threading.local()


def normalized(value):
    return re.sub(r"[^a-z0-9]", "", value.lower())


def similarity(left, right):
    return SequenceMatcher(None, normalized(left), normalized(right)).ratio()


def read_csv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, fields, rows):
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def catalog(directory, event):
    workbook = load_workbook(directory / f"{event}-2026-skin-entry.xlsx", read_only=True)
    options = defaultdict(list)
    for champion, _, skin, *_ in list(workbook["Skin lookup"].values)[1:]:
        options[champion].append((skin, ""))
    for _, champion, skin, chroma, *_ in list(workbook["Chroma lookup"].values)[1:]:
        if chroma != "default":
            options[champion].append((skin, chroma))
    return options


@lru_cache(maxsize=128)
def video_info(url):
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "skip_download": True}) as youtube:
        info = youtube.extract_info(url, download=False)
    formats = [fmt for fmt in info["formats"] if fmt.get("vcodec") != "none" and fmt.get("protocol") == "https"]
    chosen = next((fmt for fmt in formats if fmt["format_id"] == "298"), None)
    if not chosen:
        chosen = max((fmt for fmt in formats if fmt.get("height") and fmt["height"] <= 720), key=lambda fmt: fmt["height"], default=None)
    if not chosen:
        raise ValueError("No seekable video format up to 720p")
    draft_ends = [part["end_time"] for part in info.get("chapters") or []
                  if "draft" in part["title"].lower() and part.get("end_time") and 100 <= part["end_time"] <= 1200]
    return chosen["url"], info.get("duration") or 0, max(draft_ends) if draft_ends else None, info.get("release_timestamp")


def frame_at(video_url, second):
    command = [FFMPEG, "-hide_banner", "-loglevel", "quiet", "-ss", str(second), "-i", video_url,
               "-frames:v", "1", "-f", "image2pipe", "-vcodec", "mjpeg", "-"]
    result = subprocess.run(command, capture_output=True, timeout=18)
    if result.returncode or not result.stdout:
        return None
    image = cv2.imdecode(np.frombuffer(result.stdout, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        return None
    return cv2.resize(image, (1280, 720)) if image.shape[:2] != (720, 1280) else image


def card_present(frame):
    panels = (frame[420:495, :190], frame[420:495, 1090:])
    for panel in panels:
        gray = cv2.cvtColor(panel, cv2.COLOR_BGR2GRAY)
        if np.mean(gray < 30) < 0.55 or np.mean(gray > 180) < 0.015:
            return False
    return True


def get_frames(video_url, seconds, workers=2):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return [(second, frame) for second, frame in zip(seconds, pool.map(lambda t: frame_at(video_url, t), seconds))
                if frame is not None]


def clock_seconds(frame, ocr):
    crop = cv2.resize(frame[45:75, 600:685], None, fx=4, fy=4)
    recognized, _ = ocr(crop)
    for _, text, _ in recognized or []:
        match = re.search(r"(\d{1,2}):(\d{2})", text)
        if match and int(match[2]) < 60:
            return int(match[1]) * 60 + int(match[2])
    return None


def game_start_time(video_url, ocr, estimated=None):
    nearby = [estimated + offset for offset in (100, 150, 200, 250, 300, 400, 0, -100)] if estimated is not None else []
    for second in [int(value) for value in nearby if value >= 0] + [500, 600, 700, 400, 800, 900, 300, 1000, 1100]:
        frame = frame_at(video_url, second)
        if frame is None:
            continue
        elapsed = clock_seconds(frame, ocr)
        if elapsed is not None:
            start = second - elapsed
            if estimated is None or (elapsed <= 600 and abs(start - estimated) <= 600):
                return start
    return None


def scan_game_starts(video_url, duration, ocr):
    samples = []
    seconds = list(range(0, int(duration) - 2, 120))
    for offset in range(0, len(seconds), 16):
        for second, frame in get_frames(video_url, seconds[offset:offset + 16], workers=4):
            elapsed = clock_seconds(frame, ocr)
            if elapsed is not None:
                samples.append((second, elapsed))
    segments = []
    for second, elapsed in samples:
        if not segments or elapsed < segments[-1][-1][1] - 120:
            segments.append([])
        segments[-1].append((second, elapsed))
    starts = []
    for segment in segments:
        progressing = any(60 <= later[0] - earlier[0] <= 240
                          and abs((later[1] - earlier[1]) - (later[0] - earlier[0])) <= 30
                          for earlier, later in zip(segment, segment[1:]))
        if progressing:
            starts.append(segment[0][0] - segment[0][1])
    return starts


def index_video_group(group):
    group = sorted(group, key=lambda game: game["start_time_utc"])
    video_url, duration, _, release_timestamp = video_info(group[0]["youtube_url"])
    ocr = RapidOCR()
    if release_timestamp:
        starts = []
        for game in group:
            timestamp = datetime.fromisoformat(game["start_time_utc"]).replace(tzinfo=timezone.utc).timestamp()
            starts.append(game_start_time(video_url, ocr, int(timestamp - release_timestamp)))
        method = "live_timestamp"
    else:
        starts = scan_game_starts(video_url, duration, ocr)
        method = "clock_resets"
    valid = len(starts) == len(group) and all(start is not None and 0 <= start < duration for start in starts)
    valid = valid and all(left < right for left, right in zip(starts, starts[1:]))
    detail = "" if valid else f"Found {len(starts)} starts for {len(group)} games: {starts}"
    return [{"game_id": game["game_id"], "youtube_url": game["youtube_url"],
             "video_time_seconds": str(starts[index]) if valid else "", "method": method if valid else "unresolved",
             "detail": detail} for index, game in enumerate(group)]


def index_reused_vods(event, workers, retry_unresolved=False):
    directory = DIRECTORIES[event]
    games = read_csv(directory / "games.csv")
    groups = defaultdict(list)
    for game in games:
        groups[game["youtube_url"]].append(game)
    groups = {url: group for url, group in groups.items() if len(group) > 1}
    path = directory / "vod-game-starts.csv"
    indexed = {row["game_id"]: row for row in read_csv(path)} if path.exists() else {}
    pending = [group for group in groups.values() if any(game["game_id"] not in indexed for game in group)
               or (retry_unresolved and any(indexed[game["game_id"]]["method"] in ("unresolved", "error") for game in group))]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        jobs = {pool.submit(index_video_group, group): group for group in pending}
        for number, job in enumerate(as_completed(jobs), 1):
            group = jobs[job]
            try:
                rows = job.result()
            except Exception as error:
                rows = [{"game_id": game["game_id"], "youtube_url": game["youtube_url"],
                         "video_time_seconds": "", "method": "error", "detail": str(error)[:160]} for game in group]
            indexed.update((row["game_id"], row) for row in rows)
            write_csv(path, INDEX_FIELDS, [indexed[game["game_id"]] for game in games if game["game_id"] in indexed])
            print(event, "VOD", number, "/", len(pending), group[0]["youtube_url"].split("=")[-1],
                  rows[0]["method"], len(group), flush=True)


def find_intro(video_url, duration, draft_end, picks, options, ocr, start, search_from, search_through):
    if start is not None:
        sequences = [list(range(max(0, start + search_from), min(start + search_through + 1, int(duration) - 2), 8))]
    else:
        sequences = []
        if draft_end:
            sequences.append(list(range(int(draft_end) + 5, min(int(draft_end) + 201, int(duration) - 2), 8)))
        sequences.append(list(range(280, min(1001, int(duration) - 2), 12)))
    seen = set()
    for sequence in sequences:
        pending = [second for second in sequence if second not in seen]
        for index in range(0, len(pending), 8):
            chunk = pending[index:index + 8]
            seen.update(chunk)
            for second, frame in get_frames(video_url, chunk):
                if card_present(frame) and any(
                    resolve(card_text(ocr, frame, side), [row for row in picks if row["side"] == side], options)
                    for side in ("Blue", "Red")
                ):
                    return second
    return None


def card_text(ocr, frame, side):
    left = side == "Blue"
    crop = frame[415:497, :200] if left else frame[415:497, 1080:]
    result, _ = ocr(cv2.resize(crop, None, fx=3, fy=3))
    if not result:
        return []
    lines = []
    for box, text, confidence in result:
        center = sum(point[1] for point in box) / 4
        left = min(point[0] for point in box)
        lines.append((center, left, text.strip(), confidence))
    return sorted(lines, key=lambda line: (round(line[0] / 12), line[1]))


def resolve(lines, players, options):
    if len(lines) < 2:
        return None
    name = lines[0][2]
    player, player_score = max(((row, similarity(name, row["player"])) for row in players), key=lambda pair: pair[1])
    if player_score < 0.78:
        return None
    label = " ".join(line[2] for line in lines[1:])
    choices = options[player["champion_id"]]
    scored = []
    for skin, chroma in choices:
        display = chroma or (skin.removeprefix("Classic ") if skin.startswith("Classic ") else skin)
        scored.append((similarity(label, display), skin, chroma))
    score, skin, chroma = max(scored)
    if score < 0.88:
        return None
    # A variant requires its color to be legible; an OCR collision with the
    # parent skin must not manufacture a chroma choice.
    if chroma and normalized(chroma) == normalized(skin):
        return None
    return {"player": player["player"], "champion_id": player["champion_id"],
            "skin": skin, "chroma": chroma, "score": round((player_score + score) / 2, 3)}


def inspect_game(game, picks, options, ocr, search_from, search_through):
    video_url, duration, draft_end, release_timestamp = video_info(game["youtube_url"])
    estimated = None
    if release_timestamp and game.get("start_time_utc"):
        timestamp = datetime.fromisoformat(game["start_time_utc"]).replace(tzinfo=timezone.utc).timestamp()
        estimated = int(timestamp - release_timestamp)
    start = int(game["video_start_seconds"]) if game.get("video_start_seconds") else game_start_time(video_url, ocr, estimated)
    if start is None and duration > 5000:
        return [], {"status": "error", "intro_time_seconds": "", "detail": "Could not locate this game's clock in the full-series VOD"}
    intro = find_intro(video_url, duration, draft_end, picks, options, ocr, start, search_from, search_through)
    if intro is None:
        return [], {"status": "no_intro_card", "intro_time_seconds": "", "detail": f"No readable paired skin cards through {search_through} video seconds after game start"}
    seconds = range(max(0, intro - 28), min(int(duration) - 2, intro + 43), 3)
    found = {}
    for second, frame in get_frames(video_url, list(seconds)):
        if not card_present(frame):
            continue
        for side in ("Blue", "Red"):
            result = resolve(card_text(ocr, frame, side), [row for row in picks if row["side"] == side], options)
            if not result:
                continue
            key = (result["player"], result["champion_id"])
            if key not in found or result["score"] > found[key]["score"]:
                found[key] = {**result, "game_id": game["game_id"], "video_time_seconds": str(second),
                              "source_url": game["youtube_url"] + f"&t={second}s"}
    rows = [{field: result[field] for field in EVIDENCE_FIELDS} for result in found.values()]
    status = "complete" if len(rows) == 10 else "partial"
    detail = "" if status == "complete" else "Missing: " + ", ".join(row["player"] for row in picks if (row["player"], row["champion_id"]) not in found)
    return rows, {"status": status, "intro_time_seconds": str(intro), "detail": detail}


def inspect_with_local_ocr(game, picks, options, search_from, search_through):
    if not hasattr(THREAD, "ocr"):
        THREAD.ocr = RapidOCR()
    try:
        return inspect_game(game, picks, options, THREAD.ocr, search_from, search_through)
    except Exception as error:
        return [], {"status": "error", "intro_time_seconds": "", "detail": str(error)[:160]}


def review_event(event, selected_game=None, max_games=None, workers=2, resume=False, retry_status=None,
                 search_from=30, search_through=240, reused_vod_only=False):
    directory = DIRECTORIES[event]
    games = read_csv(directory / "games.csv")
    picks_by_game = defaultdict(list)
    for row in read_csv(directory / "picks.csv"):
        picks_by_game[row["game_id"]].append(row)
    evidence_path = directory / "skin-evidence.csv"
    evidence = {(row["game_id"], row["player"], row["champion_id"]): row for row in read_csv(evidence_path)}
    status_path = directory / "review-status.csv"
    statuses = {row["game_id"]: row for row in read_csv(status_path)} if status_path.exists() else {}
    starts_path = directory / "vod-game-starts.csv"
    starts = {row["game_id"]: row for row in read_csv(starts_path)} if starts_path.exists() else {}
    for game in games:
        game["video_start_seconds"] = starts.get(game["game_id"], {}).get("video_time_seconds", "")
    options = catalog(directory, event)
    vod_counts = defaultdict(int)
    for game in games:
        vod_counts[game["youtube_url"]] += 1
    pending = [game for game in games if (not selected_game or game["game_id"] == selected_game)
               and (not resume or game["game_id"] not in statuses)
               and (not retry_status or statuses.get(game["game_id"], {}).get("status") == retry_status)
               and (not reused_vod_only or (vod_counts[game["youtube_url"]] > 1
                                            and starts.get(game["game_id"], {}).get("video_time_seconds")))]
    if max_games is not None:
        pending = pending[:max_games]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        jobs = {pool.submit(inspect_with_local_ocr, game, picks_by_game[game["game_id"]], options, search_from, search_through): game
                for game in pending}
        for count, job in enumerate(as_completed(jobs), 1):
            game = jobs[job]
            game_id = game["game_id"]
            rows, outcome = job.result()
            conflicts = []
            for row in rows:
                key = (game_id, row["player"], row["champion_id"])
                previous = evidence.get(key)
                if previous and (previous["skin"], previous["chroma"]) != (row["skin"], row["chroma"]):
                    conflicts.append(row["player"])
                    continue
                if not previous:
                    evidence[key] = row
            if conflicts:
                outcome["status"] = "conflict"
                outcome["detail"] = "OCR differs from existing evidence: " + ", ".join(conflicts)
            recorded = sum(key[0] == game_id for key in evidence)
            if recorded == 10 and outcome["status"] in ("partial", "complete"):
                outcome = {**outcome, "status": "complete", "detail": ""}
            statuses[game_id] = {"game_id": game_id, "youtube_url": game["youtube_url"], **outcome,
                                 "picks_recorded": recorded}
            write_csv(evidence_path, EVIDENCE_FIELDS, list(evidence.values()))
            write_csv(status_path, STATUS_FIELDS, [statuses[row["game_id"]] for row in games if row["game_id"] in statuses])
            print(event, count, "/", len(pending), game_id, statuses[game_id]["status"], recorded, flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", choices=(*DIRECTORIES, "all"), default="all")
    parser.add_argument("--game-id")
    parser.add_argument("--max-games", type=int)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--retry-status", choices=("no_intro_card", "partial", "error"))
    parser.add_argument("--search-from", type=int, default=30, help="First game second to inspect")
    parser.add_argument("--search-through", type=int, default=240, help="Game seconds to inspect for skin introductions")
    parser.add_argument("--reused-vod-only", action="store_true", help="Inspect only games sharing a full-series VOD")
    parser.add_argument("--index-reused-vods", action="store_true", help="Find each game start in a shared series VOD")
    parser.add_argument("--retry-index-unresolved", action="store_true")
    args = parser.parse_args()
    for event in DIRECTORIES if args.event == "all" else (args.event,):
        if args.index_reused_vods:
            index_reused_vods(event, args.workers, args.retry_index_unresolved)
            continue
        review_event(event, args.game_id, args.max_games, args.workers, args.resume, args.retry_status,
                     args.search_from, args.search_through, args.reused_vod_only)


if __name__ == "__main__":
    main()
