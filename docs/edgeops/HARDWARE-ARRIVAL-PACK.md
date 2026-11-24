# EDGEOPS hardware preparation pack

**Preparation only — physical acceptance pending.** The owner reports partial hardware receipt; the full set, exact variants, wiring, calibration and acceptance are unverified. The original 30-product selection is unchanged. No equipment connection or operation is authorized by this download.

[Download the version-two ZIP](assets/EDGEOPS-original-30-arrival-pack-v2.zip?raw=true) · [SHA-256 and source provenance](arrival-pack-manifest.json) · [Saved offline verification](arrival-pack-verification.json) · [Project evidence](EVIDENCE.md)

## Contents and source

The ZIP contains the fixed-30 plan/matrix, conditional connection preparation sources, a blank receipt worksheet, existing ESP32 firmware/build configuration, capture/conversion tools, the offline timing/validity summary, tests and the pending H1 checklist. Wider production-design links require the full project repository.

Source: application commit [`99e989a`](https://github.com/shah-hussain-bangash/AI-Edge-Semiconductor-Career-Projects./commit/99e989aff13e78d2b145f159d350f079bdf85371), still in [draft PR #2](https://github.com/shah-hussain-bangash/AI-Edge-Semiconductor-Career-Projects./pull/2). [Pack review](https://github.com/shah-hussain-bangash/AI-Edge-Semiconductor-Career-Projects./blob/99e989aff13e78d2b145f159d350f079bdf85371/projects/industrial-edge-ai-predictive-maintenance/dashboard/reviews/2026-11-24-arrival-pack-source-completeness.md).

Archive: **83,360 bytes**. SHA-256: `c368c2e26be94ea313a7e2f4ce8f7fa932488cc9d8582df68a295eda8cb878e7`.

## Verify before extraction

Use an independently reviewed copy of [verify_arrival_pack.py at the pinned source](https://github.com/shah-hussain-bangash/AI-Edge-Semiconductor-Career-Projects./blob/99e989aff13e78d2b145f159d350f079bdf85371/projects/industrial-edge-ai-predictive-maintenance/dashboard/verify_arrival_pack.py). The archive's own checker is included for convenience and cannot authenticate its archive.

With Python 3.12 or later, from the directory containing that reviewed checker and the downloaded ZIP:

```powershell
python verify_arrival_pack.py EDGEOPS-original-30-arrival-pack-v2.zip
```

The checker reads bounded ZIP members without extracting or running their contents. Exit 0 means internal file consistency passed; it does not establish trusted origin, correct wiring or hardware acceptance. The current checker supports exact version-one and version-two inventories; an older version-one-only checker rejects version two. Keep existing archives unchanged.

After independent review, keep the original ZIP and blank worksheet unchanged; edit a separate worksheet copy. An aggregate report that some parts arrived must not mark individual items received. The dashboard's existing local worksheet preview treats entries as unverified owner declarations and does not enroll hardware.

## Recorded software checks

- 31 pack/API tests passed, including exact inventory/version checks and legacy compatibility.
- The actual previously saved version-one ZIP passed the updated checker unchanged.
- Version two passed offline verification: 32 non-manifest files and all 30 categories checked.
- All 60 hardware-side software tests passed from a temporary extraction of the trusted, newly generated pack. These are separate executions, not a combined unique-test total.

Application CI at `99e989a`: [Dashboard checks](https://github.com/shah-hussain-bangash/AI-Edge-Semiconductor-Career-Projects./actions/runs/45384433263) · [Browser acceptance](https://github.com/shah-hussain-bangash/AI-Edge-Semiconductor-Career-Projects./actions/runs/45384433324) · [Experiment registry](https://github.com/shah-hussain-bangash/AI-Edge-Semiconductor-Career-Projects./actions/runs/45384433317) · [Model comparison](https://github.com/shah-hussain-bangash/AI-Edge-Semiconductor-Career-Projects./actions/runs/45384433243) — all observed successful on 24 November 2026.

This is neither a signed release nor evidence of actual sensor performance. Motor operation, real acquisition, physical acceptance, merging and deployment remain outside this artifact.
