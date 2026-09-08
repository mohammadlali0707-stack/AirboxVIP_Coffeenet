import random

# Reliable fallback image URLs mapped by topic
TOPIC_IMAGE_URLS = {
    "space": [
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=800&auto=format&fit=crop"
    ],
    "brain": [
        "https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=800&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1559757175-5700dde675bc?w=800&auto=format&fit=crop"
    ],
    "nature": [
        "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop"
    ],
    "technology": [
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800&auto=format&fit=crop"
    ],
    "literature": [
        "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=800&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1474939557375-0fe248e3a246?w=800&auto=format&fit=crop"
    ],
    "poetry": [
        "https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=800&auto=format&fit=crop"
    ],
    "philosophy": [
        "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=800&auto=format&fit=crop"
    ]
}

DEFAULT_IMAGE_URL = "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&auto=format&fit=crop"

def get_image_url_for_topic(topic):
    """Returns a topic-relevant image URL with graceful fallbacks."""
    urls = TOPIC_IMAGE_URLS.get(topic, [DEFAULT_IMAGE_URL])
    return random.choice(urls)
