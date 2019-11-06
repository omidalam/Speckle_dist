def get_files(src_dir):
	path_to_images = []
	for directory, dir_names, file_names in os.walk(str(src_dir)):
	            # We are only interested in files.
		for file_name in file_names:
	   # The list contains only the file names.
	    # The full path needs to be reconstructed.
			full_path = os.path.join(directory, file_name)
	#	    print full_path
	    # Both checks are performed to filter the files.
			path_to_images.append(full_path)
	return path_to_images

def get_f2(mypath):
	from os import listdir
	from os.path import isfile, join
	mypath=str(mypath)
	onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
	return onlyfiles