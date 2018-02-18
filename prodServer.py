import random
import json
import cherrypy
import datetime
import threading

# Global dictionary data
latest_data = {"score":"","comments":"","rep_count":"","time":""}
data = {}
session = 1
terminate_flag = 1
session_type = "pushup"
session_time = 0

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
              			data[session]["leftAngleKnee"].append(int(ord(content[1])*1.4117))
           		if str(content[0]) == "b": # Angle of RightKnee
              			data[session]["rightAngleKnee"].append(int(ord(content[1])*1.4117))
                        if str(content[0]) == "c": # Angle of LeftArm
                                data[session]["leftAngleElbow"].append(int(ord(content[1])*1.4117))
                        if str(content[0]) == "d": # Angle of RightArm
                                data[session]["rightAngleElbow"].append(int(ord(content[1])*1.4117))
           		if str(content[0]) == "e": # Curvature of Back
              			data[session]["backCurvature"].append(ord(content[1])/255.0)
       			pool_sema.release()


def rep_count():
    rep_count = 0
    global data, latest_data, pool_sema, session_type, session
    if session_type == "pushup":
    	push_up = 0
   	push_down = 0
        pool_sema.acquire()
    	for angle in data[session]["leftAngleElbow"]:
            if angle >= 90:
               push_up = 1
            for ang in range(data[session]["leftAngleElbow"].index(angle),len(data[session]["leftAngleElbow"])):
               if ang < 45:
                    push_down = 1
               break
            if push_up == 1 and push_down == 1:
	            rep_count += 1
    	pool_sema.release()
    if session_type == "squat":
        squat_up = 0
        squat_down = 0
        pool_sema.acquire()
        for angle in data[session]["leftAngleKnee"]:
            if angle >= 160:
               squat_up = 1
            for ang in range(data[session]["leftAngleKnee"].index(angle),len(data[session]["leftAngleKnee"])):
               if ang <= 90:
                    squat_down = 1
               break
            if squat_up == 1 and squat_down == 1:
                    rep_count += 1
        pool_sema.release()
    return rep_count

def comments_builder(score):
    comments = ["Straight your back posture","Maintain pace", "Improper posture","Perfect posture", "Keep going"]
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
       global sessiontype, session_time,latest_data
       latest_data["session_clock"] = datetime.datetime.now() - session_time
       latest["rep_count"] = rep_count(type)
       latest["score"] = score_maker()
       latest["comment"] = comment_builder()
       return json.dumps(latest_data)

    @cherrypy.expose
    def sessionCreate(self, type):
                global data, session, terminate_flag, sessiontype, session_time
                try:
                  data[session] = {}
                  terminate_flag = 0
                  data[session] = {}
                  sessiontype = type
                  session_time = datetime.datetime.now()
                except:
                  pass

    @cherrypy.expose
    def sessionClose(self):
                global data, session, terminate_flag
                terminate_flag = 1
                print data
                session += 1
       		return json.dumps({"status": "Session closed"})

if __name__ == '__main__':
    cherrypy.server.socket_host = '0.0.0.0'
    threading.Thread(target=fetchData, args=()).start()
    cherrypy.quickstart(formFixApp())
