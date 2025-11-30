import argparse
import os
import pygame
import random

class GameSounds:
    def __init__(self, directory : str = None):
        self.music = []
        self.sounds = {}

        if directory is not None:
            self.loadSounds(directory)

    def __str__(self) -> str:
        if len(self.sounds) == 0:
            return 'No sounds loaded'
        else:
            s = ''
            s += f'music: {len(self.music)}\n'
            for key in self.sounds:
                s += f'{key}: {len(self.sounds[key])} sounds' + '\n'
            return s

    def getCategories(self):
        return list(self.sounds.keys())
    
    def getRandEffect(self, category : str) -> pygame.mixer.Sound:
        if category not in self.sounds:
            print(f'GameSounds::getRandEffect(): category {category} not found in loaded sounds')
            return None
        
        sounds = self.sounds[category]
        idx = random.randrange(len(sounds))
        #print(f'Randomly selecting index {idx} of {len(sounds)} for category {category}')
        return sounds[idx]

    def loadSounds(self, directory : str):
        # clear out existing sounds
        self.sounds.clear()
        self.music.clear()

        if not os.path.isdir(directory):
            print(f'GameSounds::loadSounds(): {directory} not found')
            return
        
        desc_file = os.path.join(directory, 'descriptions.txt')
        if not os.path.exists(desc_file):
            print(f'GameSounds::loadSounds(): Could not find \'descriptions.txt\' in {directory}')
            return
        extension = '.mp3'

        with open(desc_file, 'r') as file:
            for line in file:
                if line.startswith('#'):
                    pass
                else:
                    fields = line.strip().split(',')
                    if len(fields) != 2:
                        print(f'Error parsing line: {line}')
                    else:
                        folder = fields[1].strip()
                        if len(folder) > 0:
                                # print(f'GameSounds::loadSounds(): {folder} found in \'descriptions.txt\'')
                                folder_path = os.path.join(directory, folder)
                                if os.path.isdir(folder_path):
                                    if fields[0].strip() == 'sound':
                                        #print(f'GameSounds::loadSounds(): parsing {folder_path}')
                                        sounds : list[pygame.mixer.Sound] = []
                                        #print(f'GameSounds::loadSounds(): found {len(os.listdir(folder_path))} in {folder_path}')
                                        #print(f'{os.path.abspath(folder_path)}')
                                        for filename in os.listdir(folder_path):
                                            filename = os.path.join(os.path.abspath(folder_path), filename)
                                            #print(f'GameSounds::loadSounds(): loading {filename}, is mp3 {filename.endswith(extension)}, is file {os.path.exists(filename)}')
                                            if filename.endswith(extension) and os.path.isfile(filename):
                                                sounds.append(pygame.mixer.Sound(filename))
                                        self.sounds[folder] = sounds
                                    elif fields[0].strip() == 'music':
                                        for filename in os.listdir(folder_path):
                                            filename = os.path.join(os.path.abspath(folder_path), filename)
                                            #print(f'GameSounds::loadSounds(): loading {filename}, is mp3 {filename.endswith(extension)}, is file {os.path.exists(filename)}')
                                            if filename.endswith(extension) and os.path.isfile(filename):
                                                self.music.append(filename)
        # print('GameSounds::loadSounds(): Finished loading audio files')
        # print(self)

if __name__ == '__main__':
    pygame.init()
    pygame.mixer.init()

    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    args = parser.parse_args()

    gs = GameSounds(args.directory)
    categories = gs.getCategories()
    effect = gs.getRandEffect(categories[random.randrange(len(categories))])
    effect.set_volume(0.5)
    if effect is not None:
        print(f'Playing random sound')
        channel = effect.play()
        while channel.get_busy():
            pass