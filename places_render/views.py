from django.shortcuts import render, redirect
from .models import *
from django.views import View
from .forms import *
import googlemaps
import os
from dotenv import load_dotenv
import pandas as pd
import time
import json
from openai import OpenAI
from datetime import datetime
import requests

# Create your views here.


def getGoogleMapsKey():
    # load_dotenv()
    # return os.getenv("GOOGLE_MAPS_KEY")
    return os.environ.get("GOOGLE_MAPS_KEY")

def getChatGPTKey():
    return os.environ.get("CHAT_GPT_KEY")

class HomeView(View):
    model = Locations
    form_class = LocationForm
    template_name = "project_content/home.html"
    success_url = "/"
    df = df = pd.DataFrame(
        columns=[
            "name",
            "place_id",
            "rating",
            "types",
            "user_ratings_total",
            "photos",
            "vicinity",
            "lat",
            "lng",
        ]
    )
    context = {}

    def get(self, request):
        json_records = self.df.reset_index().to_json(orient="records")
        arr = []
        arr = json.loads(json_records)
        self.context = {"form": self.form_class, "d": arr}

        return render(request, self.template_name, self.context)

    def post(self, request):
        form = LocationForm(request.POST)
        location = form.save(commit=False)
        print(location)

        gmaps = googlemaps.Client(key=getGoogleMapsKey())
        result = gmaps.geocode(location.destination)[0]
        lat = result.get("geometry", {}).get("location", {}).get("lat")
        lng = result.get("geometry", {}).get("location", {}).get("lng")

        place_id = result.get("place_id")

        if lat != None:
            location.lat = lat
        if lng != None:
            location.lng = lng
        if place_id != None:
            location.place_id = place_id

        response = gmaps.places_nearby(
            location=(lat, lng),
            keyword="point of interest",
            radius=24140,
            open_now=True
        )

        business_list = []
        business_list.extend(response.get("results"))

        next_page_token = response.get("next_page_token")

        while next_page_token:
            time.sleep(2)
            response = gmaps.places_nearby(
                location=(lat, lng),
                keyword="point of interest",
                radius=24140,
                open_now=True,
                page_token=next_page_token,
            )
            business_list.extend(response.get("results"))
            next_page_token = response.get("next_page_token")

        df = pd.DataFrame(business_list)
        df[["lat", "lng"]] = df["geometry"].apply(
            lambda x: pd.Series([x["location"]["lat"], x["location"]["lng"]])
        )

        df.drop("geometry", axis=1, inplace=True)
        df.drop("icon", axis=1, inplace=True)
        df.drop("icon_background_color", axis=1, inplace=True)
        df.drop("icon_mask_base_uri", axis=1, inplace=True)
        df.drop("plus_code", axis=1, inplace=True)
        df.drop("reference", axis=1, inplace=True)
        df.drop("scope", axis=1, inplace=True)
        df.drop("business_status", axis=1, inplace=True)

        df = df.sort_values(by=["user_ratings_total"], ascending=False)

        client = OpenAI(
            api_key = getChatGPTKey()
        )

        places_unfiltered = df['name'].tolist()
        print(places_unfiltered)

        if location.reference != "":
            chat_completion = client.chat.completions.create(
            messages = [
                {"role": "user", "content" : 
                "Is the" + location.reference + "an entertainment attraction, a historical attraction, or a natural attraction? Give a two word answer." }
                
            ],
                model="gpt-3.5-turbo",
            )

            reference_classification = chat_completion.choices[0].message.content

            chat_completion = client.chat.completions.create(
            messages = [
                {"role": "user", "content" : 
                str(places_unfiltered) + " Categorize the above attractions into entertainment attractions, historical attractions, and natural attractions. Then, take out only the"
                + reference_classification + "Give the answer presented without bullet points and separated by three tilda symbols, without any extraneous text (e.g. Smithsonian National Museum of Natural History~~~Smithsonian National Museum of American History)"}
                
            ],
                model="gpt-3.5-turbo",
            )

            places_unreferenced_string = chat_completion.choices[0].message.content

            places_unreferenced = places_unreferenced_string.strip('][').split('~~~')

        else:
            reference_classification = ""
            places_unreferenced = places_unfiltered


        print("places_unreferenced")
        print(places_unreferenced)

        free = location.free
        freeSentence = ""
        referenceSentence = ""

        if location.reference != "":
            referenceSentence = " Then, rank this list based on how thematically similar the elements are to " + location.reference

        if free:
            freeSentence = " Remove the places with an admissions fee."

        attractionSentence = str(places_unreferenced) + " : Remove the quotations between the elements in this list and the commas." + freeSentence + referenceSentence + " and return the list, without bullet points, with each element separated by three tilda symbols, without any extraneous text."

        print(attractionSentence)

        chat_completion = client.chat.completions.create(
        messages = [
            {"role": "user", "content" : attractionSentence}
            
        ],
        model="gpt-3.5-turbo",
        )

        initial = (chat_completion.choices[0].message.content)
        places_referenced = initial.split('~~~')

        print("places-referenced:")
        print(places_referenced)

        df = df[df[['name']].isin(places_referenced).any(axis=1)]
        print(df)

        from_location_lat = location.lat
        from_location_lng = location.lng
        now = datetime.now()

        times = []
        destination_addresses = []
        images = []

        for index, row in df.iterrows():
            to_location_lat = row['lat']
            to_location_lng = row['lng']
            image = row["photos"]

            photo_reference = image[0]["photo_reference"]

            api_key = getGoogleMapsKey()
            
            url = f'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photo_reference}&key={api_key}'

            response = requests.get(url)

            images.append(response.url)

            calculate = gmaps.distance_matrix(
                (from_location_lat, from_location_lng),
                (to_location_lat, to_location_lng),
                mode = "driving",
                departure_time = now
            )

            destination_address = calculate["destination_addresses"]
            n = 2
            destination_address = str(destination_address)
            destination_address = destination_address[2:-2]

            destination_addresses.append(destination_address)

            duration_seconds = calculate["rows"][0]["elements"][0]["duration"]["value"]
            duration_minutes = duration_seconds/60
            times.append(str(round(float(duration_minutes), 2)))
            
        df['time'] = times

        df['address'] = destination_addresses

        df["photos"] = images

        df.drop("lat", axis=1, inplace=True)
        df.drop("lng", axis=1, inplace=True)

        json_records = df.reset_index().to_json(orient="records")
        arr = []
        arr = json.loads(json_records)

        self.df = df
        self.context = {"form": self.form_class, "d": arr}

        # location.save()
        return render(request, self.template_name, self.context)
        # return redirect("my_home_view")
