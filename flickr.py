import json
import requests
from config import FLICKR_API_KEY

CACHE_FNAME = 'cache_file.json'
DEBUG = False

def load_cache_json():
    # global CACHE_DICTION
    try:
        cache_file = open(CACHE_FNAME, 'r')
        cache_contents = cache_file.read()
        CACHE_DICTION = json.loads(cache_contents)
        cache_file.close()
    except:
        CACHE_DICTION = {}

    return CACHE_DICTION

def params_unique_combination(baseurl, params_d, private_keys=["api_key"]):
    alphabetized_keys = sorted(params_d.keys())
    res = []
    for k in alphabetized_keys:
        if k not in private_keys:
            res.append("{}-{}".format(k, params_d[k]))
    return baseurl + "_".join(res)

def search_flickr(method=None, photo_id=None, tags=None, ppg=None):
    '''Input either "PhotosSearch" or "getInfo" as your method'''
    if not FLICKR_API_KEY:
        raise Exception('Flickr API Key is missing!')

    if method == "PhotosSearch":
        baseurl = "https://api.flickr.com/services/rest/"
        params_diction = {
            "method": "flickr.photos.search",
            "format": "json",
            "api_key": FLICKR_API_KEY,
            "tags": tags,
            "per_page": ppg,
            "nojsoncallback": 1
        }
    elif method == "getInfo":
        baseurl = "https://api.flickr.com/services/rest/"
        params_diction = {
        "method": "flickr.photos.getInfo", 
        "format": "json",
        "api_key": FLICKR_API_KEY,
        "photo_id": photo_id
        }
    else:
        raise Exception('Incorrect method passed, please provide PhotosSearch or getInfo and required parameters')

    unique_ident = params_unique_combination(baseurl,params_diction)
    if unique_ident in CACHE_DICTION:
        return CACHE_DICTION[unique_ident]
    else:
        resp = requests.get(baseurl, params_diction)
        CACHE_DICTION[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

class Photo:
    def __init__(self, photo_dict):
        self.title = photo_dict['title']
        self.id = photo_dict['id']
        self.owner = photo_dict['owner']
        try:
            self.owner_username = photo_dict['owner']['username']
        except:
            self.owner_username = None

    def __str__(self):
        if self.owner_username:
            return '{0} by {1} aka {}'.format(self.title, self.owner, self.owner_username)
        else:
            return '{0} by {1}'.format(self.title, self.owner)



CACHE_DICTION = load_cache_json()
if DEBUG:
    print(CACHE_DICTION)

results = search_flickr(method = 'PhotosSearch', tags = 'sunset summer', ppg = 10)

photos_list = []
for r in results['photos']['photo']:
    photo_id = r['id']
    search_flickr(method='getInfo', photo_id)
    photos_list.append(Photo(r))


print()
print("= compare these outputs = >> ")
print(photos_list)
print("\n= vs = >> \n")

for photo in photos_list:
    print(photo)

    # if you get encoding error, try this
    # print(str(photo).encode('utf-8'))

print()
