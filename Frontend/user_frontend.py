from flask import Flask, render_template, request, redirect, session,session
import hashlib
import requests,random,string
from config import CONFIG
from user_api_shim import add_user, send_friend_request,login,get_user_friends_requests,update_friends,store_music,friends_music
import base64,secrets
app = Flask(__name__)
access_token=""
original_state=""
app.secret_key = 'your_secret_key_here'
spotifylogin=False
# Define your client ID and redirect URI
CLIENT_ID = "5f0954c701964757b6e0c7035645ac09"
REDIRECT_URI = "https://f85ec9ee86b9.ngrok.app"
 


@app.route("/home", methods=["GET","POST"])
def decision():
    if request.method=="GET":
        return render_template("home.html")

#polish system, db for friends
#unitesting

@app.route("/login", methods=["GET"])
def loginGET():
    # Render the login page
    return render_template("login.html")



@app.route("/signup", methods=["GET"])
def signup():
    return render_template("signup.html")
    


current_user=""

@app.route("/login", methods=["POST"])
def loginPOST():
    global current_user
    try:
        username = request.form["username"]
        password = request.form["password"]
        
        if login(username,password)==200:
        
            current_user=username
            print("#"*80)
            return redirect("/spotify")
        else:
            return redirect("/login")
    except Exception as e:
        print("An error occurred:", e)
        return redirect("/login")
    

@app.route("/signup", methods=["POST"])
def signupPost():
    user={}
    user["username"] = request.form["username"]
    user["password"]= request.form["password"]

    accepted_user=add_user(user["username"],user["password"])
    if accepted_user==200:
        return redirect("login") 
    return render_template("signup.html")

#esto es lo q tienes q mirar despues de lo de ngrok
@app.route("/spotify/friends_music", methods=["GET"])
def spoti():
    global current_user
    if request.method=="GET":
        music=friends_music(current_user)
        print(music)
        if music==401:
            return redirect("/spotify")
        return f"{music}"

@app.route("/spotify/send_friends_requests", methods=["GET", "POST"])
def spotifyy():
    global current_user
    if request.method == "GET":
        return render_template("finder.html", user=current_user)

    if request.method == "POST":
        receive_username = request.form.get('query')
        print(receive_username)
        if receive_username:
            friend_request = send_friend_request(current_user, receive_username)
            if friend_request == 200:
                return render_template("finder.html", user=current_user, message="Friend request sent successfully!")
            return render_template("finder.html", user=current_user, message="Failed to send friend request.")
        return render_template("finder.html", user=current_user, message="Please enter a username.")

@app.route("/spotify/manages_friends_requests", methods=["GET","POST"])
def friendsrequests():
    global current_user
    
    if request.method == "GET":
        
        friends_request = get_user_friends_requests(current_user)
        print(friends_request)
        friends = friends_request[0]
        response_code = friends_request[1]
        
        
        
        if friends=="you have no friends.":
            return f"you have no friends requests."
        
        elif response_code == 200:
            friends=friends["friends"]
            return render_template("manage_friends.html",friends=friends)
        return f"there was a problem gatherin your data"
    
    if request.method == "POST":
        accepted_friends = []
        denied_friends = []

        # Parse the form data
        form_data = request.form.to_dict()

        # Get the current friend's request
        friends_request = get_user_friends_requests(current_user)
        all_friends = set(friends_request[0]["friends"])
        
        for key, value in form_data.items():
            friend_name = key.split('_', 1)[1]  # Remove 'friend_' prefix
            if value == "accept":
                accepted_friends.append(friend_name)
            elif value == "deny":
                denied_friends.append(friend_name)
        friends_request=[]
        for name in all_friends:
            friends_request.append(name)
        print(current_user,accepted_friends,friends_request,"finalllllllll")
        update_friends(current_user,accepted_friends,friends_request)
        return redirect("/spotify/manages_friends_requests")

def generate_code_verifier(length=64):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

def generate_code_challenge(verifier):
    hashed = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(hashed).rstrip(b'=').decode()

def generate_random_state(length=32):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


@app.route("/spotifylogin", methods=["GET"])
def spotifylogin():
    global original_state, original_code_verifier
    if request.method == "GET":
        original_code_verifier = generate_code_verifier()
        code_challenge = generate_code_challenge(original_code_verifier)
        session['original_code_verifier'] = original_code_verifier
        original_state = generate_random_state()
        session['original_state'] = original_state
        REDIRECT_URI = "https://f85ec9ee86b9.ngrok.app"
        AUTH_URL = f"https://accounts.spotify.com/en/authorize?scope=user-top-read%20playlist-modify-public%20playlist-modify-private%20user-read-private%20user-read-recently-played&response_type=code&flow_ctx=39ce6189-6581-4e80-a021-385f32369c14%3A1714167272&state={original_state}&redirect_uri={REDIRECT_URI}&client_id=5f0954c701964757b6e0c7035645ac09&show_dialog=true&code_challenge={code_challenge}&code_challenge_method=S256"
        return redirect(AUTH_URL)
music=""
def user_token(access_token):
    global music
    if not access_token:
        return "Access token not found", 400
    headers = {"Authorization": f"Bearer {access_token}"}
    profile_url = "https://api.spotify.com/v1/me/top/tracks"
    response = requests.get(profile_url, headers=headers)
    if response.status_code == 200:
        music = response.json()
        music = {'items': music['items'][:5]}

        session['music'] = music
        return music, 200
    else:
        return "Error fetching user data from Spotify API", response.status_code

@app.route("/", methods=["GET", "POST"])
def callback():
    global original_state, original_code_verifier, access_token, current_user
    state = request.args.get("state")
    if state != original_state:
        return "Invalid state parameter", 400

    code = request.args.get("code")
    if not code:
        return "Authorization code not found", 400

    token_url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "code_verifier": original_code_verifier
    }

    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code == 200:
        access_token = response.json()["access_token"]
        session['access_token'] = access_token
        user_token(access_token)
        return redirect("/spotify")
    else:
        return "Error exchanging authorization code for access token."
    

def get_track_info(music_data):
    track_info = []
    
    for item in music_data['items']:
        track_name = item['name']
        track_artist = item['artists'][0]['name']  # Extracting the artist name
        track_image = item['album']['images'][0]['url']
        track_info.append({'name': track_name, "artist": track_artist, 'image': track_image})
    
    return track_info


def create_html_page(track_info):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Music Tracks</title>
        <style>
            .track {
                margin-bottom: 20px;
                border-bottom: 1px solid #ccc;
                padding-bottom: 20px;
            }
            .track img {
                max-width: 200px;
                max-height: 200px;
            }
        </style>
    </head>
    <body>
        <h1>Music Tracks</h1>
    """

    for track in track_info:
        html_content += f"""
        <div class="track">
            <h2>{track['name']} by {track['artist']}</h2>
            <img src="{track['image']}" alt="{track['name']}">
        </div>
        """

    html_content += """
    </body>
    </html>
    """

    return html_content


@app.route("/spotify/mymusic", methods=["GET"])
def yourmusic():
    global music, current_user
    
    access_token = session.get('access_token')
   
    track_info = get_track_info(music)
    if len(track_info)>=2: 
        html_content = create_html_page(track_info)
        print(current_user)
        store_music(current_user,track_info)
        
        return html_content
    return f"There was a problem gathering your music"

@app.route("/spotify", methods=["GET", "POST"])
def spotify():
    global current_user, access_token
    if request.method == "GET":
        if not access_token:
            return render_template("profile.html", username=current_user, signin=True)
        return redirect("/spotify/mymusic")


if __name__ == "__main__":
    app.run(port=80, debug=True)