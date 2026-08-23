# Disaster-prone locations across India, grouped by disaster type.
# Used for testing/demoing the routing engine across realistic scenarios
# instead of one arbitrary city.

DISASTER_PRONE_LOCATIONS = {
    "flood": [
        "Kochi, Kerala, India",
        "Alappuzha, Kerala, India",
        "Guwahati, Assam, India",
        "Patna, Bihar, India",
        "Kolkata, West Bengal, India",
    ],
    "cyclone": [
        "Puri, Odisha, India",
        "Visakhapatnam, Andhra Pradesh, India",
        "Chennai, Tamil Nadu, India",
        "Nagapattinam, Tamil Nadu, India",
    ],
    "earthquake": [
        "Dehradun, Uttarakhand, India",
        "Shimla, Himachal Pradesh, India",
        "Guwahati, Assam, India",
        "Bhuj, Gujarat, India",
        "Srinagar, Jammu and Kashmir, India",
    ],
    "landslide": [
        "Wayanad, Kerala, India",
        "Idukki, Kerala, India",
        "Nainital, Uttarakhand, India",
        "Shimla, Himachal Pradesh, India",
    ],
}


def get_locations_for(disaster_type):
    """
    Returns the list of test locations for a given disaster type.
    """
    return DISASTER_PRONE_LOCATIONS.get(disaster_type, [])


def get_all_locations():
    """
    Returns a flat list of every location across all disaster types,
    with duplicates removed.
    """
    all_locations = set()
    for locations in DISASTER_PRONE_LOCATIONS.values():
        all_locations.update(locations)
    return sorted(all_locations)