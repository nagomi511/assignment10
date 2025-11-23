from django.shortcuts import render

# Create your views here.
import os
import random
import datetime
import requests
from django.shortcuts import render
from pymongo import MongoClient

from .forms import ContinentForm

# --- MongoDB 接続用 ---
def get_mongo_collection():
    host = os.getenv('MONGODB_HOST')
    port = int(os.getenv('MONGODB_PORT'))
    db_name = os.getenv('MONGODB_DB')
    collection_name = os.getenv('MONGODB_COLLECTION')

    client = MongoClient(host, port)
    db = client[db_name]
    return db[collection_name]


# --- メイン画面（大陸入力 → ランダム5カ国の天気取得） ---
def continent_weather_view(request):
    results = []
    error_message = None

    if request.method == 'POST':
        form = ContinentForm(request.POST)
        if form.is_valid():
            continent = form.cleaned_data['continent']

            # ① REST Countries API 呼ぶ
            countries_url = f'https://restcountries.com/v3.1/region/{continent}'
            try:
                resp = requests.get(countries_url)
                resp.raise_for_status()
                countries_data = resp.json()
            except Exception as e:
                error_message = f"Error fetching country data: {e}"
                countries_data = []

            # capital のある国だけに絞る
            valid_countries = []
            for c in countries_data:
                name = c.get('name', {}).get('common')
                capitals = c.get('capital')
                population = c.get('population')
                latlng = c.get('latlng')

                if name and capitals:
                    valid_countries.append({
                        'name': name,
                        'capital': capitals[0],
                        'population': population,
                        'latlng': latlng,
                    })

            # ② ランダムで5国
            if len(valid_countries) == 0:
                error_message = "No countries with capitals found."
            else:
                selected = random.sample(valid_countries, min(5, len(valid_countries)))

                api_key = os.getenv('OPENWEATHERMAP_API_KEY')
                weather_results = []

                # ③ 天気API 呼ぶ
                for country in selected:
                    city = country['capital']
                    weather_url = (
                        f'https://api.openweathermap.org/data/2.5/weather'
                        f'?q={city}&appid={api_key}&units=metric'
                    )

                    try:
                        w_resp = requests.get(weather_url)
                        w_resp.raise_for_status()
                        w_data = w_resp.json()

                        temp = w_data.get('main', {}).get('temp')
                        desc = None
                        weather_list = w_data.get('weather')
                        if weather_list:
                            desc = weather_list[0].get('description')

                        weather_results.append({
                            'country': country['name'],
                            'capital': city,
                            'population': country['population'],
                            'latlng': country['latlng'],
                            'temperature': temp,
                            'description': desc,
                        })
                    except Exception as e:
                        weather_results.append({
                            'country': country['name'],
                            'capital': city,
                            'population': country['population'],
                            'latlng': country['latlng'],
                            'temperature': None,
                            'description': f"Error: {e}",
                        })

                results = weather_results

                # ④ MongoDB に保存
                try:
                    collection = get_mongo_collection()
                    collection.insert_one({
                        'continent': continent,
                        'searched_at': datetime.datetime.utcnow(),
                        'results': weather_results,
                    })
                except Exception as e:
                    error_message = f"MongoDB error: {e}"

    else:
        form = ContinentForm()

    return render(request, 'continent_form.html', {
        'form': form,
        'results': results,
        'error_message': error_message,
    })


# --- 履歴ページ ---
def history_view(request):
    collection = get_mongo_collection()
    docs = collection.find().sort('searched_at', -1).limit(10)

    history_list = []
    for doc in docs:
        history_list.append({
            'continent': doc.get('continent'),
            'searched_at': doc.get('searched_at'),
            'results': doc.get('results', []),
        })

    return render(request, 'history.html', {
        'history_list': history_list
    })
