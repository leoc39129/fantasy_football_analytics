Goal: Make a full stack web app projecting NFL player's fantasy scores

*Requirements*
Basics:
1. Host the web app on AWS
2. Use a database to store player data from previous and current seasons, with the ability to import new data as each week passes
3. Use Flask for the backend to process requests and define the API
4. Use Vue for the frontend

Frontend:
1. Display projections for top 50 projected performers of an NFL week
    a. Be able to filter by all positions, RBs, WRs, TEs, and QBs (add D/ST, K later)
    b. Be able to choose which week of the current NFL season
        I. If the week is from the past, display actual points scored, and percent error
2. Display season projections and rankings (by position only), as well as actual rankings alongside a column highlighting the difference between the projected and actual points scored through the season

Backend/Database:
1. Follow REST principles in setting up API queries
2. Research a mathematical way to determine projected points (move into ML later)
3. Set up database structure through backend ORM for...
    a. Players: 
        I. ID
        II. Position
        III. Current Team
        IV. Seasons in the league
        V. Injury Designation
        VI. Preseason Ranking
    b. Teams
        I. ID
        II. Points Per Game (PPG)
        III. Points Against Per Game (PAPG)
        IV. Record
        V. Division
        VI. Schedule
        VII. Pace of Play
    c. Division
        I. ID
        II. Teams in Division
        III. Division Record
    d. Game
        I. ID
        II. Home Team
        III. Away Team
        IV. Spread
        V. O/U
    e. Player Game - Performance for a player in a specific game
        I. Player ID
        II. Game ID
        III. Passes Thrown 
        IV. Passes Completed
        V. Pass Yds
        VI. Pass TDs
        VII. Rush Attempts
        VIII. Rush Yds
        IX. Rush TDs
        X. Receptions
        XI. Rec Yds
        XII. Rec TDs
    f. To be added later: qbr, passing yards per game, pass TDs, % routes run, target share, % rushes, yards per carry, red zone targets, team red zone percentage

4. Support a bulk import for restoring lost data or importing first time data

TO DO:

So the endpoints on sportsdata.io are just completely scrambled for historical data, and we're also going to need historical data on the defensive team, over under, home vs. away games, spread, etc. because we can't predict points using data like rush attempts, rush yards, ... we have to predict based on similar games of the past and then see what a player has done in that situation, predict rush yds, attempts ... which will THEN get us to a fantasy point prediction. So, for now, data is the #1 priority.

Before we begin importing data, let's fix the models and make sure they're EXACTLY what we want them to be and make sure this new API has all of the information we want.

Models are all set, import player data from dashboard.api-football.com
Documentation: https://api-sports.io/documentation/nfl/v1
API key is already in the .env, just gotta make it work with the headers

We'll be using these endpoints
1. "games" for Game - load in games from 2022-present 
2. "games/statistics/players" for PlayerGame - using the games we have, get players and their performances, we'll have to validate whether the player is in the database before adding their PlayerGame



##############################################################################

Setting up a development environment
1. Create your virtual environment in the ffa_flask_app folder (cd ffa_flask_app, python3 -m venv venv)
2. Activate the virtual environment (source venv/bin/activate)
3. Install the required packages (pip3 install -r requirements.txt) 
4. Make sure the URL in the app/config.py file is your local database (postgresql://username:password@localhost:5432/database)
5. Connect to your local postgres database (flask db init, flask db migrate, flask db upgrade).
    a. You can add a message, similar to a git commit, when you call flask db migrate, by adding a -m flag, and writing your message in    quotations
        ex. flask db migrate -m "changed player model to include ..."
6. Start the backend development server (make sure you're in the ffa_flask_app dir, python3 run.py)
7. Make sure npm is up to date, navigate to the frontend folder and install npm
8. Run "npm run serve" to start the development frontend server

Wiping the dev database
1. DELETE FROM table_name; 
    Be careful using this, as you can't have any foreign key dependencies


