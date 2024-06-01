from functools import reduce

from PIL import Image
import numpy as np
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb
import scipy.stats as sc
import pandas as pd

# matrix = [[1, 1, 5, 5, 5, 5, 5, 5, 1, 1, 1, 5, 3, 3, 3],
#           [5, 10, 5, 10, 10, 10, 5, 5, 10, 10, 5, 7.5, 10, 7.5, 7.5],
#           [0, 10, 10, 0, 10, 0, 10, 0, 10, 0, 10, 5, 5, 10, 5],
#           [1, 5, 5, 5, 1, 1, 1, 5, 1, 5, 5, 3, 3, 3, 5],
#           [7, 26, 25, 20, 26, 16, 21, 15, 22, 16,21, 20.5, 21, 23.5, 20.5]]

matrix = pd.read_csv(r"C:\Users\decel\Downloads\checkPlan.txt", sep='\t').transpose().to_numpy()
# with open(r"C:\Users\decel\Downloads\checkfirst.csv", 'r') as file:
#     lines = file.readlines()
#
# for line in lines:
#     line = line.replace("п»ї", "")
#     data_x.extend(map(float, line.strip().split()))
#
# with open(r"C:\Users\decel\Downloads\checksecond.csv", 'r') as file:
#     lines = file.readlines()
#
# for line in lines:
#     line = line.replace("п»ї", "")
#     data_y.extend(map(float, line.strip().split()))



# File_data = np.loadtxt(r"C:\Users\decel\Downloads\res.txt", dtype=float)

# for i in File_data:
#     correlations = []
#     for j in File_data:
#         correlations.append(str(sc.spearmanr(i, j).correlation))
#     print(' '.join(correlations))

print("-------------------------------------------------------")
# for i in File_data:
#     correlations = []
#     for j in File_data:
#         correlations.append(str(sc.kendalltau(i, j).statistic))
#     print(' '.join(correlations))
for i in matrix:
    correlations = []
    for j in matrix:
        correlations.append(str(sc.kendalltau(i, j).statistic))
    print(' '.join(correlations))

# print(sc.kendalltau(data_x, data_y))
# print(sc.kendalltau(File_data[0], File_data[1]).statistic)
# print(sc.kendalltau(File_data[0], File_data[2]).statistic)
# print(sc.kendalltau(File_data[0], File_data[3]).statistic)
# print(sc.kendalltau(File_data[1], File_data[2]).statistic)
# print(sc.kendalltau(File_data[1], File_data[3]).statistic)
# print(sc.kendalltau(File_data[2], File_data[3]).statistic)
# print("----------------------------------------------------------")
# print(kendalltau(File_data[0], File_data[1]))
# print(kendalltau(File_data[0], File_data[2]))
# print(kendalltau(File_data[0], File_data[3]))
# print(kendalltau(File_data[1], File_data[2]))
# print(kendalltau(File_data[1], File_data[3]))
# print(kendalltau(File_data[2], File_data[3]))

def compose(*funcs):
    if funcs:
        return reduce(lambda f, g: lambda *a, **kw: g(f(*a, **kw)), funcs)
    else:
        raise ValueError('Composition of empty sequence not supported.')

def letterbox_image(image, size):
    input_weight, input_height = image.size
    weight, height = size
    scale = min(weight/input_weight, height/input_height)
    new_weight = int(input_weight*scale)
    new_height = int(input_height*scale)

    image = image.resize((new_weight, new_height), Image.BICUBIC)
    new_image = Image.new('RGB', size, (128,128,128))
    new_image.paste(image, ((weight-new_weight)//2, (height-new_height)//2))
    return new_image

def rand(a=0, b=1):
    return np.random.rand()*(b-a) + a

def get_random_data(annotation_line, input_shape, random=True, max_boxes=20, jitter=.3, hue=.1, sat=1.5, val=1.5, proc_img=True):
    line = annotation_line.split()
    image = Image.open(line[0])
    input_weight, input_height = image.size
    height, weight = input_shape
    box = np.array([np.array(list(map(int,box.split(',')))) for box in line[1:]])

    if not random:
        scale = min(weight/input_weight, height/input_height)
        nw = int(input_weight*scale)
        nh = int(input_height*scale)
        dx = (weight-nw)//2
        dy = (height-nh)//2
        image_data=0
        if proc_img:
            image = image.resize((nw,nh), Image.BICUBIC)
            new_image = Image.new('RGB', (weight,height), (128,128,128))
            new_image.paste(image, (dx, dy))
            image_data = np.array(new_image)/255.

        # correct boxes
        box_data = np.zeros((max_boxes,5))
        if len(box)>0:
            np.random.shuffle(box)
            if len(box)>max_boxes: box = box[:max_boxes]
            box[:, [0,2]] = box[:, [0,2]]*scale + dx
            box[:, [1,3]] = box[:, [1,3]]*scale + dy
            box_data[:len(box)] = box

        return image_data, box_data

    # resize image
    new_ar = weight/height * rand(1-jitter,1+jitter)/rand(1-jitter,1+jitter)
    scale = rand(.25, 2)
    if new_ar < 1:
        nh = int(scale*height)
        nw = int(nh*new_ar)
    else:
        nw = int(scale*weight)
        nh = int(nw/new_ar)
    image = image.resize((nw,nh), Image.BICUBIC)

    # place image
    dx = int(rand(0, weight-nw))
    dy = int(rand(0, height-nh))
    new_image = Image.new('RGB', (weight,height), (128,128,128))
    new_image.paste(image, (dx, dy))
    image = new_image

    # flip image or not
    flip = rand()<.5
    if flip: image = image.transpose(Image.FLIP_LEFT_RIGHT)

    # distort image
    hue = rand(-hue, hue)
    sat = rand(1, sat) if rand()<.5 else 1/rand(1, sat)
    val = rand(1, val) if rand()<.5 else 1/rand(1, val)
    x = rgb_to_hsv(np.array(image)/255.)
    x[..., 0] += hue
    x[..., 0][x[..., 0]>1] -= 1
    x[..., 0][x[..., 0]<0] += 1
    x[..., 1] *= sat
    x[..., 2] *= val
    x[x>1] = 1
    x[x<0] = 0
    image_data = hsv_to_rgb(x) # numpy array, 0 to 1

    # make gray
    gray = rand() < .2
    if gray:
        image_gray = np.dot(image_data, [0.299, 0.587, 0.114])
        # a gray RGB image is GGG
        image_data = np.moveaxis(np.stack([image_gray, image_gray, image_gray]),0,-1)

    # invert colors
    invert = rand()< .1
    if invert:
        image_data = 1. - image_data

    # correct boxes
    box_data = np.zeros((max_boxes,5))
    if len(box)>0:
        np.random.shuffle(box)
        box[:, [0,2]] = box[:, [0,2]]*nw/input_weight + dx
        box[:, [1,3]] = box[:, [1,3]]*nh/input_height + dy
        if flip: box[:, [0,2]] = weight - box[:, [2,0]]
        box[:, 0:2][box[:, 0:2]<0] = 0
        box[:, 2][box[:, 2]>weight] = weight
        box[:, 3][box[:, 3]>height] = height
        box_w = box[:, 2] - box[:, 0]
        box_h = box[:, 3] - box[:, 1]
        box = box[np.logical_and(box_w>1, box_h>1)] # discard invalid box
        if len(box)>max_boxes: box = box[:max_boxes]
        box_data[:len(box)] = box

    return image_data, box_data
