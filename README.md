# GreenSummarizer

GreenSummarizer is an offline, AI-powered text and PDF summarization mobile application built with Python, Kivy, and KivyMD. Designed to be a "Green AI" tool, it provides fast, pure-Python extractive summarization without relying on cloud APIs. This preserves user privacy, saves internet bandwidth, and extends battery life on mobile devices.

## Features
- **Offline Processing:** No data is sent to the cloud. All logic executes locally.
- **Multiple NLP Algorithms:** Compares 4 extractive summarization algorithms:
  - Frequency Rank
  - TF-IDF Rank
  - TextRank
  - Hybrid Green Mode (default, optimized for speed and low energy)
- **PDF Extraction:** Built-in extraction for text-based PDFs.
- **Green Analytics Dashboard:** Tracks latency, internet data saved, and estimates battery drain, energy usage, and carbon footprint (gCO₂e) per task.
- **Model Comparison:** Directly compare the algorithms to find the most efficient one for a given document.
- **Local History:** Saves previous summaries using SQLite.

## Architecture
The app follows a modular architecture separating the UI from business logic:
- `app/`: Contains the Kivy app entry point, routing, and theming.
- `screens/`: Contains individual KivyMD UI screens.
- `widgets/`: Reusable custom UI components (Metric Cards, Charts).
- `summarizers/`: NLP extractive logic (pure Python, offline).
- `documents/`: PDF extraction (pypdf) and intelligent chunking for long text.
- `metrics/`: Energy, latency, battery, and data profiler.
- `storage/`: SQLite database and settings store.

## Folder Structure
```
green_summarizer/
├── README.md
├── requirements.txt
├── buildozer.spec
├── main.py
├── app/
├── screens/
├── summarizers/
├── documents/
├── metrics/
├── storage/
├── widgets/
├── utils/
└── tests/
```

## How Metrics are Calculated
Since accurate hardware power telemetry is often restricted on Android, GreenSummarizer uses the following approaches:
- **Latency:** Measured via standard timestamp differences (`end_time - start_time`).
- **Data Usage:** On Android, attempts to read `TrafficStats` via `pyjnius` to confirm 0 data usage.
- **Battery & Power:** Attempts to read real-time Android `BatteryManager` metrics (current, voltage).
- **Energy Estimate:** If hardware current is unavailable, falls back to estimating based on battery percentage drop, user-configured battery capacity (mAh), and nominal voltage (`Energy(Wh) = Capacity(mAh) * Nominal Voltage(V) * (Delta % / 100) / 1000`). For ultra-fast tasks where delta is 0%, an empirical estimation is used based on time.
- **Carbon Footprint:** `Energy (kWh) * Regional Grid Factor (gCO₂e/kWh)`. Configurable in Settings.
- **Efficiency Score:** A proprietary score (0-100) that penalizes high latency, high energy use, high data use, and over-compression.

## Limitations
- **Energy/Carbon are Estimates:** Accurate power tracking depends on the specific Android device hardware reporting capabilities.
- **Scanned PDFs:** The MVP supports text-based PDFs. Image-based or scanned PDFs require OCR, which is not currently included. If an image PDF is detected, the app shows a fallback message.
- **Extractive Only:** Models use extractive summarization (selecting key sentences) rather than generative abstractive summarization.

## Setup & Running on Desktop (Smoke Test)

1. Clone the repository.
2. Install requirements:
   ```bash
   pip install -r green_summarizer/requirements.txt
   ```
3. Run the app:
   ```bash
   python green_summarizer/main.py
   ```
   *Note: On desktop, Android-specific pyjnius APIs will gracefully fallback to estimations.*

## Tests
Automated tests are located in the `tests/` directory. They utilize `pytest` and temporary directories.
Run them using:
```bash
python -m pytest -q
```

## Android / Buildozer Build

To package this application as an Android APK:
1. Ensure you have Buildozer installed on a Linux environment (or WSL). It is highly recommended to use Linux for building.
2. Run the build command in the root directory:
   ```bash
   cd green_summarizer
   buildozer android debug
   ```
3. The resulting APK will be placed in `green_summarizer/bin/`. You can then install it on your device for real-world profiling.

## Future Scope
- **OCR Support:** Add support for scanned PDFs using pytesseract or similar offline libraries.
- **Abstractive Models:** Integrate quantized ONNX/TFLite small models (e.g., MobileBERT) when device hardware improves.
- **Multi-language:** Expand stopword filtering and logic for non-English languages.
- **Export Reports:** Generate shareable reports containing summaries and green metrics.
- **Real Power Profiling:** Deeper integration with Android root tools for exact power measurement on rooted devices.
