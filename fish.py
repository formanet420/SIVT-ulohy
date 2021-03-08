from PIL import Image
import numpy as np
import os
import math

def exportImage(numpy_image, output_path):
    pil_image = Image.fromarray(np.clip(np.uint8(numpy_image), 0, 255))
    pil_image.save(output_path)

class Fish(object):
    def __init__(self, mask, pic):
        exportImage(255*mask, 'F:/pic.jpg')
        self.lsize = np.sum(mask)
        self.size = [self.lsize]
        #print('size: ' + str(self.lsize))
        self.lvelocity = 0
        self.velocity = []
        
        [self.lhpos, self.lvpos] = self.findLpos(mask)
        self.hpos = [self.lhpos]
        self.vpos = [self.lvpos]
        self.lcolor = self.findColor(mask,pic)
        self.color = [self.lcolor]
        self.n_observations = 1
        #print('color: ' + str(self.color))
        
    
    def findLpos(self, mask):
        height, width = mask.shape
        n = 0
        lvpos = 0
        lhpos = 0
        for i in range(height):
            if n > self.lsize/2:
                continue
            else:
                n = n + np.sum(mask[i,:])
                lvpos = lvpos + 1 
        #print('Vpos: ' + str(lvpos))
        n = 0
        for i in range(width):
            if n > self.lsize/2:
                continue
            else:
                n = n + np.sum(mask[:,i])
                lhpos = lhpos + 1
        #print('Hpos: ' + str(lhpos))
        return lhpos, lvpos

    def findColor(self, mask, pic):
        color = []
        for ch in range(3):
            channel = pic[:,:,ch]  
            exportImage(np.where(mask == 1, channel, 0), 'F:/ch.png')          
            color.append(np.sum(np.where(mask == 1, channel, 0))/self.lsize)
        return color

    def getLpos(self):
        return self.lhpos, self.lvpos

    def getLsize(self):
        return self.lsize
        
    def getLcolor(self):
        return self.lcolor

    def predPos(self):
        if self.lvelocity == 0:
            #print('velocity is zero')
            #print(self.getLpos())
            return self.getLpos()
        else:
            print('this might not happen')
            print(tuple(sum(x) for x in zip(self.lvelocity, self.getLpos())))
            return tuple(sum(x) for x in zip(self.lvelocity, self.getLpos()))

    def addRec(self,fish):
        [nx,ny] = fish.getLpos()
        
        self.lsize = fish.getLsize()
        self.size.append(self.lsize)
        
        self.lcolor = fish.getLcolor()
        self.color.append(self.lcolor)

        self.lhpos, self.lvpos = [nx,ny]        #h = i (row), v = j (column)
        self.hpos.append(self.lhpos)
        self.vpos.append(self.lvpos)

        self.lvelocity = self.guessDX()
        self.velocity.append(self.lvelocity)
        
        self.n_observations += 1 

    def guessDX(self):
        if len(self.hpos) > 3:
            n = 3
        else:
            n = len(self.hpos)
        dh = (self.hpos[len(self.hpos)-1] - self.hpos[len(self.hpos)-1-n])/n
        dv = (self.vpos[len(self.vpos)-1] - self.vpos[len(self.vpos)-1-n])/n
        return dh, dv



def findfish(new, cat):
    similarity = []
    for nf in new:
        simp = []
        [nx,ny] = nf.getLpos()
        nsize = nf.getLsize()
        ncolor = nf.getLcolor()
        for kf in cat:
            [kx, ky] = kf.predPos()     
            ksize = kf.getLsize()
            kcolor = kf.getLcolor()
            #print('new:')
            #print(str(nx) + ' ' + str(ny) + ' ' + str(nsize) + ' ' + str(ncolor))
            #print('old:')
            #print(str(kx) + ' ' + str(ky) + ' ' + str(ksize) + ' ' + str(kcolor))
            #print('similatitty score: ' + str(comparefish(nx,ny,nsize,ncolor, kx,ky,ksize,kcolor)))
            simp.append(comparefish(nx,ny,nsize,ncolor, kx,ky,ksize,kcolor))
        print(simp)
        similarity.append(simp)
    arr = np.array([np.array(xi) for xi in similarity])
    [fishnum, catnum] = np.shape(arr)

    for i in range(fishnum):
        if np.sum(arr)==0:
            print('run out of fish')
            break
        topfish = np.argmax(arr)
        fishcol = (topfish % catnum) 
        Ncat = math.floor((topfish/fishnum)-0.0001)
        cat[Ncat].addRec(new[fishcol])

        arr[:,fishcol] = 0
        print(arr)
        print()
    return cat

def comparefish(nx,ny,nsize,ncolor, kx,ky,ksize,kcolor):
    spatial_importance = 2
    dx = abs(nx-kx)
    dy = abs(ny-ky)
    dist = math.sqrt(dx*dx + dy*dy)
    if dist < 1:
        p1 = 1.5 * spatial_importance
    else:
        p1 = spatial_importance/dist
    #print('Probabilitoes:')
    #print('spacial:   ' + str(p1))
    dsize = abs(nsize-ksize)
    if dsize < 1:
        p2 = 1.5
    else:
        p2 = 1/dsize
    #print('size dif:  ' + str(p2))
    p3=0
    for ch in range(3):
        chdif = abs(ncolor[ch]-kcolor[ch])
        if chdif < 1:
            p3 = p3 + 1.5
        else:
            p3 = p3 + 1/chdif
    p3=p3/3
    #print('color d:   ' + str(p3))
    p = (p1+p2+p3)/(1.5*(2+spatial_importance))
    return p
