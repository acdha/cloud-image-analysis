SOURCE_IMAGES=$(wildcard *.png)
IMAGE_JSON=$(patsubst %.png,%.json,$(SOURCE_IMAGES))

all: $(IMAGE_JSON) gallery

%.json: %.png
	../label-images.py $<

gallery:
	../generate-gallery.py