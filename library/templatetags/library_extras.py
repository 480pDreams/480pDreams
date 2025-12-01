from django import template

register = template.Library()


@register.simple_tag
def get_localized_data(game, user):
    """
    Returns a dictionary with 'title', 'box_art', etc.
    Logic:
    1. Check user preference.
    2. Check if that region data exists for this game.
    3. If yes, return regional data.
    4. If no, return default Game data.
    """
    # 1. Determine Target Region
    target_region = 'NTSC-U'  # Default
    if user.is_authenticated and hasattr(user, 'profile'):
        target_region = user.profile.preferred_region

    # 2. Look for the Release
    # We use .filter() instead of .get() to avoid crashes if multiples exist
    # We grab the specific release from the related manager
    release = None

    # Optimization: If the view prefetched 'regional_releases', this won't hit DB
    for r in game.regional_releases.all():
        if r.region_code == target_region:
            release = r
            break

    # 3. Build the Data Object
    data = {
        'title': game.title,
        'box_art': game.box_art,
        'back_art': game.back_art,
        'spine_art': game.spine_art,
    }

    # If we found a regional override, overwrite the defaults IF the override has data
    if release:
        if release.title: data['title'] = release.title
        if release.box_art: data['box_art'] = release.box_art
        if release.back_art: data['back_art'] = release.back_art
        if release.spine_art: data['spine_art'] = release.spine_art

    return data