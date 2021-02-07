from PIL import Image
import numpy as np
import os
import math

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

def numberAreas(areas):
    #print(np.unique(areas))
    vals = (np.unique(areas))
    for i in range(len(vals)):
        areas[areas == vals[i]] = i

def trackAreas(areas, last_areas):
    foundareas = np.zeros(areas.shape)
    for key in last_areas:
        pos = last_areas[key]
        if areas[math.floor(pos[0]),math.floor(pos[1])] != 0:
            foundareas[np.where(areas == areas[math.floor(pos[0]),math.floor(pos[1])], True, False)] = key
            areas[np.where(areas == areas[math.floor(pos[0]),math.floor(pos[1])], True, False)] = 0
    foundfish_count = countAreas(foundareas)
    numberAreas(areas)
    annoyingvalue = list(last_areas.keys())[len(last_areas.keys())-1]
    areas = areas + annoyingvalue
    areas[np.where(areas == annoyingvalue, True, False)] = 0

    foundareas = foundareas + areas

    last_areas = findCOA(areas, annoyingvalue)
    onscreenfish_count = countAreas(foundareas)
    fish_count = annoyingvalue
    return last_areas, foundfish_count, onscreenfish_count, fish_count

def findCOA(areas, offset): #finds center of each area
    center = {}
    for i in range(countAreas(areas)):
        mask = np.where(areas == i + offset, True, False)
        center[i + offset] = findEnds(mask)
    #print(center)
    return center

def findEnds(mask):
    height, width = mask.shape
    startH = 0
    endH = height
    verticalfound = False
    for i in range(height):
        if np.sum(mask[i,:]) == 0 and not verticalfound:
            startH = i
        elif(np.sum(mask[i,:]) > 0):
            verticalfound = True
        elif (np.sum(mask[i,:]) == 0 and verticalfound):
            if i<endH:
                endH = i
    j = (startH+endH)/2
    startW = 0
    endW = width
    horizontalfound = False
    for i in range(width):
        if np.sum(mask[:,i]) == 0 and not horizontalfound:
            startW = i
        elif(np.sum(mask[:,i]) > 0):
            horizontalfound = True
        elif (np.sum(mask[:,i]) == 0 and horizontalfound):
            if i<endW:
                endW = i
    k = (startW+endW)/2
    return [j,k]
        



        



frames = loadSequence('motion/coral-dense/coral-dense-', '.png', 601, 216, 384, 3)
print(frames.shape)

background = np.median(frames, 0)
fakefish = 0
for i in range(601):
    mask = getForegroundMask(frames[i], background)
    areas = identifyAreas(mask)
    areas = filterSmallAreas(areas)
    onscreenfish_count = countAreas(areas)
    if i==0:
        numberAreas(areas)
        last_areas = findCOA(areas, 0)
    else:
        last_areas, foundfish_count, onscreenfish_count, fish_count = trackAreas(areas, last_areas)
        flast_areas, ffoundfish_count, fonscreenfish_count, ffish_count = trackAreas(areas, last_areas)
        print(' old fish: ', foundfish_count, ',  onscreen fish: ', onscreenfish_count, ',  total fish count: ', fish_count)
        print('fold fish: ', ffoundfish_count, ', fonscreen fish: ', fonscreenfish_count, ', ftotal fish count: ', ffish_count)
        print('subtracted ', foundfish_count - ffoundfish_count, ',subtracted onsc: ', onscreenfish_count - fonscreenfish_count, ',subtracted tot cnt: ', fish_count - ffish_count)
        fakefish = fakefish + fonscreenfish_count - ffoundfish_count
        print('i = ',i,' _____ actual fish count: ', fish_count - fakefish, '_________________________________________')

exportImage((areas * 71) % 256 , './motion/output/areas.png')
exportImage(background, './motion/output/background2.png')

for i in range(len(frames)):
    os.makedirs('output', exist_ok=True)
    mask = removeBackground(frames[i], background)
    exportImage(mask, f'./motion/output/mask-{i+1}.png')
    exportImage((areas * 71) % 256 , f'./output/areas{i:03d}.png')
    exportImage(mask, f'./output/mask-{i+1:03d}.png')
