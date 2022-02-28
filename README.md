# splitaudio
A simple Python script for splitting any audio file into tracks from a CSV file.

The script will then work out the full duration of the file and then as it parses the CSV file 
will work out the duration of each track based upon each tracks time position. 

### CSV requirements
For the splitter to work, the CSV file columns can be any delimiter character.
The program will determine for you what delimiter is used (e.g. , | ~).

> If there are for example comma's (,) contained within a song title, try using
a pipe (|) as the separator.

#### Mandatory fields

|Field|Description|
|---|---|
|track|Track Name to apply upon the split|
|position^|Time position within audio file|

^ The `position` field value format can be either: `HH:MM:SS`, `HH:MM:SS.fff`, `MM:SS` or `MM:SS.fff`

#### Optional fields

|Field|Description|
|---|---|
|artist|Name of the artist to apply to the track|
|album|Name of the album to apply to the track|
|year|Year of release to apply to the track|

With these optional, they can also be provided as command line arguments.

> Note: The optional fields in the CSV will override 
> the command line arguments if they are not empty.

### Examples

#### Example 1
Here only the mandatory fields are shown as well as
one track (line 2) where the title contains a comma,
hence the double quoting.
```text
title,position
Song 1,0:00
"Song 2, plus more",4:28
Song 3,7:56
```
#### Example 2
This example extends on the above example by including 
the optional fields.
```text
title,position,artist,album,year
Song 1,0:00,ABC,Debut,2000
"Song 2, plus more",4:28,ABC,Debut,2000
Song 3,7:56,ABC,Debut,2000
```

## Usage

```bash
    splitaudio.py [-h] [-i INPUT] [-c CSV] [-o OUTPUT] [-r ARTIST] [-a ALBUM] [-y YEAR] [-d]
```

### Arguments
```bash
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Audio file to be split into tracks
  -c CSV, --csv CSV     CSV delimited text file containing the track names and time position in the source audio file
  -o OUTPUT, --output OUTPUT
                        Output path where split tracks are to be saved
  -r ARTIST, --artist ARTIST
                        Music artist
  -a ALBUM, --album ALBUM
                        Album title
  -y YEAR, --year YEAR  Album year of release
  -d, --dryrun          Perform a dry run without processing
```

## Dependencies
### Python
* Python 3 (only because this is what I have tested against)
* [pydub](https://pydub.com/)

### Other
As per PyDub's documentation -

> You can open and save _WAV_ files with pure python.
> For opening and saving non-wav files – like _mp3_ –
> you'll need **ffmpeg** or **libav**.

