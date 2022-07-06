import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import pathlib



def add_font():
    for font in font_manager.findSystemFonts(f'{pathlib.Path(__file__).parent.absolute()}/Source Sans Pro'):
        font_manager.fontManager.addfont(font)
    #plt.rcParams['font.family'] = 'Source Sans Pro'
    