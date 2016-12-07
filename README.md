# splitaudio
A simple Python script for splitting any audio file into tracks from a CSV file using FFMPEG and FFPROBE

## Description
For the splitter to work, the CSV file columns required are:

* Track Name
* Time position

And seperated by a comma (,).

For example:

	title,position
	01. Song 1,0:00
	"02. Song 2, plus more",4:28
	03. Song 3,7:56
	...


The script will then work out the full duration of the file using **ffprobe** and then as it parses the CSV file 
will work out the duration of each track. The splitting is then done using **ffmpeg**. 

## Usage

	python3 splitaudio.py -i <inputfile> -c <csvfile> [-s]

### Arguments
    -i  --input     Audio file to be split into it's various tracks
    -c  --csv       CSV delimited text file containing the track names and time position in the source audio file
    -s  --simulate  Optional. Simulates the process without actually running anything.

## Dependencies
### Python
* Python 3 (only because this is what I have tested against)

### External
* ffmpeg
* ffprobe


