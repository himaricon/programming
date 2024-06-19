import sqlite3

from flask import jsonify,Flask,request,json


from config import CONFIG

def dict_factory(cursor, row):
    fields = [ column[0] for column in cursor.description ]
    return {key: value for key, value in zip(fields, row)}

def get_db_connection():
    db_conn = sqlite3.connect("../Database/users.db")
    db_conn.row_factory = dict_factory
    return db_conn

def music():
    musicuser=request.json
    print(musicuser)
    conn = sqlite3.connect('../Database/users.db')
    cursor = conn.cursor()

    # Get all users from the database
    cursor.execute("SELECT username FROM musicuser")
    user = cursor.fetchall()
    UPDATE_USER = """
    UPDATE user
    SET username = ?,
        music_data = ?,
    WHERE user = ?
    """
    cursor.execute(UPDATE_USER, (musicuser["username"]),(musicuser["music_data"]))
    conn.commit()

def create():
    user = request.json

    print(user)
    with get_db_connection() as conn:
        cursor = conn.cursor()

        
        

        INSERT_USER = "INSERT INTO user (username, password, friends_requests, music_data) VALUES (?, ?, ?, ?)"
        cursor.execute(INSERT_USER, (str(user["username"]), str(user["password"]), json.dumps(user.get("friends_requests", [])),json.dumps(user.get("music_data", []))))
        conn.commit()
        new_user_id = cursor.lastrowid

    return {"user_id": new_user_id}, 201




def login():
    # Establish a connection to the database
    user=request.json
    conn = sqlite3.connect('../Database/users.db')
    cursor = conn.cursor()

    # Get all users from the database
    cursor.execute("SELECT username, password FROM user")
    users = cursor.fetchall()

    for db_user, db_password in users:
        if user['username'] == db_user and user['password'] == db_password:
            return 200  

    return 401  


def get_friends_requests():
    data = request.json
    print(data)
    username = data.get("username")

    if not username:
        return jsonify({"error": "Username is required"}), 400

    user = read_one(username)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    friends_requests = user.get("friends_requests", [])
    
    if friends_requests==[] or friends_requests=="[]":
        return "you have no friends."
    return jsonify({"friends": friends_requests}), 200

 

def friends_music():
    pass
 

def manage_friend_requests():
    data = request.json
    
    username = data.get("current_user")
    accepted_requests = data.get("accepted_friends", [])
    denied_requests = data.get("denied_friends", [])

    if not username:
        return {"error": "current_user is required"}, 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch current friends_requests
    cursor.execute("SELECT friends_requests FROM user WHERE username = ?", (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return {"error": "User not found"}, 404

    current_friends_requests = json.loads(user["friends_requests"])

    # Update friends_requests: remove denied friends, retain accepted friends
    updated_friends_requests = [req for req in current_friends_requests if req not in denied_requests and req not in accepted_requests]

    # Update the friends_requests field in the user table
    cursor.execute("UPDATE user SET friends_requests = ? WHERE username = ?", (json.dumps(updated_friends_requests), username))
    conn.commit()

    # Update friends table for accepted requests
    for friend in accepted_requests:
        # Add entry for both users to the friends table
        cursor.execute("INSERT INTO friends (user_id, friend_id, status) VALUES ((SELECT user_id FROM user WHERE username = ?), (SELECT user_id FROM user WHERE username = ?), 'accepted')", (username, friend))
        cursor.execute("INSERT INTO friends (user_id, friend_id, status) VALUES ((SELECT user_id FROM user WHERE username = ?), (SELECT user_id FROM user WHERE username = ?), 'accepted')", (friend, username))

    conn.commit()
    conn.close()

    return "Friend requests managed successfully", 200

def read_one(username):
    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
    row = cursor.fetchone()
    db_conn.close()
    if row:
        user = {
            "user_id": row["user_id"],
            "username": row["username"],
            "password": row["password"],
            "friends_requests": json.loads(row["friends_requests"]),
            "music_data": json.loads(row["music_data"]),
        }
        return user  # Return user data if found
    else:
        return None  # Return None if user not found
    
def friends_music():
    data = request.json
    username = data.get("username")
    print(username)
    # Check if the username is provided
    if not username:
        return jsonify({"error": "Username is required"}), 400

    conn = sqlite3.connect(CONFIG["database"]["name"])
    cursor = conn.cursor()

    # Retrieve the user_id of the given username
    cursor.execute("SELECT user_id FROM user WHERE username = ?", (username,))
    user_row = cursor.fetchone()

    if not user_row:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    user_id = user_row["user_id"]

    # Retrieve all friends of the given user
    cursor.execute("SELECT friend_id FROM friends WHERE user_id = ? AND status = 'accepted'", (user_id,))
    friends_rows = cursor.fetchall()

    if not friends_rows:
        conn.close()
        return jsonify({"message": "No friends found"}), 200

    friend_ids = [row["friend_id"] for row in friends_rows]

    # Retrieve music data for each friend
    music_data_list = []
    for friend_id in friend_ids:
        cursor.execute("SELECT music_data FROM user WHERE user_id = ?", (friend_id,))
        friend_music_data = cursor.fetchone()

        if friend_music_data!=[]:
            music_data_list.append(json.loads(friend_music_data["music_data"]))

    conn.close()

    return jsonify({"friends_music": music_data_list}), 200



def store_music():
    data = request.json
    username = data.get("username")
    track_info = data.get("data")
    print(username,track_info)
    if not username or not track_info:
        return {"error": "Username and track_info are required"}, 400

    conn = get_db_connection()
    cursor = conn.cursor()

    

    current_music_data=[]

    # Update music_data
    current_music_data.append(track_info)

    # Save updated music_data back to the database
    cursor.execute("UPDATE user SET music_data = ? WHERE username = ?", (json.dumps(current_music_data), username))
    conn.commit()
    conn.close()

    return "Music data stored successfully", 200





def send_friend_request():
    data = request.json
    sender_username = data.get("sender_username")
    receive_username = data.get("receive_username")

    if not sender_username or not receive_username:
        return jsonify({"error": "Both sender_username and receive_username are required"}), 400

    user = read_one(receive_username)
    print(user)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    
    friends_requests = user["friends_requests"]


    if sender_username in friends_requests:
        return jsonify({"error": "Friend request already sent"}), 400

    friends_requests.append(sender_username)
    print(friends_requests)

    UPDATE_USER = """
    UPDATE user
    SET friends_requests = ?
    WHERE username = ?
    """

    db_conn = get_db_connection()
    cursor = db_conn.cursor()
    cursor.execute(UPDATE_USER, (json.dumps(friends_requests), receive_username))
    db_conn.commit()
    db_conn.close()

    return jsonify({"message": "Friend request sent successfully"}), 204




#guardar musica en db utilizando token y guardando directamente desde q se meta para login en spotfify 
# mirar cli.py para completar opcion d arriba
#utilizar el cli.py para ver como se podria utilizar la opcionn para solo update los friends:requets, friends, music_data, eetc, etc, etc,,e tc
