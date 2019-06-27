# Adaptive Traffic Modeling

The code in this repository is for modeling traffic networks in an adaptive traffic project. The system stores traffic grids as a directed graph (using the NetworkX Python library), where lights are represented by nodes and roads by edges. Cars move along the graph and are at all times associated with a given edge.

To use this, look at the main function in grid\_networkx.py for a basic example of a one-way road with a single traffic light. A more complex example is given in oneway\_2x2.py

### Creating a traffic grid

There are three components to a traffic grid. First, instantiate the traffic grid:

`grid = TrafficGrid()`

Lights should be added first, using the function below. See the code for a more detailed list of keyword arguments. In general, the timer and light index are the most important arguments. The timer keyword can be set to -1, in which case the light will act as a "driveway" or "parking space" - that is, cars will be annihilated upon reaching that node

`grid.add_light(light_index, timer=timer, **kwargs)`

Next, roads should be added using the function below. See the code for more detailed keyword arguments. The arguments light1/light2 are the indices of the lights that the road begins/ends at. Roads are one way, so if you wish to have a two-way road you must add one from light1 to light2 and another from light2 to light1. The direction argument specifies which "traffic light" controls the flow of a given road. By default, each light node in the graph has two "traffic lights", one for vertical and one for horizontal roads. These light colors are stored in a list. The direction should be an index into this list.

`grid.add_road(light1, light2, direction, **kwargs)`

Finally, cars can be added using `grid.add_car(light0, light1, **kwargs)`. Cars are by default placed at position 0 along a given road with speed 0.

### Simulating traffic

After a grid has been created and populated, it can be updated in time using the function `grid.update()`. To get a status summary, use `grid.print_status()`. 

To get a graphical view of the state of the traffic grid, use the `GridDrawer` class, which slightly extends the `drawing` module in NetworkX. See `grid_networkx.py` for an example of how to use this.
