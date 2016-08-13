from clarifai.client import ClarifaiApi
from flask import Flask
from flask import render_template
from flask import redirect
from flask import send_from_directory
import os

clarifai_api = ClarifaiApi()

users = os.listdir('./users')
print users

def get_data(user):
    tags_dict = {}
    path = 'users/' + user + '/Photos'
    photo_names = os.listdir(path)
    tags_array = []
    for filename in photo_names:
        tags_array.append(get_tags(path + '/' + filename))
    for array in tags_array:
        for item in array:
            try:
                tags_dict[item] += 1
            except KeyError:
                tags_dict[item] = 1
    ordered_tags = sorted(tags_dict, key=lambda i: int(tags_dict[i]))
    ordered_tags = filter_tags(ordered_tags)
    return ordered_tags

def get_tags(image_path):
    result = clarifai_api.tag_images(open(image_path,'rb'))
    return result['results'][0]['result']['tag']['classes']

def check_compat(a1,a2):
    if(len(set(a1).intersection(a2)) > 5):
        return set(a1).intersection(a2)
    else:
         return False

def filter_tags(tags_array):
    bad_terms = ['man','woman','data','people','boy','girl','facial expression','two','one','backlit','color','outfit']
    for term in bad_terms:
        try:
            tags_array.remove(term)
        except ValueError:
            pass
    return tags_array[-20:]

def find_matches(username):
    global users
    temp_users = users[:]
    temp_users.remove(username)
    matches = []
    match_sets = []
    d1 = get_data(username)
    for name in temp_users:
        d2 = get_data(name)
        set1 = check_compat(d1,d2)
        if type(set1) is set:
            matches.append(name)
            match_sets.append(set1)
    return [matches,match_sets]


app = Flask(__name__)

@app.route('/')
def greeting():
     return render_template('index.html')

@app.route('/<user>')
def show_matches(user):
     matches = find_matches(user)
     return render_template('matches.html',matches=matches,name=user)

@app.route('/<user>/<match>')
def show_match(user,match):
     matches = find_matches(user)
     match_index = 0;
     for i in range(len(matches[0])):
         dude = match[0][i]
         if(dude == match):
             match_index = i
     return render_template('match.html',match=matches[0][match_index],name=user,common=matches[1][match_index])

@app.route('/users/<user>/Photos/<photo>')
def send_pic(user,photo):
    return send_from_directory('users',user+'/Photos/'+photo)

if __name__ == "__main__":
    app.run()
