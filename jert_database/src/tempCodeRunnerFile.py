nnection.cursor() #dont forget ()
                    cursor.execute("SHOW TABLES")
                    for x in cursor:
                        print(x)