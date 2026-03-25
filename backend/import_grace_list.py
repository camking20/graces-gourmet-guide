"""
Import Grace's restaurant checklist into the database.
Matches against existing restaurants by normalized name, preferring DB names.
New restaurants are added with available metadata from the list notes.
"""

import re
import unicodedata
from models import Restaurant, init_db, SessionLocal

GRACE_LIST_RAW = """
- [x] leonettas
- [ ] Pasquale Jones
- [ ] Olio e Pieu
- [ ] Atla
- [ ] Oxomoco
- [ ] Kimika
- [ ] Vic's
- [ ] Dudley's
- [ ] L'artusi
- [ ] I Sodi
- [ ] Jue Lan Club
- [ ] Little Owl
- [ ] Extra Virgin
- [ ] Minetta Tavern
- [ ] 4 Charles
- [ ] Rubirosa
- [ ] Sunday in Brooklyn
- [ ] The Dutch
- [ ] Pinto Garden
- [ ] Lola Taverna
- [ ] Lure
- [ ] Boucherie
- [ ] Au Cheval
- [ ] Bubby's
- [ ] Lilia
- [ ] Misi
- [ ] Kyma Flatiron
- [x] Cecconi's
- [ ] The Smile
- [ ] Felix Roasting Co.
- [ ] Raoul's
- [ ] Los Tacos No. 1 (Chelsea Market)
- [ ] Dante
- [ ] Uva
- [ ] Mr. Purple
- [ ] Whipped
- [ ] Malibu Farm
- [ ] The Fulton
- [ ] Industry Kitchen
- [ ] Keste
- [x] Joe's Pizza
- [ ] Bleecker Street Pizza
- [ ] Fiaschetteria Pistoia
- [ ] Death by Pizza
- [ ] Pardon my French
- [ ] Chama Mama
- [x] Surreal Creamery
- [x] Jack's Wife Freda
- [ ] Good Thanks
- [ ] Two Hands
- [ ] A Pasta Bar
- [ ] Tacovision
- [ ] Berimbau
- [ ] Torrisi
- [ ] Donut Pub
- [ ] Banter
- [ ] L&B Spumoni Gardens
- [ ] Frenchette
- [x] Rosemary's
- [ ] Le Crocodile
- [x] Forsythia
- [ ] Gemma at the Bowery Hotel
- [ ] Sunflower Cafe
- [ ] The Market Line
- [ ] Biga Bite
- [ ] Butler Coffee
- [ ] Angelina Paris
- [ ] Golden Diner
- [ ] MENO
- [ ] Mah-de-Zehr
- [ ] Thai Diner
- [ ] Roey's
- [ ] Locanda Verde
- [ ] Il Fiorista
- [ ] Anfora
- [ ] Mister Dips
- [ ] Pheasant
- [ ] Rule of Thirds
- [ ] Babs
- [ ] Question
- [ ] Vallata
- [ ] Cafe Cluny
- [ ] Maki Kosaka
- [ ] Sushi on Jone
- [ ] Bandits
- [ ] Cobble & Co
- [ ] Kubeh
- [ ] Her Name Was Carmen
- [ ] Hudson Clearwater
- [ ] Davelle
- [ ] Planta Nomad
- [ ] Nur
- [ ] Jolene
- [ ] Milu
- [ ] Xilonen
- [ ] Fan Fan Donuts
- [ ] Peasant
- [ ] Sunday to Sunday
- [ ] Seven Grams Caffe
- [ ] Dough
- [ ] Ume
- [ ] Momofuku Ko
- [ ] Momofuku Ssam Bar
- [ ] Momofuku Noodle Bar
- [ ] Yellow Rose
- [ ] Gilligan's
- [ ] Gallow Green
- [ ] La Esquina
- [ ] Lamia's Fish Market
- [ ] Westville
- [ ] B'artusi
- [ ] Via Porta
- [ ] Acme
- [ ] Baby Luc's
- [ ] The Campbell
- [ ] Public Records
- [ ] The Spaniard
- [ ] Bar pitti
- [ ] Garrett East
- [x] East Village Pizza (cheesy garlic knots)
- [ ] Sonnyboy
- [ ] Terrace at Edition
- [ ] The Smile
- [ ] Corner Bistro
- [ ] Urban Backyard
- [ ] One White Street
- [ ] Morganstern's Burgers, Fries, and Pies
- [ ] Dame
- [ ] Puglia (big group)
- [ ] Sisters Brooklyn
- [ ] Cervo's
- [ ] Contra
- [ ] Joseph Leonard
- [ ] Ro Burgies
- [ ] Song E Napule
- [ ] Wolfnight's
- [ ] Smashed Burger
- [ ] Palma
- [ ] Coco Pazzeria
- [ ] Nat's on Bank
- [ ] Republic of Booza
- [ ] Bernies
- [ ] Root & Bone
- [ ] Saint Theo's
- [ ] Portale
- [ ] Bronson's Burgers
- [ ] Honestea
- [ ] ZIZI
- [ ] Tacos Guey
- [ ] Harris Bakes
- [ ] Steve's Authentic Key Lime Pies
- [ ] Brooklyn Delicatessen
- [ ] Gallow Green
- [ ] Culture Espresso
- [ ] Brooklyn Crab
- [ ] Lodi
- [ ] Little Shop
- [ ] Day Drinks
- [ ] Employees Only
- [ ] Canary Club
- [ ] Friend of a Farmer (pancakes)
- [ ] Ribbalta
- [ ] Temperance
- [ ] St. Jardim
- [ ] Breakfast by Salt's Cure (OG Pancakes)
- [ ] Ci Siamo
- [ ] Sami and Susu
- [ ] Resident
- [ ] Sogno Toscano
- [ ] The commerce inn
- [x] Waverly Inn
- [ ] Bambina Blue
- [ ] Il cantinori
- [ ] Miracle on 9th Street
- [ ] Emmetts on Grove
- [ ] Zou Zou's
- [ ] Lamalo
- [ ] 8282
- [ ] Hawksmoor
- [ ] Jack and Charlie's 118
- [ ] Earthage Must Be Destroyed
- [ ] Bar Bête
- [ ] Scen
- [ ] Una Pizza Napoleotana
- [ ] Bar Tulix
- [ ] Mel's
- [ ] Manero's Pizza
- [ ] Ten Thousand Coffee
- [ ] Overstory
- [ ] La Cabra
- [x] Casa Carmen
- [ ] The Four Horsemen
- [ ] KYU
- [ ] Mel
- [ ] Alice
- [ ] The Ready Rooftop
- [ ] Five Leaves
- [ ] Omakaseed
- [ ] Le Gamin
- [ ] Holy Water
- [ ] Da Toscano
- [ ] Little Charli
- [ ] Maki Kosaka
- [ ] Casa tua
- [x] Parm
- [ ] 4F
- [ ] DND (Do Not Disturb)
- [ ] Bar Pasquale
- [ ] Maison Premiere
- [ ] Harry's Table
- [x] Thirteen water
- [ ] Emilia by Nai x Coffee Project
- [ ] Martiny's
- [ ] Corner Bar
- [ ] Parcelle Wine
- [ ] Apotheke
- [ ] Champers Social Club
- [ ] Saint (Outdoor garden)
- [ ] Aldama
- [ ] Moustache (Bella Hadid recc)
- [ ] Moonflower
- [ ] Batsu
- [ ] Hags
- [ ] Setsugekka
- [x] Cucina Alba
- [ ] Smyth Tavern
- [ ] Monkey Bar
- [ ] Potluck Club
- [ ] Reception Bar
- [ ] Saint ambroeus
- [ ] Casa Cruz
- [ ] Silver Apricot
- [ ] Shinji's
- [ ] Monsieur Vo
- [ ] The Wesley
- [ ] Fouquets
- [x] Rigor Hill Market
- [ ] Kame
- [ ] Tonchin
- [ ] Casino
- [ ] Ensenada
- [ ] L'Antica Pizzeria da Michele
- [ ] Koloman
- [ ] Gjelina
- [ ] Le Baratin (dinner party w good food)
- [ ] Hilot (bar)
- [ ] Foul Witch
- [ ] C as in Charlie
- [x] Bad Roman
- [ ] Jac's on Bond
- [ ] Moody Tounge Sushi
- [ ] South SoHo Bar
- [ ] Petit Patate
- [ ] Kerber's Farm
- [ ] Principe
- [ ] Stretch Pizza
- [ ] Alba Acconto
- [ ] Revelie Luncheonette
- [ ] RAF's
- [ ] Greywind
- [x] Studio 151
- [ ] Sofreh
- [ ] Para Ici
- [ ] Ciao Evento pasta party
- [ ] Ma Dé
- [ ] Mesiba
- [ ] Tacocina
- [ ] Cipriani
- [ ] Baby Blues
- [ ] Jaffa Cocktail and Raw Bar
- [ ] Rocco's
- [ ] Lillistar
- [ ] Ella Funt
- [ ] Cafe Balerica
- [ ] Ariari
- [ ] El Nico
- [ ] Drift In
- [ ] Tivoli Trattoria
- [ ] Libertine
- [ ] Milady's
- [ ] Spygold (bar Hudson Yards)
- [ ] Shingane
- [ ] Carlotto
- [ ] Chef Competition at Hudson Table
- [ ] Ixta
- [ ] Sushidelic
- [ ] Walker Rooftop (frozen spritz)
- [ ] Coarse NY (spritz hh)
- [ ] Jackdaw (hh)
- [ ] Gnocco (frozen espresso martini)
- [ ] Caffe Coretto
- [ ] Gab's
- [ ] The Wooley (grapefruit brulee)
- [ ] The Love Bakery by Erica
- [ ] Ciao Gloria
- [ ] Roscioli
- [ ] Port Said
- [ ] Madeline's Martini
- [ ] Emporio
- [x] Cecchi's
- [ ] Homemade by Bruno pasta making class
- [ ] Kobrick's (matcha martini)
- [ ] Cafe Chelsea
- [ ] Pomp & Circumstance (hh deal)
- [ ] Jean's Lafayette
- [ ] Bangkok Supper Club
- [x] Happier Grocery
- [ ] Scarpetta
- [ ] Jazba
- [ ] Southern Charm (brunch)
- [ ] Mari.ne
- [x] The Portrait Bar
- [ ] Hamburger America
- [ ] Tigre (bar)
- [ ] Le B
- [ ] Chino Grande (dinn and karaoke!)
- [ ] Hoexter's
- [ ] Meduza
- [ ] Lupetto
- [ ] Lucky Rabbit Noodle (matzo ball soup dumpling)
- [ ] Fossetta
- [ ] Afternoon tea at Aman
- [ ] Chelsea living room (live music Thursdays, get off menu lemon pie cocktail)
- [ ] Sip and Guzzle
- [ ] Frog Club
- [x] San Sabino
- [ ] COCODAQ
- [ ] Beefbar
- [ ] B&H Dairy
- [ ] Penny
- [ ] Falanzi (Asian Mexican fusion)
- [ ] Andie's Eats (duh)
- [ ] Only Love Strangers (jazz bar!)
- [ ] Apollo Bagels (LA sourdough bagels)
- [x] This bowl (Asian bowl place from Australia)
- [ ] Maki mono (fresh onigiri Chelsea Market)
- [ ] Tolo (Chinese place by Parcelles)
- [ ] Corima (Mexican Japanese contra alum)
- [ ] Tucci (vodka chicken parm)
- [ ] Amarena (Italian near us by Toloache team)
- [ ] Not as bitter (sweet treat coffee)
- [ ] Rose room lounge (espresso martini bar)
- [ ] The Highlight Room ($5 rose happy hour)
- [ ] Settepani Bakery (rainbow cookie croissant)
- [ ] Theodora (Mediterranean from people behind miss ada)
- [ ] Museum Coffee (candied croissant slices dipped in chocolate)
- [ ] Bar Primi (new location by work)
- [ ] Fini Pizza at Dante Fridays 12-6
- [ ] Crispy Heaven (brunch board)
- [ ] Shaken Not Stirred (cocktail bar on UES)
- [ ] Also Sohm wine bar (theater district, wine bar by le bernardin team)
- [ ] Janie's Life Changing Baked Goods (rainbow cookie pie crust cookie for pride!)
- [ ] Miriam (Israeli, UWS)
- [ ] Conwell Coffee Hall (fidi, gorg laptop friendly cafe)
- [ ] Good Guys (spritz bar)
- [ ] L'incontra by Rocco (new Italian on UES)
- [ ] Salswee (truffle croissant)
- [x] Massara (new restaurant from Rezdoa team, pizzetes!)
- [ ] Da Andrea (pretty, big italian restaurant in Chelsea)
- [ ] Noa, a café (date caramel drizzle frozen cold brew, matcha cloud drink)
- [ ] Hungry Llama cafe (whipped honey latte)
- [ ] Frances at Casa Cruz (rooftop UES)
- [ ] Eel Bar (cervo's team)
- [ ] Carlota (tapas bar)
- [ ] Bar Whimsy (cocktail bar in Olly Olly market)
- [ ] Sartianos
- [ ] Champagne Problems (taylor swift speakeasy)
- [ ] Wildflower (Chelsea, drinks and garden)
- [ ] Dirty Taco Tacomakase (6 seats 6 nights a month grand central terminal)
- [ ] Angels Share (speakeasy cool drinks west village)
- [x] Lil Frankie's
- [ ] Quique Crudo (Mexican west village)
- [ ] Atoboy (nomad, $75 4 course tasting menu from Atomix team)
- [ ] Hidden Grounds (East village Nola style cold brew)
- [ ] Early Terrible (Les, restaurant with club next door, walnut cake looks amazing and roast chicken)
- [ ] Sushiro (handroll bar WV)
- [ ] The Garden at the Standard EV (hh)
- [ ] Bar Contra (Mexican cocktails and bites, SoHo)
- [ ] Twentyonegrains (fast casual, Hell's Kitchen, healthy)
- [ ] Chloe (SoHo, vegan fast casual)
- [ ] Midnight Blue (jazz bar, gramercy)
- [ ] Bar Bonobo (Chelsea, fun cocktails)
- [ ] The pickle guys (pickle store LES)
- [ ] Green lane coffee (UES)
- [ ] Madison fare (organic Greek frozen yogurt ues)
- [ ] Cello's Pizzeria (EV, owner worked at L'industrie and PJ)
- [ ] Place des Fêtes (wine bar, BK)
- [ ] Temakase (hand roll bar nomad)
- [ ] Bar vivant (wine bar UES)
- [ ] SEA (nomad, jungsik chefs)
- [ ] Oases (ayurvedic café chelsea)
- [ ] La Bomboniera (Italian wine bar UES)
- [ ] The Corner Store (American martinis SoHo)
- [ ] Sushi by Scratch (omakase speakeasy)
- [ ] Souen (macrobiotic Japanese)
- [ ] Tall Poppy (croissants, flatiron)
- [ ] Taiko (casual Greek, Chelsea)
- [ ] Parla (Italian UWS)
- [ ] Experimental Cocktail Club (Flatiron, croissant kir royale cocktail)
- [ ] Borgo (Italian Flatiron)
- [ ] Little Mint (Thai with low carb noodles)
- [ ] Pearl Box (cocktail and caviar bar SoHo)
- [ ] Hero's (restaurant under Pearl Box)
- [ ] Petit Chou (laminated croissant BEC)
- [ ] Dialogue Café (flower themed coffee shop LES, carrot cake latte)
- [ ] Desert 5 Spot (cowboy cocktail bar, make a rez, Williamsburg)
- [ ] Bridges (Chinatown, Estela alum)
- [ ] Waiting on a Friend (cocktail bar EV, matchapeno, go out here)
- [ ] Clemente Bar (EMP chefs)
- [ ] Carbone
- [ ] Sloane's (hotel bar, soho, chicken nuggets and fries)
- [ ] Time and Tide (seafood flatiron)
- [ ] Nightly's (UES, American bistro)
- [ ] Crazy Pizza (party pizza restaurant SoHo)
- [ ] Twin Tails (Asian restaurant by Don Angie owners in Columbus Circle)
- [ ] Soso's (soho, cool lounge)
- [ ] The Hand Roll Bar (west village martini hand roll pairings behind moody tounge)
- [ ] Mary O's Irish Soda Bread Shop (scones, East village)
- [ ] Apt 5 (cocktail bar LES)
- [ ] Kanyakumari (Indian union square)
- [ ] Bar Miller (omakase from people behind Rosella)
- [ ] Zimmi's (WV, French, cozy farm to table vibes)
- [ ] Piccola Cucina Estiatorio
- [ ] Moody Tongue Pizza (Tokyo pizza)
- [ ] Cocoran (soba LES)
- [ ] Ho Foods (Taiwanese, EV, scallion pancake sandwich)
- [ ] Frena (Mediterranean Hell's Kitchen)
- [ ] The Snail (4 Charles owner with a burger Brooklyn)
- [ ] Mitsuru (sushi and wine by Parcelles, WV)
- [ ] Le Bar Penelope (cocktail piano bar ues from avra group)
- [ ] Elvis (wine bar noho)
- [ ] Crevette (seafood, same owner as Dame and Lord's, WV)
- [ ] Ceres (pizza EMP alums, soho)
- [ ] Café Commerce (French UES)
- [ ] Café Zaffri (Persian, Raf's team, vibes, union square area)
- [ ] Schmuck (cocktail bar EV)
- [ ] Santi (pasta Midtown same owners as Marea)
- [ ] Monsieur (medieval themed cocktail bar ev)
- [ ] Avra
- [ ] Golden Hof + NY Kimchi (Golden Diner team midtown)
- [ ] Papa San (Peruvian Hudson Yards same team as Llama San)
- [x] Opto (Italian flatiron)
- [ ] Dear Stranger (cocktail bar WV same owners employees only)
- [ ] The Lavaux (wine bar WV secret message party)
- [ ] Bar à Part (wine bar from Zimmi's team WV)
- [ ] Monsieur Bistro (French bistro UES Maison Close team)
- [ ] F&F Restaurant (Carroll Gardens f&f pizza team)
- [ ] The Gallery (Flatiron clear espresso martini)
- [ ] Isla and Co (Midtown espresso martini flight)
- [ ] Bar Snack (NoHo food themed cocktails)
- [ ] Sakagura (Japanese Midtown so close to work!)
- [ ] Kobano (sushi Bowery)
- [ ] Foreigner (crème brulée latte Chelsea)
- [ ] Obvio (cocktail bar Nomad)
- [ ] Red Room (cocktail bar inside Printmeps, FiDi)
- [ ] Lucy's (dive bar EV The Nines team)
- [ ] Leonessa (aperitivo inspired bar FiDi - SGROPINO ALERT)
- [ ] El Camino (cocktail bar EV, well priced)
- [x] Café Paradiso (soho, same owners as Dante, americano w panna cold foam)
- [ ] Sunlife Organics (SoHo)
- [ ] Hussey pop-up at Standard EV (Mexican)
- [ ] The Little Shop (LES speakeasy behind bodega, can plate bodega snacks)
- [ ] Buba Bureka (NYC's first bureka shop Greenwich village)
- [ ] Shirokuro (omakase EV unique restaurant design)
- [ ] Bergamo's (post work bar to meet men in finance)
- [ ] Bar Revival (hh LES)
- [ ] Charcuterie (charcuterie boxes and snacks by Central Park entrance 58 and 7th)
- [ ] Go Go Sing (karaoke bar inside Cocodaq)
- [ ] Maison Passerelle (restaurant inside Printemps FiDi)
- [ ] Sunn's (Korean wine bar LES - banchan)
- [ ] Peasant (Italian nolita giving date)
- [ ] Super Nice Pizza (pizza UWS)
- [ ] A Bar Called Pancakes (bar pop-up at S&P lunch on weekends May 1-June 3)
- [ ] Gazette (wine bar UES fun drinks)
- [ ] Dante Apertivio Bar (WV)
- [ ] Greenwich Street Tavern (Tribeca, go to meet boys watching sports)
- [ ] Bar Bianche (apertivio bar EV)
- [ ] JR & Son (rainbow cookie layer cake Greenpoint)
- [ ] Drai's Supper Club (restaurant + cocktail lounge WV)
- [ ] People's (dinner into going out WV)
- [ ] Rivareno (gelato SoHo)
- [ ] Adda (Indian EV)
- [ ] Suki Desu (kaisendon UES)
- [ ] Papa D'Amour (Japanese French fusion bakery by Dominique Ansel Greenwich Village)
- [ ] Terra (healthy fast casual Chelsea)
- [ ] Fortuna (Israeli Gramercy)
- [ ] Carinito (Michelin star tacos Union Square)
- [ ] Marlow (Mediterranean bistro UES)
- [ ] Mangetsu (Japanese speakeasy Chelsea)
- [ ] Le Chêne (French WV)
- [ ] Mamma Mezze (Mediterranean Flatiron from La Pecora team)
- [ ] Pull Tab Coffee (Bryant Park, aerofoam latte)
- [ ] Oyamel by José (Mexican José Andres Hudson Yards - salt foam margs)
- [ ] Mymo Kafé (Dubai chocolate bears Times Square)
- [ ] The Campbell (bar where Nate cheats on Blair gossip girl Midtown)
- [ ] The Chocolate Room (Brooklyn chocolate cake!)
- [ ] Pantry (coffee shop inside Madhappy SoHo)
- [ ] Messy (kebab fast casual SoHo)
- [ ] Milk flower (50 top pizza Astoria)
- [ ] Mamo
- [x] All Antico Vinaio (happy hour any location drink and half sandwich $15)
- [ ] Comal (Mexican Chinatown)
- [ ] Gelatoville (Dubai chocolate gelato Chelsea, Hell's Kitchen)
- [ ] Alessa's (Italian, Cacio e Pepe butter, hazelnut skillet cookie Parmesan tuille, Penn District)
- [ ] Quick Eternity (nautical theme wine bar South St seaport)
- [ ] The Gyro Project (UWS Greek fro yo)
- [ ] Cuerno (Mexican steakhouse theatre district)
- [ ] Virginias
- [x] Soothr
- [x] Upland
- [x] Isabelle's Osteria
- [x] Danny's NYC
- [ ] American bar
- [ ] Anton's
- [ ] The grill
- [ ] Piccola Cucina Estiatorio
- [ ] Saint ambroeus
- [ ] Scarpetta
- [ ] Carbone
- [ ] Bar pitti
- [ ] Torrisi
"""


def normalize(name: str) -> str:
    """Normalize a name for fuzzy matching."""
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r"[''`\"]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s


NEIGHBORHOOD_HINTS = {
    "ev": "East Village",
    "east village": "East Village",
    "wv": "West Village",
    "west village": "West Village",
    "les": "Lower East Side",
    "ues": "Upper East Side",
    "uws": "Upper West Side",
    "soho": "SoHo",
    "noho": "NoHo",
    "nolita": "Nolita",
    "chelsea": "Chelsea",
    "flatiron": "Flatiron",
    "fidi": "FiDi",
    "tribeca": "Tribeca",
    "greenpoint": "Greenpoint",
    "williamsburg": "Williamsburg",
    "bk": "Brooklyn",
    "brooklyn": "Brooklyn",
    "gramercy": "Gramercy",
    "nomad": "NoMad",
    "midtown": "Midtown",
    "hells kitchen": "Hell's Kitchen",
    "hell's kitchen": "Hell's Kitchen",
    "hudson yards": "Hudson Yards",
    "astoria": "Astoria",
    "chinatown": "Chinatown",
    "union square": "Union Square",
}


def parse_list():
    """Parse the markdown checklist into structured entries."""
    entries = []
    for line in GRACE_LIST_RAW.strip().splitlines():
        line = line.strip()
        if not line or not line.startswith("- ["):
            continue

        visited = line.startswith("- [x]")
        rest = re.sub(r"^- \[.\]\s*", "", line).strip()
        if not rest:
            continue

        paren_match = re.match(r"^(.+?)\s*\((.+)\)\s*$", rest)
        if paren_match:
            name = paren_match.group(1).strip()
            notes = paren_match.group(2).strip()
        else:
            name = rest.strip()
            notes = ""

        neighborhood = None
        if notes:
            notes_lower = notes.lower()
            for hint, hood in NEIGHBORHOOD_HINTS.items():
                if re.search(r"\b" + re.escape(hint) + r"\b", notes_lower):
                    neighborhood = hood
                    break

        entries.append({
            "name": name,
            "visited": visited,
            "notes": notes,
            "neighborhood_hint": neighborhood,
        })
    return entries


def find_best_match(entry_name: str, db_restaurants: list):
    """
    Try to match an entry name to an existing DB restaurant.
    Returns the DB restaurant object if found, None otherwise.
    """
    norm_entry = normalize(entry_name)

    for r in db_restaurants:
        if normalize(r.name) == norm_entry:
            return r

    for r in db_restaurants:
        nr = normalize(r.name)
        if nr.startswith(norm_entry) or norm_entry.startswith(nr):
            return r

    entry_words = set(norm_entry.split())
    if len(entry_words) >= 2:
        for r in db_restaurants:
            db_words = set(normalize(r.name).split())
            overlap = entry_words & db_words
            if len(overlap) >= 2 and len(overlap) / max(len(entry_words), len(db_words)) >= 0.6:
                return r

    return None


def run_import():
    init_db()
    db = SessionLocal()

    db_restaurants = db.query(Restaurant).all()
    print(f"Existing restaurants in DB: {len(db_restaurants)}")

    entries = parse_list()
    print(f"Entries parsed from Grace's list: {len(entries)}")

    matched = 0
    added = 0
    skipped_dupes = 0
    seen_db_ids = set()
    seen_normalized = set()

    for entry in entries:
        norm = normalize(entry["name"])
        if norm in seen_normalized:
            skipped_dupes += 1
            continue
        seen_normalized.add(norm)

        match = find_best_match(entry["name"], db_restaurants)

        if match:
            if match.id in seen_db_ids:
                skipped_dupes += 1
                continue
            seen_db_ids.add(match.id)

            if match.visited != entry["visited"]:
                match.visited = entry["visited"]
            matched += 1
        else:
            new_restaurant = Restaurant(
                name=entry["name"],
                visited=entry["visited"],
                notes=entry["notes"],
                neighborhood=entry["neighborhood_hint"],
                booking_urls={},
                monitor_enabled=False,
                priority="normal",
            )
            db.add(new_restaurant)
            added += 1

    db.commit()
    db.close()

    print(f"\nResults:")
    print(f"  Matched existing: {matched}")
    print(f"  Added new:        {added}")
    print(f"  Skipped dupes:    {skipped_dupes}")


if __name__ == "__main__":
    run_import()
