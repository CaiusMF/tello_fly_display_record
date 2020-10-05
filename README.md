# tello fly display record
Fly the Tello drone using the keyboard, while displaying and recording the drone video stream.

## Dependencies

### DJITelloPy
Python package for controlling the Tello drone.

Link: https://github.com/damiafuentes/DJITelloPy

Install:
```
pip install https://github.com/damiafuentes/DJITelloPy/archive/master.zip
```

### OpenCV
Computer vision library.

Install:
```
pip install opencv-python
```

### NumPy
Array computing.
```
pip install numpy
```

## Scripts
The scripts have the same basic functionality (fly/display/record). They just differ in how these functionalities are spread or not across multiple processes. The whole point of this repo (for now) is to have a good live video feed from the drone while flying it and record good videos of it.

### tello_fly_show_record_1.py
Processes:
 * Process 1 (main): drone command
 * Thread  1 (from main): read/process frame, display frame and write video

FPS (avg):
 * With video writer:    ~218 FPS
 * Without video writer: ~245 FPS

### tello_fly_show_record_2.py
Processes:
 * Process 1 (main): drone command
 * Thread  1 (from main): read/process frame, display frame
 * Process 2: write video

FPS (avg):
 * With video writer:    ~216 FPS
 * Without video writer: ~229 FPS

### tello_fly_show_record_3.py
Processes:
 * Process 1 (main): drone command
 * Thread  1 (from main): read/process frame
 * Process 2: display frame
 * Process 3: write video

FPS (avg):
 * With video writer:    ~210 FPS
 * Without video writer: ~215 FPS

## Notes
 * Tello object cannot be shared across processes. I use an extra thread to simulate this in order to solve the command/stream functionalities. Best way to keep a high FPS is to send commands via a Pipe, so that the command while loop waits until further notice and let's the stream loop uninterrupted.
 * Every Tello project I read/tried used the function time.sleep(1 / FPS) after writing a frame to file. This made the whole process way slower (reduced FPS) and also seemed redundant, but the output videos were very slow (visually) if not for the sleep function. After some experiments, I figured it out. The purpose of the sleep function is to account for duplicate frames. Because the processing of the stream is faster than the stream itself, many times you read the same frame. Not using sleep makes the output video seem slow. I solved this by comparing the previous and current frames (in gray form). Now the FPS is way higher and the recordings look good.
