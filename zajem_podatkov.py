import csv
import os
import requests
import re

frontpage_url = "https://dogtime.com/dog-breeds/profiles"
# mapa, v katero bom shranila podatke
dog_directory = os.path.join(sys.path[0], 'dog_save')
# ime datoteke v katero bom shranila glavno stran
frontpage_filename = "index_kuzki.html" #spremenit
# ime csv datoteke, v katero bomo shranili podatke
csv_filename = "kuzki.csv"

#ce bo csv datotek prevec pol jih ne vkljucis

#tega zdej ne rabm
re_pick_links_block = re.compile(
    r'<a class="list-item-title" href=(.*?)>',
    flags=re.DOTALL
)

re_pick_link = re.compile(
    r'<a class="list-item-title" href="https://dogtime.com/dog-breeds(.*?)"',
    flags=re.DOTALL
)

re_name_from_link = re.compile(
    r'/(?P<name>.*?)',
    flags=re.DOTALL
)

# primer = "<div class="list-item">
# <a class="list-item-img" href="https://dogtime.com/dog-breeds/afador">
# <img class="list-item-breed-img" src="https://www.dogtime.com/assets/uploads/2019/08/afador-mixed-dog-breed-pictures-cover-650x368.jpg" alt="Afador" ></a>
# <a class="list-item-title" href="https://dogtime.com/dog-breeds/afador">Afador</a></div>"


def download_url_to_string(url):
    """Funkcija kot argument sprejme niz in poskusi vrniti vsebino te spletne
    strani kot niz. V primeru, da med izvajanje pride do napake vrne None.
    """
    try:
        # del kode, ki morda sproži napako
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        # koda, ki se izvede pri napaki
        # dovolj je če izpišemo opozorilo in prekinemo izvajanje funkcije
        print("Napaka pri povezovanju do:", url)
        return None
    # nadaljujemo s kodo če ni prišlo do napake
    if r.status_code == requests.codes.ok:
        return r.text
    else:
        print("Napaka pri prenosu strani:", url)
        return None

def save_string_to_file(text, directory, filename):
    """Funkcija zapiše vrednost parametra "text" v novo ustvarjeno datoteko
    locirano v "directory"/"filename", ali povozi obstoječo. V primeru, da je
    niz "directory" prazen datoteko ustvari v trenutni mapi.
    """
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as file_out:
        file_out.write(text)
    return None

def save_frontpage(directory, filename):
    """Funkcija vrne celotno vsebino datoteke "directory"/"filename" kot niz"""
    text = download_url_to_string(frontpage_url)
    save_string_to_file(text, directory, filename)
    return None

# nova fuja
def save_pages_to_file(directory, filename):
    with open(os.path.join(directory, filename), "r", encoding='utf-8') as dat:
        vsebina = dat.read()
    #cel_block = re_pick_links_block.findall(vsebina)[0]
    sez_linkov = re_pick_link.findall(vsebina)
    print(sez_linkov)
    #/'afador' je link
    for link in sez_linkov:
        stran = requests.get('https://dogtime.com/dog-breeds' + link)
        names_dict = re_name_from_link.search(link)
        print(names_dict)
        ime_mape_posamezno = '{}.html'.format(names_dict['name'])
        full_filepath = os.path.join(directory, ime_mape_posamezno)
        with open(full_filepath, 'w', encoding='utf-8') as posamezna_dat:
            posamezna_dat.write(stran.text)
    return None

####################################################
# funkcije za obdelanje podatkov
####################################################

vzorec_profila = re.compile(
    r'Adaptability</h3><div class="characteristic-star-block"><div class="star star-(?P<adaptability>\w)">'
    r'All Around Friendliness</h3><div class="characteristic-star-block"><div class="star star-(?P<friendliness>\w)">'
    r'Health And Grooming Needs</h3><div class="characteristic-star-block"><div class="star star-(?P<health_and_needs>\w)">'
    r'Trainability</h3><div class="characteristic-star-block"><div class="star star-(?P<trainability>\w)">'
    r'Physical Needs</h3><div class="characteristic-star-block"><div class="star star-(?P<physical_needs>\w)">'
    r'<div class="vital-stat-title vital-stat-group">Dog Breed Group:</div>(?P<breed_group>.*?)</div>'
    r'<div class="vital-stat-title vital-stat-height">Height:</div>(?P<height>.*?)</div>'
    r'<div class="vital-stat-title vital-stat-weight">Weight:</div>(?P<weight>.*?)</div>'
    r'<div class="vital-stat-title vital-stat-lifespan">Life Span:</div>(?P<life_span>.*?)</div>'
    flags=re.DOTALL
)

# dodana
def read_information(directory):
    podatki = []
    for filename in os.listdir(directory):
        if filename != 'index_kuzki.html':
            full_path = os.path.join(directory, filename)
            with open(full_path, 'r', encoding='utf-8') as dat:
                vsebina = dat.read()
                podatki.append(get_information(vsebina)) #napisi to fujo
        else:
            continue
    return podatki

def get_information(text):
    kuzi = vzorec_profila.search(text).groupdict()
    kuzi['adaptability'] = int(kuzi['adaptability'])
    kuzi['friendliness'] = int(kuzi['friendliness'])
    kuzi['health_and_needs'] = int(kuzi['health_and_needs'])
    kuzi['trainability'] = int(kuzi['trainability'])
    kuzi['physical_needs'] = int(kuzi['physical_needs'])

    visina_sez = kuzi['height'].split()
    if len(visina_sez) == 4:
        visina_od_v_p = int(visina_sez[0])
        visina_do_v_p = int(visina_sez[2])
        kuzi['height_od'] = inches_to_cm(visina_od_v_p)
        kuzi['height_do'] = inches_to_cm(visina_do_v_p)
    elif len(visina_sez) == 2:
        visina_v_p = int(visina_sez[0])
        kuzi['height_od'] = inches_to_cm(visina_v_p)
        kuzi['height_do'] = inches_to_cm(visina_v_p)
    else:
        continue
    
    teza_sez = kuzi['weight'].split()
    if len(teza_sez) == 4:
        teza_od_v_p = int(teza_sez[0])
        teza_do_v_p = int(teza_sez[2])
        kuzi['weight_od'] = pounds_to_kg(teza_od_v_p)
        kuzi['weight_do'] = pounds_to_kg(teza_do_v_p)
    elif len(teza_sez) == 2:
        visina_v_p = int(teza_sez[0])
        kuzi['weight_od'] = pounds_to_kg(teza_v_p)
        kuzi['weight_do'] = pounds_to_kg(teza_v_p)
    else:
        continue

    zivljenje = kuzi['life_span'].split()
    if len(zivljenje) == 4:
        ziv_od = int(zivljenje[0])
        ziv_do = int(zivljenje[2])
        kuzi['life_od'] = ziv_od 
        kuzi['life_do'] = ziv_do
    
    elif len(zivljenje) == 2:
        ziv = int(zivljenje[0])
        kuzi['life_od'] = ziv
        kuzi['life_do'] = ziv
    
    else:
        continue
    
    return kuzi

def inches_to_cm(visina):
    v_cm = visina // 0.39370
    return int(v_cm)
    
def pounds_to_kg(teza):
    v_kg = teza // 2.2046
    return int(v_kg)

    
################# od tuki naprej bo treba spremenit
#ta funkcija bo mogla bit drugacna
def read_file_to_string(directory, filename):
    """Funkcija vrne celotno vsebino datoteke "directory"/"filename" kot niz"""
    path = os.path.join(directory, filename)
    with open(path, 'r', encoding='utf-8') as file_in:
        return file_in.read()

# primer = "<div class="list-item">
# <a class="list-item-img" href="https://dogtime.com/dog-breeds/afador">
# <img class="list-item-breed-img" src="https://www.dogtime.com/assets/uploads/2019/08/afador-mixed-dog-breed-pictures-cover-650x368.jpg" alt="Afador" ></a>
# <a class="list-item-title" href="https://dogtime.com/dog-breeds/afador">Afador</a></div>"

def page_to_ads(page_content):
    """Funkcija poišče posamezne oglase, ki se nahajajo v spletni strani in
    vrne njih seznam"""
    rx = re.compile(r'<div class="list-item"><a class="list-item-img"'
                    r'(.*?)</a></div>',
                    re.DOTALL)
    ads = re.findall(rx, page_content)
    return ads

def get_dict_from_ad_block(block):
    """Funkcija iz niza za posamezen oglasni blok izlušči podatke o imenu,
    lokaciji, datumu objave in ceni ter vrne slovar, ki vsebuje ustrezne
    podatke"""
    rx = re.compile(r'alt=(?P<name>.*?) >',
                    re.DOTALL)
    data = re.search(rx, block)
    ad_dict = data.groupdict()
    return ad_dict



def ads_from_file(filename, directory):
    """Funkcija prebere podatke v datoteki "directory"/"filename" in jih
   pretvori (razčleni) v pripadajoč seznam slovarjev za vsak oglas posebej."""
    page = read_file_to_string(directory, filename)
    blocks = page_to_ads(page)
    ads = [get_dict_from_ad_block(block) for block in blocks]
    return ads


def ads_frontpage():
    return ads_from_file(cat_directory, frontpage_filename)

##############################################
# obdelane podatke želimo shraniti
#############################################

def write_csv(fieldnames, rows, directory, filename):
    """
    Funkcija v csv datoteko podano s parametroma "directory"/"filename" zapiše
    vrednosti v parametru "rows" pripadajoče ključem podanim v "fieldnames"
    """
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return None

def write_dog_ads_to_csv(ads, directory, filename):
    """Funkcija vse podatke iz parametra "ads" zapiše v csv datoteko podano s
    parametroma "directory"/"filename". Funkcija predpostavi, da so ključi vseh
    slovarjev parametra ads enaki in je seznam ads neprazen."""
    # Stavek assert preveri da zahteva velja
    # Če drži se program normalno izvaja, drugače pa sproži napako
    # Prednost je v tem, da ga lahko pod določenimi pogoji izklopimo v
    # produkcijskem okolju
    assert ads and (all(j.keys() == ads[0].keys() for j in ads))
    write_csv(ads[0].keys(), ads, directory, filename)

#######################################

def main(redownload=True, reparse=True):
    """Funkcija izvede celoten del pridobivanja podatkov:
    1. Oglase prenese iz bolhe
    2. Lokalno html datoteko pretvori v lepšo predstavitev podatkov
    3. Podatke shrani v csv datoteko
    """
    # v lokalno datoteko shranimo glavno stran
    save_frontpage(dog_directory, frontpage_filename)

    save_pages_to_file(dog_directory, frontpage_filename)
    # iz lokalne html datoteke preberemo podatke
#    ads = page_to_ads(read_file_to_string(dog_directory, frontpage_filename))

    # Podatke preberemo v lepšo obliko (seznam slovarjev)
#   ads_nice = [get_dict_from_ad_block(ad) for ad in ads]
#    print(ads_from_file(frontpage_filename, dog_directory))

    # podatke shranimo v csv datoteko
#   write_dog_ads_to_csv(ads_nice, dog_directory, csv_filename)

if __name__ == "__main__":
    main()