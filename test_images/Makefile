SOURCE_IMAGES=$(wildcard *.png)
IMAGE_JSON=$(patsubst %.png,%.json,$(SOURCE_IMAGES))

all: $(IMAGE_JSON) gallery publish

%.json: %.png
	../label-images.py $<

gallery:
	../generate-gallery.py

publish:
	aws s3 sync --acl public-read --delete . s3://sandbox.wdl.org/cloud-vision-test/ --exclude="*.png"