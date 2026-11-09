# Candlehearth Rent Dim Patch

Version 0.1.2. Standalone SKSE test candidate for Skyrim AE 1.7.104.0.

Dims rent topics as soon as a successful rental makes them unavailable. It preserves Candlehearth and Tavern AI Fix scripts and needs no ESP or additional Papyrus extender.

## Requirements

- [Candlehearth - An Inn Overhaul](https://www.nexusmods.com/skyrimspecialedition/mods/97542) 1.1.1.
- Skyrim AE 1.7.104.0, SKSE 2.3.1 and the matching [Address Library](https://www.nexusmods.com/skyrimspecialedition/mods/32444).

### Supported optional mods

Tavern AI Fix with its Candlehearth compatibility patch may remain installed. This DLL does not replace RentRoomScript or change room-showing behavior. The compatible source script was inspected; runtime integration has not yet been tested. Other dialogue patches may require separate testing.

### Target versions

AE 1.7.104.0 only. Other runtimes are rejected. No SE, GOG or VR build is supplied.

## The problem

After a successful rental, Candlehearth sets Variable09 to 1. The next eligible INFO is the refusal, which has not been heard, so the menu remains bright until the player requests another rental and hears it.

## What the patch does

Marks only the eleven rental-refusal INFOs and their shared refusal response as heard in memory. When the refusal becomes eligible, it is already dim. Dialogue remains available and the refusal can still be spoken. No money, rental duration, ownership or dialogue conditions are changed. State is reapplied after loading a save; there is no Papyrus polling, dialogue playback or save-writing command.

## Install and test

Close Skyrim first. In MO2, create an empty mod named **Candlehearth Rent Dim Patch**, open that mod's folder, and copy the contents of this repository's `dist/Candlehearth Rent Dim Patch/` into it. Enable the mod in the left pane. There is no ESP to enable in the Plugins pane. Keep Candlehearth and the existing Candlehearth - Tavern AI Fix Patch enabled. LOOT needs no new rule.

Launch through SKSE and load a save from before renting. Rent once: all rent-duration choices should dim when the refusal path becomes eligible, without asking again. Ask again: the normal refusal should play and no additional gold should be charged. Confirm that showing the room still follows Tavern AI Fix settings. Repeat for a capital and non-capital inn, each duration, and after save/reload and rental expiry. Do not overwrite your pre-test save.

The log is `My Games/Skyrim Special Edition/SKSE/CandlehearthRentDim.log`. Expect `Marked eleven rental refusal INFOs and their shared response heard`. A validation error means the patch left dialogue state untouched. To remove, close Skyrim and disable this mod in MO2.

## Build from source

See [BUILDING.md](BUILDING.md). No archive has been created or published. Loose DLL and notices are staged inside this repository only.

## Verification status

Version 0.1.0 loaded successfully on AE 1.7.104. Live DevBench tests confirmed immediate dimming and correct charges with Hulda for a night (75), week (350) and month (1000). A repeated daily request played the normal refusal and charged no more gold. The unselected dimmed text was gray (#AAAAAA). Tavern AI Fix's show-room topic appeared.

Version 0.1.1 was tested and still missed Delphine's daily topic. The cause is now identified: Delphine uses a separate vanilla daily refusal, 0009CC9A:Skyrim.esm, which was absent from the original ten-record list. It is not the generic refusal 0009CC93:Skyrim.esm. The dialogue-open workaround was unnecessary and has been removed.

Version 0.1.2 adds that missing refusal, marking eleven refusals plus their shared response. Live checks passed for Delphine daily (50 gold), Hulda daily (75 gold), and a previously untested innkeeper, Keerava, for a week (350 gold). Rental topics dimmed immediately after success. Delphine's repeat request played the refusal and charged no additional gold. Evidence is in test/live-0.1.2.json.

A fresh-process, 24-hour test through Modern Wait Menu completed: Delphine's daily rental expired and Keerava's weekly rental remained active. This checks the in-game rental timer through waiting, not an actual bed-sleep animation. The attempted trip back to purchase another daily rental hit a separate rendering-path crash, so the post-expiry purchase itself was not completed. An earlier DevBench wait-tool timeout also caused an AI Process Fix safety abort during autosave; see NOTES.md for both distinct failures. No blanket claim of all save/reload, sleep, or rendering stability is made.

Tests used added gold, coc, shipped ClearRoom cleanup between rentals, and two calendar jumps in the unsaved test session. No manual save command was issued. The earlier calendar jumps did not establish expiry. The later normal 24-hour wait did; reloading an active rental remains unverified. Full room-showing movement was not tested. See NOTES.md and test/live-results.json for precise evidence and limits.

## Credits and permissions

Simon Magus, DeltaRider and wol for Candlehearth; Tavern AI Fix authors for its compatibility script; Dylbill for documenting the said-state API; CommonLibSSE-NG and SKSE contributors. No assets or scripts from those mods are distributed.

## License

Original source: MIT, kxgcayh, [LICENSE](LICENSE). Linked dependencies retain their own licenses; see [THIRD-PARTY-NOTICES.txt](THIRD-PARTY-NOTICES.txt) and [COPYING](COPYING).
