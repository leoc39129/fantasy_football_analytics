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
Next time: Start with... 

Great resource at https://sportsdata.io/developers/api-documentation/nfl
    a. Some endpoints that could definitely be used: Standings, Player Profiles - by Team, Team Profiles - by Season, Week - Last Completed, Week - Upcoming, LOOK MORE 

Set up the bulk import for past season and active season, weekly import and update for what happened in the past week

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


