from django import template

register = template.Library()


@register.simple_tag
def get_localized_data(game, user):
    """
    Returns localized title/art with smart fallbacks.
    """
    # 1. Start with Defaults
    data = {
        'title': game.title,
        'box_art': game.box_art,
        'back_art': game.back_art,
        'spine_art': game.spine_art,
    }

    # 2. Determine Preference
    target_region = 'NTSC-U'
    if user.is_authenticated:
        try:
            profile = getattr(user, 'profile', None)
            if profile:
                target_region = profile.preferred_region
        except Exception:
            pass

    # 3. LOGIC A: Simple Title Swap (The "Quick" way)
    # If user wants Japan AND we have a Japanese title field, use it immediately.
    if target_region == 'NTSC-J' and game.title_japanese:
        data['title'] = game.title_japanese

    # 4. LOGIC B: Regional Release Override (The "Full" way)
    # Check if there is a specific entry for this region (e.g. for specific Art)
    found_release = None
    for r in game.regional_releases.all():
        if r.region_code == target_region:
            found_release = r
            break

    # Apply Overrides if found
    if found_release:
        if found_release.title:
            data['title'] = found_release.title  # This beats the simple swap if populated
        if found_release.box_art:
            data['box_art'] = found_release.box_art
        if found_release.back_art:
            data['back_art'] = found_release.back_art
        if found_release.spine_art:
            data['spine_art'] = found_release.spine_art

    return data