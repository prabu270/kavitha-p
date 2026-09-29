from urllib.parse import quote


PLATFORMS = {
    "Amazon": "https://www.amazon.in/s?k=",

    "Flipkart": "https://www.flipkart.com/search?q=",

    "IKEA": "https://www.ikea.com/in/en/search/?q=",

    "Swiggy": "https://www.swiggy.com/search?query=",

    "Zomato": "https://www.zomato.com/search?q=",

    "OYO": "https://www.oyorooms.com/search?location=",
}


def search_url(
    platform: str,
    query: str,
) -> str:

    base_url = PLATFORMS.get(
        platform,
        PLATFORMS["Amazon"],
    )

    return base_url + quote(query)


HOME_CATALOG = [
    (
        "LED Ceiling Light",
        "Lighting",
        1299,
        "Amazon",
    ),
    (
        "Modern Ceiling Fan",
        "Cooling",
        2499,
        "Amazon",
    ),
    (
        "Minimalist Wall Art",
        "Decor",
        899,
        "IKEA",
    ),
    (
        "Compact Dining Table",
        "Furniture",
        7499,
        "IKEA",
    ),
    (
        "Accent Chair",
        "Furniture",
        5999,
        "Amazon",
    ),
    (
        "Bedside Table",
        "Furniture",
        2999,
        "IKEA",
    ),
    (
        "Area Rug",
        "Decor",
        2499,
        "IKEA",
    ),
]


PARTY_CATALOG = [
    (
        "Catering package",
        "Catering",
        450,
        "Swiggy",
    ),
    (
        "Party decoration kit",
        "Decoration",
        2499,
        "Amazon",
    ),
    (
        "Birthday cake",
        "Food",
        1200,
        "Zomato",
    ),
    (
        "Hotel / stay search",
        "Accommodation",
        2500,
        "OYO",
    ),
    (
        "Event snacks",
        "Food",
        180,
        "Swiggy",
    ),
]


JEWELRY_CATALOG = [
    (
        "Pearl drop earrings",
        "Earrings",
        1499,
        "Amazon",
    ),
    (
        "Minimal gold-tone necklace",
        "Necklace",
        2299,
        "Flipkart",
    ),
    (
        "Statement earrings",
        "Earrings",
        1899,
        "Amazon",
    ),
    (
        "Classic pendant",
        "Necklace",
        2999,
        "Flipkart",
    ),
    (
        "Bangle set",
        "Bangles",
        1699,
        "Amazon",
    ),
]