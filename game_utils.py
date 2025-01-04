class Utils:
    def get_opposite_end(end:str)->str:
        return {'L':'R', 'R':'L', 'U':'D', 'D':'U', None:None}[end]
