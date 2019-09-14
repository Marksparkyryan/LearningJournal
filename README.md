# LearningJournal

Learning Journal is a simple app that stores journal entries describing learning moments. Entries have a title, some content describing what was learned, a date, and the amount of hours spent on learning. Entries also have the ability to parse and store and display bulleted resources as titles (as plain text) and hyperlinks (optionally). Entries can be filtered on the home page by any hashtags saved with entries.


<br/>

# installation

1. cd into your directory of projects (or wherever you prefer to keep your clones)
2. git clone ```https://github.com/Marksparkyryan/LearningJournal.git``` to clone the app
3. ```virtualenv .venv``` to create your virtual environment
4. ```source .venv/bin/activate``` to activate the virtual environment
5. ```pip install -r LearningJournal/requirements.txt``` to install app requirements
6. cd into the LearningJournal directory
7. ```python app.py``` to run the app!


<br/>

# usage

By default, DEBUG mode is set to True in app.py. This is good for testing but not good for deployment. If deploying, make sure
DEBUG is set to False.

If deploying, the secret key should be replaced in app.py - ideally inside an environment variable.

By default, DUMMYDATA mode is set to True in app.py. DUMMYDATA populates the database with generic admin user (email=janedoe@email.com, password=password), entry, resource, and tag data. To prevent this, set DUMMYDATA to False.

<br/>

# screenshots

<img width="2046" alt="Screen Shot 2019-09-09 at 4 58 24 PM" src="https://user-images.githubusercontent.com/45185244/64566074-1c158800-d323-11e9-8c30-a0888336432f.png">

<br/>

<img width="2048" alt="Screen Shot 2019-09-09 at 4 59 33 PM" src="https://user-images.githubusercontent.com/45185244/64566131-3c454700-d323-11e9-9d82-7abaa6971da4.png">

<br/>

<img width="1586" alt="Screen Shot 2019-09-09 at 5 01 19 PM" src="https://user-images.githubusercontent.com/45185244/64566222-76aee400-d323-11e9-9e81-aac4f45b1fa2.png">

<br/>

<img width="2047" alt="Screen Shot 2019-09-09 at 5 02 30 PM" src="https://user-images.githubusercontent.com/45185244/64566295-a52cbf00-d323-11e9-9989-87f55a74887f.png">

<br/>

<img width="2047" alt="Screen Shot 2019-09-09 at 5 03 15 PM" src="https://user-images.githubusercontent.com/45185244/64566395-e58c3d00-d323-11e9-9375-afe1c1745602.png">

<br/>


# credits

Treehouse Techdegree Project 5
