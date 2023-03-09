# -*- coding: utf-8 -*-
"""Copy of Detectron2 Tutorial Demo.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1B9SxslGqW4cTllmaOfBY2F8YUUsSg0l1

# Detectron2 Beginner's Tutorial

<img src="https://dl.fbaipublicfiles.com/detectron2/Detectron2-Logo-Horz.png" width="500">

This is a modified verion of the original Detectron2 Tutorial notebook. In this version the **Train on a custom dataset** section is removed and focuses on only Object Detection, Segmentation and Panoptic Segmentation on images and video clips.

The original notebook can be found on the [Detectron2 Github repo](https://github.com/facebookresearch/detectron2).

Welcome to detectron2! This is the official colab tutorial of detectron2. Here, we will go through some basics usage of detectron2, including the following:
* Run inference on images or videos, with an existing detectron2 model
* Train a detectron2 model on a new dataset

You can make a copy of this tutorial by "File -> Open in playground mode" and make changes there. __DO NOT__ request access to this tutorial.

# Install detectron2
"""

!pip install pyyaml==5.1
# This is the current pytorch version on Colab. Uncomment this if Colab changes its pytorch version
!pip install torch==1.9.0+cu102 torchvision==0.10.0+cu102 -f https://download.pytorch.org/whl/torch_stable.html

# Install detectron2 that matches the above pytorch version
# See https://detectron2.readthedocs.io/tutorials/install.html for instructions
!pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu102/torch1.9/index.html
exit(0)  # After installation, you need to "restart runtime" in Colab. This line can also restart runtime

# check pytorch installation: 
import torch, torchvision
print(torch.__version__, torch.cuda.is_available())
assert torch.__version__.startswith("1.9")   # please manually install torch 1.9 if Colab changes its default version

# Some basic setup:
# Setup detectron2 logger
import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()

# import some common libraries
import numpy as np
import os, json, cv2, random
from google.colab.patches import cv2_imshow

# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog

"""# Run a pre-trained detectron2 model

We first download an image from the COCO dataset:
"""

!wget http://images.cocodataset.org/val2017/000000439715.jpg -q -O input.jpg
# !wget https://kharshit.github.io/img/panoptic_example.png -q -O city.jpg

im = cv2.imread("input.jpg")
im = cv2.resize(im, (640, 480), interpolation= cv2.INTER_AREA)
cv2_imshow(im)

"""Then, we create a detectron2 config and a detectron2 `DefaultPredictor` to run inference on this image."""

cfg = get_cfg()

"""### Object Detection
["...object detection, where the goal is to classify individual objects and localize them using a bounding box..."](https://kharshit.github.io/blog/2019/08/23/quick-intro-to-instance-segmentation)
"""

# Object Detection
# add project-specific config (e.g., TensorMask) here if you're not running a model in detectron2's core library
cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"))
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7  # set threshold for this model
# Find a model from detectron2's model zoo. You can use the https://dl.fbaipublicfiles... url as well
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml")
predictor = DefaultPredictor(cfg)

# Object Detection Visualizer
predictions = predictor(im)["instances"]
# We can use `Visualizer` to draw the predictions on the image.
v = Visualizer(im[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2)
out = v.draw_instance_predictions(predictions.to("cpu"))
cv2_imshow(out.get_image()[:, :, ::-1])

"""### Instance Segmentation
["...instance segmentation, we care about detection and segmentation of the instances of objects separately"](https://kharshit.github.io/blog/2019/08/23/quick-intro-to-instance-segmentation)

In other words, we perform segmentation only on the objects detected within the bounding box of object detection.
"""

# Instance Segmentation
# add project-specific config (e.g., TensorMask) here if you're not running a model in detectron2's core library
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
# Find a model from detectron2's model zoo. You can use the https://dl.fbaipublicfiles... url as well
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
predictor = DefaultPredictor(cfg)

# Instance Segmentation Visualizer
predictions = predictor(im)["instances"]
# We can use `Visualizer` to draw the predictions on the image.
v = Visualizer(im[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2)
out = v.draw_instance_predictions(predictions.to("cpu"))
cv2_imshow(out.get_image()[:, :, ::-1])

"""### Panoptic Segmentation
["...panoptic segmentation combines semantic and instance segmentation such that all pixels are assigned a class label and all object instances are uniquely segmented."](https://kharshit.github.io/blog/2019/10/18/introduction-to-panoptic-segmentation-tutorial)

Panoptic segmentation classifies all pixels in the image within a polygonal bounding area including objects and background scenery. Unlike, object and Instance segmentation which only care about individual objects in the image.


"""

# Panoptic Segmentation
# Ref: https://youtu.be/Pb3opEFP94U
# add project-specific config (e.g., TensorMask) here if you're not running a model in detectron2's core library
cfg.merge_from_file(model_zoo.get_config_file("COCO-PanopticSegmentation/panoptic_fpn_R_101_3x.yaml"))
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
# Find a model from detectron2's model zoo. You can use the https://dl.fbaipublicfiles... url as well
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-PanopticSegmentation/panoptic_fpn_R_101_3x.yaml")
predictor = DefaultPredictor(cfg)

# Panoptic Segmentation Visualizer
# We can use `Visualizer` to draw the predictions on the image.
predictions, segmentInfo = predictor(im)["panoptic_seg"]
v = Visualizer(im[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1)
# Uncomment to filter out specific segments
# out = v.draw_panoptic_seg_predictions(predictions.to("cpu"), list(filter(lambda x: x['category_id'] == 17, segmentInfo)), area_threshold=.1)
out = v.draw_panoptic_seg_predictions(predictions.to("cpu"), segmentInfo, area_threshold=.1)
cv2_imshow(out.get_image()[:, :, ::-1])

"""### Process Video Panoptic Segmentation

Ref: https://www.geeksforgeeks.org/python-opencv-capture-video-from-camera/

[Sample video](https://www.istockphoto.com/video/forward-driving-perspective-on-pennsylvania-avenue-in-dc-gm911535028-250974474)
"""

# Load video sample
!wget https://media.istockphoto.com/videos/forward-driving-perspective-on-pennsylvania-avenue-in-dc-video-id911535028 -q -O dc-street.mp4

# define a video capture object and source video
vid = cv2.VideoCapture('/content/dc-street.mp4')

# define video writer object
videoWidth = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
videoHeight = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*'MP4V')
# Set the frame rate to match your source video (change the 24.0 value if needed)
output = cv2.VideoWriter('dc-street-out.mp4', fourcc, 24.0, (videoWidth,videoHeight))
  
# Capture the video frame by frame
ret, frame = vid.read()

while(ret):
    # Panoptic Segmentation Visualizer
    # We can use `Visualizer` to draw the predictions on the image.
    predictions, segmentInfo = predictor(frame)["panoptic_seg"]
    # show full segmentation image
    v = Visualizer(frame[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1)
    # OR Optional to show only segmentation image
    # frame = np.zeros((360, 640,3), np.uint8)
    #v = Visualizer(frame[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1)
    
    # Uncomment to filter out specific segments (road only)
    # out = v.draw_panoptic_seg_predictions(predictions.to("cpu"), list(filter(lambda x: x['category_id'] == 21, segmentInfo)), area_threshold=.1)
    
    out = v.draw_panoptic_seg_predictions(predictions.to("cpu"), segmentInfo, area_threshold=.1)
    output.write(out.get_image()[:, :, ::-1])
    # display in notebook
    # cv2_imshow(out.get_image()[:, :, ::-1])
      
    # Capture the video frame by frame
    ret, frame = vid.read()
  
# # After the loop release the cap object
vid.release()
output.release()
# # Destroy all the windows
cv2.destroyAllWindows()