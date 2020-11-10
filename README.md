# Triple-Scrapers
Contains automated scrapers that collect data in the format of triples (i.e. [head, relation, tail] tuples).

## Install
1. Clone the repo.
2. Change to the top-level directory of the repo.
3. Run `./setup_repo.sh` to install dependencies and make needed virtual environments. This is run once to
setup the repo.

## Setup
1. Run `./setup_env.sh` to set needed environment variable and source the virtual environment. This is run
once each time you begin working with code in the repo.

## Scrape AI2Thor
1. Run `python thor/thor_scraper.py`. Triples extracted from simulated rooms will be contained in pickle
files inside the `triple-scrapers/thor/rooms/` folder.
2. To scrape the triples into text files instead of a pickle, see comment in the `main` function of 
`thor_scraper.py` inside the `thor` folder.