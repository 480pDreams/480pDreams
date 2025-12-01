from django import template

register = template.Library()


@register.simple_tag
def get_localized_data(game, user):
    """
    Returns localized title/art.
    FALLBACK STRATEGY: Always return default game data if logic fails.
    """
    # 1. Start with Defaults (The "Safe" Data)
    data = {
        'title': game.title,
        'box_art': game.box_art,
        'back_art': game.back_art,
        'spine_art': game.spine_art,
    }

    # 2. Determine Preference
    target_region = 'NTSC-U'  # System Default

    # robustly check for profile
    if user.is_authenticated:
        try:
            # Use getattr to avoid crash if profile is missing
            profile = getattr(user, 'profile', None)
            if profile:
                target_region = profile.preferred_region
        except Exception:
            pass  # Keep default if user DB is weird

    # 3. Look for Overrides
    # (Only if the preference is different from the game's main region)
    # But for now, we just check all regional releases attached to this game

    # We loop through the pre-fetched releases
    found_release = None
    for r in game.regional_releases.all():
        if r.region_code == target_region:
            found_release = r
            break

    # 4. Apply Overrides (Only if they exist)
    if found_release:
        if found_release.title:
            data['title'] = found_release.title
        if found_release.box_art:
            data['box_art'] = found_release.box_art
        if found_release.back_art:
            data['back_art'] = found_release.back_art
        if found_release.spine_art:
            data['spine_art'] = found_release.spine_art

    return data