![](https://github.com/erocoar/vetoboxing/blob/master/vetoboxing/assets/vetoboxingLogo%20-%20Kopie.png)

## Usage
### Main Toolbar
![](https://github.com/erocoar/vetoboxing/blob/master/vetoboxing/rmd/mainToolbar.png)
1. **Load Options and Voters**

   Preset settings and voter values can be loaded from a .json file

2. **Save Options and Voters**

   Current Options and voter setup can be saved in specified folder

3. **Run Game**

   Runs the currently selected game

4. **Run All Games**

   Run all games in the UI
   Currently **NOT** connected

5. **Run Repeatedly**

   Repeatedly run current game (a specified number of times)
   Currently **NOT** connected

6. **Show Settings**
   Opens the settings window, where you can access general options, run options and visualization options. 

7. **Show Manifesto Widget**
   Opens Manifesto Widget (if not visible) where you can connect to Manifesto Project 

8. **Show Plot**
   Show Plot Window (if not visible)

9. **Clear all games**
   Clear all games from game widget
   currently **not** connected
   
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
   
   
 

