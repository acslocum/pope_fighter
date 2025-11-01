import qrcode
from qrcode.image.styledpil import StyledPilImage
import db_parser
import os

base_url = 'https://www.aws.com/fortress_party' # update with real URL later
output_dir_base = '../assets/db/qr_codes'

# add different types/endpoints. Format is a tuple: (output_folder, endpoint)
qr_code_types = [ ('registration', 'register') ]

if __name__ == "__main__":
    db_file = '../assets/db/Pope-mon_stats.xlsx'
    popeDB = db_parser.getPopes(db_file)

    for id in popeDB.keys():
        for folder, endpoint in qr_code_types:
            url = f'{base_url}/{endpoint}/{id:03d}'
            print(url)
            exit()
            img = qrcode.make(url)
            output_dir = f'{output_dir_base}/{folder}'
            try:
                os.mkdir(output_dir)
                print(f"Directory '{output_dir}' created successfully.")
            except FileExistsError:
                #print(f"Directory '{output_dir}' already exists.")
                pass
            filename = f'{output_dir}/{id:03d}.png'
            #print(filename)
            img.save(filename)
