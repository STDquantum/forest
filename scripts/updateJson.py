import json
import time
import requests

def get_curpath():
    import sys
    return sys.path[0]

def planted():
    res = requests.get(baseUrl + "plants", headers = {"cookie" : cookie, "Authorization": Authorization}, params = {"from_date" : "2020-05-25T09:32:40.141Z"})
    return res

def user():
    res = requests.get(baseUrl + "users/{}".format(userId), headers = {"cookie" : cookie, "Authorization": Authorization})
    return res
 
def tree_types():
    res = requests.get(baseUrl + "tree_types", headers = {"cookie" : cookie, "Authorization": Authorization})
    return res

def unlocked_tree_types():
    res = requests.get(baseUrl + "tree_types/unlocked", headers = {"cookie" : cookie, "Authorization": Authorization})
    return res

def followings():
    res = requests.get(baseUrl + "followings", params = {"cookie": cookie, "Authorization" : Authorization, "from_date" : time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.localtime())})
    return res

def rooms():
    res = requests.get(baseUrl + "rooms", headers = {"cookie" : cookie, "Authorization": Authorization})
    return res

def purchases():
    res = requests.get(baseUrl + "purchases", headers = {"cookie" : cookie, "Authorization": Authorization})
    return res

def products():
    res = requests.get(baseUrl + "products", headers = {"cookie" : cookie, "Authorization": Authorization})
    return res

def tags():
    res = requests.get(baseUrl + "tags", headers = {"cookie" : cookie, "Authorization": Authorization})
    return res

def achievements():
    res = requests.get(baseUrl + "achievements", params = {"cookie": cookie, "Authorization" : Authorization, "today" : time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.localtime())})
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
    # printf(get_curpath() + "\\..\\databases\\followings.json", followings, "followings")
    # printf(get_curpath() + "\\..\\databases\\achievements.json", achievements, "achievements")
    
if __name__ == "__main__":
    userId = 12146
    baseUrl = "https://forest-china.upwardsware.com/api/v1/"
    authenticate_token = "K4aLfcqU2UDi7WoIysrPLw"
    Authorization = "Bearer eyJraWQiOiIxZGQ3YzRjYi03ZmMwLTRhYWEtODhkMC0zMDE2NDgwNzkwZjciLCJhbGciOiJFUzI1NiJ9.eyJpc3MiOiJ1cHdhcmRzd2FyZS5zZWVrcmF1dGgiLCJhdWQiOiJ1cHdhcmRzd2FyZS5mb3Jlc3QiLCJzdWIiOiIyMjhjZWFkOS1mMmFkLTQ4MzgtYWFjMS1jNzBhMzNkOWMwOTYiLCJleHAiOjE3NDYyNDQyMTgsIm5iZiI6MTc0NjI0MDYxOCwiaWF0IjoxNzQ2MjQwNjE4LCJqdGkiOiI2ZjRhOWRjMi05NTIwLTQzM2UtYTgyMC1lNjMxNjQ3N2ExNjgiLCJuYW1lIjoi5piv5bCP56yR5LqGIiwiZW1haWwiOiI0MDU3MjAzMjlAcXEuY29tIiwiYmlydGhkYXkiOiIyMDA0LTEyLTEyIDAwOjAwOjAwIFVUQyIsInNjb3BlIjoiLyJ9.VBo2Ilck_Wcv6w-a2mmg3Yd7RlhTHtoBuCSwcJPdrLJIdQI5g__VG27HgV53LITPGJIPeDSaxM6BnEKszbvPBg"
    cookie = "intercom-id-y1kzl408=33fee35a-84e9-4d1e-92ae-84f1609c8ad8; intercom-session-y1kzl408=; intercom-device-id-y1kzl408=3dcb1d82-4928-4f77-aa1b-a82e79a194ba"
    """"from_date" : time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.localtime())"""
    update()