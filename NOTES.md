# Investigation notes

## Decision

STOP before building. Neither approach reaches 80%; the project target before modifying game data is 90%. Confidence percentages below estimate meeting the requested behavior while preserving rental logic, speech and compatibility, rather than confidence in the documented failure mechanism.

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

No MO2 test steps apply: do not create or enable a mod named Candlehearth Rent Dim Patch, and no Candlehearth Rent Dim Patch.esp is supplied. Continue only with a justified higher-confidence mechanism or an explicitly authorized experimental scope.

Hook candidate: none established. Existing confidence and live-write restrictions prevented an unproven gameplay change. The CLI/package version distinction belongs in the shared tooling notes; reported to t36 because this task restricts writes to this repository.
