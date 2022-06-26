# %%
import numpy as np
import cv2
import itertools
import math
import argparse
import os
import pandas as pd
import csv

# %%
points = []

class PanZoomWindow(object):
    """ Controls an OpenCV window. Registers a mouse listener so that:
        1. right-dragging up/down zooms in/out
        2. right-clicking re-centers
        3. trackbars scroll vertically and horizontally 
    You can open multiple windows at once if you specify different window names.
    You can pass in an onLeftClickFunction, and when the user left-clicks, this 
    will call onLeftClickFunction(y,x), with y,x in original image coordinates."""
    def __init__(self, img, windowName = 'PanZoomWindow', onLeftClickFunction = None, color=(0,0,0)):
        self.WINDOW_NAME = windowName
        self.H_TRACKBAR_NAME = 'x'
        self.V_TRACKBAR_NAME = 'y'
        self.img = img
        self.onLeftClickFunction = onLeftClickFunction
        self.TRACKBAR_TICKS = 1000
        self.panAndZoomState = PanAndZoomState(img.shape, self)
        self.lButtonDownLoc = None
        self.mButtonDownLoc = None
        self.rButtonDownLoc = None
        self.color = color
        cv2.namedWindow(self.WINDOW_NAME, cv2.WINDOW_NORMAL)
        self.redrawImage()
        cv2.setMouseCallback(self.WINDOW_NAME, self.onMouse)
        cv2.createTrackbar(self.H_TRACKBAR_NAME, self.WINDOW_NAME, 0, self.TRACKBAR_TICKS, self.onHTrackbarMove)
        cv2.createTrackbar(self.V_TRACKBAR_NAME, self.WINDOW_NAME, 0, self.TRACKBAR_TICKS, self.onVTrackbarMove)
    def onMouse(self,event, x,y,_ignore1,_ignore2):
        """ Responds to mouse events within the window. 
        The x and y are pixel coordinates in the image currently being displayed.
        If the user has zoomed in, the image being displayed is a sub-region, so you'll need to
        add self.panAndZoomState.ul to get the coordinates in the full image."""
        if event == cv2.EVENT_MOUSEMOVE:
            return
        elif event == cv2.EVENT_RBUTTONDOWN:
            #record where the user started to right-drag
            self.mButtonDownLoc = np.array([y,x])
        elif event == cv2.EVENT_RBUTTONUP and self.mButtonDownLoc is not None:
            #the user just finished right-dragging
            dy = y - self.mButtonDownLoc[0]
            pixelsPerDoubling = 0.2*self.panAndZoomState.shape[0] #lower = zoom more
            changeFactor = (1.0+abs(dy)/pixelsPerDoubling)
            changeFactor = min(max(1.0,changeFactor),5.0)
            if changeFactor < 1.05:
                dy = 0 #this was a click, not a draw. So don't zoom, just re-center.
            if dy > 0: #moved down, so zoom out.
                zoomInFactor = 1.0/changeFactor
            else:
                zoomInFactor = changeFactor
#            print("zoomFactor: %s"%zoomFactor)
            self.panAndZoomState.zoom(self.mButtonDownLoc[0], self.mButtonDownLoc[1], zoomInFactor)
        elif event == cv2.EVENT_LBUTTONDOWN:
            #the user pressed the left button. 
            coordsInDisplayedImage = np.array([y,x])
            if np.any(coordsInDisplayedImage < 0) or np.any(coordsInDisplayedImage > self.panAndZoomState.shape[:2]):
                print("you clicked outside the image area")
            else:
                #print("you clicked on %s within the zoomed rectangle"%coordsInDisplayedImage)
                coordsInFullImage = self.panAndZoomState.ul + coordsInDisplayedImage
                cv2.circle(self.img,(coordsInFullImage[1],coordsInFullImage[0]),2,self.color,-1)
                points.append((coordsInFullImage[1],coordsInFullImage[0]))
                self.redrawImage()
                #print("this is %s in the actual image"%coordsInFullImage)
                #print("this pixel holds %s, %s"%(self.img[coordsInFullImage[0],coordsInFullImage[1]]))
                #if self.onLeftClickFunction is not None:
                    #self.onLeftClickFunction(coordsInFullImage[0],coordsInFullImage[1])
        #you can handle other mouse click events here
    def onVTrackbarMove(self,tickPosition):
        self.panAndZoomState.setYFractionOffset(float(tickPosition)/self.TRACKBAR_TICKS)
    def onHTrackbarMove(self,tickPosition):
        self.panAndZoomState.setXFractionOffset(float(tickPosition)/self.TRACKBAR_TICKS)
    def redrawImage(self):
        pzs = self.panAndZoomState
        cv2.imshow(self.WINDOW_NAME, self.img[pzs.ul[0]:pzs.ul[0]+pzs.shape[0], pzs.ul[1]:pzs.ul[1]+pzs.shape[1]])

class PanAndZoomState(object):
    """ Tracks the currently-shown rectangle of the image.
    Does the math to adjust this rectangle to pan and zoom."""
    MIN_SHAPE = np.array([50,50])
    def __init__(self, imShape, parentWindow):
        self.ul = np.array([0,0]) #upper left of the zoomed rectangle (expressed as y,x)
        self.imShape = np.array(imShape[0:2])
        self.shape = self.imShape #current dimensions of rectangle
        self.parentWindow = parentWindow
    def zoom(self,relativeCy,relativeCx,zoomInFactor):
        self.shape = (self.shape.astype(np.float64)/zoomInFactor).astype(np.int64)
        #expands the view to a square shape if possible. (I don't know how to get the actual window aspect ratio)
        self.shape[:] = np.max(self.shape) 
        self.shape = np.maximum(PanAndZoomState.MIN_SHAPE,self.shape) #prevent zooming in too far
        c = self.ul+np.array([relativeCy,relativeCx])
        self.ul = (c-self.shape/2).astype(np.int64)
        self._fixBoundsAndDraw()
    def _fixBoundsAndDraw(self):
        """ Ensures we didn't scroll/zoom outside the image. 
        Then draws the currently-shown rectangle of the image."""
#        print("in self.ul: %s shape: %s"%(self.ul,self.shape))
        self.ul = np.maximum(0,np.minimum(self.ul, self.imShape-self.shape))
        self.shape = np.minimum(np.maximum(PanAndZoomState.MIN_SHAPE,self.shape), self.imShape-self.ul)
#        print("out self.ul: %s shape: %s"%(self.ul,self.shape))
        yFraction = float(self.ul[0])/max(1,self.imShape[0]-self.shape[0])
        xFraction = float(self.ul[1])/max(1,self.imShape[1]-self.shape[1])
        cv2.setTrackbarPos(self.parentWindow.H_TRACKBAR_NAME, self.parentWindow.WINDOW_NAME,int(xFraction*self.parentWindow.TRACKBAR_TICKS))
        cv2.setTrackbarPos(self.parentWindow.V_TRACKBAR_NAME, self.parentWindow.WINDOW_NAME,int(yFraction*self.parentWindow.TRACKBAR_TICKS))
        self.parentWindow.redrawImage()
    def setYAbsoluteOffset(self,yPixel):
        self.ul[0] = min(max(0,yPixel), self.imShape[0]-self.shape[0])
        self._fixBoundsAndDraw()
    def setXAbsoluteOffset(self,xPixel):
        self.ul[1] = min(max(0,xPixel), self.imShape[1]-self.shape[1])
        self._fixBoundsAndDraw()
    def setYFractionOffset(self,fraction):
        """ pans so the upper-left zoomed rectange is "fraction" of the way down the image."""
        self.ul[0] = int(round((self.imShape[0]-self.shape[0])*fraction))
        self._fixBoundsAndDraw()
    def setXFractionOffset(self,fraction):
        """ pans so the upper-left zoomed rectange is "fraction" of the way right on the image."""
        self.ul[1] = int(round((self.imShape[1]-self.shape[1])*fraction))
        self._fixBoundsAndDraw()


# %%
class refpoints:
    def __init__(self,x,y,lat,long):
        self.x = x
        self.y = y
        self.lat = lat
        self.long = long
    
    def linearization(self):
        iterable = np.linspace(0,len(self.x)-1,len(self.x))
        combinations = list(itertools.combinations(iterable, 3))
        X = np.zeros(4)
        for c in combinations:
            i,j,k = int(c[0]),int(c[1]),int(c[2])
            mat_a = [[self.x[i]-self.x[j], self.y[i]-self.y[j],0,0],[0,0,self.x[i]-self.x[j], self.y[i]-self.y[j]],[self.x[j]-self.x[k], self.y[j]-self.y[k],0,0],[0,0,self.x[j]-self.x[k], self.y[j]-self.y[k]]]
            mat_b = [self.lat[i]-self.lat[j],self.long[i]-self.long[j],self.lat[j]-self.lat[k],self.long[j]-self.long[k]]
            X += np.linalg.inv(mat_a).dot(mat_b)  
        return X/len(combinations)

class unkpoints:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        #self.colour = get_colour(self.x,self.y,image)
    
    def get_coordinates(self,X,ref):
        lat = np.float64(ref.lat[0] + (self.x-ref.x[0])*X[0] + (self.y-ref.y[0])*X[1])
        long = np.float64(ref.long[0] + (self.x-ref.x[0])*X[2] + (self.y-ref.y[0])*X[3])
        return lat,long

def get_colour(x,y,image):
    kernel = image[y-1:y+2,x-1:x+2]
    avg = np.zeros(3)
    for k in range(3):
        for j in range(3):
            for i in range(3):
                avg[k] += kernel[i,j,k]
    avg /= 9
    min = 10000
    if math.sqrt((avg[0])**2 + (avg[1])**2 + (avg[2]-255)**2)<min:  #CHECKS FOR RED
        min = math.sqrt((avg[0])**2 + (avg[1])**2 + (avg[2]-255)**2)
        col = 'r' 
    if math.sqrt((avg[0])**2 + (avg[1]-255)**2 + (avg[2])**2)<min: #CHECKS FOR GREEN
        min = math.sqrt((avg[0])**2 + (avg[1]-255)**2 + (avg[2])**2)
        col = 'g'
    if math.sqrt((avg[0]-255)**2 + (avg[1]-255)**2 + (avg[2])**2)<min: #CHECKS FOR YELLOW
        min = math.sqrt((avg[0]-255)**2 + (avg[1]-255)**2 + (avg[2])**2)
        col = 'y'
    if math.sqrt((avg[0]-255)**2 + (avg[1])**2 + (avg[2]-255)**2)<min: #CHECKS FOR PINK
        min = math.sqrt((avg[0]-255)**2 + (avg[1])**2 + (avg[2]-255)**2)
        col = 'p'
    if math.sqrt((avg[0])**2 + (avg[1])**2 + (avg[2])**2)<min: #CHECKS FOR BLACK
        min = math.sqrt((avg[0])**2 + (avg[1])**2 + (avg[2])**2)
        col = 'b'
    if math.sqrt((avg[0]-255)**2 + (avg[1]-255)**2 + (avg[2]-255)**2)<min: #CHECKS FOR WHITE
        min = math.sqrt((avg[0]-255)**2 + (avg[1]-255)**2 + (avg[2]-255)**2)
        col = 'w'
    return col
        
# %% Input Arguments

parser = argparse.ArgumentParser()
parser.add_argument("--image", help="Path to the image of the area where the boat is supposed to move", default='stadium.png')
parser.add_argument("--rad", help="Save the coordinates of the waypoins in radians (default is degrees)", action="store_true")
parser.add_argument("--file", help="Path to .txt file with the reference coordinates", default=None)
args = parser.parse_args()

try:
    if not os.path.isfile(args.image):
        raise FileNotFoundError
except FileNotFoundError:
    print("Path to image does not exist")
    exit()
else:
    print('Path to image found')

if args.file:
    try:
        if not os.path.isfile(args.file):
            raise FileNotFoundError
    except FileNotFoundError:
        print("Path to file does not exist")
        exit()
    else:
        print('Path to file found')
# %%
points = []
img = cv2.imread(args.image, 1)
original = img.copy()

input("Press ENTER to select at least 3 reference points (please make sure you remember the selection order): ")
window = PanZoomWindow(img, "Reference Points",color = (0,0,0))
# wait for a key to be pressed to exit
cv2.waitKey(0)
 
# close the window
cv2.destroyAllWindows()

#print(points)

lat = []
long = []

if args.file:
    data = pd.read_csv(args.file)
    for i in range(len(data.lat)):
        lat.append(np.float64(data.lat[i]))
        long.append(np.float64(data.long[i]))
else:
    for i in range(len(points)):
        a = input('Insert Latitude for point ' + str(i+1) + ': ')
        lat.append(np.float64(a))
        b = input('Insert Longitude for point ' + str(i+1) +': ')
        long.append(np.float64(b))


ref_points = refpoints([coor[0] for coor in points],[coor[1] for coor in points],lat,long)
points = []

input("Press ENTER to select the waypoints: ")
window = PanZoomWindow(img, "Unknown Points",color = (0,0,255))
# wait for a key to be pressed to exit
cv2.waitKey(0)
 
# close the window
cv2.destroyAllWindows()

#print(points)
unk_points = []
for p in points:
    unk_points.append(unkpoints(p[0],p[1]))

# %% Write csv file to output

with open('waypoints.csv', 'w',newline='') as f:
    # create the csv writer
    writer = csv.writer(f)
    for u in unk_points:
        lat_w,long_w = u.get_coordinates(ref_points.linearization(),ref_points)

        if not args.rad:
            # write a row to the csv file
            writer.writerow([lat_w])
            writer.writerow([long_w])
        else:
            writer.writerow([lat_w*np.pi/180])
            writer.writerow([long_w*np.pi/180])
