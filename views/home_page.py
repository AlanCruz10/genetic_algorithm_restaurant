from pathlib import Path
from tkinter import Tk, Canvas, Entry, Button, PhotoImage, filedialog, ttk
import csv
import requests
from genetic_algorithm import genetic_algorithm_restaurant
from utilities.utlity import print_list


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"assets\frame0")
municipality = None
food = None
entries = {}


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


window = Tk()

window.geometry("1112x702")
window.configure(bg="#FFFFFF")

canvas = Canvas(
    window,
    bg="#FFFFFF",
    height=702,
    width=1112,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)

canvas.place(x=0, y=0)
image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    556.0,
    351.0,
    image=image_image_1
)

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: read_csv(),
    relief="flat"
)


def read_csv():
    list_restaurants = []
    if food is not None:
        food.destroy()
    try:
        data_set = filedialog.askopenfilename(filetypes=[('CSV Files', '*csv')])
        with open(data_set, newline='') as archivo_csv:
            lector_csv = csv.reader(archivo_csv, delimiter=";")
            for i, fila in enumerate(lector_csv):
                if i != 0:
                    list_restaurants.append({
                        "id": i - 1,
                        "name": fila[0],
                        "rating": float(fila[1]),
                        "reservations": int(fila[2]),
                        "frequency": int(fila[3]),
                        "evaluation": float(fila[4]),
                        "location": fila[5],
                        "food": fila[6]
                    })
            entries["list_restaurants"] = list_restaurants
    except (FileNotFoundError, UnicodeDecodeError, Exception, TypeError) as e:
        entries["list_restaurants"] = list_restaurants
        print("Invalid file")


button_1.place(
    x=108.70184326171875,
    y=117.0,
    width=142.69129943847656,
    height=32.084434509277344
)

button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=45,
    command=lambda: get_location(),
    relief="flat"
)


def get_location():
    if municipality is not None:
        municipality.destroy()
    geolocation = {}
    # ip_public
    response = requests.get('https://api.ipify.org?format=json')
    data = response.json()
    if data:
        # geolocation
        response = requests.get(f"http://ip-api.com/json/{data['ip']}")
        response_json = response.json()
        if response_json["status"] == "success":
            geolocation["city"] = response_json["city"]
            geolocation["country"] = response_json["country"]
            geolocation["regionName"] = response_json["regionName"]
            geolocation["lat"] = response_json["lat"]
            geolocation["lng"] = response_json["lon"]
            geolocation["status"] = True
        else:
            print("Error al obtener la ubicacion.")
            geolocation["status"] = False
    else:
        print("Error al obtener la ip publica.")
        geolocation["status"] = False
    entries["geolocation"] = geolocation
    if "geolocation_municipality" in entries.keys():
        entries["geolocation_municipality"] = ""
    else:
        entries["geolocation_municipality"] = ""


button_2.place(
    x=37.0,
    y=199.21107482910156,
    width=142.69129943847656,
    height=32.084434509277344
)

button_image_3 = PhotoImage(
    file=relative_to_assets("button_3.png"))
button_3 = Button(
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: get_type_food(),
    relief="flat"
)


def get_type_food():
    global food
    unique_food = set()
    unique_food.add("Otros")
    if "list_restaurants" in entries.keys():
        restaurants = entries["list_restaurants"]
        if len(restaurants) > 0:
            for r in restaurants:
                if r["food"] not in unique_food:
                    unique_food.add(r["food"])
        else:
            print("Select other data base to more type foods")
    else:
        print("Select data base to more type foods")
    combobox = ttk.Combobox(window, width=24, state='readonly', values=list(unique_food))
    food = combobox
    combobox.place(
        x=215.0,
        y=267.0,
        width=176.0,
        height=32.0
    )


button_3.place(
    x=215.0,
    y=267.0,
    width=176.0,
    height=32.0
)

button_image_4 = PhotoImage(
    file=relative_to_assets("button_4.png"))
button_4 = Button(
    image=button_image_4,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: get_data(),
    relief="flat"
)


def get_data():
    data_ok = True
    try:
        initial_population = int(entry_1.get().strip())
        max_population = int(entry_2.get().strip())
        str_prob_mut_ind = entry_3.get().strip()
        str_prob_mut_gen = entry_4.get().strip()
        if str_prob_mut_ind.isdigit():
            prob_mut_ind = int(str_prob_mut_ind)
        else:
            prob_mut_ind = float(str_prob_mut_ind)
        if str_prob_mut_gen.isdigit():
            prob_mut_gen = int(str_prob_mut_gen)
        else:
            prob_mut_gen = float(str_prob_mut_gen)
        iterations = int(entry_5.get().strip())
        if initial_population < 2:
            print("Population initial can't be less that two")
            data_ok = False
        if iterations < 1:
            print("Iterations can't be less that one")
            data_ok = False
        if "geolocation" not in entries and municipality is None:
            print("Select location")
            data_ok = False
        elif entries["geolocation"] == {} and (municipality.get() == "" or municipality.get() == "Select"):
            print("Select location")
            data_ok = False
        elif entries["geolocation"] == {} and (municipality.get() != "" or municipality.get() != "Select"):
            entries["geolocation_municipality"] = municipality.get()
        else:
            if not entries["geolocation"]["status"]:
                print("location undefined, try again or select other location")
                data_ok = False
        if food is not None and food.get() != "":
            entries["food"] = food.get()
        else:
            entries["food"] = "Otros"
        if "list_restaurants" not in entries:
            print("Select data base of restaurants")
            data_ok = False
        else:
            if not entries["list_restaurants"]:
                print("Select other data base of restaurants")
                data_ok = False
        if data_ok:
            geolocation_municipality = entries["geolocation_municipality"]
            geolocation = entries["geolocation"]
            type_food = entries["food"]
            list_restaurants = entries["list_restaurants"]
            population, population_by_generation, statistics = genetic_algorithm_restaurant(list_restaurants,
                                                                                            geolocation,
                                                                                            geolocation_municipality,
                                                                                            type_food,
                                                                                            initial_population,
                                                                                            3, max_population, 0.25,
                                                                                            prob_mut_gen,
                                                                                            prob_mut_ind, iterations,
                                                                                            "Minimizacion")
            print("------------------------------------------")
            print("population")
            print_list(population)
            print("by generation")
            for x in population_by_generation:
                print(x)
                print_list(population_by_generation[x])
            print("statistics")
            print_list(statistics)

    except (ValueError, Exception) as e:
        print("Data can't be str or null")



button_4.place(
    x=71.0,
    y=629.0,
    width=114.0,
    height=32.0
)

button_image_5 = PhotoImage(
    file=relative_to_assets("button_5.png"))
button_5 = Button(
    image=button_image_5,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: get_municipalities(),
    relief="flat"
)


def get_municipalities():
    global municipality
    if "geolocation" in entries.keys():
        entries["geolocation"] = {}
    municipalities = ["Select"]
    with open('C:\\Users\\exala\\Documents\\proyectos\\projects-8\\python\\genetic_algorithm_restaurant\\municipios.csv', newline='', encoding='utf-8') as archivo_csv:
        lector_csv = csv.reader(archivo_csv)
        for i, fila in enumerate(lector_csv):
            if i != 0:
                municipalities.append(fila[0])
    combobox = ttk.Combobox(window, width=24, state='readonly', values=municipalities)
    municipality = combobox
    combobox.place(
        x=202.48812866210938,
        y=199.21107482910156,
        width=142.69129943847656,
        height=32.084434509277344
    )


button_5.place(
    x=202.48812866210938,
    y=199.21107482910156,
    width=142.69129943847656,
    height=32.084434509277344
)

button_image_6 = PhotoImage(
    file=relative_to_assets("button_6.png"))
button_6 = Button(
    image=button_image_6,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_6 clicked"),
    relief="flat"
)
button_6.place(
    x=216.0,
    y=629.0,
    width=125.0,
    height=32.0
)

entry_image_1 = PhotoImage(
    file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(
    248.5,
    341.5,
    image=entry_image_1
)
entry_1 = Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0
)
entry_1.place(
    x=196.0,
    y=328.0,
    width=105.0,
    height=25.0
)

entry_image_2 = PhotoImage(
    file=relative_to_assets("entry_2.png"))
entry_bg_2 = canvas.create_image(
    246.5,
    393.5,
    image=entry_image_2
)
entry_2 = Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0
)
entry_2.place(
    x=194.0,
    y=380.0,
    width=105.0,
    height=25.0
)

entry_image_3 = PhotoImage(
    file=relative_to_assets("entry_3.png"))
entry_bg_3 = canvas.create_image(
    256.5,
    449.5,
    image=entry_image_3
)
entry_3 = Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0
)
entry_3.place(
    x=204.0,
    y=436.0,
    width=105.0,
    height=25.0
)

entry_image_4 = PhotoImage(
    file=relative_to_assets("entry_4.png"))
entry_bg_4 = canvas.create_image(
    261.5,
    517.5,
    image=entry_image_4
)
entry_4 = Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0
)
entry_4.place(
    x=209.0,
    y=504.0,
    width=105.0,
    height=25.0
)

entry_image_5 = PhotoImage(
    file=relative_to_assets("entry_5.png"))
entry_bg_5 = canvas.create_image(
    242.5,
    577.5,
    image=entry_image_5
)
entry_5 = Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0
)
entry_5.place(
    x=190.0,
    y=564.0,
    width=105.0,
    height=25.0
)


def home():
    window.resizable(False, False)
    window.mainloop()
