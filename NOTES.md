# Investigation notes

## Initial investigation, superseded by standalone approach below

The first pass stopped before building. Neither approach reaches 80%; the project target before modifying game data is 90%. Confidence percentages below estimate meeting the requested behavior while preserving rental logic, speech and compatibility, rather than confidence in the documented failure mechanism.

## Evidence checked

- Overhaul 1.2 report section 4.5 and the final rent-topic section of KNOWLEDGEBASE.local.md. Live evidence there establishes that successful rental leaves the topic bright and hearing the refusal dims it. No new live test was performed here.
- Candlehearth Nexus description and all five Posts pages (252 threads); Bugs tab queried. The description confirms daily/weekly/monthly rentals and higher capital prices. The pinned author reply identifies Tavern AI Fix and USMP compatibility.
- Shipped source in Candlehearth.bsa: RentRoomScript and all nine MAG_Candlehearth_TIF_* sources. Each fragment invokes the appropriate rental method. Each rental method sets Variable09 to 1; ClearRoom resets it to 0. Rentals change bed/chest ownership, charge gold, schedule expiry and show the room.
- Candlehearth.esp serialized with the toolkit Spriggit wrapper, -u, Spriggit.Yaml 0.41.0. Generated YAML is retained only in ignored build/candlehearth/. Read refusal INFO 09CC93:Skyrim.esm and 000832:Candlehearth.esp plus the capital daily topic. Refusal 000832 references shared response 000813; the success and insufficient-gold paths are separate INFO records. Reusing response data is not evidence that their runtime said states are shared.
- Vanilla Skyrim - Misc.bsa topicinfo.pex and topic.pex were read in memory. The uncompressed TopicInfo string table contains GetOwningQuest, GetState and GotoState, with no said-state setter; Topic has no additional dialogue function. Do not import Fallout 4 TopicInfo APIs into Skyrim.
- CommonLibSSE-NG include/RE/T/TESTopicInfo.h: runtime bool saidOnce at 0x3A; ChangeFlags::kSaidOnce = 1u << 31. This change flag describes saved runtime state, not an authorable INFO flag. The header alone does not prove which shared-response object the menu checks.
- Installed Candlehearth - Tavern AI Fix Patch/source/scripts/RentRoomScript.psc: rental methods use ShowPlayerRoom() instead of the base mod's WI.ShowPlayerRoom(self, Bed). Replacing RentRoomScript would override that compatibility change.

## Vanilla analogue

The closest analogue is vanilla inn rental, not a new custom mechanic: RentRoomTopic 09CC92:Skyrim.esm contains the refusal INFO 09CC93:Skyrim.esm retained by Candlehearth. The recorded live investigation reports the same rental-state transition for vanilla. No verified vanilla example was found that marks an unspoken, separate INFO as said through records or Papyrus. This is a limit of the present investigation, not a proof that no engine-native solution can exist.

## A. Record changes only

| Candidate | Confidence | Assumptions and reason not to build |
|---|---:|---|
| Change flags/order alone | 20% | Assumes there is a flag that affects the selected INFO's said state. No such authorable flag was established. SayOnce gates availability, and ordering cannot make Variable09==0 true after rental. |
| Keep success INFO selected after success | 15% | Assumes the success fragment can safely run again. It charges gold and schedules the rental again; merely loosening conditions changes gameplay. |
| InvisibleContinue into refusal | 40% | Assumes automatic playback marks the same INFO the menu tests. Requires routing changes, may need new topics, and immediately plays a refusal after a successful purchase. A silent version removes or alters the ordinary repeat refusal and remains unverified. |
| Share success/refusal ResponseData | 30% | Assumes heard state follows shared response identity. No evidence establishes that; successful and refused rentals also need different audio. Existing refusal already uses shared response data and still needs to be heard. |
| Set runtime said-once change flag in plugin | 5% | Assumes save change-state can be authored as a record field. CommonLib distinguishes these; no supported Spriggit field or vanilla example establishes this. |

Best record-only confidence: 40%. Assumptions needed to raise it: a verified vanilla routing pattern that preserves speech and repeat behavior, and a controlled live test establishing the menu's use of INFO versus shared-response said state. Current task forbids changing world state, so no such experiment was attempted.

## B. Minimal Papyrus addition to success fragment

Best confidence: 30%. Assumes an existing allowed Skyrim API can mark the refusal INFO said without speaking it. Vanilla TopicInfo provides no setter. Actor.Say(topic) speaks a selected topic rather than silently marking a specified INFO; it could interrupt the success response, affect room-showing dialogue and select a different conditional INFO. Muting the actor is neither minimal nor verified and risks unrelated speech. UI manipulation would be transient, menu-specific and outside the requested plugin-only mechanism.

A native extension exposing a correctly persisted said-state setter would be a different scope and dependency, requiring version-specific implementation and validation. No native code or runtime writes were attempted. No claim is made that merely changing the CommonLib bool would be sufficient.

## Forms considered, unchanged

Refusal INFOs: 09CC93:Skyrim.esm; 000832, 00083A, 00081A, 000826, 00080D, 000836, 000820, 000829, 000814:Candlehearth.esp. No records were changed; no patch masters or ESL flag were authored.

## Tooling finding

The local fork reports CLI version 0.1.0-audit-fixes.1, which its translation loader rejects as historical Windows-only when used as PackageVersion. Confirmed working translation arguments, supplied by t36 and then executed here: --PackageName Spriggit.Yaml --PackageVersion 0.41.0. The source serialization completed with -u and the wrapper's built-in sanity round trip. No patch round trip or xeditlib validation is claimed because no patch exists.

## Safety and next step

Only this new repository was written intentionally. No game commands, save writes, live installation, packaging or publishing. No subagents. Codex pre-tool and session-start guards reported healthy; canary also reported an unrelated degraded Claude MCP hook.

At the initial stop no artifact existed. The later user instruction authorized continuing; current installation instructions are in README.md.

Hook candidate: none established. Existing confidence and live-write restrictions prevented an unproven gameplay change. The CLI/package version distinction belongs in the shared tooling notes; reported to t36 because this task restricts writes to this repository.


## Standalone native implementation, 0.1.0

User selected investigation of a standalone SKSE plugin. A DLL avoids replacing RentRoomScript, avoids script compilation/VMAD, and adds no Dylbill dependency. It intentionally supersedes the original ESP-only implementation plan. There is no ESP, master list, new form, FOMOD or plugin load-order slot. No Spriggit deserialization of a patch is necessary.

Confidence before implementing: 92% in the approach. Assumptions: the recorded live diagnosis is accurate; the menu tests INFO/shared-response heard state; the verified CommonLib layout matches AE 1.7.104; the winning refusal records remain repeatable and retain their known shared-response links. Live behavior is still unverified, so this is a test candidate, not a verified fix.

The missing API does exist outside vanilla: [Dylbill's source](https://github.com/Dylbill-Iroh/DbSkseFunctions/blob/main/DbSkseFunctions/src/Topic.cpp), read 2026-11-09, implements SetTopicInfoSaidOnce by validating the INFO and assigning topicInfo->saidOnce. No engine call or AddChange is used. This justified using the same existing engine field directly, with original code and without importing Dylbill code. My earlier blanket statement that no Papyrus solution existed was too broad; vanilla lacks the setter, while the extender supplies it.

Native means runtime engine state here, distinct from record-only changes evaluated above. On kDataLoaded, kNewGame and kPostLoadGame the DLL resolves the ten refusal INFOs plus shared response 000813:Candlehearth.esp and marks their runtime saidOnce booleans true. No rent methods or success fragments execute. No speech is played or muted. Gold, timers, ownership, dialogue conditions, text and flags are unchanged. Before a purchase, the success INFO remains the eligible path; after Variable09 becomes 1, the refusal path is already heard. This applies to all rent-duration choices because all are unavailable during an existing rental.

All eleven INFOs must exist and lack SayOnce, and all nine Candlehearth-specific refusals must link to shared INFO 000813. Validation finishes before the first write; a mismatch logs and leaves all state untouched. Record lookup uses each plugin's local IDs so LOOT and ESL indices do not affect it. Candlehearth must be present; no soft dependency is silently ignored, and the missing-mod case is logged. Hard patching the existing mod's INFOs is intentional; copying them would not change the INFOs the existing topics select.

Runtime said state is not explicitly marked changed for save serialization. It is reapplied on new games and after every load. This avoids introducing a persistence system solely for cosmetic dialogue state. It does not promise removal of previously legitimate said-state changes already stored by the game. Shared INFO 000813 is exclusively the refusal response in the inspected Candlehearth YAML. Runtime compatibility checks do not verify an entire third-party plugin hash; another mod can alter dialogue in ways the shape checks do not detect.

Build library: local CommonLibSSE-NG commit 8eaddedd1542290701ccb0e9e88b2af8b3cea597, build-install package. TESTopicInfo::saidOnce is at 0x3A and its shared-response pointer is at 0x28; the AE 1.7.99+ tail extension does not move these members in this header. Restricting both exported metadata and Load to AE 1.7.104 avoids claiming other runtimes tested. No binary hooks, detours, executable patches or assembly thunks.

Binary verification parses the PE export table and SKSE metadata directly in verify_binary.py and is cross-checked with llvm-readobj. It checks AMD64 DLL, Load/Query/Version exports, version 0.1.0, struct dependence, Address Library V5 flag, one supported runtime and zero padding. CommonLib's VersionNumber default constructor fills unused runtime entries as 1.0.0; CMake passes explicit zero entries to avoid advertising those defaults. The build uses one job and the pre-existing installed libraries; no dependency was rebuilt or installed.

DevBench alive on port 8920 returned no response. No in-game success claim is made. Required tests: capital and non-capital innkeepers; daily, weekly and monthly rentals; refusal immediately after purchase with no further charge; save/reload; expiry and re-rental; unchanged Tavern AI Fix room-showing settings. Installation/removal is by the user through MO2 only. No live files or working modlist/report were changed.


## Live validation and 0.1.1 revision, 2026-11-09

The user installed 0.1.0, started Skyrim, and authorized driving the game independently, including coc to an innkeeper. DevBench 1.32.0 on port 8920 and PID 744 answered. The DLL log confirmed load on 1.7.104, marking at dataLoaded and again after loading a save. The normal Load menu was used; initial assumptions about the chosen save's location were wrong (live GetParentCell returned Riverwood04). Following the user's correction, coc moved to WhiterunBanneredMare. Inspect refs identified Hulda as 0001A66E; 0001A69A is Ysolda and was only read.

Manual first capital daily test: added 2,000 gold, Hulda Variable09=0; selected 75-gold night topic; gold 2,000 -> 1,925; Variable09=1. All three rent EntriesA rows became topicIsNew=false BEFORE a repeat request. Subsequent Enter captured subtitle "Are you joking? You just rented a room from me." and gold remained 1,925. The unselected weekly row textColor was 11184810 (#AAAAAA); an untouched row before purchase was 16777215 (#FFFFFF). The earlier historical claim that topicIsNew was unrelated to dimming was too broad: the property changed with rental dimming in this UI; earlier rumor observations do not establish rental behavior.

Capital week/month cases (test/live-results.json): shipped RentRoomScript.ClearRoom reset between cases, not just Variable09. Week cost 350 (1,925 -> 1,575), month cost 1,000 (1,575 -> 575); all rental rows were false immediately after each purchase, and show-room topic was present. These first harness cases did not capture repeat subtitles, so do not count them as independent proof that refusal speech played; the manual daily case establishes that behavior.

Non-capital daily regression: after a 26-hour DevBench calendar jump and coc to RiverwoodSleepingGiantInn, Delphine 00013485's night topic remained bright after the success line, a 50-gold charge (575 -> 525), and Variable09=1. Her week/month rows were false. Reopening retained this state; selecting daily again spoke the refusal and changed it to false. A read-only header/subrecord scan over the active plugins found vanilla daily refusal 09CC93 overridden only by Candlehearth; no later plugin explained the loss. The complete four-INFO vanilla daily group and all overrides were inspected. A fresh rental with Valga 0003A198 in FalkreathDeadMansDrink then charged 50 (525 -> 475) and dimmed all three topics immediately, consistent with the shared vanilla refusal having just been spoken by Delphine.

The first automated Delphine/Valga attempts charged nothing because the first Enter was consumed before a purchase; manually pressing after the greeting completed produced the success lines and charges above. The harness now waits for the greeting subtitle to clear, but input timing is still a test-driver limitation. No unsupported failure result is recorded as a passing purchase.

Two advanceTime 26-hour calls were made in this unsaved test session. Variable09 did not expire, so no natural-expiry success is claimed. The calendar result and a later Utility.GetCurrentGameTime reading did not provide a reliable timer test. The precise loss trigger for 09CC93 is UNRESOLVED; it may involve dialogue/quest initialization or reset. No binary analysis proves that trigger, and no claim of a confirmed 24-hour reset is warranted.

0.1.1 response: reapply the same validated eleven saidOnce fields on Dialogue Menu opening through a MenuOpenCloseEvent sink, in addition to dataLoaded/newGame/postLoadGame. No per-frame loop, hook or rental-script replacement is introduced. Confidence in this corrective approach: 90%, assuming the open event occurs before the subsequent successful rental rebuilds its topic choices. This assumption requires a live retest; the running game still has 0.1.0. Each log line includes the event reason and the vanilla INFO's prior heard state to make a future reset observable. This revision is not represented as verified in game.

Named rollback snapshot: backups/known-good-capital-0.1.0/ (source, metadata, README and DLL), excluded from Git. 0.1.1 independently passes verify_binary.py and llvm-readobj export checks. The code makes no AddChange request; it does not promise the engine can never serialize state for a record already marked changed elsewhere.

No manual save command, INI edit, live DLL deployment, release or publication was performed. Normal game operation may autosave on transitions; no claim is made that normal engine autosaves were disabled. The user must replace the installed DLL and restart for 0.1.1. Required follow-up: repeat fresh non-capital daily rentals before hearing a refusal, both before and after loading, and retain natural expiry/active-rental reload/full room-showing as open tests.


## 0.1.1 live failure, identified root cause and 0.1.2

0.1.1 loaded on AE 1.7.104 and logged dataLoaded, postLoadGame, and dialogue-open processing. At first opening with Delphine, its log reported vanillaPreviouslyHeard=true for 09CC93. Before the purchase, Variable09=0 and gold=2,000. A single daily rental spoke "Sure thing. It's yours for a day." and charged 50 (2,000 -> 1,950), with Variable09=1. After the VM/UI settled, daily remained topicIsNew=true and weekly/monthly became false. This disproves the reset hypothesis for that failure and shows the dialogue-open event did not fix it. The first sample in test/live-0.1.1.json was taken immediately on the gold change, before the rest of the fragment/UI refresh; the later settled state is recorded here and must be distinguished from that sample.

Root cause: incomplete record inventory in the original task findings and my implementation. Vanilla DIALs include RentRoomTopic 09CC92, DelphineRentRoomTopic 09CC99, and separate main-quest MQ106RentRoomTopic 06B93F. Delphine's ordinary daily refusal is 09CC9A, conditioned on GetIsID(Delphine 013478), the Sleeping Giant Inn cell 0133C6, the innkeeper faction 09CC97, and GetActorValue(Variable09)==1. It has no script and no SayOnce flag. Its success 09CC9B has a fragment and Variable09==0/gold conditions; insufficient-gold 09CC9C is distinct. Marking generic 09CC93 never marked Delphine's 09CC9A. The failure was NOT due to direct versus shared response storage or a demonstrated reset.

Full vanilla INFO audit for GetActorValue (function 14), actor value Variable09 (76), comparison value 1.0 found three records: 09CC93 (ordinary generic refusal), 09CC9A (ordinary Delphine refusal), and 0453EE in MQ106RentRoomTopic (scripted main-quest path, intentionally excluded). Read-only parsed evidence is in test/vanilla-variable09-dialogue-audit.json and test/vanilla-special-rent-infos.json. This is why investigating Delphine alone was insufficient; the entire vanilla class was enumerated. No vanilla daily Eydis-specific DIAL with RentRoom in its EditorID exists in that audited set; Candlehearth's own Eydis weekly/monthly records were already covered.

Standard LLVM investigation, not REA MCP: Address Library Format 5 ID 25626 maps TESTopicInfo::GetResponseList to RVA 0x3F3300 on 1.7.104; it follows dataInfo links at +0x28. MenuTopicManager dialogue constructor code at RVA 0x5ED8A7 compares the selected INFO byte at +0x3A and stores its negation into Dialogue::neverSaid at +0x49 (5ED8AE). These instructions support saidOnce being the correct field and helped reject an unnecessary new state mechanism. TESTopicInfo's mark routine at 3F2E30 also sets +0x3A and invokes the change-tracking virtual; no engine functions are hooked or called by RVA in this patch.

0.1.2 adds 09CC9A:Skyrim.esm to the validated set and removes the 0.1.1 menu event sink. Current set: two vanilla refusals, nine Candlehearth refusals and one shared response (twelve INFO objects total). Confidence before implementing this correction: 98%, assuming the selected INFO follows the verified byte layout; the field mechanism already worked for the other refusals, and the newly found conditions match the failing branch exactly. Still do not call 0.1.2 verified until its fresh-process Delphine test passes.

Build and staging are inside the repository only. Version 0.1.2 passes the independent PE metadata/export verifier. The running game still has 0.1.1. Named pre-change snapshot: backups/pre-delphine-0.1.1/. The existing overwrite command uses an unchanged staged path, now holding 0.1.2; the user must close Skyrim, run it and relaunch. No further live deployment was authorized or performed.


## Live 0.1.2 verification and wait-test abort, 2026-11-09

PID 1248 loaded 0.1.2 and successfully tested Delphine daily (2,000 -> 1,950, all rent topics false immediately), her repeat refusal (1,950 unchanged; exact refusal subtitle captured; gray unselected text #AAAAAA), Hulda daily (1,950 -> 1,875, all false), and newly tested Keerava weekly (1,875 -> 1,525, formerly bright weekly/monthly false after success). Evidence: test/live-0.1.2.json. This verifies the requested dimming across the tested ordinary and special daily paths and a new capital innkeeper.

A later expiry test attempted DevBench wait hours=24. It returned HTTP504, "wait still running after 252 polls", and Utility.GetCurrentGameTime barely advanced; no expiry result can be inferred. Loading Save2 in the same process recovered the visible UI but was not a proven reset of other SKSE plugins' state. Further rental setup used shipped RentRoomScript methods, then the actual Modern Wait Menu. The winning SWF is Modern Wait Menu - Untarnished UI Patch/Interface/sleepwaitmenu.swf (base mod metadata 117661 v2.2.0, patch 118915 v2.1.1). The End key accidentally opened Community Shaders; it was closed with End. No shader-setting tool calls were made. The SWF's real state is waitHours; HoursSlider is a legacy component and sliderChange is empty. waitHours=24 updated WaitTime to 24. Enter then triggered an autosave and process exit.

MaxsuAIProcessFix.log at 21:53:54.496: "Saving the Game!" followed by the fatal "AI updating procecure broken in saving" message. DevBench logged the same autosave name, then pending Enter release after the process stopped. A zero-byte Autosave1 ... RiftenBeeandBarb ... .ess.tmp was observed in the profile saves. No Trainwreck dump or new macOS crash report was found; PID was gone. Four logs were mirrored before restart into ignored build/wait-crash-20261109/.

Confirmed primary-source failure path: https://github.com/doodlum/MaxsuAIProcessFix-ng/blob/main/src/AIProcessLoadGameFunc.cpp checks GetActorsMapSize()>0 during kSaveGame, logs that exact fatal message, displays a message box and calls abort(). Its kPostLoadGame/kNewGame branch only sets LastRecordTime. src/AIProcessEvent_SleepWait.h populates the map on start and clears/updates it on stop. Inference: the timed-out DevBench wait left an unmatched start, and save reloading did not clear that process-local bookkeeping. This explains the observed abort but was not independently instrumented at runtime. Do not generalize it to ordinary waits from a clean process, or blame the dialogue patch from timing alone. A full process restart is required before continuing; do not use DevBench wait/sleep again in this test.

Guard candidate: an abandoned wait/sleep test should require a fresh process before any further save-capable action, because other plugins may retain unmatched event state across save loads. Avoid unverified global hotkeys while a custom menu is active; read the modlist and installed SWF handlers first.


## Fresh-process Modern Wait Menu expiry result and subsequent render crash

A full restart through MO2/SKSE created PID 2976. No DevBench wait/sleep call was issued in that process. Loaded original Save2, coc to Sleeping Giant Inn and set up a daily rental by calling shipped RentRoomScript.RentRoom(DialogueGeneric 13EB3) on Delphine; then coc to Bee and Barb and set up a weekly rental by calling CandlehearthRentRoomCapital02 with the real Candlehearth quest 000DEE (runtime FE0B9DEE) on Keerava. Gold: 2,000 -> 1,950 -> 1,600; both Variable09=1. Setup was through the shipped methods because this test targeted expiry, not initial dialogue.

Read the winning installed Modern Wait Menu Untarnished SWF with FFDec into ignored build/modern-wait-scripts/. Its public waitHours property sets _waitHours and updates WaitTime; legacy HoursSlider.value does not control the displayed clock (sliderChange is empty). In hours mode, waitHours=24 showed WaitTime.text=24. Normal injected Enter confirmed through the menu. The normal autosave completed its start without the previous AI-map abort, the menu counted down, and Maxsu logged Wait Lasting Time is 1 / Update Actor Pos Trigger.

Captured result: Utility.GetCurrentGameTime 1.089348316 -> 2.098628998; Delphine Variable09 1 -> 0, Keerava Variable09 1 -> 1; gold stayed 1,600. test/expiry-0.1.2.json records the checks and pass=true. Therefore one day ends the daily rental and preserves a weekly rental. The patch does not change these timers. Sleeping should use the same game-time registration, but an actual bed sleep was not exercised. A gray topic is heard history, not a disabled menu option.

Next coc back to Riverwood for an actual renewal purchase encountered a second, different failure at 22:02:40. Trainwreck 2026-11-09-22-02-40.log: EXCEPTION_ACCESS_VIOLATION SkyrimSE.exe+156020A, instruction and [rdx+28h],ebp; RDX=0x90, faulting address near 0xB8. The probable stack includes BSBatchRenderer / BSUtilityShader context, CommunityShaders.dll+039E427 (Deferred::Hooks::Main_RenderShadowMaps::thunk), ImprovedCameraSE.dll+00AD49C (RegisterSceneAccumulators), and the main render loop. No dialogue-patch function is named in that stack. This is a rendering-path crash; those frames alone do NOT identify which mod caused it. No matching solved case was found in the local KB/docs. No causal claim linking it to shader settings, Modern Wait Menu or the rental DLL is warranted.

crash-triage.py parsed 1/1 dump with full frame accounting and classified the signature UNKNOWN. Dump and startup/devbench/AIProcessFix logs were copied into ignored build/wait-crash-20261109-220240/. Subsequent API requests timed out; the crashed game process lingered. It was identified by its exact SkyrimSE.exe command and sent TERM only after evidence capture. No further live tests or relaunch were attempted. Post-expiry purchase and active-rental save/reload remain open; the requested rental dimming and the daily-versus-weekly expiry checks are verified.
