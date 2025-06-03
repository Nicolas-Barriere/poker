from PIL import Image, ImageEnhance
import os
import numpy as np

dir_path = os.path.dirname(os.path.abspath(__file__))
img_path = os.path.join(dir_path, "jeton_poker_R.png")
img = Image.open(img_path).convert("RGBA")

# Fonction pour recolorer le jeton


def colorize(img, color):
    r, g, b = color
    datas = img.getdata()
    newData = []
    for item in datas:
        # On ne modifie que les pixels non transparents et dominants rouges (pas blancs)
        if item[3] > 0:
            # Détecte le blanc (tous canaux élevés et proches)
            if (
                item[0] > 200
                and abs(item[0] - item[1]) < 30
                and abs(item[0] - item[2]) < 30
            ):
                newData.append(item)  # Laisse le blanc
            # Détecte le rouge (rouge dominant, vert/bleu faibles, seuil encore abaissé)
            elif item[0] > 50 and item[0] > item[1] + 20 and item[0] > item[2] + 20:
                lum = int((item[0] + item[1] + item[2]) / 3)
                newData.append(
                    (
                        int(r * lum / 255),
                        int(g * lum / 255),
                        int(b * lum / 255),
                        item[3],
                    )
                )
            else:
                newData.append(item)
        else:
            newData.append(item)
    img2 = Image.new("RGBA", img.size)
    img2.putdata(newData)
    return img2


# Détection automatique du contour du jeton pour crop
def crop_jeton(img):
    arr = np.array(img)
    # On considère qu'un pixel transparent = fond
    alpha = arr[:, :, 3]
    nonzero = np.argwhere(alpha > 10)
    if nonzero.size == 0:
        return img  # rien à crop
    (ymin, xmin), (ymax, xmax) = nonzero.min(0), nonzero.max(0)
    cropped = img.crop((xmin, ymin, xmax + 1, ymax + 1))
    return cropped


# Crop aussi le jeton rouge d'origine
red = crop_jeton(img)
red.save(os.path.join(dir_path, "jeton_poker_R.png"))
# Bleu
blue = colorize(img, (0, 90, 255))
blue = crop_jeton(blue)
blue.save(os.path.join(dir_path, "jeton_poker_B.png"))
# Vert
green = colorize(img, (0, 180, 0))
green = crop_jeton(green)
green.save(os.path.join(dir_path, "jeton_poker_V.png"))
# Noir
black = colorize(img, (30, 30, 30))
black = crop_jeton(black)
black.save(os.path.join(dir_path, "jeton_poker_N.png"))

print("Jetons générés : rouge (croppé), bleu, vert, noir (croppés)")
