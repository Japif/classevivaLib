import requests
from bs4 import BeautifulSoup
import time
s = requests.session()


def login(user, passwd):
    s = requests.session()
    url = "https://web.spaggiari.eu/auth-p7/app/default/AuthApi4.php?a=aLoginPwd"
    payload=f'cid=&pin=&pwd={passwd}&target=&uid={user}'
    headers = {
      'Accept': '*/*',
      'X-Requested-With': 'XMLHttpRequest',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
      'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
      'Sec-Fetch-Site': 'same-origin',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Dest': 'empty',
    }
    r = s.post(url, headers=headers, data=payload)
    if r.status_code != 200:
        return {"loggedIn": False}

    url = "https://web.spaggiari.eu/home/app/default/menu.php"
    r = s.get(url, headers=headers)
    if r.status_code != 200:
        return {"loggedIn": False}

    url = 'https://web.spaggiari.eu/tools/app/default/get_username.php'
    r = s.get(url)
    if r.status_code != 200:
        return {"loggedIn": False}

    return {"loggedIn": True, "session":s, "responseData":r.json()}

def getMarks(s):
    url = 'https://web.spaggiari.eu/cvv/app/default/genitori_note.php?filtro=tutto'
    response = s.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find("table")
    subjIndexArray = []
    subjects = []
    index = 0
    raws = table.find_all("tr")
    for item in raws:
        try:
            if item["valign"] == "middle" and "griglia" not in item["class"] and item.find("td").text != "":
                subjects.append(item.text.replace("\n", ""))
                subjIndexArray.append(index)
        except:
            pass
        index = index + 1

    subjIndexArray.append(len(raws))
    index = 0
    returnData = {}
    for n in range(len(subjIndexArray)-1):
        returnData[subjects[index]] = []
        for i in range(subjIndexArray[n] + 1, subjIndexArray[n+1]):
            date = raws[i].find("td", {"colspan" : "6"}).text.replace("\n", "")
            typeOfMark = raws[i].find("td", {"colspan": "5"}).text.replace("\n", "")
            mark = raws[i].find("td", {"colspan": "2"}).text.replace("\n", "")
            description = raws[i].find("td", {"colspan": "32"}).text.replace("\n", "")
            returnData[subjects[index]].append({
                "date" : date,
                "type": typeOfMark,
                "mark": mark,
                "description": description,
            })
        index = index + 1
    return returnData
def getEvents(s):
    start = int(time.time())
    end = start + 604800
    url = "https://web.spaggiari.eu/fml/app/default/agenda_studenti.php?ope=get_events"
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }
    payload = f'end={end}&gruppo_id=&nascondi_av=0&start={start}'
    response = s.post(url, headers=headers, data=payload)
    datas = response.json()
    return datas[0]


def getToday(s):
    url = "https://web.spaggiari.eu/fml/app/default/regclasse.php"
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }
    response = s.get(url, headers=headers)
    rawData = BeautifulSoup(response.content, 'html.parser')
    table = rawData.find_all("table", {"id":"data_table"})[-1]
    tableData = table.find_all("tr", {"class":"rigtab"})
    rows = []
    returnData = {}
    for row in tableData:
        if not row.has_attr('id') and not row.has_attr('valign'):
            rows.append(row)

    for row in rows:
        items = row.find_all("td")
        for item in items:
            if item.has_attr('colspan') :
                if item["colspan"] == "10":
                    subj = item["title"].replace("\n","").replace("\xa0","")
                elif item["colspan"] == "14":
                    teacher = item.text.replace("\n","").replace("\xa0","")
                elif item["colspan"] == "3":
                    hours = item.text.replace("\n","").replace("\xa0","")
                elif item["colspan"] == "17":
                    description = item.text.replace("\n","").replace("\xa0","").replace("() ","")

        returnData[subj] = {"teacher": teacher, "hours": hours, "description":description}
    return returnData
