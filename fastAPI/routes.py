from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from spotifyAPI.spotifyAPI import SpotifyAPI
from fastapi.responses import RedirectResponse
from starlette.responses import Response, HTMLResponse
import sqlite3
import secrets
from fastapi.templating import Jinja2Templates
from fastapi import Request

routes = APIRouter()
templates = Jinja2Templates(directory="fastAPI/static/templates")

def get_spotify_tokens(user_token):

    con = sqlite3.connect("spotifyDB.db")
    cur = con.cursor()

    cur.execute(
                'SELECT spotify_access_token, spotify_refresh_token FROM SpotfiyUser WHERE user_token=?', (user_token,))
    tokens = cur.fetchone()

    return tokens

def get_auth_header(token):

    return {"Authorization":"Bearer "+token}

@routes.get("/", tags=["Spotify"])
def login(request: Request):
    
    #return RedirectResponse("https://accounts.spotify.com/authorize?response_type=code&client_id=ee43edcd46554af686d5918497df08f5&scope=user-read-currently-playing&redirect_uri=http://127.0.0.1:8000/login/code")
    with open("fastAPI/static/templates/index.html", "r") as f:
        return templates.TemplateResponse("index.html", {"request": request})

@routes.get("/user/{user_token}", tags=["Spotify"])
def user(user_token:str, request: Request):

    tokens = get_spotify_tokens(user_token)

    user = SpotifyAPI()
    user.set_tokens(tokens[0], tokens[1])

    current_music = user.currently_playing()

    flag = None
    music_id=""
    if current_music==False:
        flag = False

    else:
        music_id = current_music["item"]["id"]

    me = user.me()
    me = me[1]

    playlists = user.playlists()

    lenn = len(playlists["items"])

    if flag!=False:
        return templates.TemplateResponse("me.html", {"request": request, "user_token":user_token, "music_id":music_id, "me":me, "playlists":playlists, "lenn":lenn})

    else:

        return templates.TemplateResponse("inactive.html", {"request": request, "user_token":user_token, "music_id":"dsds", "me":me, "playlists":playlists, "lenn":lenn})

@routes.get("/login/code", tags=["Spotify"])
async def loginSpotify(code:str, response: Response):
      
    user = SpotifyAPI()
    access_token, refresh_token = user.login(code)

    response = user.me()
    if response[0]==False:
        return "Spotify Development Mode also allows up to 25 users."

    spotify_user_id = response[1]["id"]

    con = sqlite3.connect("spotifyDB.db")
    cur = con.cursor()

    cur.execute(
                'SELECT user_token FROM SpotfiyUser WHERE spotify_user_id=?', (spotify_user_id,))
    user_token = cur.fetchone()

    if user_token!=None:

        return RedirectResponse("/user/{}".format(user_token[0]))
    
    user_token = str(secrets.token_urlsafe(32))

    sql = '''INSERT INTO SpotfiyUser(user_token, spotify_access_token, spotify_refresh_token, spotify_user_id)
              VALUES(?,?,?,?)'''

    cur.execute(sql, (user_token, access_token, refresh_token, spotify_user_id))
    con.commit()

    return RedirectResponse("/user/{}".format(user_token))