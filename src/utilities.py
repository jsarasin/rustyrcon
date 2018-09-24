def unity_to_pango(text):
    original_text = text
    markup_error = False

    # Add a " after all color tags
    pos = 0
    while True:
        if pos >= len(text):
            break
        found = text.find("<color=", pos)
        if found == -1:
            break

        closing = text.find(">", found)
        if closing == -1:
            markup_error = True
            print("Color markup error @", found)
            break

        text = text[0:closing] + "\"" + text[closing:]
        pos = closing + 1
    # Add a " after size tags
    pos = 0

    while True:
        if pos >= len(text):
            break
        found = text.find("<size=", pos)
        if found == -1:
            break

        closing = text.find(">", found)
        if closing == -1:
            markup_error = True
            print("Size markup error @", found)
            break

        text = text[0:closing] + "\"" + text[closing:]
        pos = closing + 1

    text = text.replace('<color=#', "<span fgcolor=\"#")
    text = text.replace('<size=', "<span font=\"")
    text = text.replace('</color>', '</span>')
    text = text.replace('</size>', '</span>')

    if markup_error:
        print("Markup Error: ", original_text)
        return False, original_text

    return True, text,

def gtkcolor_to_web(colorbutton):
    color = colorbutton.get_color().to_floats()
    r = "{:0>2X}".format((round(color[0] * 255)))
    g = "{:0>2X}".format((round(color[1] * 255)))
    b = "{:0>2X}".format((round(color[2] * 255)))
    string = "#" + str(r) + str(g) + str(b)

    return string
