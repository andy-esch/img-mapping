# img-mapping

## Andy Eschbacher, Aug, 2015

This program does this:

1. extracts latitude and longitude from the EXIF data of images
1. pushes images to an AWS S3 bucket
1. generates a csv file with the extracted geo data and url of images
1. pushes csv to CartoDB

To get started:

* install aws command line tools: [https://aws.amazon.com/cli/](https://aws.amazon.com/cli/)
* install modules listed below
* install development version of [cartodb's python module](https://github.com/CartoDB/cartodb-python):

```pip install -e git+git://github.com/CartoDB/cartodb-python.git#egg=cartodb```

Very helpful code on EXIF data extraction adapted from [https://github.com/96chan/extract_EXIF](https://github.com/96chan/extract_EXIF).
