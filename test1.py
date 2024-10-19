import cv2
import urllib.request
import numpy as np
from picamera2 import Picamera2
from ultralytics import YOLO

url='http://192.168.0.122/cam-mid.jpg'
im=None

# Load YOLOv8
model = YOLO("best.pt")

while True:
    # Capture a frame from the camera
    img_resp=urllib.request.urlopen(url)
    imgnp=np.array(bytearray(img_resp.read()),dtype=np.uint8)
    im = cv2.imdecode(imgnp,-1)
    
    # Run YOLO model on the captured frame and store the results
    results = model(im)
    
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

    # Display the resulting frame
    cv2.imshow("Camera", annotated_frame)

    # Exit the program if q is pressed
    if cv2.waitKey(1) == ord("q"):
        break

# Close all windows
cv2.destroyAllWindows()