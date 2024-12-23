from random import choice, getrandbits
from PIL import Image
import numpy as np

def gen(height, width, steps):
    rectangles = [[[x,x+1],[0,1]] for x in range(width)]
    rectangles.extend([[[0,width],[y,y+1]] for y in range(1,height)])

    joints = {}
    for x in range(1,width):
        joints[(x,0)] = [[x-1, x], 1, 1]
        joints[(x,1)] = [[x, x-1], 1, 0]
    for y in range(2,height):
        joints[(0,y)] = [[width + y-2, width + y-1], 0, 1]
        joints[(width,y)] = [[width + y-1, width + y-2], 0, 0]
    joints[(0,1)] = [[0, width], 0, 1]
    joints[(width,1)] = [[width, width-1], 0, 0]

    segments = [[[0,width] for y in range(height)],[[0,1] for x in range(width)]]

    for _ in range(steps):
        joint = choice(list(joints))
        rect_indices, xy, i = joints[joint]
        jointed = [rectangles[rect_index] for rect_index in rect_indices]
        edges = [rect[xy][i] for rect in jointed] # i=1 for +
        if edges[0] == edges[1]:
            continue
        top_left = edges[0] < edges[1]
        small = i ^ top_left
        big = 1 - small
        smallrect, bigrect = jointed[small], jointed[big]
        smallindex, bigindex = rect_indices[small], rect_indices[big]

        center, corner, new = [[None, None] for _ in range(3)]
        newbig = center[xy] = new[xy] = rectangles[smallindex][xy][i]
        newsmall = corner[1-xy] = new[1-xy] = rectangles[bigindex][1-xy][top_left]
        center[1-xy], corner[xy] = joint[1-xy], joint[xy]
        center, corner, new = tuple(center), tuple(corner), tuple(new)

        old_dist = abs(joint[xy] - center[xy])
        new_dist = abs(joint[1-xy] - corner[1-xy])
        for _ in range(new_dist-old_dist):
            if not getrandbits(2):
                break
        else:
            rectangles[bigindex][xy][1-i] = newbig
            rectangles[smallindex][1-xy][top_left] = newsmall
            
            del joints[joint]
            center_rects = joints[center][0]
            center_rects[big] = bigindex
            joints[center] = [center_rects, xy, i]
            if corner in joints:
                corner_rects = joints[corner][0]
                corner_rects[corner_rects.index(bigindex)] = smallindex
            joints[new] = [[rect_indices[1], rect_indices[0]], 1-xy, 1-top_left]
    
    return rectangles

def mondrian(height, width, steps, unit, thickness):
    image = [[255]*(unit*width) for _ in range(unit*height)]
    for rect in gen(height, width, steps):
        for xy in range(2):
            start, end = rect[xy]
            for along in range(unit*start, unit*end):
                for i in range(2):
                    for t in range(thickness):
                        fixed = unit * rect[1-xy][i]
                        fixed += ~t if i else t
                        pixel = [fixed, along]
                        image[pixel[xy]][pixel[1-xy]] = 0
    return Image.fromarray(np.array(image).astype(np.uint8))

image = mondrian(30, 36, 1000000, 25, 1)
image.save('mondy.png')
image.show()
