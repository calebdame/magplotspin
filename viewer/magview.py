import numpy as np 
import matplotlib as mpl
from matplotlib import pyplot as plt 
from mpl_toolkits.mplot3d import Axes3D
import os
import numpy.linalg as la

class MagView:
    """
    Arguments:

        X (ndarray, n x 7) : coordinate points in first 3 cols, 
            1 for if theres a vector in col 4 and has the associated 
            vectors in 5,6,7
        cif (string) : filename
        l (int) : size for arrows
        s (int) : dot size in plot
        others (ndarray, m x 7) : non-magnetic coordinates that are
            plotted for reference
    """

    def __init__(self, X, cif, l, s, others=[]):
        """
        Attributes:
        
            self.X         : (ndarray, (n,7)) copy of the X array imput into the class
            self.others    : (ndarray, (m,3)) copy of input other array
            self.l         : (int) length scale of arrows
            self.s         : (int) size scale of atoms
            self.clicked   : (list) keeps track of indices that are clicked during 
                             any given iteration
            self.fig       : (mpl figure object)
            self.ax        : (mpl axes object)
            self.plotted   : (list) saves the indices of atoms with associated 
                             vectors / arrows
            self.magscale  : (ndarray, shape: (m,)) saving the magnitudes of all spins
            self.quiver    : (list, (m)) mpl quiver objects with one per coordinate
            self.plot      : (mpl scatter object) magnetic coords dots
            self.fixed     : (mpl scatter object) non-magnetic coords dots
            self.tog       : (bool) True if the non-magnetic atoms are toggled
            self.blue      : (ndarray, (4,)) values associated to a shade of blue
            self.red       : (ndarray, (4,)) values associated to a shade of red
            self.fc        : (ndarray, (n,4)) array of color values per coordinate
            self.centroid  : (ndarray, (3,)) centroid of the structure
            self.axscalefactor
                           : (ndarray, (3,)) max coordinate distance from centroid 
                             along each axis.  Used for axes scaling to ensure centroid 
                             is centered and all points are in equally scaled axes
            self.zoom      : (float) zoom in / out factor

        """
        self.others = others
        self.clicked = []                      # to contain points receiving a vector
        self.l = l                             # default length of arrows
        self.s = s                             # default size of point
        self.X = X                             # X matrix containing coordinates and vectors
        self.fig = plt.figure(figsize=(8.,6.)) # set and save figure object
        self.ax = self.fig.add_subplot(111, projection='3d') # make 3d
        self.plotted = []
        self.magscale = np.ones(len(self.X))
        self.quiver = []

        
        #scatter the structure data
        if len(self.X) == 0: # check if there are any coordinates
            raise ValueError("no selected indeces")
        
        # plot all X values
        self.plot = self.ax.scatter(self.X[:,0],self.X[:,1],self.X[:,2],
                               picker=True, s=self.s, facecolors=["C0"]*len(self.X[:,0]),
                               edgecolors=["C0"]*len(self.X[:,0]))
        
        # plot all non-magnetic coordinates if any
        if len(self.others) != 0:
            self.tog = False
            self.fixed = self.ax.scatter(self.others[:,0],self.others[:,1],self.others[:,2],
                               s=self.s/3, facecolors="gray", edgecolors="gray")

        self.set_plot_params(cif) # set color, axes, labels, title
        self.plot_text() # instructions string
        self.setlegend() # plot legend

        # initialize functions called upon events
        self.fig.canvas.mpl_connect('close_event',self.on_close) # D, escape, enter
        self.fig.canvas.mpl_connect('pick_event',self.on_click) # click on plotted point
        self.fig.canvas.mpl_connect('key_release_event',self.on_key_press) # zoom / scale 
        plt.show()

    def setlegend(self):
        """ 
        build and plot a custom legend on the figure to label 
        the different scatterplot colors
        """
        dotsize = 8  # size of dot in legend
        
       # build legend and include non-magnetic atoms if any
        legend_elements = [mpl.lines.Line2D([0], [0], 
                           lw=0,marker='o', color=self.blue, 
                           label='Can be Assigned', 
                           markerfacecolor=self.blue, 
                           markersize=dotsize),
                           mpl.lines.Line2D([0], [0],  
                           lw=0,marker='o', color=self.red, 
                           label='Selected or\nAssigned',
                           markerfacecolor=self.red, 
                           markersize=dotsize)]
        if len(self.others) != 0: # if non-magnetic atoms in the structure, add gray to legend
            legend_elements += [mpl.lines.Line2D([0], [0], 
                                lw=0, marker='o', color='gray', 
                                label='Non-Magnetic',markerfacecolor='gray', 
                                markersize=dotsize)]
        
        # plot legend on axes
        self.ax.legend(handles=legend_elements, fontsize='x-small')

    def plot_text(self):
        """ sets the text on the bottom center of the plot
        telling user how to access instructions """

        # text instructions on plot GUI
        self.ax.text2D(0.5,-0.08,s= 
        "Press i to view control instructions", horizontalalignment='center', 
        transform=self.ax.transAxes, fontweight='bold')

    def set_plot_params(self, cif):
        """ sets plot parameters such as:
        colors for selected / non-selected
        plot and window titles
        removes axis ticks
        label axes x,y,z
        center plot around centroid and fit axes to cover all of the structure
        """
        # set colors
        self.blue = np.array([0.12156863, 0.4666667, 0.70588235, 1.])
        self.red = np.array([1,0,0,1])
        self.fc = self.plot.get_facecolors()

        # graph cosmetics
        title = "\n\n"+str(cif)
        self.fig.canvas.set_window_title("MagPlotSpin")
        self.fig.suptitle(title, fontweight='bold')
        
        # remove all axes ticks
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_zticks([])

        # label axes in bold
        self.ax.set_xlabel("X", fontweight='bold')
        self.ax.set_ylabel("Y", fontweight='bold')
        self.ax.set_zlabel("Z", fontweight='bold')
            
        # center and scale all axes equally
        if len(self.others) != 0:
            self.centroid = (np.sum(self.X[:,:3], axis=0) + np.sum(self.others, axis=0)) / (len(self.X) + len(self.others))
        else: 
            self.centroid = np.sum(self.X[:,:3], axis=0) / len(self.X)

        # get coordinate furthest from centroid and scale axes accordingly, centering the plot
        self.axscalefactor = np.max(np.abs(self.X[:,:3] - self.centroid))
        self.zoom = 1.2

        # scale axes
        self.ax.set_xlim3d(self.centroid[0] - self.zoom*self.axscalefactor, 
                           self.centroid[0] + self.zoom*self.axscalefactor)
        self.ax.set_ylim3d(self.centroid[1] - self.zoom*self.axscalefactor,
                           self.centroid[1] + self.zoom*self.axscalefactor)
        self.ax.set_zlim3d(self.centroid[2] - self.zoom*self.axscalefactor,
                           self.centroid[2] + self.zoom*self.axscalefactor)
    
    def on_close(self, event=[]):
        """
        Function called when escape is pressed / plot is closed
            Upon close, data is saved in the temp folder
        """
        os.chdir('../temp')
        with open('X.npy', 'wb') as f:
            np.save(f, self.X)
        
    def enter(self):
        """
        Function called when enter is pressed
            Upon enter, if any points are selected, vector assignement GUI 
            is opened and the input data is loaded into the magview viewer
        """
        # change directory and run vector assignment GUI
        os.chdir('../textgui')
        os.system('python3 setspin.py') 
        os.chdir('../temp')
        # if vector was set in the seperate GUI
        if os.path.exists("vector.npy"):
            with open('vector.npy', 'rb') as f:
                vector = np.load(f)
                mag = np.load(f)
            os.remove('vector.npy')
            # normalize and set vector
            if len(vector) != 1:
                norm = la.norm(vector)
                if norm != 0:
                    self.X[np.array(self.clicked),4:] = vector / norm * np.sign(mag)
                    self.X[np.array(self.clicked),3] = 1
                    self.magscale[np.array(self.clicked)] = np.abs(mag)
        else:
            # set color back to blue if nothing was done
            self.fc[np.array(self.clicked),:] = self.blue
        # reset colors and replot
        self.plot._facecolor3d = self.fc
        self.plot._edgecolor3d = self.fc
        self.clicked = []
        self.redraw_arrows()
        self.plotted = (self.X[:,3] == 1).nonzero()                

    def on_key_press(self, event):
        """
        Keyboard helper function that sends a keyboard touch to the
        appropriate action
        """

        if (event.key == "enter") and (len(self.clicked) != 0): # proceed to save and continue to vector assignemnt
            self.enter()
        elif (event.key == "escape"): # end program
            plt.close()

        else:
            if (event.key == "right") and (len(self.plotted) != 0) and (self.axscalefactor/self.l) < .26: # grow arrow
                self.l = 0.9*self.l
                self.redraw_arrows()
            elif (event.key == "left") and (len(self.plotted) != 0) and (self.axscalefactor/self.l) > .04: # shrink arrow
                self.l = 10*self.l/9
                self.redraw_arrows()
            elif event.key == "down" and self.s > 3: # shrink size of point
                self.s = 0.9*self.s
                self.redraw_scatter()
            elif event.key == "up" and self.s < 1600: # grow size of point
                self.s = 10*self.s/9
                self.redraw_scatter()
            elif event.key == "ctrl+-" and self.zoom < 2.5: # zoom out of structure
                self.zoom = 10*self.zoom/9
                self.axes_lim()
            elif event.key == "ctrl+=" and self.zoom > 0.5: # zoom into structure
                self.zoom = 9*self.zoom/10 
                self.axes_lim()
            elif event.key == "i": # open instructions
                os.chdir('../textgui')
                os.system('python3 instructions.py') 
                os.chdir('../temp')
            elif event.key == "t": # toggle non-magnetic atoms
                if len(self.others) != 0:
                    self.tog = bool(1 - self.tog)
                    if self.tog:
                        self.fixed.remove()
                    else:
                        self.fixed = self.ax.scatter(self.others[:,0],self.others[:,1],
                                                     self.others[:,2],s=self.s/3,
                                                     facecolors="gray", edgecolors="gray")
                    
        if event.key in {"right","left","t","i","down","up","ctrl+-","ctrl+=","enter"}:
            # update canvas
            self.fig.canvas.draw_idle()

    def redraw_arrows(self):
        """
        Remove and Replot arrows with updated info
        """
        if len(self.quiver) != 0: # check if there are arrows to remove
            for i in range(len(self.quiver)):
                self.quiver[i].remove()
        self.quiver = []
        for count, row in enumerate(self.X): # plot each arrow individually
            self.quiver += [self.ax.quiver(row[0], row[1], row[2], row[4], row[5], row[6], 
                                     length=2*self.axscalefactor/self.l*self.magscale[count], 
                                     color="black", pivot="middle", arrow_length_ratio=0.3)]
        
    def redraw_scatter(self):
        """
        Remove and Replot dots with updated info
        """
        self.plot.remove() # remove magnetic atoms
        if (len(self.others) != 0) and (self.tog == False): # check if there non-magnetics to remove
            self.fixed.remove()
            self.fixed = self.ax.scatter(self.others[:,0],self.others[:,1],self.others[:,2],
                               s=self.s/3, facecolors="gray", edgecolors="gray")
        # replot magnetics
        self.plot = self.ax.scatter(self.X[:,0],self.X[:,1],self.X[:,2],
                               picker=True, s=self.s, facecolors=self.fc,
                               edgecolors=self.fc)

    def on_click(self, event):
        """
        When artist (dot) is clicked, the appropriate action is taken:
            left click: selected
            right click: remove 
        """
        # indeces in X matrix that were clicked on
        ind = event.ind
        #check if any are already assigned (fixed)
        fixed = True if np.sum(self.X[ind,3]) > 0 else False

        
        if str(event.mouseevent.button) == "MouseButton.LEFT" and not fixed:
            
            for i in ind:

                # add to clicked if not already in it and change color to red
                if i not in self.clicked:
                    self.clicked += [i]
                    self.fc[i,:] = self.red
                # otherwise remove it from clicked and change color to blue
                else:
                    self.clicked.remove(i)
                    self.fc[i,:] = self.blue
                # update plot colors
                self.plot._facecolor3d = self.fc
                self.plot._edgecolor3d = self.fc
            
        elif str(event.mouseevent.button) == "MouseButton.RIGHT" and fixed:
            
            #set vector data to zero and update
            self.X[np.array(ind),3:] = np.zeros(4)
            self.redraw_arrows()   
            #reset colors to blue
            self.fc[np.array(ind),:] = self.blue
            #remove each from clicked and update colors in plot
            for i in ind:
                if i in self.clicked:
                     self.clicked.remove(i)
            self.plot._facecolor3d = self.fc
            self.plot._edgecolor3d = self.fc
            # update plotted
            self.plotted = (self.X[:,3] == 1).nonzero() 
        self.fig.canvas.draw_idle()

mpl.rcParams['toolbar'] = 'None'       # remove matplotlib toolbar for further plots
