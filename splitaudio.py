#!/usr/bin/env python3

import sys
import pathlib
import argparse
from datetime import datetime, timedelta
import csv
from pydub import AudioSegment


def split_audio(input_data: dict = [],
                audio_file: AudioSegment = None,
                output_path: str = None,
                dry_run: bool = False):
    track_title = input_data['title']
    track_pos = input_data['track']
    track_album = input_data['album'] if 'album' in input_data else None
    track_year = input_data['year'] if 'year' in input_data else None
    track_start_time = input_data['start_time']
    track_end_time = input_data['end_time']
    track_extension = input_data['extension']

    print('Title:', track_title)
    print('  Start:', datetime.strftime(track_start_time, '%H:%M:%S'))
    print('  End:', datetime.strftime(track_end_time, '%H:%M:%S'))

    duration = (track_end_time - track_start_time)
    print('  Duration:', str(duration))

    output_file = "{0}/{1:02d}. {2}.{3}".format(output_path,
                                           track_pos,
                                           track_title,
                                           track_extension)
    print("  Output: {0}".format(output_file))

    if dry_run:
        print("Simulation: Extracting audio part from time position '{0}' "
              "for the duration of '{1}' into file '{2}.{3}'"
              .format(datetime.strftime(track_start_time, '%H:%M:%S'),
                      str(duration),
                      track_title,
                      track_extension))
    else:
        start_delta = timedelta(hours=track_start_time.hour,
                                minutes=track_start_time.minute,
                                seconds=track_start_time.second,
                                microseconds=track_start_time.microsecond)
        end_delta = timedelta(hours=track_end_time.hour,
                              minutes=track_end_time.minute,
                              seconds=track_end_time.second,
                              microseconds=track_end_time.microsecond)

        start_ms = (start_delta.seconds * 1000)
        end_ms = (end_delta.seconds * 1000)

        if start_ms > 0:
            audio_track = audio_file[int(start_ms):]
        else:
            audio_track = audio_file

        audio_track_final = audio_track[:(end_ms-start_ms)]

        track_tags = {
            'title': track_title,
            'track': track_pos,
        }
        if track_album:
            track_tags['album'] = track_album
        if track_year:
            track_tags['year'] = track_year

        audio_track_final.export(out_f=output_file,
                                 format=track_extension,
                                 tags=track_tags)


def main(argv):
    input_file = ''
    csv_file = ''
    output_path = None
    album_name = None
    album_year = None
    dry_run = False
    time_formats = {1: {True: '%M:%S.%f', False: '%M:%S'},
                    2: {True: '%H:%M:%S.%f', False: '%H:%M:%S'}}

    try:
        parser = argparse.ArgumentParser(prog='splitaudio')
        parser.add_argument('-i', '--input',
                            type=pathlib.Path,
                            help='Audio file INPUT',
                            metavar='INPUT')
        parser.add_argument('-c', '--csv',
                            type=pathlib.Path,
                            help='Delimited text file of track splits',
                            metavar='CSV')
        parser.add_argument('-o', '--output',
                            type=pathlib.Path,
                            help='Output path where split tracks are to be'
                                 ' saved',
                            metavar='OUTPUT')
        parser.add_argument('-a', '--album',
                            help='Album title',
                            metavar='ALBUM')
        parser.add_argument('-y', '--year', type=int,
                            help='Album year of release',
                            metavar='YEAR')
        parser.add_argument('-d', '--dryrun',
                            action='store_true',
                            help='Perform a dry run without processing')

        args = parser.parse_args(argv)
    except Exception:
        parser.usage()
        sys.exit(2)

    input_file = args.input
    csv_file = args.csv
    album_name = args.album
    album_year = args.year
    output_path = args.output
    dry_run = args.dryrun


    if str(input_file).startswith('~'):
        input_file = pathlib.Path('{0}{1}'.format(input_file.home(),
                                                  str(input_file)[1:]))

    if str(csv_file).startswith('~'):
        csv_file = pathlib.Path('{0}{1}'.format(csv_file.home(),
                                                str(csv_file)[1:]))

    if not output_path:
        output_path = input_file.parent
    else:
        if str(output_path).startswith('~'):
            output_path = pathlib.Path('{0}{1}'.format(output_path.home(),
                                                       str(output_path)[1:]))

    print()
    print('- Input:   ', input_file)
    print('- CSV:     ', csv_file)
    print('- Output:  ', output_path)

    audio_type = input_file.suffix[1:].lower()
    audio_file = AudioSegment.from_file(str(input_file), audio_type)

    seconds = audio_file.duration_seconds
    file_duration = timedelta(seconds=seconds)
    print('- Duration:', file_duration)
    print()

    start_time = ''

    with open(csv_file) as file:
        reader = csv.DictReader(file)
        first_row = True
        track_count = 0

        for row in reader:
            track_position = row['position']

            sep_count = track_position.count(':')
            has_milliseconds = (track_position.count('.') > 0)
            time_format = time_formats[sep_count][has_milliseconds]
            new_start_time = datetime.strptime(track_position, time_format)

            if not first_row:
                track_count += 1
                if dry_run:
                    print("Simulation: Processing row ({0}) "
                          "with track position ({1})".format(track_title,
                                                             track_position))

                end_time = new_start_time
                track_data = {
                    'title': track_title,
                    'extension': audio_type,
                    'track': track_count,
                    'start_time': start_time,
                    'end_time': end_time,
                    'album': row['album'] if 'album' in row else album_name,
                    'year': row['year'] if 'year' in row else album_year
                }
                split_audio(track_data, audio_file, output_path, dry_run)

            track_title = row['title']
            start_time = new_start_time
            first_row = False

    if not first_row:
        if dry_run:
            print("Simulation: Processing row ({0}) "
                  "with track position ({1})".format(track_title,
                                                     track_position))
        end_time = datetime.strptime(str(file_duration), '%H:%M:%S.%f')

        track_data = {
            'title': track_title,
            'extension': audio_type,
            'track': (track_count+1),
            'start_time': start_time,
            'end_time': end_time,
            'album': row['album'] if 'album' in row else album_name,
            'year': row['year'] if 'year' in row else album_year
        }

        split_audio(track_data, audio_file, output_path, dry_run)


if __name__ == "__main__":
    main(sys.argv[1:])
