from pathlib import Path
from tkinter import Tk, Canvas, Entry, Button, PhotoImage, filedialog, ttk
import csv
import requests
from genetic_algorithm import genetic_algorithm_restaurant
from utilities.utlity import print_list


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"assets\frame0")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


window = Tk()
window.title("Restaurant Selector")
window.geometry("1230x720")
window.configure(bg = "#FFFFFF")


canvas = Canvas(
    window,
    bg = "#FFFFFF",
    height = 720,
    width = 1230,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    615.0,
    360.0,
    image=image_image_1
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



# Dataset
button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: read_csv(),
    relief="flat"
)
button_1.place(
    x=103.0,
    y=174.0,
    width=142.69129943847656,
    height=32.084434509277344
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


# Dispositivo
button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: get_location(),
    relief="flat"
)
button_2.place(
    x=146.0,
    y=228.0,
    width=142.69129943847656,
    height=32.084434509277344
)


def obtain_data():
    
    '''
        Pob. Inicial: entry_1
        Pob.Maxima: entry_3
        Iteraciones: entry_2
        Prob.Cruza: entry_4
        Mut. Ind: entry_5
        Mut.Gen: entry_6
    '''
    
    data = []
    data.append(entry_1.get())
    data.append(entry_2.get())
    data.append(entry_3.get())
    data.append(entry_4.get())
    data.append(entry_5.get())
    data.append(entry_6.get())
    
    for entry in data:
        print(entry)


def get_data():
    data_ok = True
    try:
        initial_population = int(entry_1.get().strip())
        max_population = int(entry_3.get().strip())
        str_prob_mut_ind = entry_5.get().strip()
        str_prob_mut_gen = entry_6.get().strip()
        prob_cross = entry_4.get().strip()
        if str_prob_mut_ind.isdigit():
            prob_mut_ind = int(str_prob_mut_ind)
        else:
            prob_mut_ind = float(str_prob_mut_ind)
        if str_prob_mut_gen.isdigit():
            prob_mut_gen = int(str_prob_mut_gen)
        else:
            prob_mut_gen = float(str_prob_mut_gen)
        iterations = int(entry_2.get().strip())
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
                                                                                            3, max_population, prob_cross,
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


# Resolver
button_image_3 = PhotoImage(
    file=relative_to_assets("button_3.png"))
button_3 = Button(
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: get_data(),
    relief="flat"
)
button_3.place(
    x=149.0,
    y=580.0,
    width=114.0,
    height=32.0
)

# button_3.place(
#     x=149.0,
#     y=620.0,
#     width=114.0,
#     height=32.0
# )


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
        x=323.0,
        y=228.0,
        width=142.69129943847656,
        height=32.084434509277344
    )


# Municipio
button_image_4 = PhotoImage(
    file=relative_to_assets("button_4.png"))
button_4 = Button(
    image=button_image_4,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: get_municipalities(),
    relief="flat"
)
button_4.place(
    x=323.0,
    y=228.0,
    width=142.69129943847656,
    height=32.084434509277344
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
        x=295.0,
        y=174.0,
        width=176.0,
        height=32.0
    )


# Tipo de comida
button_image_5 = PhotoImage(
    file=relative_to_assets("button_5.png"))
button_5 = Button(
    image=button_image_5,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: get_type_food(),
    relief="flat"
)
button_5.place(
    x=295.0,
    y=174.0,
    width=176.0,
    height=32.0
)

# Graficar
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
    x=294.0,
    y=580.0,
    width=125.0,
    height=32.0
)

# button_6.place(
#     x=294.0,
#     y=620.0,
#     width=125.0,
#     height=32.0
# )


image_image_2 = PhotoImage(
    file=relative_to_assets("image_2.png"))
image_2 = canvas.create_image(
    294.0,
    607.0,
    image=image_image_2
)


# # Minimización
# button_image_7 = PhotoImage(
#     file=relative_to_assets("button_7.png"))
# button_7 = Button(
#     image=button_image_7,
#     borderwidth=0,
#     highlightthickness=0,
#     command=lambda: print("button_7 clicked"),
#     relief="flat"
# )
# button_7.place(
#     x=292.0,
#     y=540.0,
#     width=137.0,
#     height=32.0
# )

# # Maximización
# button_image_8 = PhotoImage(
#     file=relative_to_assets("button_8.png"))
# button_8 = Button(
#     image=button_image_8,
#     borderwidth=0,
#     highlightthickness=0,
#     command=lambda: print("button_8 clicked"),
#     relief="flat"
# )


# button_8.place(
#     x=133.0,
#     y=540.0,
#     width=137.0,
#     height=32.0
# )

entry_image_1 = PhotoImage(
    file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(
    198.0,
    309.5,
    image=entry_image_1
)
entry_1 = Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0
)
entry_1.place(
    x=163.0,
    y=296.0,
    width=70.0,
    height=25.0
)

entry_image_2 = PhotoImage(
    file=relative_to_assets("entry_2.png"))
entry_bg_2 = canvas.create_image(
    198.0,
    377.5,
    image=entry_image_2
)
entry_2 = Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0
)
entry_2.place(
    x=163.0,
    y=364.0,
    width=70.0,
    height=25.0
)

entry_image_3 = PhotoImage(
    file=relative_to_assets("entry_3.png"))
entry_bg_3 = canvas.create_image(
    441.5,
    309.5,
    image=entry_image_3
)
entry_3 = Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0
)
entry_3.place(
    x=408.0,
    y=296.0,
    width=67.0,
    height=25.0
)

entry_image_4 = PhotoImage(
    file=relative_to_assets("entry_4.png"))
entry_bg_4 = canvas.create_image(
    467.5,
    377.5,
    image=entry_image_4
)
entry_4 = Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0
)
entry_4.place(
    x=423.0,
    y=364.0,
    width=89.0,
    height=25.0
)

entry_image_5 = PhotoImage(
    file=relative_to_assets("entry_5.png"))
entry_bg_5 = canvas.create_image(
    229.0,
    449.5,
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
    y=436.0,
    width=78.0,
    height=25.0
)

entry_image_6 = PhotoImage(
    file=relative_to_assets("entry_6.png"))
entry_bg_6 = canvas.create_image(
    505.5,
    449.5,
    image=entry_image_6
)
entry_6 = Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0
)
entry_6.place(
    x=473.0,
    y=436.0,
    width=65.0,
    height=25.0
)


def home():
    window.resizable(False, False)
    window.mainloop()
