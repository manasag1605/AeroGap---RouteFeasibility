import os
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from dotenv import load_dotenv
from amadeus import Client, ResponseError

load_dotenv()

amadeus = Client(
    client_id=os.getenv("AMADEUS_API_KEY"),
    client_secret=os.getenv("AMADEUS_API_SECRET")
)

DESTINATION_POOL = [
    "DXB", "SIN", "BKK", "KUL", "HKG",
    "JFK", "LAX", "ORD", "MIA", "YYZ",
    "CDG", "FRA", "AMS", "MAD", "FCO",
    "SYD", "MEL", "BOM", "DEL", "NBO",
]

def get_iata_code(city_name: str) -> str | None:
    try:
        response = amadeus.reference_data.locations.get(
            keyword=city_name,
            subType="CITY"
        )
        if response.data:
            code = response.data[0]["iataCode"]
            print(f"  Resolved '{city_name}' → {code}")
            return code
        return None
    except ResponseError as e:
        print(f"  IATA Error: {e}")
        return None

def fetch_offers(origin: str, destination: str, date: str) -> list:
    all_offers = []
    try:
        # First page — no max cap
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=date,
            adults=1
        )
        all_offers = response.data or []
    except ResponseError:
        pass
    return all_offers

def collect_all_routes(origin: str, destinations: list[str], date: str) -> pd.DataFrame:
    rows = []
    total = len(destinations)
    for i, dest in enumerate(destinations, 1):
        print(f"  [{i}/{total}] Fetching {origin} → {dest} ...", end=" ")
        offers = fetch_offers(origin, dest, date)
        if offers:
            prices   = [float(o["price"]["grandTotal"]) for o in offers]
            seats    = [o["numberOfBookableSeats"] for o in offers]
            carriers = set()
            for o in offers:
                carriers.update(o["validatingAirlineCodes"])
            rows.append({
                "destination":   dest,
                "flight_count":  len(offers),
                "total_seats":   sum(seats),
                "avg_price":     round(sum(prices) / len(prices), 2),
                "min_price":     min(prices),
                "carrier_count": len(carriers),
                "carriers":      ", ".join(sorted(carriers)),
            })
            print(f"{len(offers)} offers found")
        else:
            print("no data")
        time.sleep(0.3)
    return pd.DataFrame(rows)

def fetch_route_detail(origin: str, destination: str, date: str) -> pd.DataFrame:
    print(f"\n  Fetching detailed breakdown for {origin} → {destination} ...")
    offers = fetch_offers(origin, destination, date)
    if not offers:
        print("  No data found.")
        return pd.DataFrame()
    rows = []
    for o in offers:
        itin     = o["itineraries"][0]
        segment  = itin["segments"][0]
        rows.append({
            "carrier":    o["validatingAirlineCodes"][0],
            "flight_no":  segment["carrierCode"] + segment["number"],
            "departure":  segment["departure"]["at"],
            "arrival":    segment["arrival"]["at"],
            "duration":   itin["duration"],
            "stops":      len(itin["segments"]) - 1,
            "seats":      o["numberOfBookableSeats"],
            "price":      float(o["price"]["grandTotal"]),
            "currency":   o["price"]["currency"],
        })
    return pd.DataFrame(rows).sort_values("price")

def calculate_rfi(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    total_flights = df["flight_count"].sum()
    total_seats   = df["total_seats"].sum()
    max_price     = df["avg_price"].max()
    min_price     = df["avg_price"].min()
    price_range   = max_price - min_price if max_price != min_price else 1
    max_carriers  = df["carrier_count"].max()

    df["flight_supply_pct"] = (df["flight_count"] / total_flights * 100).round(2)
    df["seat_supply_pct"]   = (df["total_seats"]  / total_seats   * 100).round(2)
    df["price_index"]       = ((df["avg_price"] - min_price) / price_range).round(4)
    df["carrier_scarcity"]  = (1 - (df["carrier_count"] / max_carriers)).round(4)

    df["rfi_score"] = (
        0.40 * df["price_index"] +
        0.35 * df["carrier_scarcity"] +
        0.25 * (1 - df["seat_supply_pct"] / 100)
    ).round(4)

    df["opportunity"] = df["rfi_score"].apply(
        lambda x: "HIGH" if x > 0.6 else ("MODERATE" if x > 0.35 else "LOW")
    )

    return df.sort_values("rfi_score", ascending=False).reset_index(drop=True)

def print_report(df: pd.DataFrame, origin: str, date: str):
    print(f"\n{'='*78}")
    print(f"  RFI REPORT  |  Origin: {origin}  |  Date: {date}")
    print(f"{'='*78}")
    print(f"  {'Dest':<6} {'Flights':>7} {'Seats':>6} {'AvgPrice':>9} {'Carriers':>9} {'Supply%':>8} {'RFI':>6}  Opportunity")
    print(f"  {'-'*73}")
    for _, r in df.iterrows():
        tag = {"HIGH": "🔴", "MODERATE": "🟡", "LOW": "🟢"}.get(r["opportunity"], "")
        print(
            f"  {r['destination']:<6}"
            f"  {int(r['flight_count']):>6}"
            f"  {int(r['total_seats']):>5}"
            f"  {r['avg_price']:>9.2f}"
            f"  {int(r['carrier_count']):>8}"
            f"  {r['flight_supply_pct']:>7.1f}%"
            f"  {r['rfi_score']:>5.3f}"
            f"  {tag} {r['opportunity']}"
        )
    print(f"{'='*78}")
    top = df.iloc[0]
    print(f"\n  📍 Top opportunity route: {origin} → {top['destination']}")
    print(f"     Avg price: {top['avg_price']}  |  Carriers: {int(top['carrier_count'])}  |  RFI: {top['rfi_score']}")
    print(f"     Insight: High fares + limited carriers = underserved demand\n")

def print_route_detail(df: pd.DataFrame, origin: str, dest: str):
    if df.empty:
        return
    print(f"\n{'='*70}")
    print(f"  ROUTE DETAIL  |  {origin} → {dest}")
    print(f"{'='*70}")
    print(f"  {'Carrier':<8} {'Flight':<8} {'Departure':<20} {'Stops':>5} {'Seats':>5} {'Price':>8}")
    print(f"  {'-'*65}")
    for _, r in df.iterrows():
        print(
            f"  {r['carrier']:<8}"
            f"  {r['flight_no']:<7}"
            f"  {r['departure']:<19}"
            f"  {int(r['stops']):>5}"
            f"  {int(r['seats']):>5}"
            f"  {r['price']:>7.2f} {r['currency']}"
        )
    print(f"{'='*70}")
    print(f"  Total offers: {len(df)}  |  Price range: {df['price'].min():.2f} – {df['price'].max():.2f}  |  Avg: {df['price'].mean():.2f}\n")

def save_chart(df: pd.DataFrame, origin: str, date: str, out_dir: str) -> str:
    colors = {"HIGH": "#e74c3c", "MODERATE": "#f39c12", "LOW": "#2ecc71"}
    bar_colors = [colors.get(o, "#95a5a6") for o in df["opportunity"]]

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle(f"RFI Analysis  |  Origin: {origin}  |  Date: {date}", fontsize=14, fontweight="bold", y=1.01)

    # Chart 1 — RFI scores
    ax1 = axes[0]
    bars = ax1.barh(df["destination"][::-1], df["rfi_score"][::-1], color=bar_colors[::-1], edgecolor="white", linewidth=0.5)
    ax1.axvline(x=0.6, color="#e74c3c", linestyle="--", linewidth=1, alpha=0.6, label="HIGH threshold")
    ax1.axvline(x=0.35, color="#f39c12", linestyle="--", linewidth=1, alpha=0.6, label="MODERATE threshold")
    ax1.set_xlabel("RFI Score")
    ax1.set_title("Route Feasibility Index (RFI)")
    ax1.legend(fontsize=8)
    ax1.set_xlim(0, 1)
    for bar, val in zip(bars, df["rfi_score"][::-1]):
        ax1.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                 f"{val:.3f}", va="center", fontsize=8)

    # Chart 2 — Avg price vs carrier count bubble chart
    ax2 = axes[1]
    scatter = ax2.scatter(
        df["carrier_count"],
        df["avg_price"],
        s=df["flight_supply_pct"] * 40 + 50,
        c=df["rfi_score"],
        cmap="RdYlGn_r",
        alpha=0.8,
        edgecolors="white",
        linewidths=0.5
    )
    for _, r in df.iterrows():
        ax2.annotate(r["destination"],
                     (r["carrier_count"], r["avg_price"]),
                     textcoords="offset points", xytext=(5, 4), fontsize=7)
    plt.colorbar(scatter, ax=ax2, label="RFI Score")
    ax2.set_xlabel("Number of Carriers")
    ax2.set_ylabel("Avg Price (USD)")
    ax2.set_title("Price vs Carrier Count\n(bubble size = flight supply %)")

    patches = [mpatches.Patch(color=v, label=k) for k, v in colors.items()]
    fig.legend(handles=patches, loc="lower center", ncol=3, fontsize=9, bbox_to_anchor=(0.5, -0.04))

    plt.tight_layout()
    chart_path = os.path.join(out_dir, f"rfi_chart_{origin}_{date}.png")
    plt.savefig(chart_path, dpi=150, bbox_inches="tight")
    plt.close()
    return chart_path

if __name__ == "__main__":
    origin_city  = input("Enter origin city: ").strip()
    date         = input("Enter departure date (YYYY-MM-DD, default 2026-11-01): ").strip() or "2026-11-01"
    detail_city  = input("Enter a specific destination for detailed breakdown (or press Enter to skip): ").strip()

    origin_iata = get_iata_code(origin_city)
    if not origin_iata:
        raise SystemExit("Could not resolve origin IATA code.")

    destinations = [d for d in DESTINATION_POOL if d != origin_iata]

    print(f"\nFetching flight offers from {origin_iata} to {len(destinations)} destinations...")
    df = collect_all_routes(origin_iata, destinations, date)

    if df.empty:
        raise SystemExit("No flight data returned for any route.")

    df = calculate_rfi(df)
    print_report(df, origin_iata, date)

    os.makedirs("data", exist_ok=True)

    # Route detail
    if detail_city:
        dest_iata = get_iata_code(detail_city)
        if dest_iata:
            detail_df = fetch_route_detail(origin_iata, dest_iata, date)
            print_route_detail(detail_df, origin_iata, dest_iata)
            detail_out = f"data/detail_{origin_iata}_{dest_iata}_{date}.csv"
            detail_df.to_csv(detail_out, index=False)
            print(f"  Saved route detail to {detail_out}")

    # Save CSV
    csv_out = f"data/rfi_{origin_iata}_{date}.csv"
    df.to_csv(csv_out, index=False)
    print(f"  Saved RFI report to {csv_out}")

    # Save chart
    chart_out = save_chart(df, origin_iata, date, "data")
    print(f"  Saved chart to {chart_out}")