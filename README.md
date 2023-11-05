# <strong>Pong-Inertial</strong>
## A simple yet unintuitive game
#### Ben Coull-Neveu, Franco Del-Balso, Piotre Jakuc, Sandhya Rottoo

It's just pong... but rotating. We know, pretty mind-boggling.
What's different about this pong, you may ask? It turns out that on a (non-inertial) rotating body, there exist so-called fictitious forces at play.

### The Physics
These forces are fully described, rather succinctly, by just a few straightforward (okay, *maybe* not) equations. For our purposes, we don't need to consider the translational force in the non-inertial frame (unfortunately, since it is indubitably the most intuitive one of the bunch). Centrifugal, coriolis and azimuthal can be described as follows: 

```math
\begin{align} \vec{F}_{fictitious} &= \vec{F}_{centrifugal} + \vec{F}_{coriolis} + \vec{F}_{azimuthal} \nonumber \\ &= -m\vec{\omega} \times (\vec{\omega} \times \vec{r}) - 2m\vec{\omega} \times \vec{v} - m\frac{d\vec{\omega}}{dt}\times \vec{r}. \nonumber  \end{align}
 ```

### How to Play
This game runs solely on Python. All the user needs to do is download the Multimedia folder and run:
```ruby
python main.py
```
in their terminal, in the same directory. The game works by using keys *a* & *b* (for player 1) and the right & left arrows (for player 2) in order to stop the ball (the coloured, moving disk) from leaving the turn table. Note that the colour of the ball indicates the player who must next hit the ball (it is colour-coded). 

### Requirements
To run this successfully, ensure that you have up-to-date versions of Numpy,
```ruby
pip install numpy
```
and PyGame.
```ruby
pip install pygame
```
