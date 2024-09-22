#!/usr/bin/env python3

from PIL import Image
import imagehash
from argparse import ArgumentParser
from glob import glob
import os

import json

imageExtensions = set()
imageExtensions.add("jpg")
imageExtensions.add("jpeg2")
imageExtensions.add("png")

class ImageHash:

	def __init__(self, image, hash):
		self.image = image
		if isinstance(hash, str):
			self.hash = imagehash.hex_to_hash(hash)
		else:
			self.hash = hash

	def __str__(self):
		return f"{self.image} ({self.hash})"

	def distanceTo(self, other):
		if type(other) is not ImageHash:
			raise "foo"
		return self.hash - other.hash

# def getImagesFiles(directory):
# 	files = glob("*", root_dir=directory)

# 	images = list()
# 	for file in files:
# 		fileLC = file.lower()
# 		for extension in imageExtensions:
# 			if extension in fileLC:
# 				images.append(file)
# 				break

# 	return images

# def getHash(filename, directory):
# 	image = Image.open(f"{directory}/{filename}")
# 	hash = imagehash.phash(image, hash_size=8)
# 	return hash

def convertToImageHashes(hashes):
	imageHashes = dict()
	for image in hashes:
		ih = ImageHash(image, hashes[image])
		imageHashes[image] = ih
	return imageHashes

def analyze(imageHashes, threshold):

	grouped = dict()
	while len(imageHashes) > 1:
		current = imageHashes.popitem()[1]
		currentHash = current.hash
		grouped[currentHash] = list()
		grouped[currentHash].append(current)
		toRemove = list()
		for image in imageHashes:
			other = imageHashes[image]
			if current.distanceTo(other) <= threshold:
				# del imageHashes[image]
				toRemove.append(image)
				grouped[currentHash].append(other)
		for remove in toRemove:
			del imageHashes[remove]

	for remaining in imageHashes:
		imageHash = imageHashes[remaining]
		grouped[imageHash.hash] = [imageHash]

	return grouped
	# for group in grouped:
	# 	print(grouped[group])
	# count = len(grouped)
	# print(f"found {count} groups")

def commit(directory, isSymlink, groups):
	groupSubDir = f"{directory}/groups"
	os.mkdir(groupSubDir)
	for group in groups:
		imageHashes = groups[group]
		groupName = str(group)
		newGroupPath = f"{groupSubDir}/{groupName}"
		os.mkdir(newGroupPath)

		for imageHash in imageHashes:
			oldPath = f"{directory}/{imageHash.image}"
			newPath = f"{newGroupPath}/{imageHash.image}"

			if isSymlink:
				os.symlink(oldPath, newPath)
			else:
				# os.rename(oldPath, newPath)
				print("disabled rename")

def main():
	parser = ArgumentParser(description="Take a json file with pHashes and sort into similar groups.")

	parser.add_argument('--input', '-i', required=True, help="The json file.")
	parser.add_argument('--output', '-o', help="Grouped json file output")
	parser.add_argument('--threshold', '-t', default=13, type=int, help="Hamming distance threshold for a group. Differences less than this will constitute a group.")
	parser.add_argument('--commitInDirectory', help="The directory where the images reside. If set, the images will get sorted into folders.")
	parser.add_argument('--linkInDirectory', help="The directory where the images reside. If set, the images will get sorted into folders as symlinks.")

	args = parser.parse_args()

	threshold = args.threshold

	inputJSONFile = args.input
	hashes = dict()
	with open(inputJSONFile, 'r') as f:
		hashes = json.load(f)
	# print(hashes)
	# allHashes = 
	imageHashes = convertToImageHashes(hashes)
	groups = analyze(imageHashes, threshold)

	if args.linkInDirectory is not None:
		commit(args.linkInDirectory, True, groups)

	if args.commitInDirectory is not None:
		commit(args.commitInDirectory, False, groups)

	for group in groups:
		imageHashes = groups[group]
		images = [imageHash.image for imageHash in imageHashes]
		print(f"{group}: {images}")


	# directory = args.input
	# output = args.output
	# images = getImagesFiles(directory)
	
	# imageMap = dict()
	# for image in images:
	# 	hash = getHash(image, directory)
	# 	imageMap[image] = str(hash)
	# 	print(f"{image}: {hash}")

	# newjson = json.dumps(imageMap, indent="\t")
	# with open(output, 'w') as f:
	# 	f.write(newjson)

main()