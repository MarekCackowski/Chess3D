# THREE-DIMENSIONAL CHESS
In a number of Star Trek episodes, Kirk and Spock can be seen playing a three dimensional chess variant together. The set used in Star Trek was a prop with no particular rules behind it. After instructions for making the board were published in the Starfleet Technical Reference Manual in 1976, Star Trek fan Andrew Bartmess was excited about this but also disappointed that no rules were provided for the game. So he wrote to the book's author, Franz Joseph Schnaubelt, who encouraged him to develop rules for the game himself. He did and post part of them [here](http://www.yestercade.net/tactical.htm).
![image](https://user-images.githubusercontent.com/122686916/214070868-aa071379-fb11-4780-ac57-59749a262b1d.png)

### Rules
The rules are not that different from classic chess. There are 7 boards - 3 static 4x4 areas and 4 2x2 attacking boards that can be moved, 2 for each player. The moves of each piece is the same, only difference is possibility of changing levels - move is legal, if "looking down on board", as in the picture below, it would be considered legal in regular chess.

![image](https://user-images.githubusercontent.com/122686916/214076872-d89f408b-d172-43be-9ac5-45639e36d3a2.png)

I base my game on [tournament rules for 3D Chess](http://meder.spacechess.org/3dschach/chess3d.htm). I do not implement insufficient mating material, beacuse i suspect it is different than in normal chess beacuse of attack boards.

### Game
This implementation of Chess 3D was designed using Python 3.11 with help of Panda3D libraries to create an interactive board. For pieces and squares I used ready-made models from Panda3D tutorial. I was trying to keep all the rules from the link I provided above.

![image](https://user-images.githubusercontent.com/122686916/214091493-15fd5ca5-6757-48d0-9570-e0eba964573b.png)
