from dotenv import load_dotenv
import os
import requests
import json
import base64
import sqlite3

class SpotifyAPI():

    def __init__(self) -> None:
        
        load_dotenv()
        self.CLIENT_ID = os.getenv("CLIENT_ID")
        self.CLIENT_SECRET = os.getenv("CLIENT_SECRET")

        self.con = sqlite3.connect("spotifyDB.db")
        self.cur = self.con.cursor()

    def set_tokens(self, access_token, refresh_token):

        self.access_token=access_token
        self.refresh_token=refresh_token

    def get_auth_header(self, access_token):

        return {"Authorization":"Bearer "+access_token}

    def get_tokens(self):

        return self.access_token, self.refresh_token

    def get_token(self):

        auth_string = self.CLIENT_ID + ":" + self.CLIENT_SECRET
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

        return auth_base64
    
    def login(self, code):

        self.auth_base64 = self.get_token()

        url = "https://accounts.spotify.com/api/token"

        headers = {
        
            "Authorization": "Basic "+self.auth_base64,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {"code":code, "redirect_uri":"https://spotify.ahmetfurkandemir.com/login/code", "grant_type": "authorization_code"}

        result = requests.post(url, headers=headers, data=data)
        result_json = json.loads(result.content)

        self.access_token = result_json["access_token"]
        self.refresh_token = result_json["refresh_token"]

        return self.access_token, self.refresh_token

    def refresh_token_func(self):

        self.auth_base64 = self.get_token()

        url = "https://accounts.spotify.com/api/token"

        headers = {
        
            "Authorization": "Basic "+self.auth_base64,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {"refresh_token":self.refresh_token, "grant_type": "refresh_token"}

        result = requests.post(url, headers=headers, data=data)
        result_json = json.loads(result.content) 

        self.update_access_token(result_json["access_token"])
    
    def update_access_token(self, new_access_token):

        self.new_access_token = new_access_token
        
        sql = '''UPDATE SpotfiyUser
              SET spotify_access_token = ?
              WHERE spotify_refresh_token = ?'''

        self.cur.execute(sql, (new_access_token, self.refresh_token))
        self.con.commit()

    def me(self):

        url = "https://api.spotify.com/v1/me"
        result = requests.get(url, headers=self.get_auth_header(self.access_token))

        if result.status_code==401:

            access_token = self.refresh_token_func()
            self.update_access_token(access_token)

            return self.me()

        try:
            json_result = json.loads(result.content)
        except:
            return False, ""
        return True, json_result
    
    def currently_playing(self):

        url = "https://api.spotify.com/v1/me/player/currently-playing"
        result = requests.get(url, headers=self.get_auth_header(self.access_token))

        if result.status_code==401:

            access_token = self.refresh_token_func()
            return self.currently_playing()
        
        try:

            json_result = json.loads(result.content)

        except:

            return False

        return json_result

    def playlists(self):

        url = "https://api.spotify.com/v1/me/playlists"
        result = requests.get(url, headers=self.get_auth_header(self.access_token))

        if result.status_code==401:

            access_token = self.refresh_token_func()
            return self.playlists()
        
        json_result = json.loads(result.content)

        return json_result
    