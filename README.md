# tello fly show record
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
pip install opencv-contrib-python
```

### NumPy
Array computing.
```
$ pip install numpy
```

## Scripts
The scripts have the same basic functionality (fly/display/record). They just differ in how these functionalities are spread or not across multiple processes. The whole point of this repo (for now) is to have a good live video feed from the drone while flying it and record good videos of it.

### tello_fly_show_record_1.py
Processes:
 * Process 1 (main): drone command
 * Thread 1 (from main): read/process frame, display frame and write video

FPS:
 * With video writer: 20 FPS
 * Without video writer: 125 FPS

### tello_fly_show_record_2.py
Processes:
 * Process 1 (main): drone command
 * Thread 1 (from main): read/process frame, display frame
 * Process 2: write video

FPS:
 * With video writer: 25 FPS
 * Without video writer: 125 FPS

### tello_fly_show_record_3.py
Processes:
 * Process 1 (main): drone command
 * Thread 1 (from main): read/process frame
 * Process 2: display frame
 * Process 3: write video

FPS:
 * With video writer: 25 FPS
 * Without video writer: 125 FPS
