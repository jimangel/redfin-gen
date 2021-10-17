from redfin import Redfin
import datetime, requests, urllib, os, sys, json, calendar, googlemaps

# 0 index, length check for no sys.argv[1] (address)
if len(sys.argv) < 2:
    print("python3 " + sys.argv[0] + " \"4544 Radnor St, Detroit Michigan\"")
    sys.exit(1)
# set the house address based on arg passed in
address = sys.argv[1]

# map client set my OS ENV "KEY"
gmaps = googlemaps.Client(key=os.environ.get('KEY'))

# setup redfin client and capture response / url / data
client = Redfin()
response = client.search(address)
url = response['payload']['exactMatch']['url']
initial_info = client.initial_info(url)
property_id = initial_info['payload']['propertyId']
mls_data = client.below_the_fold(property_id)
listing_id = initial_info['payload']['listingId']
avm_details = client.avm_details(property_id, listing_id)

# uncomment for debugging
#print(json.dumps(avm_details, indent = 2))
#print(json.dumps(mls_data, indent = 1))

# set vars
list_price = avm_details['payload']['listingPrice']
beds = avm_details['payload']['numBeds']
baths = avm_details['payload']['numBaths']
sqft = avm_details['payload']['sqFt']['value']
year_build = mls_data['payload']['publicRecordsInfo']['basicInfo']['yearBuilt']
lot_sqft = mls_data['payload']['publicRecordsInfo']['basicInfo']['lotSqFt']
taxes = mls_data['payload']['publicRecordsInfo']['taxInfo']['taxesDue']

# function to calculate distance, implies a known source - only needs destination
def calc_dist(destination):
  # https://developers.google.com/maps/documentation/distance-matrix/overview
  my_dist = gmaps.distance_matrix(address, destination, departure_time="now", traffic_model="pessimistic")['rows'][0]['elements'][0]['duration']['text']
  # drop " mins" from the response
  return my_dist.replace(' mins', '')

# get distance to transit
oak_dist = calc_dist('1 Airport Dr, Oakland, CA 94621')
wdpb_dist = calc_dist('6501 Golden Gate Dr, Dublin, CA 94568')
dpb_dist = calc_dist('5801 Owens Dr, Pleasanton, CA 94588')

# get walk score
ws_url = "https://api.walkscore.com/score?format=json&address=" + urllib.parse.quote_plus(address) + "&lat=" + str(avm_details['payload']['latLong']['latitude']) + "&lon=" + str(avm_details['payload']['latLong']['longitude']) + "&wsapikey=" + os.environ.get('WS')
response = requests.get(ws_url)
walkscore = response.json()['walkscore']

# OUTPUT
print("Built,Lot,Price,Bed,Bth,Sqft,Cost (Sqft),Taxes, OAK, west bart, dublin bart, walkscore")
# data rows of csv file
print(year_build, lot_sqft, list_price, beds, baths, sqft, (list_price//sqft), taxes, oak_dist, wdpb_dist, dpb_dist, walkscore, sep=",")