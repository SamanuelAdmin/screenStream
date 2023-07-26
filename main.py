from flask import Flask, render_template, Response, request
import threading
import socket
import time

import pyscreenshot as ImageGrab
import numpy
import cv2
import json
import pyautogui


class ScreenManager:
	def __init__(self, delay=0.3, count=3):
		self.delay = delay
		self.count = count
		self.nowScreenImage = None
		threading.Thread(target=self.startGetThr).start()

	def startGetThr(self):
		for c in range(self.count):
			threading.Thread(target=self.getScreenImageInThread).start()
			time.sleep(self.delay)

	def getScreenImageInThread(self):
		while True:
			self.nowScreenImage = numpy.uint8(pyautogui.screenshot())  # ImageGrab.grab()
			time.sleep(self.delay)

	def getScreenImage(self):
		while True: 
			if self.nowScreenImage.any():
				yield (
					b'--frame\r\n'
					b'Content-Type: image/jpeg\r\n\r\n' + cv2.imencode('.jpg', self.nowScreenImage)[1].tobytes() + b'\r\n'
				) 

class WebServer:
	def __init__(self, ip=None, thrgetimgcount=3, delaythrimg=0.2):
		self.IP = socket.gethostbyname(socket.gethostname()) if not ip else ip
		self.PORT = 80
		self.__APP = Flask(__name__)

		self.ScreenManager = ScreenManager(count=thrgetimgcount, delay=delaythrimg)

	def init(self):
		@self.__APP.route('/')
		def index():
			return render_template('index.html')

		@self.__APP.route('/screenstream')
		def screenstream(): 
			return Response(
					self.ScreenManager.getScreenImage(), 
					mimetype='multipart/x-mixed-replace; boundary=frame'
				)

	def start(self):
		self.__APP.run(
				debug=False, 
				host=self.IP, 
				port=self.PORT
			)


def main():
	server = WebServer(ip='192.168.0.104')
	server.init()
	server.start()

if __name__ == '__main__': main()