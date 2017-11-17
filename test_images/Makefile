SOURCE_PNG=$(wildcard *.png)
SOURCE_JPG=$(wildcard *.jpg)
IMAGE_JSON=$(patsubst %.png,%.json,$(SOURCE_IMAGES)) $(patsubst %.jpg,%.json,$(SOURCE_JPG))

all: $(IMAGE_JSON) gallery publish

%.json: %.png
	../label-images.py $<

%.json: %.jpg
	../label-images.py $<

gallery:
	../generate-gallery.py

publish:
	aws s3 sync --acl public-read --delete . s3://sandbox.wdl.org/cloud-vision-test/ --exclude="*.png" --exclude="*.jpg"