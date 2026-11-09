#!/usr/bin/env python3
"""Run an explicitly authorized rental test in a loaded, unsaved game session."""
import json
from pathlib import Path
import time
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[1]


def api(tool, args):
    request = urllib.request.Request("http://127.0.0.1:8920/api/tool/" + tool,
                                    data=json.dumps(args).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=8) as response:
        result = json.load(response)
    if "error" in result:
        raise RuntimeError(result)
    return result


def papyrus(script, function, ref, args=None):
    result = api("papyrus", {"action": "call", "script": script, "function": function,
                             "args": args or [], "self": {"form": ref}})
    assert result.get("called"), result
    return result.get("returned")


def gfx(path):
    return api("gfx", {"op": "get", "menu": "Dialogue Menu", "path": "_root.DialogueMenu_mc." + path,
                       "depth": 3}).get("value")


def key(name):
    api("input", {"action": "tap", "device": "keyboard", "key": name})


def wait_speech_end():
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        text = gfx("SubtitleText.text")
        if not isinstance(text, str) or not text.strip():
            return
        time.sleep(0.15)
    raise RuntimeError("NPC speech did not finish before deadline")


def close():
    try:
        gfx("TopicList.EntriesA")
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return
        raise
    key("escape")
    time.sleep(0.3)


def rent(ref, duration, price):
    close()
    # Reset through the shipped cleanup, not by changing Variable09 alone.
    papyrus("RentRoomScript", "ClearRoom", ref)
    assert papyrus("Actor", "GetActorValue", ref, ["Variable09"]) == 0
    before = api("inspect", {"kind": "player"})["gold"]
    assert before >= price
    papyrus("ObjectReference", "Activate", ref, [{"form": "0x14"}, False])
    time.sleep(0.6)
    wait_speech_end()
    entries = gfx("TopicList.EntriesA")
    selected = int(gfx("TopicList.iSelectedIndex"))
    index = next(i for i, e in enumerate(entries) if "rent a room for a " + duration in e["text"])
    for _ in range(abs(index - selected)):
        key("down" if index > selected else "up")
    assert int(gfx("TopicList.iSelectedIndex")) == index
    key("enter")
    deadline = time.monotonic() + 12
    while time.monotonic() < deadline:
        after = api("inspect", {"kind": "player"})["gold"]
        if after == before - price and papyrus("Actor", "GetActorValue", ref, ["Variable09"]) == 1:
            break
        time.sleep(0.15)
    assert after == before - price, (before, after, price)
    time.sleep(0.4)
    result = gfx("TopicList.EntriesA")
    rentals = [e for e in result if "rent a room" in e["text"]]
    assert len(rentals) == 3 and all(e["topicIsNew"] is False for e in rentals), rentals
    snapshot = {"innkeeperRef": ref, "duration": duration, "price": price,
                "goldBefore": before, "goldAfter": after, "rentalTopicsImmediatelyAfterPurchase": rentals,
                "variable09": papyrus("Actor", "GetActorValue", ref, ["Variable09"]),
                "showRoomTopicPresent": any("show me my room" in e["text"] for e in result)}
    # Selecting an already-rented topic must never charge a second time.
    wait_speech_end()
    key("enter")
    lines = []
    for _ in range(30):
        line = gfx("SubtitleText.text")
        if isinstance(line, str) and line.strip() and line not in lines:
            lines.append(line)
        time.sleep(0.12)
    snapshot["repeatLines"] = lines
    snapshot["goldAfterRepeat"] = api("inspect", {"kind": "player"})["gold"]
    assert snapshot["goldAfterRepeat"] == after
    snapshot["pass"] = True
    path = ROOT / "test/live-results.json"
    history = json.loads(path.read_text()) if path.exists() else []
    history.append(snapshot)
    path.write_text(json.dumps(history, indent=2) + "\n")
    print(json.dumps(snapshot, indent=2))
    close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ref")
    parser.add_argument("duration", choices=["night", "week", "month"])
    parser.add_argument("price", type=int)
    args = parser.parse_args()
    rent(args.ref, args.duration, args.price)
