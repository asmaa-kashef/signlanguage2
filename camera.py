# Import OpenCV library
import cv2
import threading
# Create Face detection object from OpenCV frontal face Classifier
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade  = cv2.CascadeClassifier('haarcascade_eye.xml')
class RecordingThread (threading.Thread):
    def __init__(self, name, camera):
        threading.Thread.__init__(self)
        self.name = name
        self.isRunning = True

        self.video = camera
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.out = cv2.VideoWriter('./static/video.avi',fourcc, 20.0, (640,480))

    def run(self):
        while self.isRunning:
            ret, frame = self.video.read()
            if ret:
                self.out.write(frame)

        self.out.release()

    def stop(self):
        self.isRunning = False

    def __del__(self):
        self.out.release()
class VideoCamera(object):

    def __init__(self):
        # Using OpenCV initiate front facing built-in camera of client machine
        self.video = cv2.VideoCapture(0)
    # Initialize video recording environment
        self.is_record = False
        self.out = None

        # Thread for recording
        self.recordingThread = None
    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret, frame = self.video.read()
        frame = cv2.flip(frame, 1)  # Flip image vertically
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.2, minNeighbors=5)

        for x, y, w, h in faces:

            # For each face identified draw rectangle around it
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 3)

            # Extract face alone to detect eyes
            face_gray  = gray_image[y:y+h, x:x+w]

            # Detect eyes
            eyes = eye_cascade.detectMultiScale(face_gray, scaleFactor=1.1)

            # Execute only if the number of eyes object identified is less than 3
            if len(eyes) < 3:
                for ex, ey, ew, eh in eyes:
                    if (y+(h/2)) > (y+ey+(eh/2)):  # Eliminate nose being identified as eye

                        # For each eye identified draw rectangle around it
                        cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (255,0,0), 2)

        # JPEGs are being painted on the UI continuously as video stream.
        # However OpenCV identifies the faces on raw images.
        # So before sending response to UI the byte arrays is required to be encode into JPEG.
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
    def start_record(self):
        self.is_record = True
        self.recordingThread = RecordingThread("Video Recording Thread", self.video)
        self.recordingThread.start()

    def stop_record(self):
        self.is_record = False

        if self.recordingThread != None:
            self.recordingThread.stop()
