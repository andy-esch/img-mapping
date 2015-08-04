# img-mapping

## Andy Eschbacher, Aug, 2015

This program does this:

1. extracts latitude and longitude from the EXIF data of images
1. pushes images to an AWS S3 bucket
1. generates a csv file with the extracted geo data and url of images
1. pushes csv to CartoDB

To get started:

* install aws command line tools: [https://aws.amazon.com/cli/](https://aws.amazon.com/cli/)
* install these python modules (`pip install module_name` usually works)
  + glob
  + PIL
  + boto
* install development version of [cartodb's python module](https://github.com/CartoDB/cartodb-python):

```pip install -e git+git://github.com/CartoDB/cartodb-python.git#egg=cartodb```

* rename `config.sample.json` to `config.sample.json` and fill in your CartoDB username and API key. Be sure not to push this file to GitHub!

Very helpful code on EXIF data extraction adapted from [https://github.com/96chan/extract_EXIF](https://github.com/96chan/extract_EXIF).
