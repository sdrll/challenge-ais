# Challenge AIS

The objective is to provide
a Docker container that could ingest AIS data, compare it with available Sentinel-2 images on the
same day and provide machine learning-ready annotations

Build the docker image : `sudo make build`

Create a data folder with two subfolders inside : `input` and `output`

Store AIS csv in the input folder. Geojson result will appear in the output folder 

Run the docker image with data
volume : `sudo docker run -v <absolute_path_local_data_foler>:/opt/data <docker_image_id>`