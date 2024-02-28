# PlanetDownload
Simple scripts to download Planet imagery given an ROI and time constraints. You need a Planet account to use these scripts. 

# Install requirements

	conda create -n planetdownload python=3.7 -y
	conda activate planet
	pip install planet
	git clone https://github.com/mlundine/PlanetDownload.git

Keep in mind Windows needs paths separated by \\\

e.g., C:\\\Users\\\etc

# download_planet_imagery_cmd_flags.py 

	cd path/to/this/repo
	python download_planet_imagery_cmd_flags.py -u username -p password -o order_name -roi roi.geojson -t1 YYYY-MM-DD -t2 YYYY-MM-DD -od path/to/output/directory

download_planet_imagery_cmd_flags.py accepts cmd line arguments for Planet username and password, path to the geojson ROI, time constraints, and the path to where the images should be saved to.

# download_planet_imagery_user.py

	cd path/to/this/repo
	python download_planet_imagery_user.py 

download_planet_imagery_user.py accepts user inputs through the cmd line for Planet username and password, path to the geojson ROI, time constraints, and the path to where the images should be saved to.

# to do
merging output images, ndvi and ndwi calculation, output to coastsat and coastseg dir format