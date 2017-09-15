#!/usr/bin/env python

"""
@Author : Mohit Jain
@Email  : develop13mohit@gmail.com

@About  : Script to render simple number plate images. 
"""

# Imports
import os
import sys
import random

import argparse
import progressbar

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

def load_fonts(font_dir):
    """
    args:
        -font_dir : path to directory containing font tff's
    return:
        -fonts : dictionary of fonts loaded with various font sizes as keys for each font type
    """
    fonts = {}

    font_sizes = [120, 130, 140, 160, 180]
    font_tffs = [os.path.join(font_dir,i) for i in os.listdir(font_dir) if i.lower().endswith('.tff') or i.lower().endswith('.ttf')]

    bar = progressbar.ProgressBar(maxval=len(font_tffs)).start()
    for i, font in enumerate(font_tffs):
        font_name = '-'.join(font.split('/')[-1].split('.')[:-1]).replace(' ','-')
        fonts[font_name] = {}
        
        for size in font_sizes:
            fonts[font_name][str(size)] = ImageFont.truetype(font, size)
        
        bar.update(i)   

    print "Done."

    return fonts

def load_bg_imgs(bg_imgs_dir):
    """
    args:
        -bg_imgs_dir : path to directory containing bg images
    return:
        -bg_imgs : dictionary of bg image paths with image-name as key
    """
    bg_imgs = {}
    
    bg_imgs_path = [os.path.join(bg_imgs_dir,i) for i in os.listdir(bg_imgs_dir) if i.endswith('.png')]

    bar = progressbar.ProgressBar(maxval=len(bg_imgs_path)).start()
    for i, img in enumerate(bg_imgs_path):
        img_name = '-'.join(img.split('/')[-1].split('.')[:-1]).replace(' ','-')
        bg_imgs[img_name] = img

    print "Done."

    return bg_imgs

def load_common():
    """
    return:
        -common : dictionary containing common variables for number plate text generation.
    """
    common = {}
    
    STATES = ['AN','AP','AP','AP','AP','AR','AS','BR','CG','CH','DD','DL','DL','DL','DL','DL','DN','GA','GJ','HR','HP','JH','JK','KA','KL','LD','MH','    ML','MN','MP','MP','MP','MP','MZ','NL','OD','PB','PY','RJ','SK','TN','TR','TS','UK','UP','WB']
    NUMBERS = '0123456789'
    LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    DELIM = '  .'

    common['STATES'] = STATES
    common['NUMBERS'] = NUMBERS
    common['LETTERS'] = LETTERS
    common['DELIM'] = DELIM

    print "Done."

    return common

def gen_text(common):
    """
    args:
        -common : dict of common variables.
    return:
        -text : random permutation of possible common-texts.
    """
    state = random.choice(common['STATES'])
    delim = random.choice(common['DELIM'])
    dig1 = random.choice(common['NUMBERS'])
    dig2 = random.choice(common['NUMBERS'])
    let1 = random.choice(common['LETTERS'])
    let2 = random.choice(common['LETTERS'])
    dig3 = random.choice(common['NUMBERS'])
    dig4 = random.choice(common['NUMBERS'])
    dig5 = random.choice(common['NUMBERS'])
    dig6 = random.choice(common['NUMBERS'])
    
    """
    TODO : Support multiple formats.
    """
    text = "{}{}{}{}{}{}{}{}{}{}{}{}".format(state, delim, dig1, dig2, delim, let1, let2, delim, dig3, dig4, dig5, dig6)

    return text

def rescale_to_fit(img, text, font):
    """
    args:
        -img : image to rescale to fit to text width
        -text : text string containing number plate info
        -font : loaded font with its respective font-size
    return:
        -re_img : rescaled image
    """
    t_height = max(font.getsize(c)[1] for c in text)
    t_width, t_height = 0, 0
    for c in text:
        char_size = font.getsize(c)
        t_width += char_size[0]
        t_height = max(t_height, char_size[1])

    re_w, re_h = img.size
    offset = re_w*0.2
    if re_w < t_width+offset:
        re_w = int(t_width * 1.2)
    if re_h < t_height:
        re_h = int(t_height * 1.2)

    re_img = img.resize((re_w, re_h), resample=Image.BILINEAR)

    return re_img

def render(n_imgs, common, fonts, bg_imgs, out_dir, mask_dir):
    """
    args:
        -n_imgs   : number of images to render.
        -common   : dict of common variables.
        -fonts    : dict of loaded fonts.
        -bg_imgs  : dict of loaded bg images.
        -out_dir  : path of directory to store outputs in.
        -mask_dir : name of directory to store masks in.
    return:
        None
    """
    bar = progressbar.ProgressBar(maxval=n_imgs).start()
    for i in range(n_imgs):
        # Generate random number plate combination
        plate_text = gen_text(common)

        # Chose bg image
        bg_img_name = random.choice(bg_imgs.keys())
        bg_img = Image.open(bg_imgs[bg_img_name])

        # Chose font style and size
        font_name = random.choice(fonts.keys())
        font_type = fonts[font_name]
        font_size = random.choice(font_type.keys())
        font = font_type[font_size]

        # Rescale bg_img to fit text width
        bg_img = rescale_to_fit(bg_img, plate_text, font)
        bg_img_size = bg_img.size

        # Overlay text on bg image
        canvas = ImageDraw.Draw(bg_img)
        """
        TODO : Add offset for starting co-ordinate based on image type (fetch from image name).
             : Randomize color extraction.
        """
        x_cood = int(bg_img_size[0]*0.1)
        y_cood = int(bg_img_size[1]*0.1)
        color = int(random.random()*50)
        canvas.text((x_cood, y_cood), plate_text, (color, color, color), font=font)

        # Overlay text on white background
        white_img = Image.new("RGB", (bg_img_size), "white")
        canvas = ImageDraw.Draw(white_img)
        canvas.text((x_cood, y_cood), plate_text, (0,0,0), font=font)

        # Save Images
        out_img_name = '_'.join([bg_img_name.split('.')[0], font_name, font_size, plate_text, '.png'])
        bg_img.save(os.path.join(out_dir, out_img_name))

        out_mask_name = 'mask_'+out_img_name
        white_img.save(os.path.join(out_dir, mask_dir, out_mask_name))

        bar.update(i)

    print "Done."

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Render synthetic number plates.')
    parser.add_argument('--font_dir',type=str,nargs='?',help='path to fonts directory',default='./fonts')
    parser.add_argument('--bg_imgs_dir',type=str,nargs='?',help='path to bg-images directory',default='./cleaned')
    parser.add_argument('--out_dir',type=str,nargs='?',help='path to store the rendered images',default='./out_render')
    parser.add_argument('--mask_dir',type=str,nargs='?',help='name of directory to be created for character mask images',default='masks')
    parser.add_argument('--n_imgs',type=int,nargs='?',help='number of images to render',default='100')
    args = parser.parse_args()

    print "[INFO] Loading Fonts"
    fonts = load_fonts(args.font_dir)

    print "[INFO] Loading Background Images"
    bg_imgs = load_bg_imgs(args.bg_imgs_dir)

    print "[INFO] Loading Common Variables"
    common = load_common()

    # Create folder for character-masks
    os.mkdir(os.path.join(args.out_dir, args.mask_dir))

    print "[INFO] Rendering Synthetic Images"
    render(args.n_imgs, common, fonts, bg_imgs, args.out_dir, args.mask_dir)
