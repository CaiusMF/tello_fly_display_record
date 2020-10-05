import sys
import cv2
import time
import signal
import numpy as np

from threading import Thread
from multiprocessing import Process, Pipe, Event
from djitellopy import Tello


tello             = None
video_writer      = None
video_writer_size = (960, 720)


# function to handle keyboard interrupt
def signal_handler(sig, frame):
	if tello:
		try:
			tello.end()
		except:
			pass

	if video_writer:
		try:
			video_writer.release()
		except:
			pass

	sys.exit()

# aruco detection can be replaced here with other
# machine learning algorithm (e.g. canny edge detection)
def process_frame(exit_event, command_conn, video_writer_conn):
	global tello

	aruco_dict_name = cv2.aruco.DICT_6X6_50
	aruco_dict      = cv2.aruco.getPredefinedDictionary(aruco_dict_name)

	FONT           = cv2.FONT_HERSHEY_SIMPLEX
	FONT_SCALE     = 0.70
	FONT_THICKNESS = 2

	frame_read = tello.get_frame_read()
	battery    = tello.get_battery()

	fps = 0
	fps_avg = 0
	command_time_1 = time.time()

	times = []
	while not exit_event.is_set():
		start_time = time.time()

		# if there is no command for 15 seconds, tello will land
		command_time_2 = start_time - command_time_1

		frame = frame_read.frame.copy()
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		corners, ids, rejects = cv2.aruco.detectMarkers(gray, aruco_dict)
		if len(corners) != 0:
			points = corners[0][0].astype(np.int32)
			p1 = points[0] # tl
			p2 = points[1] # tr
			p3 = points[2] # br
			p4 = points[3] # bl

			cv2.line(frame, tuple(p1), tuple(p2), (0, 255, 0), 2)
			cv2.line(frame, tuple(p2), tuple(p3), (0, 255, 0), 1)
			cv2.line(frame, tuple(p3), tuple(p4), (0, 255, 0), 1)
			cv2.line(frame, tuple(p4), tuple(p1), (0, 255, 0), 1)


		text = f"FPS {fps}"
		cv2.putText(frame, text, (50, 50), FONT, FONT_SCALE, (255, 0, 255), FONT_THICKNESS, cv2.LINE_AA)

		text = f"FPS AVG {fps_avg}"
		cv2.putText(frame, text, (50, 75), FONT, FONT_SCALE, (255, 0, 255), FONT_THICKNESS, cv2.LINE_AA)

		text = f"BAT {battery}%"
		cv2.putText(frame, text, (50, 100), FONT, FONT_SCALE, (255, 0, 0), FONT_THICKNESS, cv2.LINE_AA)

		text = f"NCT {round(command_time_2, 2)}" # time lapse since last command
		cv2.putText(frame, text, (50, 125), FONT, FONT_SCALE, (0, 255, 0) if command_time_2 < 15 else (0, 0, 255), FONT_THICKNESS, cv2.LINE_AA)

		cv2.imshow("frame", frame)
		key = cv2.waitKey(1)
		if key != -1:
			command_conn.send(key)
			command_time_1 = time.time()

		# send frame to video writer process
		video_writer_conn.send(frame)

		fps     = round(1.0 / (time.time() - start_time), 1)
		times.append(fps)
		fps_avg = round(sum(times) / len(times), 1)


def write_video(frame_conn, video_file_name):
	global video_writer
	global video_writer_size

	signal.signal(signal.SIGINT, signal_handler)
	signal.signal(signal.SIGTERM, signal_handler)

	if video_writer is None:
		fourcc = cv2.VideoWriter_fourcc(*'XVID')
		video_writer = cv2.VideoWriter(video_file_name, fourcc, 30.0, video_writer_size)

	while True:
		frame = frame_conn.recv()
		video_writer.write(frame)
		time.sleep(1 / 30)

	# then we got the exit event so cleanup
	signal_handler(None, None)


if __name__ == '__main__':
	signal.signal(signal.SIGINT, signal_handler)
	signal.signal(signal.SIGTERM, signal_handler)

	tello_spped = 15
	video_file_name = "tello_fly_show_record_2.avi"

	write_conn_out, write_conn_in = Pipe()
	comm_conn_out, comm_conn_in = Pipe()

	exit_event = Event()

	write_process = Process(target=write_video, args=(write_conn_out, video_file_name, ))
	write_process.start()

	tello = Tello()

	tello.connect()
	tello.streamon()

	process_thread = Thread(target=process_frame, args=(exit_event, comm_conn_in, write_conn_in, ))
	process_thread.daemon = True
	process_thread.start()

	while not exit_event.is_set():
		key = comm_conn_out.recv()

		if key == 27:
			if tello.is_flying: # record the landing
				tello.land()
				time.sleep(1)
			exit_event.set()
		elif key == ord('t'): # takeoff
			tello.takeoff()
		elif key == ord('l'): # land
			tello.land()
		elif key == ord('w'): # forward
			tello.send_rc_control(0, tello_spped, 0, 0)
		elif key == ord('s'): # backward
			tello.send_rc_control(0, -tello_spped, 0, 0)
		elif key == ord('a'): # left
			tello.send_rc_control(-tello_spped, 0, 0, 0)
		elif key == ord('d'): # right
			tello.send_rc_control(tello_spped, 0, 0, 0)
		elif key == ord('1'): # up
			tello.send_rc_control(0, 0, tello_spped, 0)
		elif key == ord('2'): # down
			tello.send_rc_control(0, 0, -tello_spped, 0)
		elif key == ord('q'): # rotate left
			tello.send_rc_control(0, 0, 0, -tello_spped)
		elif key == ord('e'): # rotate right
			tello.send_rc_control(0, 0, 0, tello_spped)
		elif key == ord('h'): # rotate right
			tello.send_rc_control(0, 0, 0, 0)

	process_thread.join()

	write_process.terminate()

	write_process.join()

	tello.end()

	print("All good!")
