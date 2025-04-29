# Webslingrz Final Project
![backend.yaml](https://github.com/software-students-spring2025/5-final-webslingrz/actions/workflows/backend.yml/badge.svg?event=pull_request)

# Team
* Brian Zou [Brian's Github](https://github.com/brianzou03)
* Andrew Bao [Andrew's Github](https://github.com/andrew-bao)
* Jasmine Fan [Jasmine's Github](https://github.com/jasmine7310)
* Bryant To [Bryant's Github](https://github.com/bryantto08)

# About
### Silly game about silly birds!
Do you like birds but you wish they wouldn't fly away the moment you got near them? Do you wonder if there is a way to interact with these silly goobers at comfort of your desk? Then this game is for you!  
  
Birds will spawn on your screen. Click them to add them to your collection!  
  
Keep track of the birds you collected with the Birdiary!  
  
Just like in real life, your collected birds will generate gold.  
  
Use this gold to buy decoration to drip out your desktop and attract rarer birds!  
  
Buy the Froggy Fountain to become worthy of the bird who stands above all other birds...  

# Subsystems
* Mongodb: [Docker Hub](https://hub.docker.com/_/mongo)
* Flask/Pygame: [Docker Hub](https://hub.docker.com/repository/docker/bt2181/webslingerz/general)

# How to Run via Docker
### Full Application
```
docker compose up --build
```


# Running without Docker (Mac instructions)
## Web App
```
python3 -m venv venv
source venv/bin/activate 
cd backend
pip install -r requirements.txt
brew tap mongodb/brew
brew uninstall mongodb-community
brew cleanup
brew install mongodb/brew/mongodb-community
brew services stop mongodb/brew/mongodb-community
brew services cleanup
brew services start mongodb/brew/mongodb-community
cd ..
./venv/bin/python backend/app.py
```

Visit localhost via: http://127.0.0.1:5001

# Running bird game standalone
```
python3 -m venv venv
source venv/bin/activate 
./venv/bin/python backend/bird_game.py
```

### Unit tests for web app
A note about unit testing: bird_game.py is excluded via .coveragerc as bird_game contains advanced logic such as audio and visuals that are not meant to be unit tested
#### coverage testing (run from root directory)
```
coverage erase

coverage run -m pytest
coverage html
open htmlcov/index.html

```


#### main game loop test
* test_bird_spawn_probability_logic
* test_gold_accumulation_over_time
* test_collect_bird_removes_from_spawn
* test_open_birdiary_view
* test_open_store_view
* test_purchase_deco_with_enough_gold
* test_purchase_deco_with_insufficient_gold
```

```

#### routes test
* test_dashboard_requires_login
* test_dashboard_loads_correct_money
* test_birds_requires_login
* test_birds_loads_correct_collection
* test_play_requires_login
* test_build_game_logged_in
* test_build_game_not_logged_in
* test_update_money_valid
* test_update_money_invalid_data
* test_update_money_not_logged_in
* test_update_birds_valid
* test_update_birds_invalid_data
* test_update_birds_not_logged_in
```
pytest test_app/test_game_routes.py
```

#### auth test
* test_register_new_user
* test_register_existing_user
* test_login_valid_user
* test_login_invalid_user
* test_logout_clears_session
```
cd backend
pytest test_app/test_auth.py
```

#### utilities test
* test_load_scaled_image_valid_path
* test_load_scaled_image_invalid_path
* test_greyscale_surface_returns_correct_shape
* test_add_error_message_limit
* test_draw_error_messages_displays_recent
```
cd backend
pytest test_app/test_utilities.py
```

#### flask test
* test_app_home_redirects_to_dashboard
* test_register_blueprints_sets_routes
```
pytest backend/test_app/test_flask_app.py
```

# Task Board
View our task board [here](https://github.com/orgs/software-students-spring2025/projects/234/views/2)

# Technology
* Python / Flask
* PyGame
* Docker
* MongoDB
* Digital Ocean


