import json
import requests
from flask import jsonify,json
from config import CONFIG
from Server.user import create



def usermusic(username, music):
    new_data={"username":username, "music":music}
    print(new_data)
    response=requests.post("http://127.0.0.1:8080/userdata",json=new_data)
    if response.status_code == 201:  
        print("USER MUSIC UPDATED:","#"*80)
        return 200
    print("USER MUSIC NOT UPDATED:","#"*80)
    return 0





# --- General function definitions ---
def add_user(username, password):
    new_user = {
        "username": str(username),
        "password": str(password),
    }
    
    print(new_user)
    # Assuming the user object is properly formatted and ready to be sent
    response = requests.post("http://127.0.0.1:8080/signup", json=new_user)
    if response.status_code == 201:  
        print("USER CREATED:","#"*80)
        return 200
    print("USER NOT CREATED:","#"*80)
    return 0

def login(username, password):
   
    user={"username":username, "password":password}
    response = requests.post(f"http://127.0.0.1:8080/login", json=user)
    if response.status_code==200:
        return 200
    return 401


def friends_music(username):
   
    user={"username":username}
    response = requests.get(f"http://127.0.0.1:8080/friends_music", json=user)
    if response.status_code==200:
        music=response.json()
        return [music,200]
    return 401

def store_music(current_user,data):
   
    user={"username":current_user,"data":data}
    print(user)
    response = requests.post(f"http://127.0.0.1:8080/store_music", json=user)
    if response.status_code==200:
        music=response.json()
        return 200
    return 401
   
   
def send_friend_request(sender_username,receive_username):
    data={"sender_username":sender_username, "receive_username":receive_username}
    print(data)
    results = requests.post( f"http://127.0.0.1:8080/spotify/send_friend_request",json=data)
    print(results.status_code)# si va bien es 200 o 201? o 204
    if results.status_code == 200:
        return 200
    return 400

def update_friends(current_user,accepted_friends, denied_friends):
   
    user={"current_user": current_user, "accepted_friends":accepted_friends, "denied_friends":denied_friends}
    print(user)
    response = requests.post(f"http://127.0.0.1:8080/update_friends", json=user)
    if response.status_code==200:
        return 200
    return 401

def get_user_friends(username):
    # Assuming your API endpoint for getting user friends is /api/user/{username}/friends
    url = f"http://127.0.0.1:8080/get_friends"
    data = {
        "username": username}
    try:
        # Sending a GET request to fetch the user's friends
        response = requests.get(url, json=data)
        # Checking if the request was successful (status code 200)
        if response.status_code == 200:
            # Returning the JSON response
            friends=response.json()
            return friends, 200
        else:
            # If the request was unsuccessful, print the error message
            print(f"Error: Unable to fetch friends for user {username}. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        # Catching any exceptions that may occur during the request
        print(f"Error: {e}")
        return None

def get_user_friends_requests(username):
    
    url = f"http://127.0.0.1:8080/get_friends_requests"
    data = {"username": username}
    try:
        # Sending a GET request to fetch the user's friends
        response = requests.get(url, json=data)  # Use json=data instead of username=username
        # Checking if the request was successful (status code 200)
        friends_requests = response.json()
        if response.status_code == 200:
            # Returning the JSON response
            return [friends_requests, 200]
        elif friends_requests=="you have no friends":
            return [f"you have no friends",{response.status_code}]
        else:
            # Handle other status codes
            return [f"Error: {response.status_code}", response.status_code]
    except Exception as e:
        # Handle exceptions
        return [f"Error: {e}", 500]





