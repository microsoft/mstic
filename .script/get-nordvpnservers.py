import requests
import json
import pandas as pd

# Download Nord Server list using API
r  = requests.get('https://api.nordvpn.com/server')

#Decode byte array into string
my_json = r.content.decode('utf8')

#Convert string to JSON
data = json.loads(my_json)

# Load list of JSON records into dataframe
df = pd.DataFrame(data)

# Convert to csv
df.to_csv('nordvpn-servers.csv',  index=False)