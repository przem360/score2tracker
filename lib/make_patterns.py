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

class HarryPattern:
    def __init__(self,note_list,tracker,channel,instrument,cutnote):
        self.note_list = note_list
        self.instrument = instrument
        if tracker == 'pt' or tracker == 'protracker':
            self.preoctave_spacer = '-'
            self.postoctave_spacer = '-'
            self.rest_command = 'EC'
            self.rest_note = '-'
            self.empty_frame = '---------'
        elif tracker == 'tic' or tracker == 'tic89' or tracker == 't80':
            self.preoctave_spacer = '-'
            self.postoctave_spacer = ''
            self.rest_command = '00'
            self.rest_note = '-'
            self.instrument = ''
            self.empty_frame = '--------'
    def get_duration(self,ntype,dot):
        duration_out = ''
        if ntype == 'whole':
            duration_out = '64'
            if dot == 1: duration_out = int(duration_out)*1.5
        elif ntype == 'measure':
            duration_out = '64'
            if dot == 1: duration_out = int(duration_out)*1.5
        elif ntype == 'half':
            duration_out = '32'
            if dot == 1: duration_out = int(duration_out)*1.5
        elif ntype == 'quarter':
            duration_out = '16'
            if dot == 1: duration_out = int(duration_out)*1.5
        elif ntype == 'eighth':
            duration_out = '8'
            if dot == 1: duration_out = int(duration_out)*1.5
        elif ntype == '16th':
            duration_out = '4'
            if dot == 1: duration_out = int(duration_out)*1.5
        elif ntype == '32th':
            duration_out = '2'
            if dot == 1: duration_out = int(duration_out)*1.5
        elif ntype == '64th':duration_out = '1'
        else: duration_out = ntype
        return duration_out
    def make_frames(self,command,command_parameter):
        basic_command = command
        basic_command_parameter = command_parameter
        frame_list = []
        for event in self.note_list:
            if event[0] == 'R':
                event[0] = self.rest_note
                event[1] = '-'
                event[2] = '-'
                command = self.rest_command
                current_instrument = '00'
                command_parameter='0' # '00'
            else:
                command = basic_command
                command_parameter = basic_command_parameter
                current_instrument = self.instrument
            if (event[1] == '') or (event[1] is None): event[1] = self.preoctave_spacer # if no accidental then put '-'
            cduration = int(self.get_duration(event[5],event[4]))*2
            frame = event[0]+str(event[1])+event[2]+self.postoctave_spacer+current_instrument+command+command_parameter
            # [current_element,current_acc,current_octave,current_type,read_dot,current_duration]
            frame_list.append(frame)
            while(cduration-1)>0:
                frame_list.append(self.empty_frame)
                cduration = cduration-1
        return frame_list
    def make_patterns(self,frame_list,pt_size):
        patterns = []
        while len(frame_list):
            patterns.append(frame_list[0:pt_size]) # patterns.append([frame_list[0:pt_size]])
            del frame_list[0:pt_size]
        last_pattern_size = len(patterns[-1])
        i = last_pattern_size
        while i < pt_size:
            patterns[-1].append(self.empty_frame)
            i+=1
        return patterns
def add_empty_pattern(list_of_patterns,to_add,pt_lenght):
    empty_pattern = []
    while pt_lenght>0:
        empty_pattern.append('---------')
        pt_lenght -=1
    while to_add > 0:
        list_of_patterns.append(empty_pattern)
        print('ADDED!')
        to_add -=1
    return list_of_patterns