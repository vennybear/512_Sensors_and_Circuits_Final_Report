# Cosmic Tilt: A 90s-Style Embedded Reflex Game

**Cosmic Tilt** is a handheld electronic reflex game inspired by 90s classics like *Bop It* and *Brain Warp*. Built using **CircuitPython** on the **Seeed Xiao ESP32C3**, the game challenges players to respond to rapid-fire commands using motion (tilting) and tactile inputs (twisting) under increasingly difficult time constraints.

![Final Product](images/final_product.jpg)
*(Note: Please replace `Images/final_product.jpg` with the actual path to your photo)*

## 🎮 Project Overview

*   **Goal:** Correctly input the displayed command before the timer runs out.
*   **Levels:** 10 Levels of increasing speed.
*   **Modes:** 4 Difficulty settings (Easy, Medium, Hard, Difficult).
*   **Feedback:** OLED screen for instructions, NeoPixel for status, and Rotary Encoder for menu navigation.

## 🕹️ How to Play

1.  **Power On:** Toggle the latching switch on the side. The screen will light up, and the LED will glow Blue.
2.  **Select Difficulty:** Rotate the knob to scroll through difficulties:
    *   **EASY:** 3.0 seconds per move.
    *   **MED:** 2.2 seconds per move.
    *   **HARD:** 1.5 seconds per move.
    *   **DIFF+:** 0.8 seconds per move (Extreme mode).
    *   *Press the knob to confirm and start.*
3.  **The Game Loop:**
    *   **"LEFT / RIGHT / FORWARD / BACK":** Physically tilt the device in the direction shown.
    *   **"TWIST":** Rotate the knob in any direction.
4.  **Win/Loss:**
    *   **Victory:** Complete 10 levels to see the Win Screen and Rainbow LED animation.
    *   **Game Over:** If you run out of time or make the wrong move, the Red LED lights up. Press the knob to restart.

## 🛠️ Hardware Implementation

This project utilizes a modular design on a perfboard. All components are connected via **female headers**, ensuring that the microcontroller and sensors can be easily removed or replaced.

![Internal Wiring](Images/wiring_inside.jpg)
*(Note: Please replace with your internal wiring photo)*

### Component List
*   **Microcontroller:** Seeed Xiao ESP32C3
*   **Motion Sensor:** ADXL345 Accelerometer (I2C)
*   **Display:** 0.96" SSD1306 OLED (I2C)
*   **Input:** EC11 Rotary Encoder with Push Button
*   **Feedback:** Single NeoPixel LED
*   **Power:** 3.7V LiPo Battery + Latching Push-Button Switch

### Circuit Diagram
The circuit includes a power management circuit where the battery is connected via a JST connector, and the positive line runs through a latching switch to the Xiao's 5V pin.

*   [View System Block Diagram](Documentation/System_Block_Diagram.png)
*   [View Circuit Diagram](Documentation/Circuit_Diagram.pdf)

*(Make sure you upload these diagrams to a folder named 'Documentation' in your repo)*

## 📦 Enclosure Design

The enclosure was designed in **Autodesk Fusion 360** and 3D printed using **White PLA**.

### Design Features:
*   **Sandwich Structure:** Consists of a deep base and a flat lid, secured by four M3 screws.
*   **Component Mounting:**
    *   The **Perfboard** sits on 4 internal printed pillars (5mm height) to protect the wiring underneath.
    *   The **Rotary Encoder** and **Power Switch** are panel-mounted for stability.
    *   **Cutouts:** Precise cutouts were made for the OLED screen, NeoPixel, and USB-C charging port.
*   **Ergonomics:** Filleted edges (rounded corners) ensure a comfortable grip during handheld gameplay.

## 💻 Software Logic

The code is written in **CircuitPython 9.x**.

### Key Technical Implementation:
1.  **DisplayIO Graphics:** Utilizes the modern `displayio` library and the built-in `terminalio.FONT` for flicker-free, scalable text rendering without external font files.
2.  **Software Encoder Driver:** Due to hardware limitations on the specific Xiao firmware, a custom **Software-based Debouncing Class** was written to read the Rotary Encoder's GPIO signals accurately.
3.  **Sensor Filtering:** The ADXL345 accelerometer data is read and compared against a threshold (6.0 m/s²) to distinguish deliberate tilts from natural hand tremors.
4.  **Hardware Fail-Safe:** The code includes a startup check. If the OLED or ADXL is not detected (e.g., loose wire), it attempts to reconnect 3 times and reports the error via Serial.

## 📂 File Structure

```text
Cosmic-Tilt-Game/
├── README.md               # Project Overview
├── code.py                 # Main Source Code
├── lib/                    # CircuitPython Libraries
│   ├── adafruit_displayio_ssd1306.mpy
│   ├── adafruit_adxl34x.mpy
│   ├── neopixel.mpy
│   └── ...
├── Documentation/          # Diagrams (Assignment 4)
│   ├── System_Block_Diagram.png
│   └── Circuit_Diagram.pdf
└── Images/                 # Project Photos
    ├── final_product.jpg
    └── wiring_inside.jpg
