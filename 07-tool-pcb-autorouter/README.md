# Python PCB autorouter (grid A*, from the Victron relay extension project)

## Files
- rt.py: Router class. Grid A* / Dijkstra router on a 0.05 mm grid, octilinear moves, layer costs, through vias, obstacles grown by clearance plus half track width, and the net routing loop.
- pl.py: helpers for pcbnew geometry (pad and track shapes as shapely polygons, net and layer mapping, coordinate conversion).
- ncls.py: net class (width, clearance, via size) definitions.
- example_mk12_search.py: how the router is driven: place parts, search terminal pin order and relay rotation with backtracking, route hardest nets first, then check.

## Requirements
- Python 3, KiCad pcbnew Python module (KiCad 7/8/9), numpy, shapely, Pillow (PIL).
- Works on a board file loaded with pcbnew.LoadBoard().

## Use in another project
1. Copy rt.py, pl.py and ncls.py into a folder (for example lib/) in the new project.
2. Add that folder to sys.path, then: import pl; import rt
3. Set pl.b = pcbnew.LoadBoard(path), create Router(region=(x0,y0,x1,y1), g=0.05, layers=(F,B,I2)), then route each net with the router's methods (see example file).
4. Re-run KiCad DRC after routing. The router is a heuristic; check results and route critical nets by hand.

## Notes
- Layer names and stack-up (F.Cu, B.Cu, In2.Cu) are set inside pl.py/rt.py. Change them for other stack-ups.
- The example file depends on this project's part layout and net names. It is a template, not a turnkey script.
