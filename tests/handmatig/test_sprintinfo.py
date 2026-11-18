
from datetime import date
from sprintinfo import SprintInfo

sprints = [
    {
        "sprintID": 43,
        "begindatum": date(2026, 10, 5),
        "einddatum": date(2026, 10, 23),
    },
    {
        "sprintID": 44,
        "begindatum": date(2026, 10, 26),
        "einddatum": date(2026, 11, 13),
    },
    {
        "sprintID": 45,
        "begindatum": date(2026, 11, 16),
        "einddatum": date(2026, 12, 4),
    },
]

SprintInfo(sprints, 1).window.mainloop()
