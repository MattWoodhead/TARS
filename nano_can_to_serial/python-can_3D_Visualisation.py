# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 19:23:57 2022

@author: matth

based on https://github.com/efstathios-chatzikyriakidis/3d-opengl-shape-rotation-with-input-sensors
"""

import sys
import threading
import can

from OpenGL.GL import (
    glClearColor,
    glClearDepth,
    glDepthFunc,
    glEnable,
    glShadeModel,
    glMatrixMode,
    glLoadIdentity,
    glClear,
    glViewport,
    glTranslatef,
    glRotatef,
    glBegin,
    glColor3f,
    glVertex3f,
    glEnd,
    GL_LESS,
    GL_DEPTH_TEST,
    GL_PROJECTION,
    GL_MODELVIEW,
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_QUADS,
    GL_TRIANGLES,
    GL_SMOOTH,
)
from OpenGL.GLU import (gluPerspective,
)
from OpenGL.GLUT import (
    glutInit,
    glutInitDisplayMode,
    glutInitWindowSize,
    glutInitWindowPosition,
    glutCreateWindow,
    glutDisplayFunc,
    glutIdleFunc,
    glutReshapeFunc,
    glutKeyboardFunc,
    glutMainLoop,
    glutPostRedisplay,
    glutSwapBuffers,
    GLUT_RGBA,
    GLUT_DOUBLE,
    GLUT_DEPTH,
)


CAN_CLIENT = can.interface.Bus(interface="serial", channel="COM4", baudrate=115200)


# Escape key code.
ESCAPE_KEY = '\033'

# window settings
WINDOW_TITLE = "Honeywell TARS J1939 3D OpenGL Shape"
WINDOW_HEIGHT = 480
WINDOW_WIDTH = 480

# new and old angle values of the 3D object.
newXAngleValue = 0.0
newYAngleValue = 0.0
newZAngleValue = 0.0
oldXAngleValue = 0.0
oldYAngleValue = 0.0
oldZAngleValue = 0.0

PREVIOUS_TIMESTAMP = 0
YAW = 0
PITCH = 0
ROLL = 0
SWAY = 0
SURGE = 0
HEAVE = 0
CAN_UPDATE = False

def can_receive():

    global YAW  # TODO - globals are horrid
    global PITCH
    global ROLL
    global SWAY
    global SURGE
    global HEAVE
    global PREVIOUS_TIMESTAMP
    global CAN_UPDATE

    rx_msg = CAN_CLIENT.recv(1)
    if rx_msg is not None:
        if rx_msg.arbitration_id == 0x0cf029e2:  # PITCH AND ROLL BROADCAST DATA
            PITCH = rx_msg.data[0] + (rx_msg.data[1] << 8) + (rx_msg.data[2] << 16)
            ROLL = rx_msg.data[3] + (rx_msg.data[4] << 8) + (rx_msg.data[5] << 16)
            PITCH = (PITCH - 8192000)/32768
            ROLL = (ROLL - 8192000)/32768
            CAN_UPDATE = True
        elif rx_msg.arbitration_id == 0x0Cf02ae2:  # ANGULAR RATE BROADCAST DATA
            pitch_rate = ((rx_msg.data[0] + (rx_msg.data[1] << 8)) - 32000)/128
            roll_rate = ((rx_msg.data[2] + (rx_msg.data[3] << 8)) - 32000)/128
            yaw_rate = ((rx_msg.data[4] + (rx_msg.data[5] << 8)) - 32000)/128
            new_timestamp = rx_msg.timestamp
            if PREVIOUS_TIMESTAMP > 0:
                YAW = YAW + yaw_rate*(new_timestamp - PREVIOUS_TIMESTAMP)
            PREVIOUS_TIMESTAMP = new_timestamp
            CAN_UPDATE = True
        elif rx_msg.arbitration_id == 0x08f02de2:  # ACCELERATION BROADCAST DATA
            SWAY = ((rx_msg.data[0] + (rx_msg.data[1] << 8)) - 32000)/100
            SURGE = ((rx_msg.data[2] + (rx_msg.data[3] << 8)) - 32000)/100
            HEAVE = (((rx_msg.data[4] + (rx_msg.data[5] << 8)) - 32000)/100) - 1  # remove gravity component
            CAN_UPDATE = True
    else:
        CAN_UPDATE = False



# this function is called right after our OpenGL window is created.
def initGL(width, height):
    glClearColor(0.0, 0.0, 0.0, 0.0)      # clear the background color to black.
    glClearDepth(1.0)                     # enable clearing of the depth buffer.
    glDepthFunc(GL_LESS)                  # type of depth test to do.
    glEnable(GL_DEPTH_TEST)               # enable depth testing.
    glShadeModel(GL_SMOOTH)               # enable smooth color shading.
    glMatrixMode(GL_PROJECTION)           # specify current matrix.
    glLoadIdentity()                      # replace the current matrix with the identity matrix.

    # calculate the aspect ratio of the window.
    gluPerspective(45.0, float(width) / float(height), 0.1, 100.0)

    # specify current matrix.
    glMatrixMode(GL_MODELVIEW)


# call this function when the window is resized.
def resizeGLScene(width, height):
    # prevent a divide by zero if the window is too small.
    if height == 0: height = 1

    glViewport(0, 0, width, height)   # reset the current viewport.
    glMatrixMode(GL_PROJECTION)       # specify current matrix.
    glLoadIdentity()                  # replace the current matrix with the identity matrix.

    # calculate the aspect ratio of the window.
    gluPerspective(45.0, float(width) / float(height), 0.1, 100.0)

    # specify current matrix.
    glMatrixMode(GL_MODELVIEW)


# the main drawing function.
def drawGLScene():
    # clear the screen and the depth buffer.
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()                             # replace the current matrix with the identity matrix.
    glTranslatef(0.2*SURGE, 0.2*HEAVE, 0.4*(SWAY)-8)
    glRotatef(newXAngleValue, 1.0, 0.0, 0.0)       # rotate the cube on X.
    glRotatef(newYAngleValue, 0.0, 1.0, 0.0)       # rotate the cube on Y.
    glRotatef(newZAngleValue, 0.0, 0.0, 1.0)       # rotate the cube on Z.

    glBegin(GL_TRIANGLES)

    glColor3f( 1.0, 0.0, 0.0 )  # Red
    glVertex3f( 0.0, 1.0, 0.0 )
    glVertex3f( -1.0, -1.0, 1.0 )
    glVertex3f( 1.0, -1.0, 1.0)

    glColor3f( 0.0, 1.0, 0.0 )  # green
    glVertex3f( 0.0, 1.0, 0.0 )
    glVertex3f( -1.0, -1.0, -1.0 )
    glVertex3f( -1.0, -1.0, 1.0)

    glColor3f( 1.0, 0.0, 1.0 )  # violet
    glVertex3f( 0.0, 1.0, 0.0 )
    glVertex3f( 1.0, -1.0, -1.0 )
    glVertex3f( -1.0, -1.0, -1.0)

    glColor3f( 1.0, 1.0, 0.0 )  # yellow
    glVertex3f( 0.0, 1.0, 0.0 )
    glVertex3f( 1.0, -1.0, 1.0 )
    glVertex3f( 1.0, -1.0, -1.0)

    glColor3f( 0.0, 0.0, 1.0 )  # blue
    glVertex3f( -1.0, -1.0, 1.0 )
    glVertex3f( 1.0, -1.0, 1.0 )
    glVertex3f( -1.0, -1.0, -1.0)

    glVertex3f( 1.0, -1.0, -1.0 )
    glVertex3f( 1.0, -1.0, 1.0 )
    glVertex3f( -1.0, -1.0, -1.0)

    glEnd()

    glutSwapBuffers()


# call this function whenever a key is pressed.
def keyPressed(key, x, y):
    # exit the program if escape key pressed.
    if key == ESCAPE_KEY: sys.exit()


# call this function whenever there is an idle moment.
def idleMoment():
    global oldXAngleValue, oldYAngleValue, oldZAngleValue
    global newXAngleValue, newYAngleValue, newZAngleValue
    global CAN_UPDATE

    # fetch CAN data
    can_receive()

    # if the line is not empty try to handle it.
    if CAN_UPDATE:

        # get the new angle values.
        newXAngleValue = ROLL
        newYAngleValue = YAW
        newZAngleValue = PITCH

        # redisplay the scene only if there was a change in angles.
        if (newXAngleValue != oldXAngleValue or
            newYAngleValue != oldYAngleValue or
            newZAngleValue != oldZAngleValue
            ):
            # store previous angles' values.
            oldXAngleValue = newXAngleValue
            oldYAngleValue = newYAngleValue
            oldZAngleValue = newZAngleValue

            # print newXAngleValue
            # print newYAngleValue

            # set flag for redisplay the scene.
            glutPostRedisplay()


# call this function to start the application
def main():

    # initialize the GLUT library.
    glutInit(sys.argv)

    # select display mode:
    #   bit mask to select an RGBA mode window.
    #   bit mask to select a double buffered window.
    #   bit mask to request a window with a depth buffer.
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)

    # get a window size.
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)

    # the window starts at the upper left corner of the screen.
    glutInitWindowPosition(0, 0)

    # create a window and set its title.
    glutCreateWindow(WINDOW_TITLE)

    # register the drawing function with glut.
    glutDisplayFunc(drawGLScene)

    # when we are doing nothing, try to redraw the scene.
    glutIdleFunc(idleMoment)

    # register the function called when the window is resized.
    glutReshapeFunc(resizeGLScene)

    # register the function called when the keyboard is pressed.
    glutKeyboardFunc(keyPressed)

    # initialize our window.
    initGL(WINDOW_WIDTH, WINDOW_HEIGHT)

    # start event processing engine.
    t_visualisation = threading.Thread(target=glutMainLoop())
    t_visualisation.start()



# run the script if executed
if __name__ == '__main__':
    main()
