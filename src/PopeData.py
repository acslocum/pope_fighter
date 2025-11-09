import json
import pandas as pd

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
    
    def statsString(self):
        return f'{self.id}, {self.name}, {self.holiness}, {self.miracles}, {self.wisdom}, {self.legacy}, {self.length_of_reign}'

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

    def updateFromJSON(self, jsonData):
        data = json.loads(jsonData)
        if self.id != data['ID']:
            return
        
        self.holiness = int(data['holiness'])
        self.miracles = int(data['miracles'])
        self.wisdom = int(data['wisdom'])
        self.legacy = int(data['legacy'])
        self.length_of_reign = float(data['length_of_reign'])
        #print(self.statsString())
