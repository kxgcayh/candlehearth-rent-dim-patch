#include <RE/Skyrim.h>
#include <SKSE/SKSE.h>
#include <spdlog/sinks/basic_file_sink.h>

#include <array>
#include <memory>

namespace
{
    constexpr std::array<RE::FormID, 2> kVanillaRefusals{0x09CC93, 0x09CC9A};
    constexpr std::array<RE::FormID, 9> kCandlehearthRefusals{
        0x832, 0x83A, 0x81A, 0x826, 0x80D, 0x836, 0x820, 0x829, 0x814
    };

    bool Repeatable(const RE::TESTopicInfo* info)
    {
        return info && !info->data.flags.any(RE::TOPIC_INFO_DATA::TOPIC_INFO_FLAGS::kSayOnce);
    }

    void MarkRentalRefusalsHeard()
    {
        auto* data = RE::TESDataHandler::GetSingleton();
        if (!data || !data->LookupModByName("Candlehearth.esp")) {
            spdlog::info("Candlehearth absent; no dialogue changed");
            return;
        }

        std::array<RE::TESTopicInfo*, 12> infos{};
        for (std::size_t i = 0; i < kVanillaRefusals.size(); ++i) {
            infos[i] = data->LookupForm<RE::TESTopicInfo>(kVanillaRefusals[i], "Skyrim.esm");
        }
        auto* shared = data->LookupForm<RE::TESTopicInfo>(0x813, "Candlehearth.esp");
        infos.back() = shared;
        for (std::size_t i = 0; i < kCandlehearthRefusals.size(); ++i) {
            infos[i + kVanillaRefusals.size()] = data->LookupForm<RE::TESTopicInfo>(kCandlehearthRefusals[i], "Candlehearth.esp");
        }

        // Validate the complete set before changing runtime state; a changed mod fails closed.
        for (const auto* info : infos) {
            if (!Repeatable(info)) {
                spdlog::error("Expected repeatable rental INFO missing or SayOnce; no dialogue changed");
                return;
            }
        }
        for (std::size_t i = kVanillaRefusals.size(); i < infos.size() - 1; ++i) {
            if (infos[i]->dataInfo != shared) {
                spdlog::error("Rental refusal response link changed; no dialogue changed");
                return;
            }
        }

        // Reapply state without requesting save persistence through AddChange.
        for (auto* info : infos) {
            info->saidOnce = true;
        }
        spdlog::info("Marked eleven rental refusal INFOs and their shared response heard");
    }

    void OnMessage(SKSE::MessagingInterface::Message* message)
    {
        switch (message->type) {
        case SKSE::MessagingInterface::kDataLoaded:
        case SKSE::MessagingInterface::kNewGame:
        case SKSE::MessagingInterface::kPostLoadGame:
            MarkRentalRefusalsHeard();
            break;
        default:
            break;
        }
    }
}

SKSEPluginLoad(const SKSE::LoadInterface* skse)
{
    if (skse->RuntimeVersion() != REL::Version{1, 7, 104, 0}) {
        return false;
    }
    auto logPath = SKSE::log::log_directory();
    if (!logPath) {
        return false;
    }
    *logPath /= "CandlehearthRentDim.log";
    auto sink = std::make_shared<spdlog::sinks::basic_file_sink_mt>(logPath->string(), true);
    auto log = std::make_shared<spdlog::logger>("CandlehearthRentDim", sink);
    spdlog::set_default_logger(std::move(log));
    spdlog::flush_on(spdlog::level::info);
    SKSE::Init(skse);
    spdlog::info("CandlehearthRentDim 0.1.2 on {}", skse->RuntimeVersion().string());
    return SKSE::GetMessagingInterface()->RegisterListener(OnMessage);
}
