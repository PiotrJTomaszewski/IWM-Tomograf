# Only for result comparison - remove later
def cheat_radon(image):
    import skimage.transform as skitran
    theta = None
    radon_img = skitran.radon(image, theta)
    return radon_img
