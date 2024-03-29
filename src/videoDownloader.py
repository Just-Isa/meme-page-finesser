import pathlib, os
import urllib.request as vd
from pathlib import Path 
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from requests_html import HTMLSession

def get_form_details(form):
    details = {}

    # actions
    action = form.attrs.get("action").lower()

    # method, get is default
    method = form.attrs.get("method", "get").lower()

    # all form inputs
    inputs = []

    for input_tag in form.find_all("input"):
        input_type = input_tag.attrs.get("type", "text")
        input_name = input_tag.attrs.get("name")
        input_value = input_tag.attrs.get("value", "")

        inputs.append({"type" : input_type, "name" : input_name, "value" : input_value})

    for textarea in form.find_all("textarea"):
        textarea_name = textarea.attrs.get("name")
        textarea_type = "textarea"
        textarea_value = textarea.attrs.get("value", "")
        inputs.append({"type": textarea_type, "name": textarea_name, "value": textarea_value})

    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
    return details

def submitall(link, name):
    session = HTMLSession()
    actualLink = ""
    for i in range(6):
        actualLink += link.split('/')[i] + "/"
    res = session.get('https://twdown.net/')
    soup = BeautifulSoup(res.html.html, 'html.parser')
    form_details = get_form_details(soup.find_all('form')[0])

    data = {}
    for input_tag in form_details["inputs"]:
        if input_tag["type"] == "hidden":
            # if it's hidden, use the default value
            data[input_tag["name"]] = input_tag["value"]
        elif input_tag["type"] != "submit":
            # if not submit field, must be input field
            data[input_tag["name"]] = actualLink

    # submi
    url = urljoin('https://twdown.net/', form_details["action"])

    if not os.path.exists(str(pathlib.Path().resolve())+'\\videos\\'+name):
        os.makedirs(str(pathlib.Path().resolve())+'\\videos\\'+name, exist_ok=True)
    if form_details["method"] == "post":
        res = session.post(url, data=data)
    elif form_details["method"] == "get":
        res = session.get(url, params=data)

    try:
        downloadUrl = BeautifulSoup(res.html.html, 'html.parser').find_all("a", text="Download")[0].attrs.get("href")
    except IndexError:
        print("weird link")
        exit(0)

    Path("/videos/"+name).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(str(pathlib.Path().resolve())+'\\videos\\'+name+'\\' + actualLink.split('/')[-2]+'.mp4'):
        vd.urlretrieve(downloadUrl.split("?")[0], str(pathlib.Path().resolve())+'\\videos\\'+name+'\\' + actualLink.split('/')[-2]+'.mp4')
    else:
        print("File already downloaded!")
    session.close()