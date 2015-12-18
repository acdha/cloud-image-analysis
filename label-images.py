#!/usr/bin/env python
# encoding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import base64
import urllib
import os
import sys

import requests

# Life is _way_ too short to spend debugging the undocumented Google API Client authentication process:
with open(os.path.join(os.path.dirname(__file__), 'google-api-key')) as f:
    API_KEY = f.read().strip()

ANNOTATION_URL = 'https://vision.googleapis.com/v1alpha1/images:annotate?key=%s' % urllib.quote(API_KEY)


def label_image(image_filename):
    '''Run a label request on a single image'''

    output_name = '%s.json' % os.path.splitext(image_filename)[0]

    with open(image_filename, 'rb') as f:
        image_data = f.read()

    image_content = base64.b64encode(image_data)

    payload = {
        'requests': [
            {
                'image': {
                    'content': image_content
                },
                'features': [
                    {'type': 'LABEL_DETECTION', 'maxResults': 10},
                    {'type': 'LANDMARK_DETECTION', 'maxResults': 3},
                    {'type': 'TEXT_DETECTION', 'maxResults': 10},
                ]
            }
        ]
    }

    response = requests.post(ANNOTATION_URL, json=payload)

    if response.status_code != 200:
        print(ANNOTATION_URL, response.status_code, response.reason, file=sys.stderr)
        print(response.content, file=sys.stderr)
    else:
        print('Results for %s:' % image_filename)
        print(response.json())
        with open(output_name, 'wb') as f:
            f.write(response.content)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image_files', metavar='IMAGE_FILE', nargs='+')
    args = parser.parse_args()

    for filename in args.image_files:
        label_image(filename)
