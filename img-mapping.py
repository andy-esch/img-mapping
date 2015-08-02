#
# img-mapping
# Andy Eschbacher
# Aug, 2015
#
# This program does this:
#   * extracts lat lon from exif data of images
#   * pushes image to an aws s3 bucket
#   * generates a csv file with geo data and url of images
#   * pushes csv to cartodb
#
# To get started:
#   * install aws command line tools: https://aws.amazon.com/cli/
#   * install modules listed below
#   * install development version of cartodb's python module: 
#       pip install -e git+git://github.com/CartoDB/cartodb-python.git#egg=cartodb
#
# EXIF code adapted from https://github.com/96chan/extract_EXIF
# 
#
#

# generic
import glob
import sys

# image processing
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# aws modules
import boto
import boto.s3
from boto.s3.key import Key

# cartodb
from cartodb import CartoDBAPIKey, CartoDBException, FileImport
import json

def loadConfig():
    with open('./config.json') as data_file:
        data = json.load(data_file)
        return data

def get_exif_data(fn):
    """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
    exif_data = {}
    i = Image.open(fn)
    info = i._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]
                    exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value
    return exif_data
 
def _get_if_exist(data, key):
    if key in data:
        return data[key]
        
    return None
    
def _convert_to_decimal(value):
    """Helper function to convert the GPS coordinates stored in the EXIF to degrees in float format"""
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)
 
    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)
 
    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)
 
    return d + (m / 60.0) + (s / 3600.0)
 
def get_lat_lon(exif_data):
    """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
    lat = None
    lon = None

    if "GPSInfo" in exif_data:        
        gps_info = exif_data["GPSInfo"]
 
        gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
        gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
        gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
        gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')
 
        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = _convert_to_decimal(gps_latitude)
            if gps_latitude_ref != "N":                     
                lat = 0.0 - lat
 
            lon = _convert_to_decimal(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0.0 - lon
    return lat, lon

def put_files(f):
    k = bucket.new_key(f[-9:])
    print "--> pushing '%s' to s3 bucket '%s'" % \
         (f, bucket_name)
    k.set_contents_from_filename(f)
    k.set_metadata('Content-Type', 'image/jpeg')
    k.set_acl('public-read')
    url = k.generate_url(expires_in=0, query_auth=False,force_http=True)
    return url

def write_csv(file_name, header, data):
    import csv
    with open(file_name, 'wb') as csvfile:
        csvout = csv.writer(csvfile)
        csvout.writerow(header)
        for row in data:
            csvout.writerow(row)

    return True

def push_to_cartodb(f):
    """
        send dataset f to cartodb, return success of import
    """
    print "attempting to import into cartodb"
    config = loadConfig()
    cl = CartoDBAPIKey(config["API_KEY"],config["user"])
    fi = FileImport(f,cl,table_name='python_table_test')
    fi.run()

    return fi.success

if __name__ == "__main__":

    project_name = ""

    if len(sys.argv) > 1:
        project_name = sys.argv[1]
    else:
        project_name = 'summer_project'

    # setup aws s3 bucket
    bucket_name = project_name
    conn = boto.connect_s3()
    bucket = conn.create_bucket(bucket_name,location=boto.s3.connection.Location.DEFAULT,policy='public-read')
    print "--> S3 bucket created with name '%s'" % bucket_name
    
    # for image metadata
    data = []

    # get paths of all images
    images  = glob.glob('img/*.jpg')
    
    # for each image, extract exif, get url in s3 bucket, build data table
    for i in images: 
        # grab exif data
        exif_data = get_exif_data(i)
        date = exif_data['DateTimeOriginal'].split()[0].replace(':','-')
        time = exif_data['DateTimeOriginal'].split()[1]
        [lat, lon] = get_lat_lon(exif_data)

        # send image to s3 bucket, get back url
        url = put_files(i)
        # url = ''

        # compile data
        if lat != None and lon != None:
            data +=[[i, url, date, time, lat, lon]]
        else:
            data +=[[i, url, date, time, None, None]]

    # csv header
    header = ['filename', 'url', 'date_taken', 'time_taken', 'lat', 'lon']
    
    output_file_name = ("%s.csv" % project_name)

    # write data on csv file
    out_result = write_csv(output_file_name,header,data)

    if out_result:
        print "--> data saved in %s" % output_file_name
    else:
        print "--> error saving data in %s" % output_file_name

    # send data to cartodb
    import_status = push_to_cartodb(output_file_name)
    # import_status = True

    if import_status:
        print "--> '%s' successfully imported into cartodb" % output_file_name
    else:
        print "--> import of '%s' into cartodb failed" % output_file_name
