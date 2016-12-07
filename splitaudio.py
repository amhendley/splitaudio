#!/usr/bin/python

import sys
import getopt
import subprocess
from datetime import datetime
from datetime import  timedelta
import formatters
import csv
import time


def open_csv(filename):
    with open(filename) as csvFile:
        reader = csv.DictReader(csvFile)

        # Read the column names from the first line of the file
        fields = reader.next()

        for row in reader:
            # Zip together the field names and values
            items = zip(fields, row)
            item = {}
            # Add the value to our dictionary
            for (name, value) in items:
                item[name] = value.strip()

    return items


def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    d["H"], rem = divmod(tdelta.seconds, 3600)
    d["M"], d["S"] = divmod(rem, 60)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)


def get_audiofile_duration(filename):
    cmd = ['ffprobe', '-show_format', '-pretty', '-loglevel', 'quiet', filename]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = p.communicate()
    # print("==========output==========")
    # print(out)
    if err:
        print("========= error ========")
        print(err)

    lines = out.decode().splitlines()
    for line in lines:
        parts = line.split('=')
        if parts[0] == 'duration':
            time_length = parts[1]

    if time_length.count('.') == 1:
        return datetime.strptime(time_length, '%H:%M:%S.%f')
    else:
        return datetime.strptime(time_length, '%H:%M:%S')


def split_audio(track_title, start_time, end_time, audio_file, simulate):
    print('Title:', track_title)
    print('Start:', datetime.strftime(start_time, '%H:%M:%S'))
    print('End:', datetime.strftime(end_time, '%H:%M:%S'))

    duration = (end_time - start_time)
    print('Duration:', str(duration))

    # start_time_string = "{0}:{1}:{2}".format(start_time.hour, start_time.minute, start_time.second)
    start_time_string = datetime.strftime(start_time, '%H:%M:%S')
    duration_string = str(duration)

    # days, seconds = duration.days, duration.seconds
    # hours = days * 24 + seconds // 3600
    # minutes = (seconds % 3600) // 60
    # seconds = seconds % 60

    file_parts = audio_file.split(sep='.')
    file_ext = file_parts[len(file_parts)-1]
    output_file = "{0}.{1}".format(track_title, file_ext)

    print("Output: {0}".format(output_file))

    if simulate:
        print("Simulation: Extracting audio part from time position '{0}' for the duration of '{1}' into file '{2}.{3}'"
              .format(start_time_string, duration_string, track_title, file_ext))
    else:
        cmd = ['ffmpeg',
               '-y',
               '-v', 'warning',
               '-ss', start_time_string,
               '-i', audio_file,
               '-c', 'copy',
               '-t', duration_string,
               output_file]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        out, err = p.communicate()
        # print("==========output==========")
        # print(out.decode())
        if err:
            print("========= error ========")
            print(err.decode())
            exit


def main(argv):
    input_file = ''
    csv_file = ''
    simulate = False

    try:
        opts, args = getopt.getopt(argv, "hi:c:s", ["input=", "csv=", "simulate"])
    except getopt.GetoptError:
        print('usage: splitaudio.py -i <input_file> -c <csv_file> [-s]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('splitaudio.py -i <input_file> -c <csv_file> [-s]')
            sys.exit()
        elif opt in ("-i", "--input"):
            input_file = arg
        elif opt in ("-c", "--csv"):
            csv_file = arg
        elif opt in ("-s", "--simulate"):
            simulate = True

    print('Input file is "', input_file)
    print('CSV file is "', csv_file)

    file_duration = get_audiofile_duration(input_file)
    print('File duration:', file_duration)

    start_time = ''
    end_time = ''

    # with open(csv_file) as f:
    #    data = f.readlines()

    with open(csv_file) as file:
        reader = csv.DictReader(file)
        first_row = True

        for row in reader:
            track_position = row['position']

            # if len(track_title.strip()) > 0:
            # parts = row.split(",")
            # parts[1] = parts[1].rstrip('\n')
            sep_count = track_position.count(':')

            # TODO: Capture time with milliseconds
            if sep_count == 1:
                new_start_time = datetime.strptime(track_position, '%M:%S')
            elif sep_count == 2:
                new_start_time = datetime.strptime(track_position, '%H:%M:%S')

            if not first_row:
                if simulate:
                    print("Simulation: Processing row ({0}) with track position ({1})".format(track_title,
                                                                                              track_position))

                end_time = new_start_time
                split_audio(track_title, start_time, end_time, input_file, simulate)

            track_title = row['title']
            start_time = new_start_time
            first_row = False

    if not first_row:
        if simulate:
            print("Simulation: Processing row ({0}) with track position ({1})".format(track_title, track_position))
        end_time = file_duration
        split_audio(track_title, start_time, end_time, input_file, simulate)


if __name__ == "__main__":
    main(sys.argv[1:])
