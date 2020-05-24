Irene Liu  
irliu@chapman.edu  
2313260  
CPSC 408  
Final Project - Batch Report  

**Slideshow and Report are in the Deliverables folder**

#### To Run
1. Setup a new virtual environment, or have the packages in requirements.txt installed  
  * you can use: `pip install -r requirements.txt`
2. In run.py, change the connection string to point to your MySql database   
`app.config['SQLALCHEMY_DATABASE_URI'] = 'YOUR DATABASE'`
3. Run the Python shell and execute the following commands to create the tables  
`From run import db`   
`db.create_all()`  
4. Launch the web server with `python run.py`

#### References
[Column Names](https://stackoverflow.com/questions/6455560/how-to-get-column-names-from-sqlalchemy-result-declarative-syntax)  
[Export as CSV Dynamically](https://stackoverflow.com/questions/28011341/create-and-download-a-csv-file-from-a-flask-view?lq=1)  
[Flask Tutorial by Corey Schafer](https://www.youtube.com/playlist?list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH)  
[Flask Tutorial from CodeLoop.org](https://codeloop.org/flask-crud-application-with-sqlalchemy/)  
