#! /bin/sh
for img in *.png; do
  magick "$img" -gravity center -crop 812:1006 +repage "cropped_$img"
done