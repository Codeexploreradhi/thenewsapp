

def get_hashtags(keywords):
    return " ".join([("#" + k.strip().replace(" ", "")) for k in keywords.split(",")])
