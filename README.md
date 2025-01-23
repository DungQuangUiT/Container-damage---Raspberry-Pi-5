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

## Demo csv

# Container Damage Report

## Detailed Damage Assessment

| Container ID | Time | Image Path | Damage Types | Damage Details | Total Cost |
|--------------|------|------------|--------------|----------------|------------|
| 1 | 10/22/2024 17:40 | data\1\1a605a35-9062-11ef-913d-005056c00008.jpg | None | No damage found | $0 |
| 2 | 10/22/2024 17:41 | data\2\33952cba-9062-11ef-a8c3-005056c00008.jpg | Dent | - Base Cost: $50<br>- Confidence: 0.26<br>- Severity: Dim<br>- Adjusted Cost: $6.46<br>- Penalty: No | $6.46 |
| 3 | 10/22/2024 17:41 | data\3\391ab12d-9062-11ef-aec4-005056c00008.jpg | Dent (2), Hole (1) | **Dent 1:**<br>- Base Cost: $50<br>- Confidence: 0.67<br>- Severity: Moderate<br>- Adjusted Cost: $40.40<br>- Penalty: No<br><br>**Hole:**<br>- Base Cost: $100<br>- Confidence: 0.43<br>- Severity: Minor<br>- Adjusted Cost: $43.08<br>- Penalty: No<br><br>**Dent 2:**<br>- Base Cost: $50<br>- Confidence: 0.29<br>- Severity: Dim<br>- Adjusted Cost: $6.86<br>- Penalty: Yes (4% reduction) | $90.34 |
