SOURCE_IMAGES=$(wildcard *.png)
IMAGE_JSON=$(patsubst %.png,%.json,$(SOURCE_IMAGES))

all: $(IMAGE_JSON) gallery publish

%.json: %.png
	../label-images.py $<

gallery:
	../generate-gallery.py

publish:
	aws s3 cp --acl public-read index.html s3://sandbox.wdl.org/cloud-vision-test/