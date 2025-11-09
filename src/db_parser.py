import json
import os
import pandas as pd
import pygame
from PopeData import PopeData

def getPopes(filename) -> dict[int, PopeData]:
    directory = os.path.dirname(filename)
    print(f'Pope database directory: {directory}')
    df = pd.read_excel(filename, sheet_name=0)
    # print(df.head())
    #print(pygame.get_init())

    popes : dict[int, PopeData] = {}
    for index, row in df.iterrows():
        p = PopeData()
        p.parseFromPandasRow(row)
        img_filename = os.path.join(directory, 'png_images', f'cropped_{p.id:03d}.png')
        if pygame.get_init() and os.path.exists(img_filename):
            p.image = pygame.image.load(img_filename)
            #print(f'Loaded {img_filename}')
        popes[p.id] = p

    return popes

if __name__ == "__main__":
    db_file = 'assets/db/Pope-mon_stats.xlsx'
    popeDB = getPopes(db_file)