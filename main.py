from selenium import webdriver
from time import sleep
import json
import requests
from variables import slack_webhook_url, discord_webhook_url
from selenium.webdriver.chrome.options import Options
from datetime import datetime as dt
options = Options()
options.headless = True
driver = webdriver.Chrome(
    executable_path="/home/krn/repos/chromedriver/chromedriver", options=options
)
driver.maximize_window()
total_group_growth = 0

with open('tracker.json') as json_file:
    tracker = json.load(json_file)


def get_followers(user):
    global total_group_growth
    driver.get(f"https://twitter.com/{user}")
    sleep(3)
    follower_count = driver.find_element_by_xpath(
        "/html/body/div/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/div[1]/div/div[5]/div[2]/a/span[1]/span"
    ).text.replace(',', '')
    user = user.strip()
    tracker[user].append(follower_count)
    growth = int(follower_count) - int(tracker[user][-2])
    total_group_growth += growth
    return update_slack(user, follower_count, growth)


def update_slack(user, follower_count, growth):
    message = f"@{user} has {follower_count} followers, up {growth} followers from {tracker[user][-2]} yesterday."
    response = requests.post(
        slack_webhook_url,
        data=json.dumps({"text": message}),
        headers={"Content-Type": "application/json"},
    )
    if response.status_code != 200:
        raise ValueError(
            "Request to slack returned an error %s, the response is:\n%s"
            % (response.status_code, response.text)
        )
    print(message)


for key in tracker.keys():
    get_followers(key)
    sleep(2)

# Update the webhook with Total Group Growth
message = f"In total, the group has grown by {total_group_growth} followers in the last 24 hours."
response = requests.post(
    slack_webhook_url,
    data=json.dumps({"text": message}),
    headers={"Content-Type": "application/json"},
)

# Discord cron job update via webhook
requests.post(discord_webhook_url, data={
              'content': f'Ran Twitter Follower Updates Slack Bot at {dt.now().strftime("%I:%M:%S %p")} on {dt.now().strftime("%A, %-d %b %Y")}'})

with open('tracker.json', 'w') as outfile:
    json.dump(tracker, outfile)
