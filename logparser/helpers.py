# System
import re
import sys
import datetime
from collections import Counter
from dateutil import parser
from dateutil.rrule import rrule, DAILY
# 3rd party
import boto3
import smart_open

# AWS globals setup
bucket_name =  'techtest-alb-logs'
bucket_prefix = 'webservices/AWSLogs/158469572311/elasticloadbalancing/us-west-2/'

s3 = boto3.resource('s3')
client = boto3.client('s3')
bucket = s3.Bucket(name=bucket_name)

def normalize_date(date):
    """Helper function to get a normalized date to build an s3 URL."""

    date_obj = parser.parse(date)
    normal_date = datetime.date.strftime(date_obj, "%Y/%m/%d")
    return normal_date


def s3_directory_exists(bucket, prefix):
    """Helper function to determine if a directory exists."""

    results = client.list_objects(Bucket=bucket, Prefix=prefix)
    return 'Contents' in results

def filter_s3_logs(from_date, to_date):
    """Helper function to dump out all logs that fall within a date range."""

    from_date_obj = parser.parse(from_date)
    to_date_obj = parser.parse(to_date)

    # TODO Handle out of order dates

    s3_log_urls = []
    # Loop over dates
    for single_date in rrule(DAILY, dtstart=from_date_obj, until=to_date_obj):
        # Make a URL and get logs for dates in range
        formatted_date = single_date.strftime("%Y/%m/%d")
        s3_dir = bucket_prefix + formatted_date + '/'
        for obj in bucket.objects.filter(Prefix=s3_dir):
            # Put the full url into the list
            s3_log_urls.append(bucket_name + '/' + obj.key)

    return s3_log_urls


def analyze_codes(*log_urls):
    """ Helper function to Read through log entries and calculate stats."""
    status_codes = []
    for url in log_urls:
        # Decode and read lines from the log files
        for line in smart_open.smart_open('s3://' + url):
            line = line.decode('utf-8')
            print(line)

            # Parse HTTPS codes - the position should always be the same
            line_parts = line.split(' ')
            status_codes.append(line_parts[8])

    return status_codes


