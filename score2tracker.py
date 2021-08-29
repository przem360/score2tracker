#!/usr/bin/python3

#  score2tracker - MusicXML to MOD converter
#  copyright (c) 2018 Przemysław Wolski <wolski@gmx.co.uk>
#  URL: https://github.com/przem360/score2tracker
 
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
 
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 
from os import system, name
import sys, getopt
import argparse
import string
import re
from pathlib import Path
from lib.read_musicxml import ScoreTranscriber
from lib.make_patterns import HarryPattern
from lib.make_patterns import add_empty_pattern
from lib.mod_files import FileOperator

parser = argparse.ArgumentParser()
parser.add_argument('--i', help="MusicXML filename or path")
parser.add_argument('--s', help="list of samples")
parser.add_argument('--spc', help="sample per channel")
parser.add_argument('--sel', help="Selecting parts and staffs for each channel")
parser.add_argument('--txt', help="Export MOD structure to text file")
parser.add_argument('--o', help="MOD filename or path")
args = parser.parse_args()
validchars = string.ascii_letters + string.digits + '_'
validpath = string.ascii_letters + string.digits + '_' + '/' + '\\'
channels_counter = 4
selected_samples = ''
sample_per_channel = ''
curr_ch_selection = ''
curr_st_selection = ''
txt_file_path = ''
title = ''
com_selected_channels = ''
selected_channels = []
mod_visualisation = []
pt_lenght = 64
sample_folder = 'samples/'
score_selection_format = re.compile('^((\([Pp][0-9]+\,[0-9]+\)),?){1,4}$')
the_file = ''
mod_file_path = ''
def clear():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')
def clear_string(raw_string,is_path):
    if is_path == 0:
        clean_string = ''.join(c for c in raw_string if c in validchars)
    else:
        clean_string = ''.join(c for c in raw_string if c in validpath)
    return clean_string
def cut_string (raw_string,size):
    if len(raw_string)>int(size):
        raw_string = raw_string[:int(size)]
    return raw_string
def print_part_staff_list(staff_list):
    staff_counter = 1
    for staff in staff_list:
        print (str(staff_counter)+'. Part ID: '+str(staff[0])+'. Staff ID '+str(staff[1])+'\n')
        staff_counter+=1
def channel_selection(channels_counter):
    i = 0
    print('Parts and staffs in XML file:')
    print_part_staff_list(transcribed.analyse_score())
    parts = []
    for psline in transcribed.analyse_score():
        if psline[0] not in parts:
            parts.append(psline[0])
    while i < channels_counter:
        curr_ch_selection = input('Type PART id fo channel '+str(i+1)+'... ')
        curr_ch_selection.upper()
        while curr_ch_selection not in parts:
            curr_ch_selection = input('Sorry, but this id is not present in your score.\nType PART id fo channel '+str(i+1)+'... ')
            curr_ch_selection.upper()
        staffs_in_part = []
        for psline in transcribed.analyse_score():
            if curr_ch_selection == psline[0]:
                staffs_in_part.append(str(psline[1]))
        curr_st_selection = input('Type STAFF id fo channel '+str(i+1)+'... ')
        while (curr_st_selection !='skip') and (curr_st_selection not in staffs_in_part):
            curr_st_selection = input('Sorry, but this staff id is not present in selected part.\nType STAFF id for channel '+str(i+1)+', of part '+str(curr_ch_selection)+'... ')
        selected_channels.append([curr_ch_selection,curr_st_selection])
        i = i+1
    return selected_channels
def validate_selection (user_selection,hints):
    val = 1
    staffs_in_part = []
    for selection in user_selection:
        if (selection not in hints):
            print('Selection error in pair: '+str(selection)+'.')
            sys.exit()
    return val
if args.i: the_file = args.i
if args.txt: txt_file_path = args.txt
if args.s: selected_samples = args.s
if args.spc: sample_per_channel = args.spc
if args.sel: com_selected_channels = args.sel
if args.o: mod_file_path = args.o

# txt_file_path = 'log.txt'

if (the_file == '')or(the_file is None):
    get_file = input('Type MusicXML filename or path... ')
    get_file = clear_string(get_file,1)
    the_file = Path(get_file)
else:
    the_file = Path(the_file)
transcribed = ScoreTranscriber(the_file)
if (title != None)and(title != ''):
    title = transcribed.get_score_title().replace(' ', '_')
if (title is None)or(title==''):
    title = 'score2tracker'
title = clear_string(title,0)
title = cut_string(title,20)

if (mod_file_path == '')or(mod_file_path is None):
    get_mod_file = input('Type MOD filename or path... ')
    get_mod_file = clear_string(get_mod_file,1)
    mod_file_path = Path(get_mod_file)
else:
    mod_file_path = Path(mod_file_path)
if (selected_samples == '')or(selected_samples is None):
    #i = 0
    test_samples = []
    selected_samples = []
    # sample loading function is optinal since wave files are corrupted
    # while i<channels_counter:
    #     get_sample_file = input('Type SAMPLE filename or patch for channel '+str(i+1)+': ')
    #     test_samples.append(get_sample_file)
    #     selected_samples.append(Path(sample_folder+get_sample_file))
    #     i+=1
else:
    get_selected_samples = selected_samples.split(',')
    selected_samples = []
    test_samples = []
    for get_sample_path in get_selected_samples:
        test_samples.append(get_sample_path)
        selected_samples.append(Path(sample_folder+get_sample_path))
for sample_path in selected_samples:
    if not(sample_path.is_file()):
        print('Error while checking sample list. Unable to find one or more sample file.')
        sys.exit()
if (sample_per_channel == '')or(sample_per_channel is None): sample_per_channel = [1,2,3,4]
else:
    sample_per_channel = sample_per_channel.split(',')

if (score_selection_format.match(com_selected_channels)):
    com_selected_channels.upper()
    com_selected_channels=''.join(c for c in com_selected_channels if c in string.digits+'P,')
    com_selected_channels=com_selected_channels.split(',')
    sch_tmp_list = []
    while len(com_selected_channels)>0:
        i = 0
        while i<2:
            sch_tmp_list.append(com_selected_channels.pop(0))
            i+=1
        selected_channels.append(sch_tmp_list)
        sch_tmp_list = []
    i=0
    selected_staffs = selected_channels
    test = validate_selection(selected_channels,transcribed.analyse_score())

if (selected_channels is None)or(len(selected_channels)==0):
    print ('Could not read channel or staff selection, please type:')
    selected_channels = channel_selection(channels_counter)
    selected_staffs = selected_channels

def selection_to_channels(selected_channels):
    sample_per_channel_id = 0
    for selected_staff in selected_channels:
        selected_instrument = sample_per_channel[sample_per_channel_id]
        transcribed = ScoreTranscriber(the_file,selected_staff[0],selected_staff[1])
        pattern = HarryPattern(transcribed.get_notes(),'pt',4,str(selected_instrument).zfill(2),'EC')
        mod_visualisation.append(pattern.make_patterns(pattern.make_frames('00','0'),pt_lenght)) # make_frames(command,command_parameter)
        sample_per_channel_id +=1
    return mod_visualisation
def draw_mod(pattern_pack):
    line = '|'
    i = 0
    p_i = 0 # pattern iteration
    t_i = 0 # iterating thru patterns in strack
    longest_track = 0
    amount_of_patterns = len(pattern_pack[0])
    for ctrack in pattern_pack:
        if len(ctrack)>longest_track: longest_track = len(ctrack)
    for ctrack in pattern_pack:
        if len(ctrack)<longest_track:
            to_add = longest_track - len(ctrack)
            ctrack = add_empty_pattern(ctrack, to_add,pt_lenght)
        if len(ctrack)>amount_of_patterns:
            amount_of_patterns = len(ctrack)
    pattern_lenght = len(pattern_pack[0][0])
    clear()
    while t_i < amount_of_patterns:
        while p_i < pattern_lenght:
            while i < len(selected_staffs):
                line = line + pattern_pack[i][t_i][p_i] + '|'
                i+=1
            line = line+'\n|'
            i = 0
            p_i+=1
        p_i=0
        t_i+=1
    t_i = 0
    clear()
    if line != '':
        print(line)
    return line
lines = ''
mod_visualisation = selection_to_channels(selected_staffs) # blocked for mod format testing
for mv in mod_visualisation: # blocked for mod format testing
    lines += draw_mod(mod_visualisation) # blocked for mod format testing
if len(txt_file_path)>0:
    txt_file_path = Path(txt_file_path)
    with open(txt_file_path,'w') as text_file:
        text_file.write(lines)
mod_file = FileOperator(test_samples)
mod_file.save_file(title,lines,mod_file_path,64)
