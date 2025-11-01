import qrcode
from qrcode.image.styledpil import StyledPilImage
import db_parser
import os
from PIL import Image, ImageDraw, ImageFont

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
            #print(url)
            img = qrcode.make(url)
            img = img.convert('RGB')
            #img.show()
            #print(type(img))
            #print(f'Image mode: {img.mode}')
            #print(img.size)
            output_dir = f'{output_dir_base}/{folder}'
            try:
                os.mkdir(output_dir)
                print(f"Directory '{output_dir}' created successfully.")
            except FileExistsError:
                #print(f"Directory '{output_dir}' already exists.")
                pass
            filename = f'{output_dir}/{id:03d}.png'
            #print(filename)

            # add the pope ID string below the QR code
            # Calculate new image dimensions
            text_height = 20 # Adjust as needed for your text size
            new_width, new_height = img.size
            img_width, img_height = img.size
            new_height += text_height
            #print(f'({new_width}, {new_height})')

             # Create a new blank image
            img_final = Image.new('RGB', (new_width, new_height), (255,255,255))
            # print(f'Original image size: {img.size}, Final image size: {img_final.size}')
            # print(type(img))
            img_final.paste(img, (0, 0, img_width, img_height)) # Paste QR code at the top-left 
            #img_final.paste(Image.new("RGB", (20, 20), "blue"), (10, 10)) # Paste QR code at the top-left 
            
            draw = ImageDraw.Draw(img_final)
            font = ImageFont.truetype("Arial.ttf", 20) # Specify font and size
            text_to_add = f'{id:03d}'
            text_color = (0, 0, 0) # Black color

            # Calculate text position (e.g., centered below the QR code)
            text_width = draw.textlength(text_to_add, font=font)
            text_height_actual = 100
            text_x = (new_width - text_width) / 2
            text_y = img.height + (text_height - text_height_actual) / 2

            draw.text((text_x, text_y), text_to_add, font=font, fill=text_color)
            # img_final.show()

            img_final.save(filename)
