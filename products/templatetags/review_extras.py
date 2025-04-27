from django import template

register = template.Library()

@register.filter
def rating_count(product, rating):
    return product.get_rating_count(rating)

@register.filter
def ordinal_word(value):
    try:
        value = int(value)
    except (ValueError, TypeError):
        return value
    ordinals = {
        1: 'First',
        2: 'Second',
        3: 'Third',
        4: 'Fourth',
        5: 'Fifth',
        6: 'Sixth',
        7: 'Seventh',
        8: 'Eighth',
        9: 'Ninth',
        10: 'Tenth',
    }
    return ordinals.get(value, f"{value}th") 