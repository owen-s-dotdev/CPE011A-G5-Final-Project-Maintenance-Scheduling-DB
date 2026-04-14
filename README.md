# CPE011A-G5-Final-Project-Maintenance-Scheduling-DB

db_manager.py
MANAGER FOR THE MYSQL LOCALLY HOSTED CONNECTION.

main.py
MAIN GUI COMPONENT OF THE DATABASE. 

Prerequisites:
1. You must have XAMPP MySQL installed on your system
2. In your Python IDE, make sure you have the MySQL Connector Python Driver installed
    For Windows:
    pip install mysql-connector-python

    For Mac/Linux:
    pip3 install mysql-connector-python

Steps to Run:
1. Activate the XAMPP control panel and press start on MariaDB MySQL and Apache
2. Click on "Admin" on the Apache service to open a locally hosted instance of MySQL.
   This will open a new tab in your browser.
3. Click "phpmyadmin" to open the interface of all of your databases. From here on out,
   if downloading maintenance_record.db does not work, then create your own database on the left side.
4. Click the SQL button on the task bar at the top, then paste the MySQL Query to create your
   copy of the database. Click "GO" to proceed.
5. Now, while the MySQL and Apache services are still running, you may now run the main.py file 
   to activate the GUI.
