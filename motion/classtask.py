from PIL import Image
import numpy as np
import os
import math

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
def filterSmallAreas(areas):
    max_value = int(np.round(np.max(areas)))
    for i in range(1, max_value):
        area_size = np.sum(areas == i)
        if (area_size < 3):
            areas[areas == i] = 0
    return areas
def countAreas(areas):
    #print(np.unique(areas))
    return len(np.unique(areas)) - 1
def exportImage(numpy_image, num):
    pil_image = Image.fromarray(np.clip(np.uint8(numpy_image), 0, 255))
    if num == 0:
        pil_image.save('OUTTT.jpg')
    else:
        pil_image.save('OUTTT2.jpg')
 
num=0
fp = ['motion/c1.jpg','motion/c2.jpg']
for filepath in fp:
    pil_image = Image.open(filepath)
    a = np.asarray(pil_image, np.int)
    b = np.mean(a,2)
    b = np.where(b>200, 255, 0)
    print()
    areas = identifyAreas(b)
    areas = filterSmallAreas(areas)
    print(countAreas(areas))
    exportImage(np.where(areas==0,0,255),num)
    num+=1

    