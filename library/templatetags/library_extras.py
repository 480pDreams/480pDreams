from django import template

register = template.Library()


@register.simple_tag
def get_localized_data(game, user):
    """
    Returns localized title/art/date with smart fallbacks.
    """
    # 1. Start with Defaults
    data = {
        'title': game.title,
        'release_date': game.release_date,  # Default Date
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

    # 3. LOGIC A: Simple Title Swap
    if target_region == 'NTSC-J' and game.title_japanese:
        data['title'] = game.title_japanese

    # 4. LOGIC B: Regional Release Override
    found_release = None
    for r in game.regional_releases.all():
        if r.region_code == target_region:
            found_release = r
            break

    if found_release:
        if found_release.title:
            data['title'] = found_release.title
        if found_release.release_date:
            data['release_date'] = found_release.release_date  # Override Date
        if found_release.box_art:
            data['box_art'] = found_release.box_art
        if found_release.back_art:
            data['back_art'] = found_release.back_art
        if found_release.spine_art:
            data['spine_art'] = found_release.spine_art

    return data


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return query.urlencode()


@register.inclusion_tag('library/partials/star_rating.html')
def render_stars(score):
    """
    Converts a score (0-10) into a list of stars.
    """
    if score is None:
        return {'stars': []}

    full_stars = int(score)
    has_half = (score - full_stars) >= 0.5
    empty_stars = 10 - full_stars - (1 if has_half else 0)

    return {
        'full_stars': range(full_stars),
        'has_half': has_half,
        'empty_stars': range(empty_stars),
        'score': score
    }