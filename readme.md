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
    Use team_id and season to get a season's worth of games
2. "games/statistics/players" for PlayerGame - using the games we have, get players and their performances, we'll have to validate whether the player is in the database before adding their PlayerGame

We'll cruise along with importing player game statistics for the past 3 seasons, while working in tandem on the prediction/ML aspect of player performance. There should be no more roadblocks importing player statistics for more recent games, so we should be able to import the remaining ~550 games over the next week.

One problem that will arise with the PlayerTeam table is if we decide to import games from before 2021, as the PlayerTeam object specifies a start date which we assume is the earliest game in the database. Importing earlier games will cause duplicate PlayerTeam objects based on different starting dates or errors that will need to be handled. This is just the dev environment for a reason though - we'll cross that bridge when we get to it.

Otherwise, we just need to do some research on what should be the features of our prediction model, test them, and refine them until a somewhat accurate, cohesive model is created. 

So for predictions, we have a couple problems:
1. Filter out inconsequential performances (from backups, players who don't get much attention/playing time, etc.)
2. Predict based on the specified player's past performances AND players who have played against the specified team IN COMPARISON TO their performances -- this will mean if we're looking at Breece Hall vs. LAR, look at Breece Hall's past performances. ALSO, look at (for ex.) James Conner's performance vs. LAR compared to his other past performances to make a prediction.

I'm not sure how this will take shape, but it's a lot more complicated than feeding a bunch of data into a RandomForest

Also, the way we create player_team objects is incorrect at the moment. We're going to have to go through all of each player's PlayerGames to see if they change teams, and create a new player_team object when that happens. For now, let's get all the player performances and we can write a script to make that fix afterwards. After that, we can import new games that we don't have, import player performances, and continue on with prediction.

For now, let's keep it simple. Predict a player's performance by...
1) Looking at their past performances
2) Looking at how other players have performed against the current player's opponent

What's the best way to do all of this?




So I think we found a good way to do it. 

Basically the issue right now is that our initial vision doesn't match up with how the models are being trained. Right now, models are being trained on isolated positional performances -- i.e. the RB1 performances for all the games in the database are being fed into the model for training and testing. However, what we should be looking to do is train the models on three "tuples"
1. The RB1's performance that game (what we have now)
2. What's in the first "tuple" of the combined features df right now -- the player's averages from the past 8 games
3. What's in the second "tuple" of the combined features df right now -- the averages from the 8 past games against the same position

THAT will make for a banging prediction model. Input is #2, #3, output is #1. Train it, test it, then we can SAVE that model. There will be a RB model, trained on ALL of the data in the database, and all you need to do to predict a player's performance is...

1. Get the player's past 8 games of performance
2. Get the opponent's past 8 games performance against that same position
3. Feed them to the model and you get predictions for ALL the relevant stats, and they should be damn good

We need alignment between what the model is trained on and what the model is given for predictions. I really like the idea of feeding a model a chosen player's past 8 game averages and that player's opponent's average last 8 performances against the chosen player's position, so the prediction would be the player's performance for that game, for every relevant statistic. The only way I see that working with the current code we have is to modify the load_historical_data function so that we get those three bundles of data, train the models on that data, so that predictions are as easy as feeding the model the two 8 game averages specified.

Keep load_historical_data as is, but then create two new dataframes with the result of that function. After we do that, we have to line those three dataframes up correctly, which I think will be the toughest task.

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


