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
So there are some major issues with some of the endpoints -- the stats are just wrong for the bulk imports, and still a little bit wrong for individual players, but very fixable

For Javonte Williams (playerID: 22558)
https://api.sportsdata.io/v3/nfl/stats/json/PlayerGameStatsBySeason/2024/22558/all?key=eb609e05efa8406fba6c84327f4ff4dc

Rushing attempts, targets, and receptions are not integers -- round them up and they're fine
For rushing/reception yds, once the number gets to >50 yds, often you have to add one yard and round up

Confirming that trend with a few other players/positions...

WR:
Drake London (playerID: 23151)
Receptions and targets just need to be rounded up
Reception yds just need to be rounded up (except one entry -- 152.8 vs. 154)

QB:
Bo Nix (playerID: 25069)
https://api.sportsdata.io/v3/nfl/stats/json/PlayerGameStatsBySeason/2024/25069/all?key=eb609e05efa8406fba6c84327f4ff4dc

These stats don't seem to have any rhyme or reason with them, the passing yards are WAY off, like 100 yards off, interceptions are off, passing TDs and probably attempts/completions are correct

For now, I guess we'll ignore QBs and only worry about WRs and RBs, using this player by player approach to get the most accurate stats

So I got Drake London added as a player and each of his games as a playergame. Do this for the top RBs and WRs, move on to prediction soon
1. Prediction
2. Smoother importing, DB backups
3. Connect Team and Game models to Player and PlayerGame models



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


