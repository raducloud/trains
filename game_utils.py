import math


class Utils:
    def get_opposite_end(end:str)->str:
        return {'L':'R', 'R':'L', 'U':'D', 'D':'U', None:None}[end]
    def get_endings_by_prev_tile(prev_tile_x, prev_tile_y, current_tile_x, current_tile_y)->tuple[str, str]:
        # the below assumes Manhattan-like geometry (no diagonals). 
        # Note that y axis increases DOWNWARDS in Pygame.
        # end2 value is just a default (opposite of end1)
        if current_tile_x > prev_tile_x: return ('L', 'R') 
        elif current_tile_x < prev_tile_x: return ('R', 'L')
        elif current_tile_y > prev_tile_y: return ('U', 'D') # this case is for current_tile_x = prev_tile_x
        else: return ('D', 'U')
    def sign(n: int) -> int:
        if n > 0: return 1
        elif n < 0: return -1
        else: return 0
    def smart_range(start:int, end:int, step:int = 0, inclusive = True):
        """A version of range() which:
         - has the option to include the end value
         - allows implicit descending step, in case start > end"""

        direction_unit = Utils.sign(end - start)
        if step == 0:
          step = direction_unit # so it will take a default of either 1 or -1, depending if start->end is ascending or descending
        if step > 0:
            return range(start, end + int(inclusive), step)
        elif step < 0:
            return range(start, end - int(inclusive), step)
        else:  # step parameter is 0 and start and end are the same - only one thing to do in this case, return the single value
            return range(start, end + int(inclusive))
    def round_with_direction(number: float, direction: int) -> int:
      """Rounds a float to the nearest integer, either flooring or ceiling."""
      if direction >= 0: return math.ceil(number)
      else: return math.floor(number)
    