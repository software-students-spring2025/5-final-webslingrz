# Webslingrz Final Project


# Team
* Brian Zou [Brian's Github](https://github.com/brianzou03)
* Andrew Bao
* Ritz (Jasmine) Fan
* Bryant To

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
View our task board [here]()

# Technology
* Python / Flask
* PyGame
* Docker
* MongoDB
* Digital Ocean
