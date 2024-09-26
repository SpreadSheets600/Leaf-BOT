import json

def get_forum_channel(user_id):
    with open("DATA/Forums.json", "r") as f:
        data = json.load(f)

    return data[user_id]

print(get_forum_channel("1234"))

def update_forum_channel(user_id, channel_id):
    with open("DATA/Forums.json", "r") as f:
        data = json.load(f)

    data[user_id] = channel_id

    with open("DATA/Forums.json", "w") as f:
        json.dump(data, f)

update_forum_channel("1234sad", 5678)