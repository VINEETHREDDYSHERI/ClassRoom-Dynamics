import pymysql
import socket
import time

host="major-project.csgfvfcvbaj9.ap-south-1.rds.amazonaws.com"
port=3306
dbname="majorProject"
user="admin"
password="admin12345678"
# Open database connection
conn = pymysql.connect(host, user=user,port=port,passwd=password, db=dbname)

# prepare a cursor object using cursor  method
cursor = conn.cursor()

sql = "create table test_table(name varchar(20))"
print(str(cursor.execute(sql)))
#results = cursor.fetchall()
#for row in results:
#    print row[0]

# disconnect from server
conn.close()
