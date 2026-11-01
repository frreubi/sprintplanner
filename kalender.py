from datetime import date, timedelta


def eerste_roostermaandag(jaar):
    eerste_donderdag = date(jaar, 1, 1)
    while eerste_donderdag.weekday() != 3:
        eerste_donderdag += timedelta(days=1)

    return eerste_donderdag - timedelta(days=3)

def eerste_maandag_na_jaar(jaar):
    laatste_dag = date(jaar, 12, 31)
    dagen_tot_maandag = (7 - laatste_dag.weekday()) % 7
    dagen_tot_maandag = dagen_tot_maandag or 7
    return laatste_dag + timedelta(days=dagen_tot_maandag)

def einde_rooster(jaar):
    begin = eerste_roostermaandag(jaar)
    return begin + timedelta(days=371)

def datums_roosterjaar(jaar):
    begin = eerste_roostermaandag(jaar)
    return [begin + timedelta(days=i) for i in range(371)]

MAANDNAMEN = (
    "JANUARI", "FEBRUARI", "MAART", "APRIL",
    "MEI", "JUNI", "JULI", "AUGUSTUS",
    "SEPTEMBER", "OKTOBER", "NOVEMBER", "DECEMBER",
)

def maandkoppen_roosterjaar(jaar):
    datums = datums_roosterjaar(jaar)
    maandkoppen = []

    for maand in range(1, 13):
        indices = [
            i for i, datum in enumerate(datums)
            if datum.year == jaar and datum.month == maand
        ]

        maandkoppen.append((
            MAANDNAMEN[maand - 1],
            indices[0],
            indices[-1],
        ))

    return maandkoppen