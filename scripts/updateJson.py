import json
import time
import requests

def get_curpath():
    import sys
    return sys.path[0]

def planted():
    res = requests.get(baseUrl + "plants", headers = {"cookie" : cookie}, params = {"from_date" : "2020-05-25T09:32:40.141Z"})
    return res

def user():
    res = requests.get(baseUrl + "users/{}".format(userId), headers = {"cookie" : cookie})
    return res
 
def tree_types():
    res = requests.get(baseUrl + "tree_types", headers = {"cookie" : cookie})
    return res

def unlocked_tree_types():
    res = requests.get(baseUrl + "tree_types/unlocked", headers = {"cookie" : cookie})
    return res

def followings():
    res = requests.get(baseUrl + "followings", params = {"authenticate_token" : authenticate_token, "from_date" : time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.localtime())})
    return res

def rooms():
    res = requests.get(baseUrl + "rooms", headers = {"cookie" : cookie})
    return res

def purchases():
    res = requests.get(baseUrl + "purchases", headers = {"cookie" : cookie})
    return res

def products():
    res = requests.get(baseUrl + "products", headers = {"cookie" : cookie})
    return res

def tags():
    res = requests.get(baseUrl + "tags", headers = {"cookie" : cookie})
    return res

def achievements():
    res = requests.get(baseUrl + "achievements", params = {"authenticate_token" : authenticate_token, "today" : time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.localtime())})
    return res

def printf(path, info, title = "info"):
    s = time.time()
    with open(path, "w", encoding = "utf-8") as f:
        json.dump(info().json(), f, indent = 4, ensure_ascii = False)
    print("{} {:.3f}s".format(title, time.time() - s))

def update():
    printf(get_curpath() + "\\..\\databases\\plant.json", planted, "plant")
    printf(get_curpath() + "\\..\\databases\\user.json", user, "user")
    printf(get_curpath() + "\\..\\databases\\rooms.json", rooms, "rooms")
    printf(get_curpath() + "\\..\\databases\\purchases.json", purchases, "purchases")
    printf(get_curpath() + "\\..\\databases\\products.json", products, "products")
    printf(get_curpath() + "\\..\\databases\\tags.json", tags, "tags")
    printf(get_curpath() + "\\..\\databases\\followings.json", followings, "followings")
    printf(get_curpath() + "\\..\\databases\\achievements.json", achievements, "achievements")
    
if __name__ == "__main__":
    userId = 12146
    baseUrl = "https://forest-china.upwardsware.com/api/v1/"
    authenticate_token = "K4aLfcqU2UDi7WoIysrPLw"
    cookie = "remember_token=K4aLfcqU2UDi7WoIysrPLw"
    """"from_date" : time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.localtime())"""
    update()