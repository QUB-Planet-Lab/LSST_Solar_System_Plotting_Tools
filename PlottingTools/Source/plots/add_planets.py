from matplotlib import patches

def add_planets(ax, xlim):
        planets = {
            0.387 : 'mercury',
            0.723 : 'venus',
            1 : 'earth',
            1.524: 'mars',
            5.203 : 'jupiter',
            9.540 : 'saturn',
            19.18 : 'uranus',
            30.06 : 'neptune'
        }
        
        for dist in planets.keys():
            if dist < xlim:
                ax.add_patch(patches.Circle((0,0), radius = dist, fill = False, edgecolor="black"))