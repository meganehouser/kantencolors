# coding: utf-8

from flask import (Flask,
                   request,
                   render_template,
                   url_for,
                   session,
                   redirect,
                   flash,
                   Response)
import json
from io import BytesIO
import tweepy
import kanten

DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_pyfile('settings.cfg')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/tweet', methods=['POST'])
def tweet():
    session['request_data'] = request.form['data']
    session['status'] = request.form['status']

    oauth_callback = url_for('authorized', _external=True)
    auth = tweepy.OAuthHandler(app.config['TW_KEY'], app.config['TW_SECRET'], oauth_callback)
    auth_url = auth.get_authorization_url()
    auth_url = auth_url.replace('authorize', 'authenticate')
    session['request_token'] = auth.request_token

    return redirect(auth_url)


@app.route('/twitter/authorized')
def authorized():
    data = session['request_data']
    del session['request_data']
    tw_status = session['status']
    del session['status']
    token = session['request_token']
    del session['request_token']

    auth = tweepy.OAuthHandler(app.config['TW_KEY'], app.config['TW_SECRET'])
    gif_image = kanten.imagefy(json.loads(data))

    auth.request_token = token
    verifier = request.values.get('oauth_verifier', '')

    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError as e:
        flash('There was a problem logging into Twitter: ' + str(e))
        return redirect(url_for('index'))

    try:
        api = tweepy.API(auth)
        resp = api.media_upload('kanten1.gif', file=BytesIO(gif_image))

        media_id = resp.media_id_string
        resp = api.update_status(media_ids=[media_id], status=tw_status)
    except tweepy.TweepError as e:
        flash('There was a problem tweeting into Twitter: ' + str(e))
        return redirect(url_for('index'))

    flash('Your colors have been tweeted !')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
