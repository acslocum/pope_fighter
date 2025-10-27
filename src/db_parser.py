import os
import pandas as pd
import pygame

class PopeData:
    def __init__(self):
        self.name : str = ''
        self.pontiff_num : float = 0.0
        self.id : int = 0
        self.century : str = ''
        self.type : str = ''
        self.canonization : str = ''
        self.signature_move : str = ''
        self.flavor_text : str = ''
        self.holiness : int = 0
        self.miracles : int = 0
        self.wisdom : int = 0
        self.legacy : int = 0
        self.image_file : str = ''
        self.image = None
        self.length_of_reign : float = 0.0

    def __str__(self):
        return f'{self.id}, {self.name}'

    def parseFromPandasRow(self, row):
        self.name = str(row['name'])
        self.pontiff_num = float(row['Pontiff_Number'])
        self.id = int(row['PopeID'])
        self.century = str(row['Century'])
        self.type = str(row['Type'])
        self.canonization = str(row['Canonization'])
        self.signature_move = str(row['Signature_Move'])
        self.flavor_text = str(row['Flavor_Text'])
        self.holiness = int(row['Holiness'])
        self.miracles = int(row['Miracles'])
        self.wisdom = int(row['Wisdom'])
        self.legacy = int(row['Legacy'])
        self.image_file = str(row['Image'])
        self.length_of_reign = float(row['Length_of_Reign'])

def getPopes(filename) -> dict[int, PopeData]:
    directory = os.path.dirname(filename)
    print(f'Pope database directory: {directory}')
    df = pd.read_excel(filename, sheet_name=0)
    # print(df.head())
    print(pygame.get_init())

    popes : dict[int, PopeData] = {}
    for index, row in df.iterrows():
        p = PopeData()
        p.parseFromPandasRow(row)
        img_filename = os.path.join(directory, f'{p.id:03d}.png')
        if pygame.get_init() and os.path.exists(img_filename):
            p.image = pygame.image.load(img_filename)
            print(f'Loaded {img_filename}')
        popes[p.id] = p

    return popes

if __name__ == "__main__":
    db_file = 'assets/db/Pope-mon_stats.xlsx'
    popeDB = getPopes(db_file)