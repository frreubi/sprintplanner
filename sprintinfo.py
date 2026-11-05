
import tkinter as tk
from tkinter import ttk
import json
import sys
from datetime import date


class SprintInfo:

    def __init__(self, sprints, huidige_index):
        self.sprints = sprints
        self.huidige_index = huidige_index
        self.index = huidige_index
        self.build_controls()

    def build_controls(self):
        self.window = tk.Tk()
        self.window.title("Sprintinfo")
        self.window.geometry("460x400")
        self.window.resizable(False, False)
        stijl = ttk.Style()
        stijl.configure(
            "Treeview.Heading",
            background="#D9E2F3",
            foreground="#222222",
            font=("Arial", 9, "bold"),
        )

        self.tekst = tk.Label(
            self.window,
            font=("Arial", 12)
        )
        self.tekst.pack(pady=12)

        self.weergave = tk.StringVar(value="Storypoints")

        ttk.Radiobutton(
            self.window,
            text="Storypoints",
            variable=self.weergave,
            value="Storypoints",
            command=self.toon_sprint
        ).pack()

        ttk.Radiobutton(
            self.window,
            text="Uren",
            variable=self.weergave,
            value="Uren",
            command=self.toon_sprint
        ).pack()

        self.tabel = ttk.Treeview(
            self.window,
            columns=("medewerker",),
            show="headings",
            height=13,
        )
        self.tabel.heading("medewerker", text="Medewerker", anchor="w")
        self.tabel.column("medewerker", width=320)
        self.tabel.pack(padx=10, fill="x")

        knoppen = tk.Frame(self.window)
        knoppen.pack(pady=12)

        self.vorige_knop = tk.Button(
            knoppen,
            text="Vorige sprint",
            command=lambda: self.wijzig_sprint(-1)
        )
        self.vorige_knop.pack(side="left", padx=3)

        self.huidige_knop = tk.Button(
            knoppen,
            text="Huidige sprint",
            command=lambda: self.wijzig_sprint(0),
            state="disabled",
        )
        self.huidige_knop.pack(side="left", padx=3)

        self.volgende_knop = tk.Button(
            knoppen,
            text="Volgende sprint",
            command=lambda: self.wijzig_sprint(1)
        )
        self.volgende_knop.pack(side="left", padx=3)
 
        self.toon_sprint()

    def wijzig_sprint(self, stap):
        if stap == 0:
            self.index = self.huidige_index
        else:
            nieuw_index = self.index + stap
            if 0 <= nieuw_index < len(self.sprints):
                self.index = nieuw_index

        self.huidige_knop.config(
            state="disabled" if self.index == self.huidige_index else "normal"
        )

        self.toon_sprint()

    def toon_sprint(self):
        for item in self.tabel.get_children():
            self.tabel.delete(item)

        if not 0 <= self.index < len(self.sprints):
            self.tekst.config(text="Geen sprint beschikbaar")
            return

        sprint = self.sprints[self.index]
        veld = (
            "storypoints_per_werkstroom"
            if self.weergave.get() == "Storypoints"
            else "uren_per_werkstroom"
        )
        werkstromen = sorted({
            werkstroom
            for medewerker in sprint["netto_uren"]
            for werkstroom, punten in medewerker[veld].items()
            if punten > 0
        })
        kolommen = ("medewerker", *werkstromen)
        self.tabel["columns"] = kolommen
        self.tabel.heading("medewerker", text="Medewerker", anchor="w")
        for werkstroom in werkstromen:
            self.tabel.heading(werkstroom, text=werkstroom.upper())
            self.tabel.column(werkstroom, width=70, anchor="center")    
        self.tekst.config(
            text=(
                f"{sprint['naam']}\n"
                f"{sprint['begindatum']:%d-%m-%Y} t/m "
                f"{sprint['einddatum']:%d-%m-%Y}"
            )
        )

        for medewerker in sprint["netto_uren"]:
            waarden = [
                medewerker["naam"],
                *(
                    medewerker[veld].get(werkstroom, 0)
                    for werkstroom in werkstromen
                ),
            ]
            self.tabel.insert("", "end", values=waarden)

        self.vorige_knop.config(
            state="normal" if self.index > 0 else "disabled"
        )
        self.volgende_knop.config(
            state="normal"
            if self.index < len(self.sprints) - 1
            else "disabled"
        )    


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as bestand:
        sprints = json.load(bestand)

    for sprint in sprints:
        sprint["begindatum"] = date.fromisoformat(
            sprint["begindatum"]
        )
        sprint["einddatum"] = date.fromisoformat(
            sprint["einddatum"]
        )

    vandaag = date.today()
    huidige_index = next(
        (
            i for i, sprint in enumerate(sprints)
            if sprint["begindatum"] <= vandaag <= sprint["einddatum"]
        ),
        0,
    )

    SprintInfo(sprints, huidige_index).window.mainloop()
