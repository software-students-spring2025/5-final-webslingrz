# Webslingrz Final Project


# Team
* Brian Zou [Brian's Github](https://github.com/brianzou03)
* Andrew Bao [Andrew's Github](https://github.com/andrew-bao)
* Jasmine Fan [Jasmine's Github](https://github.com/jasmine7310)
* Bryant To [Bryant's Github](https://github.com/bryantto08)

# How to Run via Docker
### Full Application
```

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

# Running bird game (temporarily, until pygame is linked with flask)
```
python3 -m venv venv
source venv/bin/activate 
./venv/bin/python backend/bird_game.py
```

### Unit tests for web app
```

```


# Task Board
View our task board [here](https://github.com/orgs/software-students-spring2025/projects/234/views/2)

# Technology
* Python / Flask
* PyGame
* Docker
* MongoDB
* Digital Ocean
