def update_rating(profile):
    profile_reviews = profile.reviews.all() 
    no_of_reviews = profile_reviews.count()
    sum_of_stars = 0
    for review in profile_reviews:
        sum_of_stars += review.stars
    try:
        profile.rating = sum_of_stars/no_of_reviews
    except ZeroDivisionError:
        profile.rating = 0
    return profile.save()