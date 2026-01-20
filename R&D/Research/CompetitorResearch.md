# StrideTrack Competitor Research

## Striv Smart Insoles

**TL;DR:** AI-powered smart insoles with pressure mapping and real-time voice coaching. $325 hardware + $96/year subscription. Consumer running focus.

**Target Market:** Recreational to competitive runners (5K to marathon), injury-prone athletes seeking prevention

**Technology Details:**
- **Pressure Sensors:** 256 textile pressure sensors per insole (512 total across both feet)
- **IMU:** 9-axis inertial measurement unit (accelerometer + gyroscope + magnetometer)
- **Barometer:** High-precision altitude/elevation tracking
- **Battery:** External pod clipped to shoe, 20-hour runtime, 2-3 hour charge time
- **Connectivity:** Bluetooth Low Energy to iOS/Android smartphone
- **Sampling Rate:** Not specified, pressure measured continuously
- **Form Factor:** Full insole replacement with integrated sensors

**Key Metrics:** GCT, Flight Time, Footstrike Pattern, Impact Forces, Foot Roll Direction (pronation/supination), Center of Pressure movement, Stride Variance, Power Output, Stride Efficiency Score

**Visualizations:**
- Real-time metrics dashboard displayed during runs
- Foot pressure heat maps showing force distribution across the foot
- Form score breakdowns with color-coded performance indicators
- Stride consistency graphs tracking variability over time
- Power and efficiency trend lines across training periods
- Left/right symmetry comparison bar charts
- Fatigue vs efficiency scatter plots
- Historical progress tracking with benchmark comparisons
- 3D foot motion visualization animations

**Strengths:** Real-time AI voice coaching during runs, detailed pressure distribution maps, adaptive training plans, 250+ sensors provide comprehensive foot data

**Weaknesses:** Insole format less comfortable than original insoles, battery pod visible on shoe exterior, ongoing subscription cost, running-only (no track & field specific features)

**vs. StrideTrack:** Both wearable systems measuring GCT/Flight Time, but Striv uses pressure mapping while StrideTrack uses force detection. Striv targets distance runners; StrideTrack targets sprinters/hurdlers. Striv requires replacing shoe insole; StrideTrack sensor inserts into existing shoe.

---

## Freelap Timing System

**TL;DR:** Electromagnetic timing system with transmitter cones and athlete-worn chips. Measures split times only—no biomechanics. $2,045 for 6-cone setup.

**Target Market:** Track & field coaches managing teams, football combine testing, multi-athlete training programs

**Technology Details:**
- **Transmitters:** Magnetic field emitting cones (Tx Junior Pro, Tx Touch Pro, e-Starter variants)
- **Chips:** FxChip BLE worn on athlete's waist, detects magnetic field crossings
- **Technology:** Electromagnetic field detection (not optical/infrared like photocells)
- **Accuracy:** 0.02 second precision
- **Range:** Wireless Bluetooth transmission up to 150 meters
- **Battery:** Tx cones use 2x AA batteries (user replaceable), chips use CR2032 or rechargeable
- **Connectivity:** Bluetooth to iOS/Android via MyFreelap app
- **Setup:** Place cones at checkpoints, athletes clip chip to waistband

**Key Metrics:** Split times, total time, reaction time (with e-Starter), time gaps, rankings—**NO biomechanical data whatsoever**

**Visualizations:**
- Live timing display showing real-time results as athletes cross transmitters
- Results tables with sortable athlete rankings by time
- Time comparison bar charts comparing athletes or sessions
- Split time breakdown tables showing checkpoint times
- Best/slowest time tracking with automatic PR detection
- PDF report exports of workout summaries
- Limited graphics—primarily data tables and simple charts, no biomechanical visualizations

**Strengths:** Time multiple athletes simultaneously across different distances, modular system (add more cones/chips), sub-60-second setup time, coach-focused team management

**Weaknesses:** Only measures timing intervals—cannot detect GCT, Flight Time, step count, or any form/technique data. Requires placing cones at each measurement point.

**vs. StrideTrack:** Fundamentally different products. Freelap answers "how fast" (split times); StrideTrack answers "how well" (biomechanics). Both target track & field coaches, but Freelap is for timing workouts while StrideTrack analyzes running mechanics.

---

## RunScribe

**TL;DR:** Dual IMU foot pods providing the most comprehensive gait metrics available. Originally consumer ($250), pivoted to B2B clinic model ($399). Professional data depth.

**Target Market:** Gait analysis clinics, physical therapists, podiatrists, biomechanics researchers, elite data-driven athletes

**Technology Details:**
- **IMU Sensors:** 9-axis motion sensors (3-axis accelerometer + 3-axis gyroscope + 3-axis magnetometer)
- **High-G Accelerometer:** 400G capacity for capturing peak impact forces
- **Sampling Rate:** 500Hz (RunScribe Plus) or 1000Hz (RunScribe Red)
- **Additional Sensors:** Altitude sensor, temperature sensor
- **Optional Sacral Pod:** 3rd IMU for hip/pelvis tracking (RunScribe Gait Lab system)
- **Mounting:** Lace-mounted clips (one pod per shoe)
- **Battery:** Rechargeable via dual-pod USB-C charging cradle
- **Memory:** 32MB onboard storage for offline recording
- **Connectivity:** Bluetooth to smartphone, Garmin Connect IQ integration

**Key Metrics:** Contact Time, Flight Time, Flight Ratio, Cadence, Stride Length, Footstrike Type (with heat maps), Pronation Angle & Velocity, Toe-Off Angle, Impact Gs, Braking Gs, Ground Reaction Force, Running Power, Leg Spring Stiffness, **Left/Right symmetry on ALL metrics**

**Visualizations:**
- ShoePrint visual maps showing footstrike and toe-off positions
- ShoeRide animations displaying dynamic foot contact progression through stance phase
- Time-series metric charts for all parameters across runs
- Left vs. right symmetry overlays with side-by-side comparisons
- Community percentile rankings showing where you rank in RunScribe database
- Stride efficiency dashboards with multi-metric color-coded zones
- Impact force heat maps visualizing shock distribution patterns
- Historical trend tracking charts for technique improvement over time

**Strengths:** Most comprehensive gait metrics available from wearable, bilateral (L/R) comparison across every metric, professional multi-patient management, raw IMU data export for research, "ShoePrint" visualization of foot contact progression

**Weaknesses:** Complex data interpretation requires expertise, shifted to B2B model making consumer purchase difficult, $399 clinic version requires annual subscription, too much data overwhelming for casual users

**vs. StrideTrack:** Both measure GCT and Flight Time with wearable sensors. RunScribe uses high-frequency IMUs to infer ground contact; StrideTrack uses direct force sensing. RunScribe captures much deeper biomechanics (pronation, impact forces, power) but requires expertise. RunScribe serves professionals/elites; StrideTrack targets college track coaches needing actionable sprint metrics.

---

## NURVV Run - (Site is down, maybe out of business?)

**TL;DR:** Pressure-sensing insoles with 32 sensors focused on injury prevention and footstrike analysis. Originally $300, frequently discounted to $70-100. Good for roads, struggles on trails.

**Target Market:** Injury-prone recreational runners, road-focused athletes, runners seeking biomechanical insights without clinic visits

**Technology Details:**
- **Pressure Sensors:** 16 sensors per insole (32 total) sampling at 1000Hz
- **Sensor Distribution:** Spread across heel, midfoot, forefoot regions
- **GPS Trackers:** External pods clipping to shoe ankle collar with integrated GPS + INS (Inertial Navigation System)
- **Battery:** Lithium polymer, 5-hour runtime, charges via proprietary clip connector
- **Connectivity:** Bluetooth to iOS/Android, compatible with Apple Watch and Garmin watches
- **Water Resistance:** IP67 rated
- **Form Factor:** Ultra-slim insoles placed UNDER existing shoe insole (not as replacement)
- **Lifespan:** 1,500 miles before insole replacement needed

**Key Metrics:** Footstrike Location (heel/mid/forefoot with %), Pronation Percentage & Type, Pressure Distribution Heat Maps, GCT, Cadence, Step Length, Balance (L/R symmetry), Running Power, Running Health Score, Training Load

**Visualizations:**
- Pressure heat maps with color-coded foot pressure distribution per run segment
- Footstrike breakdown pie charts showing heel/midfoot/forefoot percentages
- Pronation graphs with time-series angles and neutral zones highlighted
- Running Health dashboard providing multi-factor health score with trend indicators
- Training load timeline showing weekly/monthly patterns with recovery recommendations
- Balance symmetry bar charts comparing left vs. right
- Pace Coach target zones with real-time barbell indicator showing zone adherence
- Comprehensive post-run reports with multi-page analysis of all key metrics

**Strengths:** Detailed pressure mapping shows exactly where foot contacts ground, injury risk prediction via Running Health Score, Pace Coach feature for structured workouts, works standalone (without phone via button press)

**Weaknesses:** 5-hour battery insufficient for ultras/long training days, insole placement adds bulk affecting shoe fit, poor performance on technical trails (terrain interference), proprietary charger easily breaks, $300 MSRP high for features delivered

**vs. StrideTrack:** Both measure GCT via foot sensors. NURVV uses distributed pressure sensors; StrideTrack uses force-sensitive resistor. NURVV provides pressure distribution maps; StrideTrack focuses on temporal metrics (GCT, Flight Time, splits). NURVV targets distance runners on roads; StrideTrack targets sprinters/hurdlers on track. NURVV insole format vs. StrideTrack in-shoe sensor placement.

---

## Microgate OptoJump Next

**TL;DR:** Professional optical measurement system using infrared LED bars. No wearables required. $15K-25K for lab/clinic use.

**Target Market:** Professional sports teams, university athletic programs, medical/rehab clinics, biomechanics research labs

**Technology Details:**
- **Optical System:** Transmit (TX) and receive (RX) bars with infrared sensor
- **Setup:** Bars placed parallel on floor/treadmill, max 6m separation, no cables between bars
- **Video Integration:** Up to 2 webcams recording at 30fps, synchronized with sensor data
- **Power:** AC mains or battery (8 hours autonomous)
- **Software:** Windows desktop application with athlete database

**Key Metrics:** Ground Contact Time, Flight Time, Step Count, Stride Length, Cadence, Stride Symmetry, Imbalance Index, Speed, Jump Height, Reaction Time

**Visualizations:**
- Real-time bar graphs of contact/flight times during testing
- Line graphs showing temporal progression across runs
- Spider/radar charts for multi-parameter athlete comparisons
- Video playback synchronized with measurement data
- 2D position mapping showing foot centroid movement
- Heat maps for pressure distribution analysis
- Comparative charts (athlete vs athlete, session vs session)
- PDF report generation with comprehensive graphs and metrics

**Strengths:** Lab-grade accuracy, comprehensive spatial data, video synchronization, non-invasive (no wearables)

**Weaknesses:** $15K-25K price point, requires controlled environment, setup time 5+ minutes, completely non-portable

**vs. StrideTrack:** Both measure GCT and Flight Time, but OptoJump uses stationary optical infrastructure while StrideTrack uses wearable force sensors. OptoJump captures spatial positioning (where foot lands); StrideTrack focuses on temporal metrics (when/how long).


## Competitive Positioning

| Competitor | Price | Technology | Target | Core Strength | Major Limitation |
|------------|-------|-----------|--------|---------------|------------------|
| **OptoJump** | $15K-25K | Optical (LED bars) | Pro labs | Lab accuracy, spatial data | Non-portable, indoor only |
| **Striv** | $325 + $96/yr | Pressure insoles (256 sensors) | Runners | AI coaching, pressure maps | Insole discomfort, subscription |
| **Freelap** | $2K-2.6K | EM field (cones + chip) | Coaches | Multi-athlete timing | Timing only, no biomechanics |
| **RunScribe** | $250-399 | IMU pods (500-1000Hz) | Gait pros | Deepest metrics, L/R symmetry | Too complex, B2B pivot |
| **NURVV** | $70-300 | Pressure insoles (32 sensors) | Road runners | Injury prediction, pressure data | 5hr battery, trail issues |
| **StrideTrack** | $199 + $89 | Force sensors + ESP32 | T&F coaches | Sprint/hurdle focus, simplicity | TBD |

---

## Key Takeaways

**Market Positioning:**
- No competitor specifically targets track & field sprinting/hurdling—most focus on distance running (Striv, NURVV) or general athletics (RunScribe, OptoJump)
- StrideTrack's force sensor approach is simpler than IMU-based systems, enabling faster data processing and lower cost
- StrideTrack seems to be one of the only products focusing less on overwhleming statistics to dig through and more on quick actionable measurements to improve on during practice

**Technology Differentiation:**
- Force sensors directly measure ground contact (binary on/off), while IMUs infer it from acceleration data—different approaches for same metrics
- Insole formats (Striv, NURVV) consistently show comfort and fit issues across reviews
- Dual-sensor systems (RunScribe, StrideTrack's planned L/R design) enable powerful symmetry analysis that single-sensor systems cannot provide

---

## Feature Comparison Matrix

| Feature | OptoJump | Striv | Freelap | RunScribe | NURVV | StrideTrack |
|---------|:--------:|:-----:|:-------:|:---------:|:-----:|:-----------:|
| **GCT** | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| **Flight Time** | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ |
| **Step Count** | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| **Hurdle Splits** | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ |
| **Pressure Mapping** | ❌ | ✅ (256) | ❌ | ❌ | ✅ (32) | ❌ |
| **Pronation** | ❌ | ✅ | ❌ | ✅ | ✅ | ❌ |
| **Running Power** | ❌ | ❌ | ❌ | ✅ | ✅ | Future |
| **L/R Symmetry** | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ (planned) |
| **Real-Time Data** | ✅ | ✅ | ✅ | ✅ | ✅ | Post-run |
| **Battery Life** | 8hr | 20hr | Varies | 20+hr | 5hr | TBD |
| **Wearable Type** | None | Insole | Waist | Lace pod | Insole | In-shoe sensor |
| **Setup Time** | 5+ min | Instant | <1 min | Instant | 2-3 min | Instant |
| **Track Focus** | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ |

---

## Pricing Summary

| Product | Hardware | Subscription | Year 1 Total | Ongoing Annual |
|---------|----------|--------------|--------------|----------------|
| OptoJump (10m) | $20,000 | Included | $20,000 | $0 |
| Striv | $325 | $96/yr | $421 | $96 |
| Freelap (6-cone) | $2,045-2,649 | $0 | $2,045-2,649 | $0 |
| RunScribe | $250-399 | $0-99/yr | $250-399 | $0-99 |
| NURVV | $70-300 | $0 | $70-300 | Insole replacement (~$150/yr at 3000mi/yr) |
| **StrideTrack** | **$199** | **$89/yr** | **$288** | **$89** |

---

## Links

**OptoJump Next**
- Product page: https://training.microgate.it/en/products/optojump-next
- Modular system: https://training.microgate.it/en/products/optojump-next/modular-system
- User manual: https://www.manualslib.com/manual/920247/Microgate-Optojump-Next.html
- FAQ: http://www.optojump.com/Support/Faq.aspx

**Striv**
- Official site: https://striv.run/
- Analysis features: https://striv.run/analysis
- Sensor tech: https://striv.run/sensors
- Press release: https://finance.yahoo.com/news/striv-unveils-ai-powered-insoles-150000223.html
- User manual: https://a.striv.run/manual
- Kickstarter: https://www.kickstarter.com/projects/striv/striv-meet-your-personal-running-coach/faqs

**Freelap**
- Official site: https://www.freelap.com/
- US site: https://www.freelapusa.com/
- Timing systems: https://www.freelap.com/timing-systems/
- FAQ: https://www.freelapusa.com/faq/

**RunScribe**
- Official site: https://runscribe.com/
- RunScribe Red: https://runscribe.com/red/
- Sacral pod: https://runscribe.com/the-importance-of-sacral-data-our-new-release/
- Review (The5kRunner): https://the5krunner.com/2018/01/05/runscribe-plus-review-running-power-meter/
- B2B pivot: https://the5krunner.com/2019/02/04/runscribe-new-direction/
- Outdoor analysis: https://simplifaster.com/articles/outdoor-gait-analysis-wearables/

**NURVV**
- Official site: https://www.nurvv.com/en-us/
- Product page: https://www.nurvv.com/en-us/products/nurvv-run-insoles-trackers/
- Runner's World review: https://www.runnersworld.com/gear/a37578474/nurvv-run-smart-insoles-review-2022/
- T3 review: https://www.t3.com/reviews/nurvv-run-review
- DC Rainmaker: https://www.dcrainmaker.com/2021/02/nurvv-depth-review.html
- NBC guide: https://www.nbcnews.com/select/shopping/nurvv-run-smart-insoles-ncn1269954
