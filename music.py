import json
import os
from tkinter import Tk, Button, Label, Text, filedialog
from pygame import mixer
import re
import requests
from deep_translator import GoogleTranslator

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player with Lyrics")

        self.playing = False
        self.current_track = None
        self.lyrics = None
        self.lyrics_dict = None

        mixer.init()

        self.label = Label(root, text="Music Player")
        self.label.pack(pady=10)

        self.play_button = Button(root, text="Play", command=self.play_music)
        self.play_button.pack(pady=10)

        self.stop_button = Button(root, text="Stop", command=self.stop_music)
        self.stop_button.pack(pady=10)

        self.choose_file_button = Button(root, text="Choose File", command=self.choose_file)
        self.choose_file_button.pack(pady=10)

        self.lyrics_text = Text(root, height=10, width=40)
        self.lyrics_text.pack(pady=10)


        self.lyrics_api_response = requests.get("https://spotify-lyric-api-984e7b4face0.herokuapp.com/?url=https://open.spotify.com/track/0SqLN8ZqucYOGZH7SD4HGC?si=01fc836cbe164158&format=lrc").content.decode()
        self.lyrics = self.parse_response(self.lyrics_api_response)
        
        a = """[00:00.00]Lyrics Line 1
[00:10.00]Lyrics Line 2
[00:20.00]Lyrics Line 3
"""
        print(a)
        self.lyrics_dict = self.parse_lyrics(self.lyrics)


    def parse_response(self,r):
        lyrics = ""

        data = json.loads(r)

        res = ''

        for i in data['lines']:
            line = '[' + i['timeTag'] + ']' + i['words'] + '\n'
            res+=line
            print(line)

        return res
            

    def play_music(self):
        if self.current_track:
            mixer.music.load(self.current_track)
            mixer.music.play()
            self.playing = True
            self.update_lyrics()
        else:
            print("No track selected.")

    def stop_music(self):
        mixer.music.stop()
        self.playing = False

    def choose_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".mp3",
                                                filetypes=[("MP3 files", "*.mp3"),
                                                           ("All files", "*.*")])
        if file_path:
            self.current_track = file_path
            self.label.config(text=os.path.basename(file_path))
            self.lyrics_dict = self.parse_lyrics(self.lyrics)
            self.root.after(100, self.update_lyrics)  

    def parse_lyrics(self, lyrics):
        lines = lyrics.split('\n')
        lyrics_dict = {}

        for line in lines:
            match = re.search(r'\[(\d+:\d+\.\d+)\](.*)', line)
            if match:
                timestamp = match.group(1)
                content = match.group(2)
                lyrics_dict[timestamp] = content

        return lyrics_dict

    def update_lyrics(self):
        if self.playing:
            current_time = mixer.music.get_pos() / 1000  
            #current_timestamp = "{:02d}:{:05.2f}".format(int(current_time // 60), current_time % 60)
            

      
            # closest_timestamp = min((key for key in self.lyrics_dict.keys() if self.convert_timestamp(key) <= current_time),
            #             key=lambda x: abs(self.convert_timestamp(x) - current_time))
            

            closest_timestamp = None
            for i in self.lyrics_dict:
                if(self.convert_timestamp(i)<=current_time):
                  closest_timestamp = i
                else:
                    break
                if closest_timestamp == None:
                  closest_timestamp = i
                  break
              

                translated = GoogleTranslator(source='auto', target='ro').translate(self.lyrics_dict[closest_timestamp])  # output -> Weiter so, du bist großartig
                if translated == None:
                    translated = ""
                displayed_lyrics = translated
                self.lyrics_text.delete("1.0", "end")
                self.lyrics_text.insert("1.0", displayed_lyrics)

            self.root.after(100, self.update_lyrics)

    def convert_timestamp(self, timestamp):
        minutes, seconds = map(float, timestamp.split(':'))
        return minutes * 60 + seconds


root = Tk()
music_player = MusicPlayer(root)
root.mainloop()
