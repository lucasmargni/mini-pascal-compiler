class Token:
    name : str = ""
    atribute : str = ""

    # constructor
    def __init__(self, name : str, atribute : str = ""):
        self.name = name
        self.atribute = atribute

    # shows the token name and atribute (if exists) between < and >
    def toString(self) -> str:
        string : str = ""

        if(self.atribute):
            string = f"<{self.name}, {self.atribute}>"
        else:
            string = f"<{self.name}>"

        return string