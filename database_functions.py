import pandas as pd
import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    #cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='images'")
    cur.execute('''CREATE TABLE if not exists Images 
    (filename TEXT, localpath TEXT, id TEXT, media_key TEXT, type TEXT, tweet_url TEXT, image_url TEXT)''')
    cur.execute('''CREATE TABLE if not exists Newest 
    (username TEXT, user_id TEXT, like TEXT, tweet TEXT)''')
    conn.commit()
    cur.close()
    conn.close()

def add_username(username, user_id, like, tweet):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    insert_query = '''INSERT INTO Newest
        (username, user_id, like, tweet) 
        VALUES (?, ?, ?, ?);'''
    data_tuple = (username, user_id, like, tweet)
    cur.execute(insert_query, data_tuple)
    conn.commit()
    cur.close()
    conn.close()

def lookup_newest(username):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT like, tweet FROM Newest where username=?", (username,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return(data)

def update_newest(username, idtype, t_id):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    if(idtype == 'like'):
        update_query = '''UPDATE Newest SET like = ? WHERE username = ?'''
    elif(idtype == 'tweet'):
        update_query = '''UPDATE Newest SET tweet = ? WHERE username = ?'''
    data_tuple = (t_id, username)
    cur.execute(update_query, data_tuple)
    conn.commit()
    cur.close()
    conn.close()

def delete_newest(username):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("DELETE from Newest where username=?", (username,))
    conn.commit()
    cur.close()
    conn.close()

def add_to_db(filename, localpath, t_id, media_key, m_type, t_url, i_url):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    insert_query = '''INSERT INTO Images
        (filename, localpath, id, media_key, type, tweet_url, image_url) 
        VALUES (?, ?, ?, ?, ?, ?, ?);'''
    data_tuple = (filename, localpath, t_id, media_key, m_type, t_url, i_url)
    cur.execute(insert_query, data_tuple)
    conn.commit()
    cur.close()
    conn.close()

def update_db(t_id, t_url, media_key):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    update_query = '''UPDATE Images SET id = ?, tweet_url = ? WHERE media_key = ?'''
    data_tuple = (t_id, t_url, media_key,)
    print(data_tuple)
    cur.execute(update_query, data_tuple)
    conn.commit()
    cur.close()
    conn.close()

def check_media_key(media_key):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT media_key FROM Images where media_key=?", (media_key,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return(data)

def display_table():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    print(pd.read_sql_query("SELECT * FROM Images", conn))
    cur.close()
    conn.close()
