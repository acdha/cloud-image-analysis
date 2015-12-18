#!/usr/bin/env python3
"""Quick and shamefully dirty HTML gallery generator to review CV API results"""

from html import escape
import glob
from itertools import zip_longest
import json
import random
import re

PAGE_SIZE = 32

def grouper(iterable, n):
    args = [iter(iterable)] * n
    return zip_longest(*args)

filenames = glob.glob('*.json')
filenames.sort(key=lambda i: tuple(map(int, re.findall('\d+', i))))

max_page = (1 + (len(filenames) // PAGE_SIZE))

for page_number, page_files in enumerate(grouper(filenames, PAGE_SIZE), start=1):
    print('Generating page', page_number)

    output_file = open('index-%d.html' % page_number, 'w')

    print("""<!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>CV API Result Gallery</title>
            <style>
                td, th {
                    vertical-align: top;
                }

                ul {
                    list-style: none
                }

                nav {
                    display: flex;
                    flex-direction: row;
                    font-size: xx-large;
                }

                nav > a {
                    flex: 1;
                    text-decoration: none
                }

                nav > a:last-child {
                    text-align: right;
                }

                .image-wrapper {
                    position: relative;
                    display: inline-block;
                }

                .image-wrapper img {
                    max-height: 50vh;
                    max-width: 50vw;
                }

                .image-wrapper .overlay {
                    position: absolute;
                    background-color: yellow;
                    opacity: 0.3;
                    border-radius: 50%;
                }
            </style>
        </head>
        <body>
    """, file=output_file)

    print('<nav>', file=output_file)
    if page_number > 1:
        print('<a href="index-{0}.html">⬅️ {0}</a>'.format(page_number - 1), file=output_file)

    if page_number < max_page:
        print('<a href="index-{0}.html">{0} ➡️</a>'.format(page_number + 1), file=output_file)

    print('</nav>', file=output_file)

    print("""
            <table id="results">
                <thead>
                    <tr>
                        <th>Item</th>
                        <th>Landmarks</th>
                        <th>Labels</th>
                        <th>Text</th>
                    </tr>
                </thead>
                <tbody>
    """, file=output_file)

    for json_filename in filter(None, page_files):
        image_filename = json_filename.replace('.json', '.png')

        with open(json_filename, 'r') as j:
            data = json.load(j)

        text = []
        landmarks = []
        labels = []

        for response in data['responses']:
            for i in response.get('textAnnotations', []):
                locale = i['locale']
                description = escape(i['description'])

                vertices = i['boundingPoly']['vertices']
                assert len(vertices) == 4

                boundingPoly = escape(json.dumps(i['boundingPoly']), quote=True)
                text.append('<li lang="%s" data-bounding-poly="%s">%s</li>' % (locale, boundingPoly, description))

            for i in response.get('landmarkAnnotations', []):
                mid = i.get('mid', '')
                score = i['score']
                description = escape(i['description'])

                if mid:
                    landmarks.append('<li><a href="https://www.freebase.com%s" title="%0.02f%%">%s</a></li>' % (mid, score, description))
                else:
                    landmarks.append('<li title="%0.02f%%">%s</li>' % (score, description))

            for i in response.get('labelAnnotations', []):
                mid = i.get('mid', '')
                score = i['score']
                description = escape(i['description'])

                if mid:
                    labels.append('<li><a href="https://www.freebase.com%s" title="%0.02f%%">%s</a></li>' % (mid, score, description))
                else:
                    labels.append('<li title="%0.02f%%">%s</li>' % (score, description))

        print('''
            <tr id="{0}">
                <td class="image"><a class="image-wrapper" href="http://dl.wdl.org/{0}"><img src="http://dl.wdl.org/{0}"></a></td>
                <td class="landmarks"><ul>{1}</ul></td>
                <td class="labels"><ul>{2}</ul></td>
                <td class="text"><ul>{3}</ul></td>
            </tr>
    '''.format(image_filename, "\n".join(landmarks), "\n".join(labels), "\n".join(text)), file=output_file)

    print("""
                </tbody>
            </table>
    """, file=output_file)

    print('<nav>', file=output_file)
    if page_number > 1:
        print('<a href="index-{0}.html">⬅️ {0}</a>'.format(page_number - 1), file=output_file)

    if page_number < max_page:
        print('<a href="index-{0}.html">{0} ➡️</a>'.format(page_number + 1), file=output_file)

    print('</nav>', file=output_file)

    print("""
            <script>
                "use strict";

                function percentageToCSS(i) {
                    // Convert a float between 0 to 1 into a CSS percentage
                    return (100 * i).toFixed(0) + "%";
                }

                function highlightTextBox(evt) {
                    Array.prototype.forEach.call(document.querySelectorAll(".overlay"),
                                                 function (i) { i.parentNode.removeChild(i); });

                    var boundingPoly = evt.target.dataset.boundingPoly;

                    if (!boundingPoly) {
                        console.error('Unable to load bounding poly from', evt.target);
                    }

                    boundingPoly = JSON.parse(boundingPoly);

                    var d = document.createElement('div');
                    d.className = "overlay";

                    var xValues = boundingPoly.vertices.map(function (j) { return j.x; }),
                        yValues = boundingPoly.vertices.map(function (j) { return j.y; });

                    var lowX = Math.min.apply(null, xValues),
                        lowY = Math.min.apply(null, yValues),
                        highX = Math.max.apply(null, xValues),
                        highY = Math.max.apply(null, yValues);

                    var imageContainer = evt.target.parentNode.parentNode.parentNode.querySelector('.image-wrapper');

                    var img = imageContainer.querySelector('img');

                    d.style.top = percentageToCSS(lowY / img.naturalHeight);
                    d.style.left = percentageToCSS(lowX / img.naturalWidth);
                    d.style.height = percentageToCSS((highY - lowY) / img.naturalHeight);
                    d.style.width = percentageToCSS((highX - lowX) / img.naturalWidth);

                    imageContainer.appendChild(d);
                }

                var textResults = document.querySelectorAll(".text li");
                for (var i = 0; i < textResults.length; i++) {
                    textResults[i].addEventListener('mouseenter', highlightTextBox);
                }
            </script>
        </body>
    </html>
    """, file=output_file)

    output_file.close()

    with open('index.html', 'w') as index_f:
        print('''<!DOCTYPE html><html><head><title>Results Index</title></head><body><ol>''', file=index_f)

        for i in range(0, max_page):
            print('<li><a href="index-{0}.html">Page {0}</a></li>'.format(i + 1), file=index_f)

        print('''</ol></body></html>''', file=index_f)