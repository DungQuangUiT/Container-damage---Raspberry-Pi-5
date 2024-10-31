import cv2
import urllib.request
import numpy as np
from picamera2 import Picamera2
from ultralytics import YOLO
import csv
from datetime import datetime
import uuid
import os
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)

url='http://192.168.0.122/cam-mid.jpg'
im=None

# Damage types with base costs (in currency units)
damages = {0: 'dent', 1: 'hole', 2: 'rust'}
base_costs = {0: 50, 1: 100, 2: 30}  # Base cost for dent, hole, rust
index = 0   # Container ID

# Function to calculate repair cost and generate a detailed report
def calculate_repair_cost(detected_objects, penalty_rate=1):
    total_cost = 0
    damage_count = {0: 0, 1: 0, 2: 0}  # To track how many of each damage type were detected
    cost_count = {0: 0, 1: 0, 2: 0}  # To track how much of each damage type cost
    report = []  # To store detailed report information
    statistics = [] # To store number and cost for each type

    for obj in detected_objects:
        damage_type = obj['class_id']
        confidence = obj['confidence']

        # Base cost for the detected damage type
        base_cost = base_costs[damage_type]

        # Severity-based multiplier
        if confidence > 0.8:
            severity_multiplier = 1.5  # Severe
            severity = 'Severe'
        elif confidence > 0.6:
            severity_multiplier = 1.2  # Moderate
            severity = 'Moderate'
        elif confidence > 0.4:
            severity_multiplier = 1.0  # Minor
            severity = 'Minor'
        else:
            severity_multiplier = 0.5  # Dim
            severity = 'Dim'

        # Adjusted cost based on confidence and severity
        adjusted_cost = base_cost * confidence * severity_multiplier

        # Apply penalty for multiple instances of the same damage type
        if damage_count[damage_type] > 0 and penalty_rate < 1:
            adjusted_cost *= penalty_rate
            penalty_applied = True
        else:
            penalty_applied = False

        # Add the cost for this damage instance to the total
        total_cost += round(adjusted_cost, 2)

        # Increment the count of this damage type (cost)
        damage_count[damage_type] += 1
        cost_count[damage_type] += round(adjusted_cost, 2)

        # Prepare detailed report for this damage
        damage_report = {
            'Damage Type': damages[damage_type],
            'Base Cost': base_cost,
            'Confidence': confidence,
            'Severity': severity,
            'Adjusted Cost': round(adjusted_cost, 2),
            'Penalty Applied': penalty_applied,
            'reduction': round((1-penalty_rate)*100)
        }
        report.append(damage_report)
    statistics.append(damage_count)
    statistics.append(cost_count)

    return total_cost, report, statistics

# Save final data to csv (including image path, report, cost)
def save_to_csv(total_cost, report, statistics, annotated_frame, output_csv="container_damage_report.csv"):

    # Generate the current time for the 'time' column
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Prepare the detailed report as a string
    detail_report_str = ""
    if total_cost > 0:
        for entry in report:
            detail_report_str += f"Damage Type: {entry['Damage Type']}\n"
            detail_report_str += f"  Base Cost: ${entry['Base Cost']}\n"
            detail_report_str += f"  Confidence: {entry['Confidence']:.2f}\n"
            detail_report_str += f"  Severity: {entry['Severity']}\n"
            detail_report_str += f"  Adjusted Cost: ${entry['Adjusted Cost']}\n"
            if entry['Penalty Applied']:
                detail_report_str += f"  Penalty Applied: Yes ({entry['reduction']}% reduction)\n"
            else:
                detail_report_str += "  Penalty Applied: No\n"
            detail_report_str += "-------------------------\n"
    else:
        detail_report_str = "No damage found!"

    # Prepare the summary report as a string
    if total_cost > 0:
        summary_report_str = (f"Dent: {statistics[0][0]} (cost: ${statistics[1][0]})\n"
                              f"Hole: {statistics[0][1]} (cost: ${statistics[1][1]})\n"
                              f"Rust: {statistics[0][2]} (cost: ${statistics[1][2]})\n")
    else:
        summary_report_str = "No damage found!"

    image_dir = 'data'
    image_dir = os.path.join(image_dir, str(index))
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    
    # Save image with a unique filename using UUID
    image_filename = '{}.jpg'.format(uuid.uuid1())
    image_path = os.path.join(image_dir, image_filename)
    cv2.imwrite(image_path, annotated_frame)

    # Open CSV file in append mode
    with open(output_csv, mode='a', newline='') as file:
        writer = csv.writer(file)

        # Write the header only once
        file.seek(0, 2)  # Go to end of the file to check if it's empty
        if file.tell() == 0:
            writer.writerow(['Container ID', 'Time', 'Image', 'Detail Report', 'Summary Report', 'Total Cost'])

        # Write the row for this detection
        writer.writerow([index, current_time, image_path, detail_report_str, summary_report_str, total_cost])


# Load YOLOv10
model = YOLO("best.pt")

try:
    while True:
        # Capture a frame from the camera
        img_resp=urllib.request.urlopen(url)
        imgnp=np.array(bytearray(img_resp.read()),dtype=np.uint8)
        im = cv2.imdecode(imgnp,-1)

        # Run YOLO model on the captured frame and store the results
        results = model(im, conf=0.2)

        # Output the visual detection data, we will draw this on our camera preview window
        annotated_frame = results[0].plot()

        # Get inference time
        inference_time = results[0].speed['inference']
        fps = 1000 / inference_time  # Convert to milliseconds
        text = f'FPS: {fps:.1f}'

        # Define font and position
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 1, 2)[0]
        text_x = annotated_frame.shape[1] - text_size[0] - 10  # 10 pixels from the right
        text_y = text_size[1] + 10  # 10 pixels from the top
        # Draw the text on the annotated frame
        cv2.putText(annotated_frame, text, (text_x, text_y), font, 1, (255, 255, 255), 2, cv2.LINE_AA)


        # capture the image when e is pressed
        if GPIO.input(17) == 0:
            print("Data capture in:")
            c = 6
            for i in range(5):
                c -= 1
                print(c)
                time.sleep(1)

            # Update container ID
            index += 1

            # Create a list to store detected objects
            detected_objects = []

            # Get raw data (detected damage)
            for detection in results[0].boxes:
                # Extract object details (e.g., class label, confidence score, bounding box coordinates)
                class_id = int(detection.cls.item())
                confidence = float(detection.conf.item())
                bbox = detection.xyxy  # Bounding box coordinates in [x_min, y_min, x_max, y_max] format

                # Append object details to the list
                detected_objects.append({
                    'class_id': class_id,
                    'confidence': confidence,
                    'bbox': bbox
                })

            # Calculate the epair cost
            total_cost, report, statistics = calculate_repair_cost(detected_objects,penalty_rate=0.96)
            # Save final data
            save_to_csv(total_cost, report, statistics, annotated_frame)

            print("End in:")
            c = 6
            for i in range(5):
                c -= 1
                print(c)
                time.sleep(1)


        #cv2.imshow("Camera", annotated_frame)

        # Exit the program if q is pressed
        if cv2.waitKey(1) == ord("q"):
            break

    # Close all windows
    cv2.destroyAllWindows()

except KeyboardInterrupt:
    print("Process stopped by user")

finally:
    GPIO.cleanup()  # This ensures GPIO pins are released properly
    print("GPIO cleaned up")