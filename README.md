# Design-Studio: Trafic Flow Ninja

## Dev-Setup Instructions

Manual:

1. Download pipenv - `pip install pipenv`, https://pypi.org/project/pipenv/
2. Execute in projects directory `pipenv --three` to create a virtual environment
3. Execute `pipenv install` to install dependencies into virtual environment
4. Make sure you are using right python version

Requirements:
- python 3.8.1

Usage:
1. Run `tfn.sh` (or `tfn.ps1` on windows) in console.
2. Script takes two arguments: latitude and longitude. If you don't know exact coordinates of your road you can copy them from open street maps url: https://www.openstreetmap.org/
3. Script will list you nearest roads and info about the first one. Lastly you will get hourly traffic measured in cars/h.

Options:

`--tomtom-key KEY` - provide tomtom api key

`--length METERS` - length of road taken into account (real road length will be slightly bigger)

`--road ROAD` - specify number of road you want to perform calculations for

`--list-roads` - this will only list you roads without calculating traffic.

`--timeout SECONDS` - timeout for road provider

`--road-provider ROAD_PROVIDER` - if you wish to implement your own road provider, then you can run our app with it, by using this option.

`--model MODEL` - if you wish to implement your own model, then you can run our app with it, by using this option.

`--json FILENAME` - specify filename you want to dump results to in json format.