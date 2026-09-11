"""
game_ids.py - Complete Supercell Titan Global ID Catalog & Search Utility
========================================================================
Explains the internal architecture of Hay Day Global IDs and provides
instant lookup for any Item, Building, Animal, Feed, Tool, or Recipe.

TITAN GLOBAL ID FORMULA:
  GlobalID = (ClassID * 1,000,000) + InstanceIndex

CLASS IDS:
  Class  4: Field Crops & Plants (Wheat, Corn, Carrot, Soybean...)
  Class  6: Animal Feeds (Chicken Feed, Cow Feed, Pig Feed...)
  Class 11: Manufactured Goods & Recipes (Bread, Butter, Cream, Sugar...)
  Class 13: Buildings, Machines, Pens, Trees & Bushes (Bakery, Dairy, Coops...)
  Class 18: Tools, Mining Supplies & Expansion Items (Saws, Nails, Bolts...)
  Class 23: Animals & Livestock (Chickens, Cows, Pigs, Sheep, Goats...)
"""

import sys

# Comprehensive Master Catalog of Hay Day Global IDs
CROPS = {
    400000: "Wheat (Crop entity)",
    400001: "Wheat (Silo/Shop Item)",
    400002: "Corn",
    400003: "Soybean",
    400004: "Sugarcane",
    400005: "Carrot",
    400006: "Indigo",
    400007: "Pumpkin",
    400008: "Cotton",
    400009: "Chili Pepper",
    400010: "Tomato",
    400011: "Strawberry",
    400012: "Potato",
    400013: "Rice",
    400014: "Lettuce",
    400015: "Lavender",
    400016: "Tea Leaf",
    400017: "Onion",
    400018: "Cucumber",
    400019: "Bell Pepper",
    400020: "Broccoli",
    400021: "Mint",
    400022: "Ginger",
    400023: "Garlic",
    400024: "Watermelon",
    400025: "Clay",
}

FEEDS = {
    600001: "Chicken Feed (Variant 1)",
    600002: "Chicken Feed (Standard)",
    600003: "Cow Feed",
    600004: "Pig Feed",
    600005: "Sheep Feed",
    600006: "Goat Feed",
}

RECIPES_AND_GOODS = {
    # Dairy Products
    1100000: "Cream",
    1100001: "Butter",
    1100002: "Cheese",
    1100003: "Goat Cheese",
    
    # Sugar Mill
    1100013: "Brown Sugar",
    1100014: "White Sugar",
    1100015: "Bread (Bakery)",
    1100016: "Corn Bread (Bakery)",
    1100017: "Cookie (Bakery)",
    1100018: "Syrup (Sugar Mill)",
    
    # Bakery & Oven
    1100019: "Pizza",
    1100020: "Spicy Pizza",
    1100021: "Potato Bread",
    1100022: "Frutti di Mare Pizza",
    1100023: "Banana Bread",
    
    # Grill
    1100024: "Pancake",
    1100025: "Bacon and Eggs",
    1100026: "Hamburger",
    1100027: "Fish Burger",
    1100028: "Roasted Tomatoes",
    1100029: "Baked Potato",
    1100030: "Grilled Onion",
    
    # Popcorn Pot
    1100031: "Popcorn",
    1100032: "Buttered Popcorn",
    1100033: "Chili Popcorn",
    1100034: "Honey Popcorn",
    1100035: "Chocolate Popcorn",
    
    # Pie Oven
    1100040: "Carrot Pie",
    1100041: "Pumpkin Pie",
    1100042: "Bacon Pie",
    1100043: "Apple Pie",
    1100044: "Fish Pie",
    1100045: "Feta Pie",
    1100046: "Casserole",
    1100047: "Shepherd's Pie",
    1100048: "Peach Tart",
    
    # Loom & Sewing Machine
    1100050: "Sweater",
    1100051: "Cotton Fabric",
    1100052: "Blue Woolly Hat",
    1100053: "Blue Sweater",
    1100054: "Red Scarf",
    1100055: "Flower Shawl",
    1100056: "Cotton Shirt",
    1100057: "Wooly Chaps",
    1100058: "Violet Dress",
    1100059: "Pillow",
    1100060: "Blanket",
    
    # BBQ & Sauce Maker
    1100070: "Soy Sauce",
    1100071: "Olive Oil",
    1100072: "Mayonnaise",
    1100073: "Tomato Sauce",
    1100074: "Salsa",
    
    # Juice Press & Jam
    1100080: "Carrot Juice",
    1100081: "Apple Juice",
    1100082: "Cherry Juice",
    1100083: "Tomato Juice",
    1100084: "Berry Juice",
    1100085: "Orange Juice",
    1100090: "Apple Jam",
    1100091: "Raspberry Jam",
    1100092: "Blackberry Jam",
    1100093: "Cherry Jam",
    1100094: "Strawberry Jam",
    1100095: "Marmalade",
    1100096: "Peach Jam",
    
    # Animal Products (Yields)
    1100100: "Egg",
    1100101: "Cow Milk",
    1100102: "Bacon",
    1100103: "Sheep Wool",
    1100104: "Goat Milk",
    1100105: "Honeycomb",
    1100106: "Duck Feather",
    1100107: "Lobster Tail",
    
    # Fruit Items (Harvested from Trees/Bushes)
    1100120: "Apple",
    1100121: "Cherry",
    1100122: "Berry / Raspberry",
    1100123: "Blackberry",
    1100124: "Cacao",
    1100125: "Coffee Bean",
    1100126: "Olive",
    1100127: "Lemon",
    1100128: "Orange",
    1100129: "Peach",
    1100130: "Banana",
    1100131: "Plum",
    1100132: "Mango",
    1100133: "Coconut",
    1100134: "Guava",
    1100135: "Pomegranate",
}

BUILDINGS_AND_MACHINES = {
    # Core Farm Structures
    1300000: "Farmhouse / Base Structure",
    1300001: "Barn (Main Storage)",
    1300002: "Silo / Starter Pen (Chicken Coop #1)",
    1300003: "Roadside Shop",
    1300004: "Cow Pasture #1",
    1300005: "Dairy",
    1300006: "Chicken Coop #2",
    1300007: "Pig Pen #1",
    1300008: "Sheep Pasture #1",
    1300009: "Feed Mill #1",
    1300010: "Feed Mill #2",
    1300011: "Chicken Coop #3",
    1300012: "Cow Pasture #2",
    1300013: "Pig Pen #2",
    1300014: "Sheep Pasture #2",
    1300015: "Goat Pen #1",
    1300016: "Goat Pen #2",
    1300017: "Goat Pen #3",
    
    # Production Machines
    1300025: "Sugar Mill",
    1300067: "Pie Oven",
    1300069: "Grill / BBQ Grill",
    1300076: "Popcorn Pot",
    1300080: "Loom",
    1300082: "Bakery",
    1300085: "Sewing Machine",
    1300090: "Cake Oven",
    1300095: "Smelter #1",
    1300096: "Smelter #2",
    1300097: "Smelter #3",
    1300098: "Smelter #4",
    1300099: "Smelter #5",
    1300105: "Juice Press",
    1300110: "Ice Cream Maker",
    1300115: "Jam Maker",
    1300120: "Coffee Kiosk",
    1300125: "Soup Kitchen",
    1300130: "Candle Maker",
    1300135: "Flower Shop",
    1300140: "Sauce Maker",
    1300145: "Sushi Bar",
    1300150: "Salad Bar",
    1300155: "Sandwich Bar",
    1300160: "Smoothie Mixer",
    1300165: "Pasta Kitchen",
    1300170: "Wok Kitchen",
    1300175: "Hat Maker",
    1300180: "Tea Stand",
    1300185: "Fondue Pot",
    1300190: "Taco Kitchen",
    1300195: "Omelet Station",
    1300200: "Donut Maker",
    1300205: "Waffle Maker",
    1300210: "Fudge Shop",
    1300215: "Yogurt Maker",
    1300220: "Porridge Bar",
    1300225: "Milkshake Bar",
    
    # Orchard Trees & Bushes (Instances on Farm)
    # Range 1300020 - 1300300 covers dynamic trees & bushes planted on your farm
}

TOOLS_AND_MATERIALS = {
    # Clearing & Land Tools
    1800000: "Axe",
    1800001: "Saw",
    1800002: "Shovel",
    1800003: "Dynamite",
    1800004: "TNT Barrel",
    1800005: "Pickaxe",
    
    # Barn Upgrade Materials
    1800010: "Bolt",
    1800011: "Plank",
    1800012: "Duct Tape",
    
    # Silo Upgrade Materials
    1800020: "Box of Nails",
    1800021: "Screw",
    1800022: "Wood Panel",
    
    # Land Expansion Materials
    1800030: "Land Deed",
    1800031: "Mallet",
    1800032: "Marker Stake",
    
    # Town Materials
    1800040: "Brick",
    1800041: "Paint Bucket",
    1800042: "Hand Drill",
    1800043: "Tar Bucket",
    1800044: "Stone Block",
    1800045: "Hammer",
}

ANIMALS = {
    # Chickens (Pen 1..3: 6 per pen = 18 chickens)
    2300000: "Chicken #1 (Pen 1)",
    2300001: "Chicken #2 (Pen 1)",
    2300002: "Chicken #3 (Pen 1)",
    2300003: "Chicken #4 (Pen 1)",
    2300004: "Chicken #5 (Pen 1)",
    2300005: "Chicken #6 (Pen 1)",
    2300006: "Chicken #7 (Pen 2)",
    2300007: "Chicken #8 (Pen 2)",
    2300008: "Chicken #9 (Pen 2)",
    2300009: "Chicken #10 (Pen 2)",
    2300010: "Chicken #11 (Pen 2)",
    2300011: "Chicken #12 (Pen 2)",
    2300012: "Chicken #13 (Pen 3)",
    2300013: "Chicken #14 (Pen 3)",
    2300014: "Chicken #15 (Pen 3)",
    2300015: "Chicken #16 (Pen 3)",
    2300016: "Chicken #17 (Pen 3)",
    2300017: "Chicken #18 (Pen 3)",
    
    # Cows (5 per pasture = 15 cows)
    2300018: "Cow #1 (Pasture 1)",
    2300019: "Cow #2 (Pasture 1)",
    2300020: "Cow #3 (Pasture 1)",
    2300021: "Cow #4 (Pasture 1)",
    2300022: "Cow #5 (Pasture 1)",
    2300023: "Cow #6 (Pasture 2)",
    2300024: "Cow #7 (Pasture 2)",
    2300025: "Cow #8 (Pasture 2)",
    2300026: "Cow #9 (Pasture 2)",
    2300027: "Cow #10 (Pasture 2)",
    2300028: "Cow #11 (Pasture 3)",
    2300029: "Cow #12 (Pasture 3)",
    2300030: "Cow #13 (Pasture 3)",
    2300031: "Cow #14 (Pasture 3)",
    2300032: "Cow #15 (Pasture 3)",
    
    # Pigs (5 per pen = 15 pigs)
    2300036: "Pig #1",
    2300037: "Pig #2",
    2300038: "Pig #3",
    2300039: "Pig #4",
    2300040: "Pig #5",
    
    # Sheep (5 per pasture = 15 sheep)
    2300054: "Sheep #1",
    2300055: "Sheep #2",
    2300056: "Sheep #3",
    2300057: "Sheep #4",
    2300058: "Sheep #5",
    
    # Goats (4 per pen = 12 goats)
    2300072: "Goat #1",
    2300073: "Goat #2",
    2300074: "Goat #3",
    2300075: "Goat #4",
}

ALL_CATEGORIES = {
    "Crops (Field Plants)": CROPS,
    "Animal Feeds": FEEDS,
    "Goods & Recipes (Products)": RECIPES_AND_GOODS,
    "Buildings & Production Machines": BUILDINGS_AND_MACHINES,
    "Tools & Expansion Materials": TOOLS_AND_MATERIALS,
    "Livestock Animals": ANIMALS,
}



# Mapping of Animal ID Ranges to their exact feed ID (from animals.csv & animal_feed.csv)
ANIMAL_FEED_MAP = {
    # Chickens: 2300000 - 2300017 -> Chicken Feed (600002)
    "chickens": {"range": range(2300000, 2300018), "feed_id": 600002, "name": "Chicken Feed"},
    # Cows: 2300018 - 2300032 -> Cow Feed (600003)
    "cows": {"range": range(2300018, 2300033), "feed_id": 600003, "name": "Cow Feed"},
    # Pigs: 2300036 - 2300050 -> Pig Feed (600004)
    "pigs": {"range": range(2300036, 2300051), "feed_id": 600004, "name": "Pig Feed"},
    # Sheep: 2300054 - 2300068 -> Sheep Feed (600005)
    "sheep": {"range": range(2300054, 2300069), "feed_id": 600005, "name": "Sheep Feed"},
    # Goats: 2300072 - 2300083 -> Goat Feed (600006)
    "goats": {"range": range(2300072, 2300084), "feed_id": 600006, "name": "Goat Feed"},
}

def get_feed_for_animal(animal_id):
    """Return the proper feed ID for any given animal ID."""
    for animal_type, info in ANIMAL_FEED_MAP.items():
        if animal_id in info["range"]:
            return info["feed_id"]
    return 600002  # Default to chicken feed


# Standard base prices from fields.csv, bakery_goods.csv, etc.
# Max price percentage in Hay Day is 360% (game_config.csv: RoadsideShopMaxPricePercentage,360)
BASE_PRICES = {
    400001: 1,    # Wheat: base 1 -> max 36 for 10 (3.6 ea)
    400002: 2,    # Corn: base 2 -> max 72 for 10 (7.2 ea)
    400003: 3,    # Soybean: base 3 -> max 108 for 10 (10.8 ea)
    400004: 4,    # Sugarcane: base 4 -> max 144 for 10 (14.4 ea)
    400005: 2,    # Carrot: base 2 -> max 72 for 10 (7.2 ea)
    400006: 7,    # Indigo: base 7 -> max 252 for 10
    400007: 9,    # Pumpkin: base 9 -> max 324 for 10
    400008: 8,    # Cotton: base 8 -> max 288 for 10
    400009: 10,   # Chili Pepper
    400010: 12,   # Tomato
    400011: 14,   # Strawberry
    400012: 10,   # Potato
    1100015: 6,   # Bread: base 6 -> max 21 coins
    1100000: 14,  # Cream
    1100001: 33,  # Butter
    1100002: 34,  # Cheese
    1100013: 9,   # Brown Sugar
    1100014: 14,  # White Sugar
    1800000: 7,   # Saw -> max 270 (tools max at 270 coins each)
    1800001: 7,   # Axe -> max 270
    1800004: 8,   # Bolt -> max 270
    1800005: 8,   # Plank -> max 270
    1800006: 8,   # Duct Tape -> max 270
}

# Screen landmark navigation points (relative drag / coordinate offsets for teleport)
SCREEN_LANDMARKS = {
    "farm": {"name": "Farm Center (Main Crops & House)", "dx": 0, "dy": 0, "note": "Center of farm"},
    "shop": {"name": "Roadside Shop (Market & Stand)", "dx": 380, "dy": 420, "note": "Bottom-right entrance"},
    "animals": {"name": "Livestock Pens (Chickens, Cows, Pigs)", "dx": -320, "dy": 180, "note": "West pastures"},
    "machines": {"name": "Production Factories (Bakery, Dairy, Sugar)", "dx": 260, "dy": -220, "note": "North-east yard"},
    "mine": {"name": "The Mine (Ore & Minerals)", "dx": 550, "dy": -480, "note": "Far north-east mountains"},
    "boat": {"name": "Fishing Docks & River Boat", "dx": -520, "dy": -360, "note": "North-west river"},
    "town": {"name": "Town Train Station", "dx": 600, "dy": 250, "note": "East railway line"},
}

EXPANSION_DAILY_CAP = 80

EXPANSION_MATERIALS = {
    # Barn expansion
    1800004: "Bolt",
    1800005: "Plank",
    1800006: "Duct Tape",
    # Silo expansion
    1800009: "Box of Nails",
    1800010: "Wood Panel",
    1800011: "Screw",
    # Land & Town expansion
    1800012: "Land Deed",
    1800013: "Mallet",
    1800014: "Marker Stake",
    # Clearing & Mining Tools
    1800000: "Saw",
    1800001: "Axe",
    1800002: "Shovel",
    1800003: "Pickaxe",
    1800007: "Dynamite",
    1800008: "TNT Barrel",
}

MINING_TOOLS = {
    1800007: "Dynamite",
    1800008: "TNT Barrel",
    1800003: "Pickaxe",
    1800002: "Shovel",
}

FISHING_CATALOG = {
    # Fishing Lures
    9800000: "Red Lure (Free/Worm)",
    9800001: "Green Lure",
    9800002: "Blue Lure",
    9800003: "Purple Lure",
    9800004: "Gold Lure",
    # Nets & Traps
    9800005: "Fishing Net",
    9800006: "Mystery Net",
    9800007: "Lobster Trap",
    9800008: "Duck Trap",
}

TREES_AND_BUSHES = {
    # Trees (cleared with Saws 1800000)
    1300015: "Apple Tree",
    1300016: "Cherry Tree",
    1300017: "Cacao Tree",
    1300018: "Coffee Bush / Tree",
    1300019: "Olive Tree",
    1300071: "Peach Tree",
    1300072: "Banana Tree",
    1300073: "Coconut Tree",
    # Bushes (cleared with Axes 1800001)
    1300013: "Raspberry Bush",
    1300014: "Blackberry Bush",
    1300080: "Peanut Bush",
    1300081: "Dandelion Bush",
}

def calculate_shop_price(item_id, count=10, mode="highest"):
    """
    Calculate price for Roadside Shop sale based on choice:
      'highest' / 'max' / '100%' : 100% full maximum allowed price ceiling
      '75%' / '75'               : 75% of maximum allowed price ceiling
      'half' / '50%' / '50'      : 50% of maximum allowed price ceiling
      'lowest' / 'low' / 'min'   : 1 coin total (fastest possible emergency dump)
      'antibank' / 'safe'        : Anti-Ban Humanized Max (Full ceiling minus 1-3 coins to bypass bot pattern detection)
      <number>                   : Explicit coin value
    """
    import random
    base = BASE_PRICES.get(item_id, 2)
    # 3.6x base is max in Hay Day (capped for tools at 270)
    if str(item_id).startswith("180"):  # Tools
        single_max = 270
    else:
        single_max = max(1, round(base * 3.6))

    total_max = single_max * count

    m = str(mode).strip().lower()
    if m in ("lowest", "low", "min", "1"):
        return 1
    elif m in ("75%", "75", "threequarters"):
        return max(1, round(total_max * 0.75))
    elif m in ("half", "50%", "50", "medium", "mid"):
        return max(1, round(total_max * 0.50))
    elif m in ("antibank", "anti-ban", "human", "safe"):
        # Humanize: slightly below max (e.g. 34 or 35 coins for wheat instead of static 36)
        if total_max <= 3:
            return total_max
        reduction = random.randint(1, min(3, total_max - 1))
        return total_max - reduction
    elif m.isdigit():
        return int(m)
    else:  # "highest", "max", "100%"
        return total_max



def search_id(query):
    """Search for items by name substring or numeric ID."""
    results = []
    q_str = str(query).strip().lower()
    is_num = q_str.isdigit()
    num_val = int(q_str) if is_num else None

    for cat_name, items in ALL_CATEGORIES.items():
        for item_id, item_name in items.items():
            if is_num and item_id == num_val:
                results.append((item_id, item_name, cat_name))
            elif not is_num and q_str in item_name.lower():
                results.append((item_id, item_name, cat_name))

    return results


def print_search(query):
    matches = search_id(query)
    print(f"\nSearch results for '{query}': ({len(matches)} matches)")
    print("-" * 65)
    if not matches:
        print("  No matches found. Try a broader search term (e.g. 'bread', 'feed', 'cow').")
    else:
        for item_id, name, cat in matches:
            print(f"  ID: {item_id:<8} | Name: {name:<32} | [{cat}]")
    print("-" * 65 + "\n")


def print_category_summary():
    print("================================================================")
    print("      HAY DAY TITAN ENGINE GLOBAL ID ARCHITECTURE SUMMARY       ")
    print("================================================================")
    print("Formula: GlobalID = (ClassID * 1,000,000) + InstanceIndex\n")
    print("  Class  4 -> Field Crops & Plants       (400000 - 400050)")
    print("  Class  6 -> Animal Feeds               (600001 - 600010)")
    print("  Class 11 -> Goods, Recipes & Harvests  (1100000 - 1100999)")
    print("  Class 13 -> Buildings, Machines, Pens  (1300000 - 1300999)")
    print("  Class 18 -> Tools & Expansion Items    (1800000 - 1800099)")
    print("  Class 23 -> Livestock Animals          (2300000 - 2300099)")
    print("================================================================\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print_search(query)
    else:
        print_category_summary()
        print("Usage: python game_ids.py <name_or_id>")
        print("Example: python game_ids.py bread")
        print("         python game_ids.py 1300082")
        print("         python game_ids.py chicken")

