import math
import socket  # for socket
import sys
import pygame

IP = '192.168.8.150'
port = 23
scale = 20

last_angle = 0

BLACK = (0, 0, 0)
YELLOW = (255, 196, 5)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 50, 150)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
RED = (255, 0, 0)
ORANGE = (100, 50, 0)

pygame.init()
clock = pygame.time.Clock()

pygame.font.init()
myfont = pygame.font.SysFont('Arial', 15)

window_name = "Lidar view"
frameWidth = 1500  # should be the same as in vision server
frameHeight = 1200  # should be the same as in vision server
size = [frameWidth, frameHeight]
screen = pygame.display.set_mode(size)
pygame.display.set_caption(window_name)
center = (int(frameWidth / 2), int(frameHeight / 2))

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket successfully created")
except socket.error as err:
    print("socket creation failed with error %s" % (err))


try:
    host_ip = socket.gethostbyname(IP)
except socket.gaierror:
    # this means could not resolve the host
    print("there was an error resolving the host")
    sys.exit()

# connecting to the server
s.connect((host_ip, port))
print("the socket has successfully connected")


def checksum(frame):
    cs = int.from_bytes(frame[-2:], byteorder='big', signed=False)
    result = 0

    for i in frame[0:-2]:
        result += int(i)

    return result == cs


def parseData(payload, payloadLen):
    global last_angle
    global scale

    speed = payload[0]
    speed = speed * 0.05  # r/s
    # print ('RPM: %.2fr/s or %drpm'%(speed, speed*60))

    angOffset = int.from_bytes(payload[1:3], byteorder='big', signed=True)
    angOffset = angOffset * 0.01
    # print ('Angle Offset: %.2f'%angOffset)

    angStart = int.from_bytes(payload[3:5], byteorder='big', signed=False)
    angStart = angStart * 0.01
    # print ('Starting Angle: %.2f'%angStart)

    nSamples = int((payloadLen - 5) / 3)
    # print("N Samples: %d"%nSamples)

    for i in range(nSamples):
        index = 5 + i * 3
        sampleID = payload[index]
        distance = int.from_bytes(
            payload[index + 1:index + 3], byteorder='big', signed=False)
        ang = angStart + 22.5 * i / nSamples
        # print ('%.2f: %.2f mm'%(ang, distance))

        x = center[0] + distance / scale * math.sin(math.radians(ang))
        y = center[1] + distance / scale * math.cos(math.radians(ang))

        if (ang < last_angle):
            pygame.display.flip()
            screen.fill(BLACK)
            pygame.draw.circle(screen, ORANGE, center, 1*400 / scale, 1) # 10cm circle
            pygame.draw.circle(screen, ORANGE, center, 2*400 / scale, 1) # 20cm circle
            pygame.draw.circle(screen, ORANGE, center, 3*400 / scale, 1) # 30cm circle
            pygame.draw.circle(screen, ORANGE, center, 4*400 / scale, 1) # 40cm circle
            pygame.draw.circle(screen, ORANGE, center, 5*400 / scale, 1) # 50cm circle
            pygame.draw.circle(screen, ORANGE, center, 6*400 / scale, 1) # 60cm circle
            pygame.draw.circle(screen, ORANGE, center, 7*400 / scale, 1) # 70cm circle
            pygame.draw.circle(screen, ORANGE, center, 8*400 / scale, 1) # 80cm circle
            pygame.draw.circle(screen, ORANGE, center, 9*400 / scale, 1) # 90cm circle
            pygame.draw.circle(screen, ORANGE, center, 10*400 / scale, 1) # 100cm circle
            pygame.draw.rect(screen,YELLOW,pygame.Rect(10, 10, 4000/scale, 10)) #draw 1meter in scale

        last_angle = ang

        pygame.draw.rect(screen, GREEN, pygame.Rect(x, y, 3, 3))
        pass
    
    # pygame.display.flip()
    # screen.fill(BLACK)


def parseError(payload):
    speed = payload[0]
    speed = speed * 0.05  # r/s
    print('Error: Low RPM - %.2fr/s or %drpm' % (speed, speed * 60))


def processFrame(frame):
    if len(frame) < 3:
        return False
    frameLen = int.from_bytes(frame[1:3], byteorder='big', signed=False)
    if len(frame) < frameLen + 2:
        return False  # include 2bytes checksum

    if not checksum(frame):
        return True  # checksum failed

    try:
        protocalVer = frame[3]  # 0x00
        frameType = frame[4]  # 0x61
        payloadType = frame[5]  # 0xAE or 0XAD
        payloadLen = int.from_bytes(frame[6:8], byteorder='big', signed=False)

        if payloadType == 0xAD:
            parseData(frame[8:frameLen + 1], payloadLen)
        elif payloadType == 0xAE:
            parseError(frame[8:frameLen + 1])
    except:
        pass
    return True


frame = ''


def onData(x):
    global frame
    if x == b'\xaa' and len(frame) == 0:
        frame = x
    elif len(frame) > 0:
        frame += x
        if processFrame(frame):
            frame = ''


while 1:
    onData(s.recv(1))
