'''
Utilities for downloading ImageNet images.
'''

from cropping_utils import crop_image_randomly

from random import shuffle, randint
from os.path import dirname, abspath, join, exists, basename
from glob import glob
from os import system


ROOT = dirname(abspath(__file__))

def bounding_boxes_are_available_for_this_noun(wnid):
  '''
  It turns out the sets of bounding boxes are too incomplete for use,
  so I wrote a Pygame to manually draw the bounding boxes.

  Bounding boxes are only available for the 300 synsets (out of the current
  21841 total synsets on ImageNet)

  Here is the list of synsets with bounding boxes.
  http://www.image-net.org/api/text/imagenet.bbox.obtain_synset_list
  '''
  bbox_synset_list_filename = join(ROOT, 'data/imagenet_bbox_synset_list')
  system('wget http://www.image-net.org/api/text/'
         'imagenet.bbox.obtain_synset_list '
         '-O ' + bbox_synset_list_filename)
  with open(bbox_synset_list_filename) as f:
   return wnid + '\n' in list(f)

# TODO multithread this because it takes forever
def download_negative_images(wnid, count, target_dir):
  '''
  Downloads `count` random images from imagenet that have any wnid other than
  `wnid', and place them in `target_dir`.
  Each image is renamed:
    <original wnid>_<original image name>

  The negative images are cropped by a random crop_box in
  `imagenet/<wnid>/bounding_boxes.csv`, because the positive images
  are, and are therefore often more zoomed-in than the typical
  imagenet photo.
  '''
  target_count = count
  system('mkdir -p ' + target_dir)
  wnids = all_wnids()
  shuffle(wnids)
  wnids.remove(wnid)
  # images may be in the dir from a previous run. Keep 'em.
  count -= len(glob(join(target_dir, '*.[Jj][Pp][Gg]')))
  tmp = '/tmp/negative_image'

  while count > 0:
    for id in wnids:
      system('rm -rf ' + tmp)
      system('mkdir -p ' + tmp)
      download_one_random_image(id, tmp)
      one_or_zero_filenames = glob(join(tmp, '*.[Jj][Pp][Gg]'))
      if len(one_or_zero_filenames) == 0:
        continue
      name = basename(one_or_zero_filenames[0])
      if crop_image_randomly(wnid, join(tmp, name),
                            join(target_dir, id + '_' + name)):
        count -= 1
        print '>>>>>', count, '/', target_count
        if count == 0:
          break

def download_one_random_image(wnid, target_dir):
  '''
  Downloads a random image identified by the synset id, and places it in
  `target_dir`

  Given the wnid of a synset, the URLs of its images can be obtained at
  http://www.image-net.org/api/text/imagenet.synset.geturls?wnid=[wnid]

  If the image
  '''
  system('mkdir -p /tmp/image-urls')
  wnid_list_filename = join('/tmp/image-urls', wnid + '.txt')
  if not exists(wnid_list_filename):
    system('wget http://www.image-net.org/api/text/'
           'imagenet.synset.geturls?wnid=' + wnid + ' -O ' + \
           wnid_list_filename)
  image_url = get_random_url(wnid_list_filename)
  system('wget ' + image_url + ' --directory-prefix=' + target_dir)

def get_random_url(filename):
  '''
  Arguments:
    filename: identifies a file that contains a list of urls
  Returns:
    a random url in the file
  '''
  with open(filename) as f:
    lines = [line for line in list(f) if len(line) > 4] # skip empty lines
    if len(lines) == 0:
      import pdb; pdb.set_trace()
    try:
      return lines[randint(0, len(lines) - 1)][:-2] # strip trailing '\r\n'
    except IndexError as e:
      print e
      import pdb; pdb.set_trace()

def download_images(wnid):
  '''
  Downloads all images identified by the synset id, and places them in
  `target_dir`

  Returns:
    the number of images placed in `target_dir`

  Given the wnid of a synset, the URLs of its images can be obtained at
  http://www.image-net.org/api/text/imagenet.synset.geturls?wnid=[wnid]
  '''
  images_dir = join(ROOT, 'data/imagenet', FLAGS.wnid, 'images/all')
  system('mkdir -p ' + images_dir)
  tmp = '/tmp/image_urls.txt'
  system('wget http://www.image-net.org/api/text/'
         'imagenet.synset.geturls?wnid=' + FLAGS.wnid + ' -O ' + tmp)
  with open(tmp) as f:
    for line in f:
      image_url = line[:-2] # strip trailing '\r\n'
      system('wget ' + image_url + ' --directory-prefix=' + images_dir)

def download_bounding_boxes(wnid):
  '''
  You can use the following API to download the bounding boxes of a
  particular synset:
  http://www.image-net.org/api/download/imagenet.bbox.synset?wnid=[wnid]

  The number of bounding boxes per image is way too small to be useful...
  like 10% and the mapping between image and "annotation" seems unclear

  And that endpoint above doesn't actually work. I emailed
  the imagenet list about it. The endpoint that does work is:
  "You can download all the bounding boxes available packaged in one file:
  http://image-net.org/Annotation/Annotation.tar.gz"

  I await an email to see if I'll need to write a pygame for bounding
  the boxes. I've done it before, so it should be quick...

  Well hey, if I can draw bounding boxes in six seconds per image on
  average, it'll take two hours. I can handle that...
  haha unfortunately for eggs, there are often several (like 20) eggs
  per image. It takes much longer.
  '''
  pass

ALL_WNIDS = []
def all_wnids():
  '''
  Returns all wnids for which ImageNet has images

  The list of all wordnet ids (which identify the synsets) is at:
  http://www.image-net.org/api/text/imagenet.synset.obtain_synset_list
  '''
  if len(ALL_WNIDS) > 0:
    return ALL_WNIDS

  tmp = '/tmp/wnids.txt'
  system('wget http://www.image-net.org/api/text/'
         'imagenet.synset.obtain_synset_list -O ' + tmp)
  with open(tmp) as f:
    for line in f:
      if len(line) > 2: # skip the last two empty lines
        ALL_WNIDS.append(line[:-1]) # strip trailing '\n'
  return ALL_WNIDS
