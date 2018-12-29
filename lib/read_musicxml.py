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

import xml.etree.ElementTree as ET
import sys
class ScoreTranscriber:
    def __init__(self,score,p_id='',s_num=0): # p_id - part id, s_id - staff selection
        self.p_id = p_id
        self.s_num = s_num
        self.file = ET.parse(score)
        self.root = self.file.getroot()
        self.parts = self.root.findall('part')
        self.repetition = False
    def get_score_title(self):
        sc_title = self.root.find('work/work-title')
        if (sc_title is not None):
            return sc_title.text
    def analyse_score(self):
        parts_ids = []
        cstaves = 0
        i = 1
        for part in self.parts:
            parts_ids.append([part.attrib['id'],str(i)])
            staves = part.find('measure/attributes/staves')
            if staves is not None:
                cstaves = int(staves.text)
                while i < cstaves:
                    i = i + 1
                    parts_ids.append([part.attrib['id'],str(i)])
        return parts_ids
    def convert_accidentals(self,note, alter):
        alter = str(alter)
        if alter == '-1': accidental = 'b'
        elif alter == '1': accidental = '#'
        elif alter == '2': accidental = '##'
        else: accidental = ''
        if accidental == 'b':
            accidental = '#'
            if (note == 'A'): note = 'G'
            if (note == 'B'): note = 'A'
            if (note == 'H'): note = 'A'
            if (note == 'C'):
                note = 'B'
                accidental = ''
            if (note == 'D'): note = 'C'
            if (note == 'E'): note = 'D'
            if (note == 'F'):
                note = 'E'
                accidental = ''
            if (note == 'G'): note = 'F'
        if accidental == '##':
            if (note == 'A'): note = 'B'
            if (note == 'B'):
                note = 'C'
                accidental = '#'
            if (note == 'C'): note = 'D'
            if (note == 'D'): note = 'E'
            if (note == 'E'):
                note = 'F'
                accidental = '#'
            if (note == 'G'): note = 'A'
        converted_accidentals = [note,accidental]
        return (converted_accidentals)
    def get_notes(self): # p_id - part id, s_id - staff selection
        read_note = ''
        read_rest = ''
        read_duration = ''
        current_element=''
        current_type=''
        current_acc = ''
        transcribed_notes = []
        needed_part = ''
        repeated_notes = []
        rep_node = ''
        s_num = str(self.s_num)
        for part in self.parts:
            if part.attrib['id'] == self.p_id:
                needed_part = part # its ok - part can be scanned when it was not selected
        if (needed_part == '')or(needed_part is None):
            print('Error in musicxml: Part '+str(self.p_id)+' missing.')
            sys.exit()
        for ms in needed_part.findall('measure'):
            rep_node = ms.find('barline/repeat')
            if rep_node is not None:
                rep_node = rep_node.attrib['direction']
                if rep_node == 'forward': self.repetition = True
            for note in ms.findall('note'):
                current_staff = note.find('staff')
                if current_staff is not None:
                    current_staff = current_staff.text
                if (s_num is not '0') and (current_staff is None):
                    print('There is no staff obiects, setting s_num to 0.') # works if selected part is 1 but in one staff parts staffs are not described
                    s_num='0'
                if (s_num == str(current_staff)) or ((s_num=='0') and (current_staff is None)):
                    read_note = note.find('pitch')
                    read_rest = note.find('rest')
                    read_duration = note.find('duration')
                    read_bck_duration = note.find('backup/duration')
                    is_chord = note.find('chord')
                    read_type = note.find('type')
                    read_dot = note.find('dot')
                    if (read_dot is not None): read_dot = 1
                    else: read_dot = 0
                    if (read_note is not '')and(read_note is not None):
                        current_note = read_note.find('step')
                        current_element = current_note.text
                        current_octave = read_note.find('octave')
                        current_octave = current_octave.text
                        current_alter = read_note.find('alter')
                        if (current_alter is not None) and (current_alter is not ''):
                            current_alter = current_alter.text
                            converted_accidentals = self.convert_accidentals(current_element,current_alter)
                            current_element = converted_accidentals[0]
                            current_acc = converted_accidentals[1]
                        else: current_acc = ''
                    elif (read_rest is not '')and(read_rest is not None)and((read_note=='') or (read_note is None)):
                        current_element = 'R'
                        current_octave = '0'
                        if (read_type is '')or(read_type is None):
                            current_type = 'measure'
                    if (read_duration is not '')and(read_duration is not None):
                        current_duration = read_duration.text
                    if (read_bck_duration is not '')and(read_bck_duration is not None):
                        current_duration = read_bck_duration.text
                        print('Backup duration present')
                    if (read_type is not '')and(read_type is not None):
                        current_type = read_type.text
                if current_element is not '' and current_duration is not '' and is_chord is None:
                    transcribed_notes.append([current_element,current_acc,current_octave,current_type,read_dot,current_duration])
                    if self.repetition == True:
                        repeated_notes.append([current_element,current_acc,current_octave,current_type,read_dot,current_duration])
                    else: repeated_notes = []
                current_element = ''
                current_duration = ''
                current_type = ''
                is_dotted = 0
            if rep_node == 'backward': self.repetition = False
            if (len(repeated_notes)>0)and(self.repetition==False):
                for repeated_note in repeated_notes:
                    transcribed_notes.append(repeated_note)
        return(transcribed_notes)