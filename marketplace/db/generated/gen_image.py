'''
Owen Jennings
11/7/2023
Inspiration from: https://awik.io/generate-random-images-unsplash-without-using-api/

Sample Usage:
python3 get_image.py 1920 1080 product,apple 100

Parameters: width, height, image description (format description1,desciption2,...), number_images

'''

import sys
import urllib.request 


BASE_URL = "https://source.unsplash.com/random/"

def gen_images(url, num_images):
    """
    Generate images from unsplash.com random image url

    :param url: unsplash.com formatted random image url
    """ 

    print("Download Started")
    for i in range(1, num_images + 1):
        if (i % 10 == 0):
            print("Downloading Images: " + str(i) + "/" + str(num_images))
        urllib.request.urlretrieve(url, str(i) + ".jpg")

if __name__ == "__main__":
    args = sys.argv[1:]
    width = args[0]
    height = args[1]
    description = args[2]
    num_images = int(args[3])

    url = BASE_URL + width + "x" + height + "/?" + description
    url = BASE_URL + "/?" + description

    gen_images(url, num_images)