"""Auth handling for UniFi Access API."""


def build_headers(
    api_token: str, content_type: str | None = "application/json"
) -> dict[str, str]:
    """Build HTTP headers for API requests.

    Args:
        api_token: Bearer token for authentication.
        content_type: Content-Type header. Pass None for multipart/form-data
            uploads where aiohttp sets the header automatically.
    """
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
    }
    if content_type is not None:
        headers["Content-Type"] = content_type
    return headers
