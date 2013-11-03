#!/usr/bin/env python
import Image
import os
import sys

def thumbnails(path, filelist):
	for file in filelist:
		print file
		im = Image.open(path + '/' + file)
		if(im.mode == "P"): im = im.convert("RGB")

		sM = (70, 70)
		sS = (30, 30)
		sL = (145, 145)
		im.thumbnail(sL)
		im.save(path + '/high/' + file, 'JPEG')
		im.thumbnail(sM)
		im.save(path + '/medium/' + file, 'JPEG')
		im.thumbnail(sS)
		im.save(path + '/low/' + file, 'JPEG')

if __name__ == '__main__':
	path = sys.argv[1]
	if not os.path.exists(path + '/high'):
		os.mkdir(path + '/high')
	if not os.path.exists(path + '/medium'):
		os.mkdir(path + '/medium')
	if not os.path.exists(path + '/low'):
		os.mkdir(path + '/low')
	raw_list = os.listdir(path)
	filelist = [f for f in raw_list if f.endswith('jpg') or f.endswith('gif')]
	thumbnails(path, filelist)
