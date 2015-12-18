#!/usr/bin/env python3

from __future__ import absolute_import, division, print_function, unicode_literals

from html import escape
import glob
import json

output_file = open('index.html', 'w')

print("""<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>CV API Result Gallery</title>
        <style>
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
        <h1>CloudVision API Results</h1>
        <table id="results">
            <tbody>
""", file=output_file)

for json_filename in sorted(glob.glob('*.json'), key=lambda i: int(i.split(".", 1)[0])):
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
            boundingPoly = escape(json.dumps(i['boundingPoly']), quote=True)
            text.append('<li lang="%s" data-bounding-poly="%s">%s</li>' % (locale, boundingPoly, description))

        for i in response.get('landmarkAnnotations', []):
            score = i['score']
            description = escape(i['description'])
            landmarks.append('<li title="%0.02f">%s</li>' % (score, description))

        for i in response.get('labelAnnotations', []):
            score = i['score']
            description = escape(i['description'])
            labels.append('<li title="%0.02f">%s</li>' % (score, description))

    print('''
        <tr>
            <td class="image"><a class="image-wrapper" href="http://dl.wdl.org/{0}"><img src="http://dl.wdl.org/{0}"></a></td>
            <td class="landmarks"><ul>{1}</ul></td>
            <td class="labels"><ul>{2}</ul></td>
            <td class="text"><ul>{3}</ul></td>
        </tr>
'''.format(image_filename, "\n".join(landmarks), "\n".join(labels), "\n".join(text)), file=output_file)

print("""
            </tbody>
        </table>

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
