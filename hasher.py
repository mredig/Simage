#!/usr/bin/env python3

from PIL import Image
import imagehash
from argparse import ArgumentParser
from glob import glob
import os

import json

imageExtensions = set()
imageExtensions.add("jpg")
imageExtensions.add("jpeg")
imageExtensions.add("png")


def getImagesFiles(directory):
	files = glob("*", root_dir=directory)

	images = list()
	for file in files:
		fileLC = file.lower()
		for extension in imageExtensions:
			if extension in fileLC:
				images.append(file)
				break

	return images

def getHash(filename, directory, hashSize):
	image = Image.open(f"{directory}/{filename}")
	hash = imagehash.phash(image, hash_size=hashSize)
	return hash


def main():
	parser = ArgumentParser(description="Take a directory with images and output a json file with pHashes.")

	parser.add_argument('--input', '-i', required=True, help="The directory with images.")
	parser.add_argument('--output', '-o', help="destination json file")
	parser.add_argument('--hashSize', '-s', default=8, type=int, help="hash size (default 8)")

	args = parser.parse_args()

	directory = args.input
	output = args.output
	hashSize = args.hashSize
	images = getImagesFiles(directory)
	
	imageMap = dict()
	for image in images:
		hash = getHash(image, directory, hashSize)
		imageMap[image] = str(hash)
		print(f"{image}: {hash}")

	newjson = json.dumps(imageMap, indent="\t")
	with open(output, 'w') as f:
		f.write(newjson)

main()