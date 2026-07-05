import os


def extract_brand_from_url(url: str) -> str:
    """
    Best-effort brand name extraction from a URL, used whenever scraping
    or meta-tag extraction fails.

    Order of operations matters:
      1. Strip protocol            -> "www.example.com/products/xyz"
      2. Strip path                -> "www.example.com"
      3. Strip leading "www."      -> "example.com"
      4. Split on "." and take [0] -> "example"
      5. Capitalize                -> "Example"

    NOTE: the previous implementation in scraper_module.py split on "."
    BEFORE stripping "www.", which meant it always returned "Www" for any
    URL starting with "www." (since "www.example.com".split(".")[0] == "www",
    and replacing "www." on the string "www" is a no-op).
    """
    if not url:
        return "UnknownBrand"

    domain = url.split("://")[-1].split("/")[0]
    domain = domain.replace("www.", "")
    brand = domain.split(".")[0]
    return brand.capitalize() if brand else "UnknownBrand"


# ---------------------------------------------------------------------------
# Shared runtime configuration
# ---------------------------------------------------------------------------
# SQLite DB path: overridable via env var so it can be pointed at a
# persistent volume/mount in hosted environments (see DEPLOYMENT.md).
DB_PATH = os.getenv("SUSTAINABILITY_DB_PATH", "sustainability.db")

# Default port for local runs; hosted platforms should set $PORT and
# main.py will respect it automatically.
DEFAULT_PORT = int(os.getenv("PORT", 8000))