from genetic_algorithm import generic_algorithm
import csv
import requests

if __name__ == '__main__':
    geolocation = {}
    # selected municipality
    municipality = ""
    with open('municipios.csv', newline='', encoding='utf-8') as archivo_csv:
        lector_csv = csv.reader(archivo_csv)
        for fila in lector_csv:
            if fila[0] == "Tuxtla Gutiérrez":
                municipality = fila[0]

    # ip_public
    response = requests.get('https://api.ipify.org?format=json')
    data = response.json()
    if data:
        # geolocation
        response = requests.get(f"http://ip-api.com/json/{data['ip']}")
        response_json = response.json()
        if response_json["status"] == "success":
                geolocation["city"] = response_json["city"]
                geolocation["regionName"] = response_json["regionName"]
                geolocation["lat"] = response_json["lat"]
                geolocation["lon"] = response_json["lon"]
        else:
            print("Error al obtener la información.")
    else:
        print("Error al obtener la ip publica.")

    print(geolocation)
