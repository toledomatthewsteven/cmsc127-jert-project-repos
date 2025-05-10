# INSTALL mysql ('s connector)
# pip install mysql-connector-python
# py -m pip install mysql-connector-python
# ^^^ runthis in ur terminal or idk where maybe in the folder ure running this...

#############################################
# https://www.youtube.com/watch?v=oDR7k66x-AU 
# file steven used to learn basics of python and sql eme eme
# putting this in the repo in case it can help? idk. this is small scale rn
# but it does actually modify the sql/mariadb databases in ur laptop
#############################################

import mysql.connector as mariadb

mariadb_connection = mariadb.connect(user="root", password="password" ,host = "localhost", port = "3306")
# mariadb_connection = mariadb.connect(user="root", password="password", database = 'test_database', host = "localhost", port = "3306")
#should our project just use the root user LOLLL.... um.... hmm.... 
create_cursor = mariadb_connection.cursor(); 
    # add as a paramter: dictionary = true "if you want get values returned values in a databse in dicitonary format"

# MariaDB [(none)]> SHOW GLOBAL VARIABLES LIKE 'PORT';
# +---------------+-------+
# | Variable_name | Value |
# +---------------+-------+
# | port          | 3306  |
# +---------------+-------+
# 1 row in set (0.027 sec)

create_cursor = mariadb_connection.cursor() ; 



########################################## CREATE DATABASE & TABLES ##########################################
# at this section, there should be no databases = "test_database" or whatever in ur connection

## Show databases

# execute this on its own
# create_cursor.execute("CREATE DATABASE 127projectplaceholder")

# # execute the ff together:
# create_cursor.execute("SHOW DATABASES")

# for x in create_cursor:
#     print(x)
# # up til this

############################################## EXECUTE COMMANDS AGAINST/RELATING TO TABLES####################################
# (at this point there should be a databses = "test_database" in your connection)
##############################################################################################################################

### create tables 
create_cursor.execute("CREATE TABLE python_creation_table (COLUMN1 VARCHAR(2), COLUMN2 Int)")

create_cursor.execute("SHOW TABLES")
for x in create_cursor:
    print(x)

#======

# #use single quotes for the biggest ... quote
# sql_statement = 'INSERT INTO python_creation_table (COLUMN1, COLUMN2) VALUES ("hi", 1), ("h1", 2)'
# create_cursor.execute(sql_statement)
# mariadb_connection.commit(); #not sure if our system is an auto-commit

#insert into table with variables
# sql_statement = 'INSERT INTO python_creation_table (COLUMN1, COLUMN2) VALUES (%s, %s)';
# items_to_insert = ('hi', 4)  #since we know it's just a touple we're inserting into... yeah
# create_cursor.execute(sql_statement, items_to_insert)
# mariadb_connection.commit();
# for now let me try to not commit...

######### SELECT ###########
# sql_statement = 'SELECT * from python_creation_table' # can do LIMIT 15 smth
# create_cursor.execute(sql_statement)
# myresult = create_cursor.fetchall() # fetchone() will only return the first.. one
# print(myresult)

#okk sooo, since we didnt commit, it didnt show up for me! so.... lemme do that real quick.
#can i run multiple segments at once...
# i can !!! (i uncommented both insert into table ,,, and the select)

### use of where clause
# sql_statement = 'SELECT * FROM python_creation_table WHERE COLUMN2 = 4'
# create_cursor.execute(sql_statement)
# myresult = create_cursor.fetchall() 
# print(myresult)

### slightly more complicated sql
# im not copying all that...

## close connection
#when done with everything that you must... 
mariadb_connection.close()