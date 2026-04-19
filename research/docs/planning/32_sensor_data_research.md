# 16-Sensor Pressure Insole EDA Notes

## What the Data Looks Like

Long format - one row per sensor per timestamp, 32 rows per frame (L01–L16, R01–R16). This is different from our existing raw data which was wide format with one column per foot. Pipelines built on the old format will need updating if we go through with that.

Values are much more analog (0 to ~505), not so binary like before. We should have an easier time seeing pressure magnitude and distribution across the foot, not just so much on/off.

The previous system was technically analog but practically binary in that any real pressure immediately spiked to 4095 or close to it. The new data appears to genuinely use the full range, with low values like 8, 12, 28 on the light-contact end and 463, 484, 505 at the high end, and a spread of values in between. A few caveats worth knowing:

- 505 appears to be the effective ceiling (Possibly 512? A multiple of 2?). It may be that this sensor also saturates, just at a lower max. Worth confirming with the client if possible.
- Very low values (single digits) could be real light contact or sensor noise/crosstalk. Hard to say without more context or a super in depth dive with manual analysis of each contact.
- The distribution isn't a smooth spread - values tend to cluster either low (under 100) or high (over 300). It's less extreme than before but still somewhat bimodal in practice.

---

## Sampling Rate (The Main Issue)

The device is firing at roughly 7–8 Hz with some jitter (intervals vary from ~113ms to ~182ms). That means one frame every ~120–143ms on average.

A sprint ground contact is typically 80–150ms. At 7–8 Hz we're getting 1–2 frames per contact at best, sometimes zero (this is a major, major, major problem). Our existing pipeline detects IC and TO events and needs ~100 Hz to do that reliably. This data cannot feed that pipeline as-is.

- IC/TO detection and the existing stride transformation - not possible at this rate. We need to reliably catch the moment the foot hits and leaves the ground, and at 1–2 frames per contact we'll miss events entirely or get the timing badly wrong.
- Within-stride pressure flow analysis - not possible at this rate. Things like heel-to-toe progression require enough frames within a single contact to see pressure moving across the foot over time.
- Aggregate pressure per contact (average, peak) - not possible at this rate. If a contact only produces 1 frame we're treating a single snapshot as the whole contact, which is going to be inaccurate.
- Spatial distribution and foot zone loading - possible. Which zones of the foot are loading and how much is a per-frame question, not a temporal one, so the sampling rate doesn't hurt us as badly here.
- Asymmetry between feet - possible. As long as we can identify which foot is active in a given frame, comparing left vs right loading should be straightforward and the sampling rate doesn't hurt us as badly here.

For anything requiring within-stride resolution we'll need mock data at around 100 or more Hz to demonstrate the analytics until the hardware is upgraded.

---

## Sensor Coverage and Dead Sensors

All 32 sensors show up in every frame, so nothing is missing from the stream. However several sensors are consistently zero or near-zero across all four files:

- L04, L05, L09, L10 and R05, R06, R09, R10 - these are considered arch and lateral midfoot zones. This is honestly expected, since the arch of the foot doesn't load in sprinting.
- L06, L15, L16 and R15, R16 - these are considered heel and outer mid-arch. This seems to just be wrong and unexpected. The hop drill in particular should show heel contact and these sensors barely register across any recording. I can't confirm whether this is a dead sensors issue or a fit/placement issue. It's probably worth talking to the client to see if he can notice anything.

# Storage and Integration Idea

## New Tables Required

The pressure data doesn't mesh well with the RUN_METRICS table. The table stores one row per stride/step, whereas pressure data is one row per sensor per frame with no stride context. I think the best way to go about it is with two new tables, both linked to the existing RUN table via run_id.

---

## PRESSURE_FRAMES

Stores the raw sensor data as it came off the device. One row per timestamp, one column per sensor. This works because all 32 sensors fire together and represent one moment in time. Storing it as 32 separate rows would be a mess, unnecessary, and also make it less readable.

This data allows us to reprocess the data later with different aggregation logic without going back to the client for the original files. Once the hardware sampling rate improves, the same table structure will support much richer within-stride analysis without any schema changes. I believe it's also important for spatial asymmetry where we're comparing not just how much each foot loads but where on the foot, which requires the individual sensor values.

| column       | type        | description                |
| ------------ | ----------- | -------------------------- |
| frame_id     | UUID        | primary key                |
| run_id       | UUID        | foreign key to RUN         |
| timestamp_ms | BIGINT      | Unix epoch timestamp in ms |
| l01 – l16    | INTEGER     | left foot sensor values    |
| r01 – r16    | INTEGER     | right foot sensor values   |
| created_at   | TIMESTAMPTZ | row creation time          |

---

## pressure_contacts

Stores aggregated per-contact summaries derived from the raw frames. One row per contact per foot. This is the pre-computed summary layer that feeds coach-facing analytics directly, so we're not recalculating aggregates from the raw frames table every time something needs to be displayed.

Given the 7–8 Hz sampling rate this won't always be accurate, but it gives us a best-effort join between pressure and stride data.

| column            | type    | description                               |
| ----------------- | ------- | ----------------------------------------- |
| contact_id        | UUID    | primary key                               |
| run_id            | UUID    | foreign key to RUN                        |
| stride_num        | INTEGER | nullable, best-effort link to RUN_METRICS |
| foot              | VARCHAR | left or right                             |
| timestamp_ms      | BIGINT  | timestamp of the contact frame            |
| total_pressure    | INTEGER | sum of all active sensors for this foot   |
| peak_pressure     | INTEGER | highest single sensor value               |
| forefoot_pressure | INTEGER | sum of forefoot zone sensors              |
| midfoot_pressure  | INTEGER | sum of midfoot zone sensors               |
| heel_pressure     | INTEGER | sum of heel zone sensors                  |

# Coach-Facing Pressure Analytics

The existing system covers asymmetry and timing from a single pressure based system. This distributed pressure allows us to see where on the foot is loading happening, how hard, and whether that changes over the course of a run. This allows for some fun analytics.

---

## Selected Analytics

### Foot Zone Pressure Distribution

Breaks each foot into forefoot, midfoot, and heel zones and shows average pressure per zone across a run. Tells a coach whether an athlete is heel striking, midfoot, or forefoot dominant. This is something the existing system has no visibility into at all.

### Bilateral Pressure Asymmetry

Compares left and right loading broken down by zone. Two feet can have identical GCT but completely different loading patterns, and the existing asymmetry metrics would miss that. Zone-level asymmetry can show those differences.

### Pressure Drift Over Run

Tracks how zone distribution changes from the start to the end of a run. This is primarily to track fatigue and see if the athlete drifts from forefoot dominant to heel striking as they get tired.
