#!/usr/bin/env python

"""
@Author : Mohit Jain
@Email  : develop13mohit@gmail.com

@About  : Script to duplicate images with some random noise addition.
"""

# Imports
import os
import random
import progressbar

import cv2
import numpy as np
from skimage.util import random_noise


def perspective_dist(cv_img, pts1=None, pts2=None):
    """
    args:
        -img   : input numpy image
        -pts1  : set of points to map from
        -pts2  : set of points to map to
    return:
        -d_img : distorted numpy image
    """
    rows,cols,ch = cv_img.shape

    if not pts1:
        pts1 = np.float32([[0,0],[cols,0],[0,rows],[cols,rows]])
    if not pts2:
        seed = random.random()
        scale = random.uniform(0.1, 0.3)
        n_scale = 1-scale
        if seed < 0.4:
            pts2 = np.float32([[0,0],[int(n_scale*cols),int(scale*rows)],[0,rows],[int(n_scale*cols),int(n_scale*rows)]])
        elif seed < 0.8:
            pts2 = np.float32([[int(scale*cols),int(scale*rows)],[cols,0],[int(scale*cols),int(n_scale*rows)],[cols,int(n_scale*rows)]])
        else:
            pts2 = np.float32([[int(scale*cols),int(scale*rows)],[int(n_scale*cols),int(scale*rows)],[int(scale*cols),int(n_scale*rows)],
                                    [int(n_scale*cols),int(n_scale*rows)]])

    M = cv2.getPerspectiveTransform(pts1,pts2)
    d_img = cv2.warpPerspective(cv_img,M,(cols,rows))

    return d_img

def skew_dist(cv_img, pts1=None, pts2=None, skew=None):
    """
    args:
        -cv_img: input numpy image
        -pts1  : reference source points
        -pts2  : reference destination points
        -skew  : skew factor
    return:
        -s_img : skewed numpy image
    """
    rows,cols,ch = cv_img.shape

    if not skew:
        skew = random.randint(-100, 100)
    if not pts1:
        pts1 = np.float32([[0,0],[cols,0],[0,rows]])
    if not pts2:
        pts2 = np.float32([[pts1[0][0]+skew,pts1[0][1]],[pts1[1][0]+skew,pts1[1][1]],pts1[2]])

    M = cv2.getAffineTransform(pts1,pts2)
    s_img = cv2.warpAffine(cv_img,M,(cols+np.abs(skew),rows))

    return s_img

def add_noise(cv_img, n_type=None):
    """
    args:
        -cv_img : input numpy image
        -n_type : type of noise to be added, one of 'gaussian','localvar','poisson','salt','pepper','s&p','speckle'
    return:
        -n_img  : noisy numpy image
    """
    if not n_type:
        modes = ['gaussian','localvar','poisson','salt','pepper','s&p','speckle']
        n_type = random.choice(modes)

    n_img = random_noise(cv_img, mode=n_type)*255 #random_noise return image in 0->1 format.

    return n_img, n_type

if __name__=='__main__':
    out_dir = 'distorted'
    n_loop = 3

    img_dir = '/mnt/Deepak'
    n_types = os.listdir(img_dir)

    imgs = []
    for x in range(n_loop):
        for n_type in n_types:
            imgs += [os.path.join(img_dir, n_type, i) for i in os.listdir(os.path.join(img_dir, n_type))]

    bar = progressbar.ProgressBar(maxval=len(imgs)).start()
    for n, img in enumerate(imgs):
        f_name = '_'.join(img.split('/')[-2:])
        im = cv2.imread(img)
        try:
            shape = im.shape
        except:
            print "[ERROR] : Unable to read file :",img
            continue
    
        if random.random()<0.8:
            f_name = 'perspec_'+f_name
            im = perspective_dist(im)
            if random.random()<0.5:
                f_name = 'skew_'+f_name
                im = skew_dist(im)
            if random.random()<0.5:
                im, n_type = add_noise(im)
                f_name = n_type+'_'+f_name
        else:
            f_name = 'skew_'+f_name
            im = skew_dist(im)
            if random.random()<0.5:
                im, n_type = add_noise(im)
                f_name = n_type+'_'+f_name

        cv2.imwrite(os.path.join(out_dir, f_name), im)
        
        bar.update(n)
