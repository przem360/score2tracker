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

from pathlib import Path
import wave
import os
import sys
from pprint import pprint
class FileOperator:
    def __init__(self,samples):
        self.selected_samples = samples
        self.sample_files = samples
        while (len(self.selected_samples)<31):
            self.selected_samples.append('')
    def get_stereo_duration(self, filename):
        fileSize=os.path.getsize('samples/'+filename)
        return int((fileSize-44)/2)
    def get_wave_duration(self,wav_filename): # alternative function to calculate file duration
        f = wave.open(wav_filename, 'r')
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames/float(rate)
        f.close()
        return duration
    def swapNibbles(self,x): 
        for b in x:
            c = bytes(((b<<4 & 0xF0) + (b >> 4)))
        return c
    def save_file(self,title,lines,fname,pt_limit):
        # dirty way - hardcoded periods
        periods = {
        'c0':1712,'c#0': 1616,'d0': 1524,'d#0': 1440,'e0': 1356,'f0':1280,'f#0': 1208,'g0':1140,'g#0':1076,'a0':1016,'a#0':960,'b0':906,'h0':906,
        'c':856,'c#': 808,'d': 762,'d#': 720,'e': 678,'f':640,'f#': 604,'g':570,'g#':538,'a':508,'a#':480,'b':453,'h':453,
        'c1':856,'c#1': 808,'d1': 762,'d#1': 720,'e1': 678,'f1':640,'f#1': 604,'g1':570,'g#1':538,'a1':508,'a#1':480,'b1':453,'h1':453,
        'c2':428,'c#2': 404,'d2': 381,'d#2': 360,'e2': 339,'f2':320,'f#2': 302,'g2':285,'g#2':269,'a2':254,'a#2':240,'b2':226,'h2':226,
        'c3':214,'c#3': 202,'d3': 190,'d#3': 180,'e3': 170,'f3':160,'f#3': 151,'g3':143,'g#3':135,'a3':127,'a#3':120,'b3':113,'h3':113,
        'c4':107,'c#4': 101,'d4': 95,'d#4': 90,'e4': 85,'f4':80,'f#4': 75,'g4':71,'g#4':67,'a4':63,'a#4':60,'b4':56,'h4':56
        }
        swapped_hex = {
        '01':b'\x10','02':b'\x20','03':b'\x30','04':b'\x40','05':b'\x50','06':b'\x60','07':b'\x70','08':b'\x80','09':b'\x90','10':b'\xA0','11':b'\xB0','12':b'\xC0','13':b'\xD0',
        '14':b'\xE0','15': b'\xF0','16':b'\x10'
        }
        if ((pt_limit>0)and((len(lines.splitlines())/64)>64)):
            to_cut_out = len(lines.splitlines())-4096 # 64 events in 128 patterns = 8192
            new_lines = lines.rsplit('\n',int(to_cut_out))
            lines = new_lines[0]
        with open(fname,'wb') as mod_file:
            title_len = len(title);
            if (title_len>20):
                title = title[0:20]
            mod_file.write(title.encode('utf8'))
            while (title_len<20):
                mod_file.write(b'\x00')
                title_len +=1
            for sample_data in self.selected_samples:
                if (sample_data is not ''):
                    sample_file = sample_data
                    duration = self.get_stereo_duration(str(sample_file))
                    sd = sample_data
                    sample_name = sd
                    name_len = len(sample_name)
                    if (name_len>22):
                        sample_name = sample_name[0:22]
                    mod_file.write(sample_name.encode('utf8'))
                    while(name_len<22):
                        mod_file.write(b'\x00')
                        name_len += 1
                    duration_byte = duration.to_bytes(2, byteorder='big', signed=True)
                    mod_file.write(duration_byte) #set sapmle size
                    mod_file.write(b'\x00') #set fine tuning
                    mod_file.write(b'\x10') #set volume
                    mod_file.write(b'\x00\x00\x00\x00') # loop start and lenght
                else:
                    mod_file.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
                    mod_file.write(b'\x00\x00') #set sapmle size
                    mod_file.write(b'\x00') #set fine tuning
                    mod_file.write(b'\x00') #set volume
                    mod_file.write(b'\x00\x00\x00\x00') # loop start and lenght
            # song lenght:
            mod_file.write(b'\x7F') # 127
            mod_file.write(b'\x7F') # 127 ??
            # writing pattern sequence?
            total_evnts = len(lines.splitlines())/64
            if total_evnts<1:
                total_evnts = 1
            if total_evnts>128:
                total_evnts =128
            event_counter = 0
            while (event_counter<128):
                pt_counter = 0
                while (pt_counter<64):
                    event_byte = pt_counter.to_bytes(1,byteorder='big', signed=True) # one byte for every pattern number
                    mod_file.write(event_byte)
                    event_counter+=1
                    pt_counter +=1
            mod_file.write("M.K.".encode('utf8'))
            # notes:
            for line in lines.splitlines():
                line = line.split('|')
                line = list(filter(None,line))
                for event in line:
                    if event == '---------':
                        mod_file.write(b'\x00\x00\x00\x00')
                    elif event == '----00EC0':
                        mod_file.write(b'\x00\x00\x0E\xC0')
                    else:
                        note_name = event[0]
                        note_name = note_name.lower()
                        note_sign = event[1]
                        note_octave = event[2]
                        instr_id = str(''.join(event[4:6]))
                        instr_byte = swapped_hex[instr_id]
                        if ((note_octave is not None) and (note_octave is not '-')):
                            if int(note_octave) > 4:
                                note_octave = str('4')
                            else:
                                note_octave = str(note_octave)
                        if ((note_name is not '-')and(note_sign is not '-')):
                            note_name = ''.join([note_name, note_sign])
                        if ((note_name is not None) and (note_name is not '-') and (note_octave is not '-')):
                            note_name = ''.join([note_name, note_octave])
                            current_period = periods[note_name]
                        if note_name == '-': current_period = 0;
                        current_byte = current_period.to_bytes(2, byteorder='big', signed=True)
                        mod_file.write(current_byte)
                        mod_file.write(instr_byte)
                        mod_file.write(b'\x00')
            # add wave files
            for sample_data in self.selected_samples:
                if (sample_data is not ''):
                    sample_file = 'samples/'+sample_data
                    #with open(sample_file, "rb") as wave_file:
                    wr = wave.open(sample_file,'r')
                    data = wr.readframes(wr.getnframes()-1)
                    mod_file.write(data)
            