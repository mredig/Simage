#!/usr/bin/env python3

from PIL import Image
import imagehash
from argparse import ArgumentParser
from glob import glob
import os
import json

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


def convertToImageHashes(hashes):
	imageHashes = dict()
	for image in hashes:
		ih = ImageHash(image, hashes[image])
		imageHashes[image] = ih

	imageHashesList = [imageHashes[key] for key in imageHashes]
	return imageHashesList

def analyzeIntoDupGroups(imageHashes, threshold):

	grouped = dict()

	for (index, imageHash) in enumerate(imageHashes):
		grouped[imageHash] = set()
		for otherIndex in range(index, len(imageHashes)):
			other = imageHashes[otherIndex]
			difference = imageHash.distanceTo(other)
			if difference <= threshold:
				grouped[imageHash].add(other)

	return grouped

def getKey(dict):
	return next(iter(dict))

def filterDupGroups(dupGroups):
	# for (key, group) in items(dupGroups):
	# 	print(dupGroups[group])
	filterGroups = dict()
	while len(dupGroups) > 0:
		largestKey = getKey(dupGroups)
		largest = dupGroups[largestKey]

		for (key, group) in dupGroups.items():
			if len(group) > len(largest):
				largest = group
				largestKey = key

		dupGroups.pop(largestKey)
		filterGroups[largestKey] = largest

		for ih in largest:
			keys = list(dupGroups)
			for key in keys:
				dupGroups[key].discard(ih)
				if len(dupGroups[key]) == 0:
					dupGroups.pop(key)

	return filterGroups

def commit(directory, isSymlink, groups, threshold):
	groupSubDir = f"{directory}/groups({threshold})"
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
				os.rename(oldPath, newPath)
				# print("disabled rename")

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
	dupGroups = analyzeIntoDupGroups(imageHashes, threshold)
	groups = filterDupGroups(dupGroups)

	if args.linkInDirectory is not None:
		commit(args.linkInDirectory, True, groups, threshold)

	if args.commitInDirectory is not None:
		commit(args.commitInDirectory, False, groups, threshold)

	for group in groups:
		imageHashes = groups[group]
		images = [imageHash.image for imageHash in imageHashes]
		print(f"{group}: {images}")

	print(f"total {len(groups)} group(s)")

main()