def google_maps_url(lat, lon):
    url = "https://maps.google.com/maps?q={lat},{lon}"
    return url.format(lat=lat, lon=lon)
