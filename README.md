# EMBEDDED CONTAINER DAMAGE DETECTION

## Overview
An automated system using Raspberry Pi 5 and YOLOv10 for detecting and assessing container damages through image processing and AI.

## Features
- Automated container damage detection
- Identifies three types of damage: Dent, Hole, Rust
- Real-time image processing
- Damage cost estimation

## Hardware Requirements
- Raspberry Pi 5 (4GB)
- OV5647 5MP Camera Module
- ESP32-CAM (optional)
- Infrared proximity sensor

## Usage Workflow
1. Container arrives at inspection station
2. Infrared sensor detects container position
3. Camera captures container images
4. YOLOv10 model processes images
5. Damage types and locations identified
6. Damage cost calculated and logged

## Output
- CSV file with:
  - Image path
  - Detected damage types
  - Confidence levels
  - Estimated repair costs
- Folder contain reference image

## Performance Metrics
- Overall Precision: 0.68
- Overall Recall: 0.554
- mAP-50: 0.557