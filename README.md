![](https://github.com/erocoar/vetoboxing/blob/master/vetoboxing/assets/vetoboxingLogo%20-%20Kopie.png)
## Dependencies
[Shapely](https://anaconda.org/conda-forge/shapely)

scipy, pandas, numpy, matplotlib that are included in anaconda

## Run Vetoboxing
```
python vetoboxing.py
```

## Interface
![][(https://puu.sh/yjBu4/53af0408fe.png)
### Main Toolbar
![](https://github.com/erocoar/vetoboxing/blob/master/vetoboxing/rmd/mainToolbar.png)

1. ![](https://puu.sh/yjc9S/4bb6bd826e.png) **Load, Save, Save All**

   **Load** preset settings and voter values from a .json file
   
   **Save** current options and voter values in specified folder in a .json file
   
   **Save All** options and voter games in specified folder (currently not connected)
   
2. ![](https://puu.sh/yjbEH/f012e42bf0.png) **Run, Run All, Run Repeatedly**

   **Run** the currently selected game
   
   **Run All** games that are open
   
   **Run Repeatedly** the currently selected game (a specified number of times) (currently not connected)
   
3. ![](https://puu.sh/yjbOM/3afea006f6.png) **Open Settings, Manifesto, Plot**

   Opens specified window if not visible
   
   [**Settings**](https://github.com/erocoar/vetoboxing/blob/master/README.md#run)
   
   **Manifesto**
   
   **Plot**
   
4. ![](https://puu.sh/yjbQl/9a0ba04cc6.png) **Clear**

   Clears all open games (currently not connected)
   
### Game Widget
![](https://github.com/erocoar/vetoboxing/blob/master/vetoboxing/rmd/gameTable.png)

The game widget is where you can manage and set up simulations (games). Each tab here represents a game **with its own distinct run options** (this means, when switching tabs, the run options will change to the now selected game's options - also in the settings). 

   The first table represents the voters. Names and starting positions per dimension can be filled in. Agenda setter and veto player roles can be assigned by entering True or False (alternatively, 1 or 0) for every voter. Note that the agenda setter role can only be assigned once, but has to be assigned.
 
 ### Game Widget Toolbar
 ![](https://github.com/erocoar/vetoboxing/blob/master/vetoboxing/rmd/gameTableToolbar.png)
 
 The game widget toolbar is for ease of setting up games. 
 
1. ![](https://puu.sh/yjbkI/544e2ff0f8.png) **Add and Clear**

   A click on the add button will add a row (a voter) to the simulation
   A click on the clear button will remove the last row (voter) from the simulation
   Alternatively, rows can be inserted / removed in specified locations via right click
    
2. ![](https://puu.sh/yjbpY/71b2ae502b.png) **Set up Voter Roles**

   Changing the value in the spin box will change the number of veto players that will be added
   Adding Agenda Setter (AS) and Veto Players (VP) can be toggled on and off. Green background = Toggled on
   A click on the shuffle button will randomly assign the agenda setter role and the specified number of veto player roles
   
### Settings 
#### General

(currently not connected)
#### Run
![](https://puu.sh/yjBuF/ff1340743f.png)

Run settings are specific to each game (that is, each tab).

**Runs** specifies the number of times the simulation will run

**Dimensions** specifies the number of dimensions the game will be evaluated on

**Breaks** specifies the density of the grid on which the game is evaluated - this is only necessary if the grid method is selected

**Method** Grid: Evaluate the game on a grid of points. Optimization: Evaluate via circle intersections and interpolation. Optimization can only be chosen for 1D and 2D.

**Save** If yes, a CSV with data of all runs will be created

**Visualize** If yes, data will be visualized and displayed in the plot widget.

**Save Visualize** If yes, plots of each run will be made and saved. **NOTE** that if this is set to yes, and visualize is also set to yes, plots will be made and saved BEFORE plot data is sent to the UI. It takes about 1 second per plot to save.

**Alter Preferences** Drift: Voter positions drift a specified (or random) amount every run. No: Voter positions are fixed.

**Alter Status Quo** History + Drift: Status Quo is evaluated on history (the outcome of a voting game becomes the new status quo) and drift (specified or random). History: The outcome of a run becomes the new status quo. Random: The status quo changes randomly every run. No: Status Quo is constant. 

**Distance Type** Euclidean or City-Block

**Distribution** The distribution drawn from if there is random drift

#### Visualization
(currently not connected)





   
 

