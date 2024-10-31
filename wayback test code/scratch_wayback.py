def get_wayback_snapshots(base_url, from_date, to_date):
    """Fetch available snapshots from Wayback Machine for the given URL within a date range."""
    # Check if the result is already cached
    cache_key = f"{base_url}-{from_date}-{to_date}"
    if cache_key in cache:
        print("Fetching from cache...")
        return cache[cache_key]

    # API URL for Wayback Machine CDX
    api_url = f'http://web.archive.org/cdx/search/cdx?url={base_url}&output=json&fl=timestamp&from={from_date}&to={to_date}&sort=asc'
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad responses
        
        data = response.json()  # Try to decode JSON response
        snapshots = []
        
        if len(data) > 1:
            snapshots = [snapshot[0] for snapshot in data[1:]]  # Skip the header
        else:
            print("No snapshots found for the given date range.")
        
        # Store the result in the cache
        cache[cache_key] = snapshots
        save_cache()  # Save cache after updating
        return snapshots

    except requests.RequestException as e:
        print(f"HTTP error occurred: {e}")
        return []