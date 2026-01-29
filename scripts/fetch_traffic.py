import os
import pandas as pd
from dotenv import load_dotenv
from amadeus import Client, ResponseError 

load_dotenv()

amadeus = Client(
    client_id=os.getenv('AMADEUS_KEY'),
    client_secret=os.getenv('AMADEUS_SECRET')
)

def get_iata_code(city_name):
    try:
        response = amadeus.reference_data.locations.get(
            keyword=city_name,
            subType='CITY'
        )
        if response.data:
            code = response.data[0]['iataCode']
            print(f"IATA: Found {code} for {city_name}")
            return code
        return None
    except ResponseError as e:
        print(f"IATA Error: {e}")
        return None

def fetch_market_data(origin_code, destination_code):
    try:
        # Search for flights in November 2026
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin_code,
            destinationLocationCode=destination_code,
            departureDate='2026-11-01',
            adults=1
        )
        return response.data
    except ResponseError as e:
        print(f"Flight Search Error: {e}")
        return None

def parse_to_csv(raw_data, origin, dest):
    if not raw_data:
        print(f"No data to save for {origin} -> {dest}")
        return

    parsed = []
    for offer in raw_data:
        parsed.append({
            "origin": origin,
            "destination": dest,
            "price": float(offer['price']['grandTotal']),
            "currency": offer['price']['currency'],
            "seats": offer['numberOfBookableSeats'],
            "carrier": offer['validatingAirlineCodes'][0],
            "duration": offer['itineraries'][0]['duration']
        })

    df = pd.DataFrame(parsed)
    os.makedirs('data', exist_ok=True)
    filename = f"data/{origin}_{dest}_market.csv"
    df.to_csv(filename, index=False)
    print(f"SUCCESS: Saved {len(df)} offers to {filename}")

if __name__ == "__main__":
    # Get user inputs
    origin_city = input("Enter Origin City: ")                                     
    dest_city = input("Enter Destination City: ")

    # Step 1: Resolve IATA codes
    origin_iata = get_iata_code(origin_city)
    dest_iata = get_iata_code(dest_city)

    if origin_iata and dest_iata:
        # Step 2: Fetch flight data
        print(f"Fetching market prices for {origin_iata} to {dest_iata}...")
        raw_flights = fetch_market_data(origin_iata, dest_iata)

        # Step 3: Parse and Save
        parse_to_csv(raw_flights, origin_iata, dest_iata)
    else:
        print("Could not resolve IATA codes. Please check city names.")