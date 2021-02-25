from selenium import webdriver
from time import sleep
import json
import requests
from variables import accountpassword, accountusername, webhook_url
from selenium.webdriver.chrome.options import Options

options = Options()
options.headless = True
driver = webdriver.Chrome(
    executable_path="/home/krn/repos/chromedriver/chromedriver", options=options
)
driver.maximize_window()


def login(user, pw):
    driver.get("https://twitter.com")
    sleep(1)
    login_btn = driver.find_element_by_xpath(
        "/html/body/div/div/div/div/main/div/div/div/div[1]/div/div[3]/a[2]"
    )
    login_btn.click()
    sleep(1)
    user_field = driver.find_element_by_name("session[username_or_email]")
    pass_field = driver.find_element_by_name("session[password]")
    user_field.click()
    sleep(1)
    user_field.send_keys(user)
    sleep(1)
    pass_field.click()
    pass_field.send_keys(pw)
    sleep(1)
    submit_btn = driver.find_element_by_xpath(
        "/html/body/div/div/div/div[2]/main/div/div/div[2]/form/div/div[3]/div"
    )
    submit_btn.click()


def get_followers(user):
    driver.get(f"https://twitter.com/{user}")
    sleep(3)
    follower_count = driver.find_element_by_xpath(
        "/html/body/div/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/div[1]/div/div[5]/div[2]/a/span[1]/span"
    ).text
    name = driver.find_element_by_xpath(
        "/html/body/div/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/div[1]/div[2]/div[2]/div/div/div[1]/div/span[1]/span"
    ).text
    return update_slack(name.strip(), follower_count)


def update_slack(user, follower_count):
    message = f"{user} has {follower_count} followers."
    response = requests.post(
        webhook_url,
        data=json.dumps({"text": message}),
        headers={"Content-Type": "application/json"},
    )
    if response.status_code != 200:
        raise ValueError(
            "Request to slack returned an error %s, the response is:\n%s"
            % (response.status_code, response.text)
        )


login(accountusername, accountpassword)
lines = open("users.txt", "r").readlines()
for line in lines:
    get_followers(line)
    sleep(2)
