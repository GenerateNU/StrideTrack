# Breakdown of the Turin (Politecnico di Torino) Running Project

[Politecnico di Torino – Running Analysis Thesis (PDF)](https://webthesis.biblio.polito.it/25728/1/tesi.pdf)

## Project Overview

_More information avaible at (Abstract, p. III)_

The goal of the Politecnico di Torino project was to figure out the best way to detect when a runner's foot hits the ground, **initial contact (IC)**, and when it leaves the ground, **final contact (FC)**, across both slow runs and full-speed sprints.

The project focuses on timing-based running metrics like **how long each step takes**, **how long the foot stays on the ground**, and **how long it stays in the air**. These timing measurements are useful for understanding performance and potential injury risks.

A key goal of the study was to make sure these measurements work outside of a lab, using wearable sensors instead of specialized lab equipment, which is the same idea we're seeing with StrideTrack.

The researchers tested it across a bunch of different types of runs and speeds. Data collection took place among three main scenarios:

- Recreational running at **8 km/h and 10 km/h** in both indoor and outdoor environments.
- Treadmill running at **14 km/h**.
- Elite sprinting on an outdoor track with speeds ranging from **20 km/h to 32 km/h**.

This system was tested in the same kinds of situations StrideTrack is meant to support. The data covers normal training runs, structured workouts, and high-speed track sessions, making it a strong fit for StrideTrack's data pipeline.

## System Architecture Overview

_More information avaible at (Abstract, p. III)_

The Turin system uses both shoe-mounted motion sensors and pressure-sensing insoles. The shoe-mounted sensors collect the main data, while the pressure insoles are used only to double-check that the data is correct.

During testing, every runner was **"equipped with a MIMU fixed to the shoelaces of each shoe"**. These sensors captured how the foot moved during each step.

In the project, the primary tracking was done using shoe-mounted motion sensors, which were responsible for detecting step timing and foot contact events. The pressure-sensing insole was used only as a validation tool to confirm that the motion sensors were detecting these events accurately.

This does not mean the researchers lacked or avoided data from the sole of the shoe. **It is a design choice to rely on motion sensors as the main input, while using pressure data to verify correctness during testing**.

## Shoe-Mounted Magneto-Inertial Measurement Units (MIMUs)

_More information avaible at (Section 1.3.1.1, p. 23 - Section 1.3.1.3, p. 28)_

The main sensors used in the Turin system are **magneto-inertial measurement units (MIMUs)**, which are small motion sensors attached directly to the athletes' shoes. A MIMU combines three types of sensors that work together to track how the foot moves:

- **Tri-axial accelerometer:** measures how fast the foot is speeding up or slowing down in different directions, which is useful for detecting foot strikes and impacts.
- **Tri-axial gyroscope:** measures how the foot rotates as it moves through each step, helping identify swing and push-off motion.
- **Tri-axial magnetometer:** measures orientation relative to the Earth's magnetic field, which can help with direction and overall foot orientation.

Since the shoe-mounted motion sensors were used to capture **both timing-based data and movement-based data**, they can estimate not only when events happen (like foot contact times), but also how the foot moves through space.

In contrast, our current insole-based approach focuses primarily on **temporal data** such as how long the foot is on the ground by measuring pressure under the foot.

## Sensorised Pressure Insoles (Validation Reference)

_More information available at (Section 1.3.2.4, p. 32; Figure 1-13)_

The pressure insoles used for validation were placed inside the shoe and contained 16 pressure sensors spread across the sole. Their purpose was not to measure detailed foot pressure patterns. They just provide reliable timing information for when the foot touched and left the ground.

Each pressure sensor responds to force applied under the foot and outputs a signal that changes as pressure increases or decreases.

The key takeaway is that the pressure insoles were used only for validation, not as a required part of the system. For StrideTrack, this means pressure sensors are a design option and will work perfectly fine for basic statistics. However they are not strictly necessary to support core timing-based metrics if we ever chose to move past this model.

# Sensors in Devices

## Motion Sensors (IMUs)

### Accelerometer

- Measures how quickly the foot speeds up or slows down.
- Useful for detecting foot strikes and impacts.
- Produces high-frequency motion data.

### Gyroscope

- Measures how the foot rotates during each step.
- Useful for identifying swing, push-off, and foot clearance.

### Magnetometer

- Measures orientation relative to the Earth's magnetic field.
- Sometimes used for direction or heading.

Together, these sensors can estimate **both timing-based data** (when the foot hits or leaves the ground) and **movement-based data** (how the foot moves through space).

## 3.2 Pressure Sensors (In-Shoe Insoles)

Pressure insoles are really strong at capturing **temporal data**, such as when the foot is in contact with the ground.

Unlike IMUs, pressure sensors do not track how the foot moves through space which makes timing-based metrics simple and reliable since they don't have to be derived from deceleration or other metrics.

## Possible Output Data

### Sampling Rate

In the Turin project, the shoe-mounted motion sensors collected data at **100 Hz** in most running tests. This means the sensors recorded movement data 100 times per second.

The Turin project, shows that sampling rates around **100–200 Hz** should be completely sufficient to reliably detect all running metrics.

The thesis explains that using a 100 Hz sampling rate helped **reduce computational load** while still allowing reliable detection of these key running events. In other words, the researchers showed that very high sampling rates were **not necessary** to accurately measure foot contact timing during running.

### IMU Output (Motion-Based)

IMU data gets recorded as motion signals over time. A typical structure would look something like:

```text
timestamp,
acc_x, acc_y, acc_z,
gyro_x, gyro_y, gyro_z
```

This data represents how the foot is moving and rotating at each moment in time. However, without data directly from the source there's no way of determining exactly the format the metrics would take.

### Pressure Insole Output (Contact-Based)

Pressure insole data gets recorded as pressure values over time. A typical structure would look something like:

```text
timestamp,
pressure_1, pressure_2, ..., pressure_n
```

This data represents when the foot is on or off the ground based on applied pressure. However, without data directly from the source there's no way of determining exactly the format the metrics would take.

# TLDR

## What the Turin project studied

- The project focused on detecting when the foot hits the ground (Initial Contact) and when it leaves the ground (Final Contact) during running.
- From these two events, they derived timing-based metrics like step duration, flight time, etc.
- The system was tested across real training conditions, from slow runs to elite sprinting up to 32 km/h.
- Closely matches the real-time enviornments and goals of StrideTrack.

## How the system worked

- The main data came from shoe-mounted motion sensors (IMUs) attached to the laces.
- Pressure insoles were used as a validation reference to confirm the motion sensor results.

## What sensors were inside

- **Tri-axial accelerometer:** measures how fast the foot is speeding up or slowing down in different directions, which is useful for detecting foot strikes and impacts.
- **Tri-axial gyroscope:** measures how the foot rotates as it moves through each step, helping identify swing and push-off motion.
- **Tri-axial magnetometer:** measures orientation relative to the Earth's magnetic field, which can help with direction and overall foot orientation.

Since the shoe-mounted motion sensors were used to capture **both timing-based data and movement-based data**, they can estimate not only when events happen (like foot contact times), but also how the foot moves through space.

## Sampling Rate

- The motion sensors collected data at 100 Hz, meaning 100 samples per second.

## Implications

- Pressure insoles and motion sensors are both valid approaches depending on desired metrics.
- An IMU would allow for much deeper analysis of how the foot moves during each step, not just when it hits the ground.
