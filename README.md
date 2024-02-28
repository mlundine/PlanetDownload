# PlanetDownload
Simple scripts to download Planet imagery given an ROI and time constraints. You need a Planet account to use these scripts. 

# Install requirements

	conda create -n planetdownload python -y
	conda activate planet
	pip install planet
	git clone https://github.com/mlundine/PlanetDownload.git

# download_planet_imagery_cmd_flags.py 

	cd path/to/this/repo
	python download_planet_imagery_cmd_flags.py -u username -p password -o order_name -r="path/to/roi.geojson" -t1 YYYY-MM-DD -t2 YYYY-MM-DD -od="path/to/output/directory"

download_planet_imagery_cmd_flags.py accepts cmd line arguments for Planet username and password (flags -u and -p), path to the geojson ROI (flag -r), time constraints (flags -t1 and -t2 or the start and end time respectively), and the path to where the images should be saved to (flag -od).

# download_planet_imagery_user.py

	cd path/to/this/repo
	python download_planet_imagery_user.py 

download_planet_imagery_user.py accepts user inputs through the cmd line for Planet username and password, path to the geojson ROI, time constraints, and the path to where the images should be saved to.

# to do
merging output images, ndvi and ndwi calculation, output to coastsat and coastseg dir format