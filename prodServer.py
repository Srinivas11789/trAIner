import random
import json
import cherrypy
import datetime
import threading
import math

# Global dictionary data
latest_data = {}
data = {}
session = 1
terminate_flag = 1
session_type = "pushup"
session_time = 0
pushup_is_started = 1 # reset when session starts
squat_is_started = 1 # reset when session starts
num_pushups = 0 # reset when session starts
num_squats = 0 # reset when session starts

# Semaphore logic
maxconnections = 10
pool_sema = threading.BoundedSemaphore(value=maxconnections)

# Stub function - only used for mobile testing purposes
def updateData():
    global data
    data["score"] = str("%.1f" % random.uniform(0,1))
    data["comments"] = ["Straight your back posture","Maintain pace"]
    data["rep_count"] = str(random.randint(1,100))
    data["time"] = str(random.randint(1,100))
    threading.Timer(4.0, updateData).start()

#updateData()

# Fetch Data from the Iot and Openpose
def fetchData():
    global data, pool_sema, terminate_flag, session
    import socket
    TCP_IP = '0.0.0.0'
    TCP_PORT = 4444
    BUFFER_SIZE = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)
    conn, addr = s.accept()
    while 1:
       content = conn.recv(1024)
       if terminate_flag == 0:
       			pool_sema.acquire()
                	if "leftAngleKnee" not in data[session]:
				data[session]["leftAngleKnee"] = []
                        if "rightAngleKnee" not in data[session]:
				data[session]["rightAngleKnee"] = []
                        if "leftAngleElbow" not in data[session]:
                                data[session]["leftAngleElbow"] = []
                        if "rightAngleElbow" not in data[session]:
                                data[session]["rightAngleElbow"] = []
                        if "backCurvature" not in data[session]:
                        	data[session]["backCurvature"] = []
           		if str(content[0]) == "a": # Angle of LeftKnee
                                newData = int(ord(content[1])*1.4117)
              			data[session]["leftAngleKnee"].append(newData)
                                check_squat(newData)
           		if str(content[0]) == "b": # Angle of RightKnee
                                newData = int(ord(content[1])*1.4117)
              			data[session]["rightAngleKnee"].append(newData)
                                check_squat(newData)
                        if str(content[0]) == "c": # Angle of LeftArm
                                newData = int(ord(content[1])*1.4117)
                                data[session]["leftAngleElbow"].append(newData)
                                check_pushup(newData)
                        if str(content[0]) == "d": # Angle of RightArm
                                newData = int(ord(content[1])*1.4117)
                                data[session]["rightAngleElbow"].append(newData)
                                check_pushup(newData)
           		if str(content[0]) == "e": # Curvature of Back
              			data[session]["backCurvature"].append(ord(content[1])/255.0)
       			pool_sema.release()

def check_pushup(angle):
    global pushup_is_started,num_pushups
    if (pushup_is_started):
        if (angle >= 90):
            pushup_is_started = False
            num_pushups = num_pushups + 1
    else:
        if (angle <= 20):
            pushup_is_started = True

def check_squat(angle):
    global squat_is_started, num_squats
    print("got angle for squat: " + str(angle))
    if (squat_is_started):
        if (angle >= 120):
            squat_is_started = False
            num_squats = num_squats + 1
    else:
        if (angle <= 20):
            squat_is_started = True

def current_reps():
    global is_squat_session, is_pushup_session, num_pushups, num_squats
    if (is_squat_session):
        return num_squats
    elif (is_pushup_session):
        return num_pushups

def startSession(session_type):
    global num_squats, is_squat_session, is_pushup_sesssion, num_pushups
    if (session_type == "squat"):
        num_squats = 0
        is_squat_session = True
        is_pushup_sesssion = False
    elif (session_type == "pushup"):
        num_pushups = 0
        is_pushup_session = True
        is_squat_session = False

def comments_builder(score):
    comments = ["Straighten your back posture","Maintain pace", "Improper posture","Perfect posture", "Keep going"]
    if float(score) > 0.85:
       return [comments[4], comments[3],comments[1]]
    if float(score) < 0.85 and float(score) > 0.5:
       return [comments[0], comments[4]]
    if float(score) < 0.5:
       return [comments[2]]

#Update new Data
def latestData():
    global data, latest_data, pool_sema
    pool_sema.acquire()
    data["score"] = str("%.1f" % random.uniform(0,1))
    data["comments"] = ["Straight your back posture","Maintain pace"]
    data["rep_count"] = str(random.randint(1,100))
    data["time"] = str(random.randint(1,100))
    pool_sema.release()
    threading.Timer(1.0, latestData).start()

class formFixApp(object):

    @cherrypy.expose
    def getData(self):
       global  session_time,latest_data, session, sessiontype
       timedelta = math.floor(((datetime.datetime.now() - session_time).total_seconds())/3600)
       latest_data[session]["session_clock"] = timedelta
       latest_data[session]["rep_count"] = current_reps()
       latest_data[session]["type"] = sessiontype
       #try:
       #    latest_data[session]["minimum_angle"] = {"rightAngleElbow": min(data[session]["rightAngleElbow"]), "leftAngleElbow":min(data[session]["leftAngleElbow"]), "rightAngleKnee":data[session]["rightAngleKnee"],"leftAngleKnee":data[session]["leftAngleKnee"], "backCurvature":data[session]["backCurvature"]}
       #except:
       #     latest_data[session]["minimum_angle"] = {}   
       return json.dumps(latest_data[session])

    @cherrypy.expose
    def sessionCreate(self, sType):
                global data, session, terminate_flag, sessiontype, session_time, latest_data
                if terminate_flag == 1:
                	startSession(sType) # type = "pushup" or "squat"z
                	terminate_flag = 0
                	data[session] = {}
                	latest_data[session] = {}
                	sessiontype = sType
                	session_time = datetime.datetime.now()
                	return json.dumps({"status": "Session opened","type":sType,"session": session})
                else:
                        return json.dumps({"status": "Session already opened","type":sessiontype,"session": session})

    @cherrypy.expose
    def sessionClose(self):
                global data, session, terminate_flag, num_squat, num_pushups
                terminate_flag = 1
                session += 1
                num_squats = 0
                num_pushups = 0
       		return json.dumps({"status": "Session closed"})

    @cherrypy.expose
    def getAllData(self):
                global latest_data
                return json.dumps(latest_data)

    @cherrypy.expose
    def getbackcurvature(self):
                global data, session
                if "backCurvature" in data[session]:
                        length = len(data[session]["backCurvature"])
                	return json.dumps({"backCurvature":data[session]["backCurvature"][length-1]})
                else:
                        return json.dumps({"backCurvature":""})

if __name__ == '__main__':
    cherrypy.server.socket_host = '0.0.0.0'
    threading.Thread(target=fetchData, args=()).start()
    cherrypy.quickstart(formFixApp())
