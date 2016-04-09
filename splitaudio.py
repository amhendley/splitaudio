#!/usr/bin/python

import sys
import getopt
import subprocess
from datetime import datetime
import formatters


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
    print("==========output==========")
    print(out)
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


def split_audio(track_title, start_time, end_time, audio_file):
    print('Title:', track_title)
    print('Start:', start_time)
    print('End:', end_time)

    duration = (end_time - start_time)
    print('Duration:', duration)

    start_time_string = "{0}:{1}:{2}".format(start_time.hour, start_time.minute, start_time.second)
    duration_string = formatters.strfdelta(duration, '%H:%M:%S')

    file_parts = audio_file.split(sep='.')
    file_ext = file_parts[len(file_parts)-1]
    output_file = "{0}.{1}".format(track_title, file_ext)

    cmd = ['ffmpeg', '-ss', start_time_string, '-i', audio_file, '-c', 'copy', '-t', duration_string, output_file]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = p.communicate()
    # print("==========output==========")
    # print(out.decode())
    if err:
        print("========= error ========")
        print(err.decode())
        exit


def main(argv):
    inputFile = ''
    csvFile = ''

    try:
        opts, args = getopt.getopt(argv, "hi:c:", ["input=", "csv="])
    except getopt.GetoptError:
        print('usage: splitaudio.py -i <inputfile> -c <csvfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('splitaudio.py -i <inputfile> -c <csvfile>')
            sys.exit()
        elif opt in ("-i", "--input"):
            inputFile = arg
        elif opt in ("-c", "--csv"):
            csvFile = arg

    print('Input file is "', inputFile)
    print('CSV file is "', csvFile)

    file_duration = get_audiofile_duration(inputFile)
    print('File duration:', file_duration)

    start_time = ''

    with open(csvFile) as f:
        data = f.readlines()

    for line in data:
        parts = line.split(",")
        parts[1] = parts[1].rstrip('\n')
        sep_count = parts[1].count(':')

        if sep_count == 1:
            dt = datetime.strptime(parts[1], '%M:%S')
        elif sep_count == 2:
            dt = datetime.strptime(parts[1], '%H:%M:%S')

        if start_time != '':
            end_time = dt
            split_audio(track_title, start_time, end_time, inputFile)

        track_title = parts[0]

        start_time = dt

    if start_time != '':
        end_time = file_duration

        split_audio(track_title, start_time, end_time, inputFile)


if __name__ == "__main__":
    main(sys.argv[1:])
