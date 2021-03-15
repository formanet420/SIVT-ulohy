from PIL import Image
import numpy as np
import os
import math
import fish
from matplotlib import pyplot as plot



def loadImage(file_path):
    pil_image = Image.open(file_path)
    numpy_image = np.asarray(pil_image, np.int)
    return numpy_image

def loadSequence(prefix, suffix, length, height, width, color_depth):
    video = np.zeros((length, height, width, color_depth))
    for i in range(length):
        image = loadImage(f'{prefix}{i+1:03d}{suffix}')
        video[i, :, :, :] = image
    # gray = np.sum(video,3) / 3
    # return gray
    return video

def exportImage(numpy_image, output_path):
    pil_image = Image.fromarray(np.clip(np.uint8(numpy_image), 0, 255))
    pil_image.save(output_path)

def getForegroundMask(frame, background):
    differences = np.mean(np.abs(frame - background), 2)
    foregroundMask = differences >= 15
    return foregroundMask

def removeBackground(frame, background):
    height, width, depth = frame.shape
    newBackground = np.zeros((height, width, depth))
    backgroundMask = getForegroundMask(frame, background) == False
    expandedMask = np.tile(np.reshape(backgroundMask, (height, width, 1)), (1, 1, 3))
    frame[expandedMask] = newBackground[expandedMask]
    return frame

def markArea(start_i, start_j, areas, area_id, mask):
    height, width = mask.shape
    stack = [(start_i, start_j)]
    while len(stack) > 0:
        i, j = stack.pop()
        if i < 0 or j < 0 or i >= height or j >= width: continue
        if (mask[i, j] == False): continue
        if (areas[i, j] != 0): continue
        areas[i, j] = area_id
        stack.append((i, j - 1))
        stack.append((i - 1, j))
        stack.append((i, j + 1))
        stack.append((i + 1, j))

def identifyAreas(mask):
    height, width = mask.shape
    areas = np.zeros(mask.shape)
    area_id = 1
    for i in range(height):
      for j in range(width):
        # do not search background.
        if (mask[i, j] == False): continue
        # do not search from already marked pixels.
        if (areas[i, j] != 0): continue
        markArea(i, j, areas, area_id, mask)
        area_id += 1
    return areas

def filterSmallAreas(areas):
    max_value = int(np.round(np.max(areas)))
    for i in range(1, max_value):
        area_size = np.sum(areas == i)
        if (area_size < 40):
            areas[areas == i] = 0
    return areas
            #print(f'deleted {i}')
def countAreas(areas):
    #print(np.unique(areas))
    return len(np.unique(areas)) - 1


frames = loadSequence('motion/coral-dense/coral-dense-', '.png', 601, 216, 384, 3)
print(frames.shape)

background = np.median(frames, 0)
fakefish = 0
totalfishcount = 0

fishcatalog = []
catlen = []
for i in range(601):
    mask = getForegroundMask(frames[i], background)
    areas = identifyAreas(mask)
    areas = filterSmallAreas(areas)
    onscreenfish_count = countAreas(areas)
    newfish = []
    for j in np.unique(areas).tolist():
        if j!=0:
            fishmask = np.where(areas == j, 1, 0)
            newfish.append(fish.Fish(fishmask, frames[i]))
    if i==0:
        fishcatalog = newfish          
    else:
        fishcatalog = fish.findfish(newfish, fishcatalog)
        catlen.append(len(fishcatalog))
        #if i in [20,100,400,600]:
        #    plot.plot(catlen)
        #    plot.show()
        
        print ('onscreen fish: '+str(onscreenfish_count))

print('total fish in video: ' + str(len(catlen)))









