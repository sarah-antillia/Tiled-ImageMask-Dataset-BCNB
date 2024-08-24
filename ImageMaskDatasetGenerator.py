# Copyright 2024 antillia.com Toshiyuki Arai
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# 2024/08/24
# ImageMaskDatasetGenerator.py


import os
import sys
os.environ["OPENCV_IO_MAX_IMAGE_PIXELS"] = pow(2,40).__str__()
import shutil
import cv2
import numpy as np

import glob
import json
import math

import traceback

class ImageMaskDatasetGenerator:

  def __init__(self, images_dir, jsons_dir, output_dir, shrink_ratio=0.1):
     self.images_dir = images_dir
     self.jsons_dir  = jsons_dir
     self.output_dir = output_dir
     self.SHRINK_RATIO = shrink_ratio
     self.output_images_dir = output_dir + "/images"
     self.output_masks_dir  = output_dir + "/masks"
     os.makedirs(self.output_images_dir)
     os.makedirs(self.output_masks_dir)
     
  def generate(self):
    image_files = glob.glob(self.images_dir + "/*.jpg")
    image_files = sorted(image_files)

    json_files  = glob.glob(self.jsons_dir + "/*.json")
    json_files  = sorted(json_files)
    num_image_files = len(image_files)
    num_json_files  = len(json_files)

    if num_image_files != num_json_files:
      raise Exception("Unmatched image_files and json_files")
    
    index = 10000
    for i in range(num_image_files):
      index += 1
      output_filename  = str(index) + ".jpg"

      image_file = image_files[i]
      image = cv2.imread(image_file)
      h, w = image.shape[:2]
      rh = int(h* self.SHRINK_RATIO)
      rw = int(w* self.SHRINK_RATIO)
      image = cv2.resize(image, (rw, rh))
      output_image_filepath = os.path.join(self.output_images_dir, output_filename)
      cv2.imwrite(output_image_filepath, image)
      print("=== Save {}".format(output_image_filepath))

      json_file = json_files[i]

      with open(json_file, 'r') as f:
        json_data   = json.load(f)
        json_string = json.dumps(json_data, indent=4)
        data        = json.loads(json_string)
        self.parse_json(data, rw, rh, output_filename, )
        
  def parse_json(self, data, rw, rh, output_filename ):
      positive = data["positive"]
      if positive == None or type(positive) !=list:
        return

      mask    = np.zeros((rh, rw, 1))
      print("---len {}".format(len(positive)))
      for p in positive:
        vertices = p["vertices"]
        print("---- vertices {}".format(len(vertices)))
        points = []
        for xy in vertices:
          x = int( xy[0] * self.SHRINK_RATIO)
          y = int( xy[1] * self.SHRINK_RATIO)
          points += [x, y]

        # Please see https://stackoverflow.com/questions/17241830/opencv-polylines-function-in-python-throws-exception
        array = np.array(points).reshape((-1,1,2)).astype(np.int32)
        cv2.fillPoly(mask, pts=[array], color=(255, 255, 255))
   
      output_mask_filepath = os.path.join(self.output_masks_dir, output_filename)
      cv2.imwrite(output_mask_filepath, mask)
      print("=== Saved {}".format(output_mask_filepath))



if __name__ == "__main__":
  try:
    shrink_ratio = 0.1
    if len(sys.argv) == 2:
       shrink_ratio = eval(sys.argv[1])
    if shrink_ratio <0 or  shrink_ratio >0.4:
      error = "Invalid shrink_ratio " + str(shrink_ratio)
      raise Exception(error)
    print("---shrink_ratio {}".format(shrink_ratio))
    input("OK: ENTER, ABORT: CTRL/C")        
    images_dir = "./WSIs/"
    jsons_dir  = "./WSIs/"

    output_dir = "./BCNB-master"
    if os.path.exists(output_dir):
      shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    
    generator = ImageMaskDatasetGenerator(images_dir,  
                                          jsons_dir, 
                                          output_dir,
                                          shrink_ratio = shrink_ratio)

    generator.generate()
    

  except:
    traceback.print_exc()
