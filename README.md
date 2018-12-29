# score2tracker
If you are like me - a composer interested in creating music for retro games but you find it hard to work with trackers - this project is for you.
S2T is simple Python3 script that converts MusicXML to 4-channels MOD file.
It is a console aplication so you can specify all the options in command line or you will be prompted to do so after runing the script. After converting your score to mod all you need to do is to open .mod file in tracker and assign samples (and set proper fine tuning for each sample). In many cases you may also need to adjust song tempo.

![demo](https://raw.githubusercontent.com/przem360/score2tracker/master/demo.gif)



### Keep in mind!

  - Lenght of song in MOD format is limited. Longer scores will be converted to the point that can fit in MOD format.
  - In tracker you can use many instruments on single channel but S2T will assign one sample number per channel.

### Usage

You can find example of conversion settings inside of example_usage.sh file.


S2T is pure Python 3 script so all you need to get it to work is P3.

```sh
$ python3 score2tracker.py --i file.musicxml ---sel '(P1,1),(P1,2)' --o file.mod
```

`--sel` option is important. It's a list of parts and staff for each channel. So staff that should go to first channel is specified in first bracket and so on. First position is part id specified in MusicXML and second is staff number in that part. IE, if part 1 is violin and part 2 is piano - you can assign first staff in part one (P1,1) to channel one, first staff in part 2 to channel 2 and second staff in part 2 to channel 3 like so: `(P1,1),(P2,1),(P2,2)` - fourth channel will be empty.
MusicXML is markup language saved as plain text so you can lookup part ids in every text editor.

### MusicXML

Every major scorewriting software can export your comosition to MusicXML format. This is standard option in MuseScore and Noteflight. Sibelius users will need to install free MusicXML plugin.

### TODO

 - Importing samples
 - GUI
 - MIDI format input
 - Export to SND/SNDH format
 - Export to TIC-80

There are some code remainings after attempts to implement sample importing. However I cannot get this to work properly (samples seems to be corrupted after writing to MOD file).
