[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/AHFn7Vbn)
# Superjoin Hiring Assignment

### Welcome to Superjoin's hiring assignment! 🚀

### Objective
Build a solution that enables real-time synchronization of data between a Google Sheet and a specified database (e.g., MySQL, PostgreSQL). The solution should detect changes in the Google Sheet and update the database accordingly, and vice versa.

### Problem Statement
Many businesses use Google Sheets for collaborative data management and databases for more robust and scalable data storage. However, keeping the data synchronised between Google Sheets and databases is often a manual and error-prone process. Your task is to develop a solution that automates this synchronisation, ensuring that changes in one are reflected in the other in real-time.

### Requirements:
1. Real-time Synchronisation
  - Implement a system that detects changes in Google Sheets and updates the database accordingly.
   - Similarly, detect changes in the database and update the Google Sheet.
  2.	CRUD Operations
   - Ensure the system supports Create, Read, Update, and Delete operations for both Google Sheets and the database.
   - Maintain data consistency across both platforms.
   
### Optional Challenges (This is not mandatory):
1. Conflict Handling
- Develop a strategy to handle conflicts that may arise when changes are made simultaneously in both Google Sheets and the database.
- Provide options for conflict resolution (e.g., last write wins, user-defined rules).
    
2. Scalability: 	
- Ensure the solution can handle large datasets and high-frequency updates without performance degradation.
- Optimize for scalability and efficiency.

## Submission ⏰
The timeline for this submission is: **Next 2 days**

Some things you might want to take care of:
- Make use of git and commit your steps!
- Use good coding practices.
- Write beautiful and readable code. Well-written code is nothing less than a work of art.
- Use semantic variable naming.
- Your code should be organized well in files and folders which is easy to figure out.
- If there is something happening in your code that is not very intuitive, add some comments.
- Add to this README at the bottom explaining your approach (brownie points 😋)
- Use ChatGPT4o/o1/Github Co-pilot, anything that accelerates how you work 💪🏽. 

Make sure you finish the assignment a little earlier than this so you have time to make any final changes.

Once you're done, make sure you **record a video** showing your project working. The video should **NOT** be longer than 120 seconds. While you record the video, tell us about your biggest blocker, and how you overcame it! Don't be shy, talk us through, we'd love that.

We have a checklist at the bottom of this README file, which you should update as your progress with your assignment. It will help us evaluate your project.

- [ ] My code's working just fine! 🥳
- [ ] I have recorded a video showing it working and embedded it in the README ▶️
- [ ] I have tested all the normal working cases 😎
- [ ] I have even solved some edge cases (brownie points) 💪
- [ ] I added my very planned-out approach to the problem at the end of this README 📜

## Got Questions❓
Feel free to check the discussions tab, you might get some help there. Check out that tab before reaching out to us. Also, did you know, the internet is a great place to explore? 😛

We're available at techhiring@superjoin.ai for all queries. 

All the best ✨.

## Developer's Section
Hello!
Sorry the video exceeds the time limit mentioned xD
https://drive.google.com/file/d/1-nMFedXzjPFLEygImIgRlYw0IPLludV8/view?usp=sharing

So here's my approach to Synchronizing Google Sheets with MySQL Database


Authentication and Setup:

I used the Google Sheets API for accessing and modifying data in Google Sheets. I set up OAuth 2.0 credentials using credentials.json and token.json files for authentication.
For database access, I connected to a MySQL database using Python’s mysql.connector.

Data Retrieval:

Google Sheets: I fetch data from a defined range in Google Sheets using the API. If the sheet is empty, I handle that by checking if any data exists in the MySQL database and then copying the database contents into Google Sheets.
MySQL: I query all candidate records from the MySQL table for comparison with Google Sheets data.

Efficient Sync Using "Last Updated":

I focused on efficiency by ensuring that only records that were changed or updated are scanned and synchronized, rather than processing the entire dataset. This was achieved by introducing a "Last Updated" timestamp column in both Google Sheets and MySQL.
The "Last Updated" timestamp helps identify records that have been modified since the last sync. I only synchronize entries where the timestamp indicates recent changes, significantly reducing the amount of data processed.

Synchronizing Columns:

I ensure both systems have a "Last Updated" column to track data changes. If this column is missing in Google Sheets, I add it and initialize timestamps where necessary.
I map the column names from Google Sheets to the corresponding columns in MySQL to ensure a smooth data flow.

Conflict Handling:

I use the "Last Updated" timestamp to detect changes and resolve conflicts. When data is modified in either Google Sheets or the MySQL database, I check the timestamps and update the newer entries in the opposite system.
If new columns or fields appear in Google Sheets, I dynamically add those columns to the MySQL database to maintain consistency.

Data Updates:

I update Google Sheets with any changes from the MySQL database and vice versa. The approach ensures that new data is synchronized in both directions.
I used sheet.values().update() for updating Google Sheets data and appropriate SQL INSERT or UPDATE commands for modifying the database records.

CRUD Operations:

I implemented full CRUD operations for managing records, allowing users to create, read, update, and delete entries either in MySQL, with changes reflected in both systems.
I ask the user whether they want to add new records or modify existing data at each sync cycle.

Automation and Looping:

I set up the synchronization process to run in a loop at fixed intervals (every 10 seconds), ensuring real-time updates between Google Sheets and MySQL.
I used Python's time.sleep() function to control the interval between sync cycles.

Error Handling and Logging:

I implemented logging to track synchronization issues, such as unknown columns and missing data. This helps me debug and ensure smooth operation.

Summary
Using Google Sheets API and MySQL, I’ve set up a two-way synchronization process that handles CRUD operations, conflict resolution based on timestamps, and ensures complete data integrity between both systems. This method allows me to maintain consistent and up-to-date records in real time.