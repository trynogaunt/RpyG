def splash() -> list[str]:

        R = [
            "██████╗",
            "██╔══██╗",
            "██║  ██║",
            "██████╔╝",
            "██╔══██╗",
            "██║  ██║",
            "╚═╝  ╚═╝",
        ]

        P = [
            "██████╗",
            "██╔══██╗",
            "██████╔╝",
            "██╔═══╝ ",
            "██║     ",
            "██║     ",
            "╚═╝     ",
        ]

        Y = [
            "██╗   ██╗",
            "╚██╗ ██╔╝",
            " ╚████╔╝ ",
            "  ╚██╔╝  ",
            "   ██║   ",
            "   ██║   ",
            "   ╚═╝   ",
        ]

        G = [
            " ██████╗",
            "██╔════╝",
            "██║  ███╗",
            "██║   ██║",
            "██║   ██║",
            "╚██████╔╝",
            " ╚═════╝ ",
        ]

        return [R, P, Y, G]

def rows() -> list[list[str]]:
    letters = splash()
    widths = [max(len(line) for line in letter) for letter in letters]
    return [
        [letter[row].ljust(width) for letter, width in zip(letters, widths)]
        for row in range(len(letters[0]))
    ]