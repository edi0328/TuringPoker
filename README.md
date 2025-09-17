#Poker Bot
This repository contains our code for the **McGill Poker Bot Tournament**, where our bot finished with a **profit of \$32**.  

---

## Strategy Overview
Our bot uses a simple but effective heuristic:  
- **Go all-in** when the probability of a good hand is below a certain threshold.  
- **Check otherwise**.
- **Fold if bet is too high and chances of winning are low**

This algorithm was surprisingly competitive in the tournament setting, though it leaves plenty of room for strategic improvements.  
