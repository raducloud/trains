class Utils:
    def get_opposite_end(end:str)->str:
        return {'L':'R', 'R':'L', 'U':'D', 'D':'U', None:None}[end]
    def get_endings_by_prev_tile(prev_tile_x, prev_tile_y, current_tile_x, current_tile_y)->tuple[str, str]:
        if current_tile_x > prev_tile_x: return ('L', 'R') # end2 is just a default
        elif current_tile_x < prev_tile_x: return ('R', 'L')
        elif current_tile_y > prev_tile_y: return ('U', 'D')
        else: return ('D', 'U')
        