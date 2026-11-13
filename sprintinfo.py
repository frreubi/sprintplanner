import customtkinter as ctk
from tkinter import messagebox
import json
import sys
from datetime import date

from sprintgegevens import haal_sprintresultaten_op


ctk.deactivate_automatic_dpi_awareness()

ACHTERGROND = "#24212B"
PANEEL = "#302C38"
RIJ = "#393442"
PAARS = "#8050B5"
TEKST = "#E9E6EF"
GEDIMD = "#AAA5B5"
PAARS_HOVER = "#9569C5"


class SprintInfo:

    def __init__(self, sprints, huidige_index):
        self.sprints = sprints
        self.huidige_index = huidige_index
        self.index = huidige_index
        self.window = ctk.CTk()

        self.build_controls()

    def build_controls(self):
        ctk.set_appearance_mode("dark")

        self.window.title("SprintInfo")
        self.window.geometry("700x800")
        self.window.minsize(600, 540)
        self.window.configure(fg_color=ACHTERGROND)

        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(3, weight=1)

        self.build_header()
        self.build_sprint_header()
        self.build_view_selector()
        self.build_table()
        self.build_navigation()

        self.toon_sprint()

    def build_header(self):
        frame = ctk.CTkFrame(self.window, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="ew", padx=20, pady=15)

        ctk.CTkLabel(
            frame,
            text="📊  SprintInfo",
            font=("Segoe UI", 19, "bold"),
            text_color=TEKST,
        ).pack(side="left")

        self.vernieuw_knop = ctk.CTkButton(
            frame,
            text="↻",
            width=38,
            height=36,
            corner_radius=10,
            fg_color=PAARS,
            hover_color=PAARS_HOVER,
            command=self.vernieuw_sprints,
        )
        self.vernieuw_knop.pack(side="right")

    def build_sprint_header(self):
        frame = ctk.CTkFrame(self.window, fg_color="transparent")
        frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 15))

        self.sprint_naam = ctk.CTkLabel(
            frame,
            text="",
            text_color="#B99ADC",
            font=("Segoe UI", 11, "bold"),
        )
        self.sprint_naam.pack(anchor="w")

        self.sprint_datums = ctk.CTkLabel(
            frame,
            text="",
            text_color=TEKST,
            font=("Segoe UI", 23, "bold"),
        )
        self.sprint_datums.pack(anchor="w", pady=(3, 0))

    def build_view_selector(self):
        frame = ctk.CTkFrame(self.window, fg_color="transparent")
        frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

        ctk.CTkLabel(
            frame,
            text="Weergave",
            text_color=GEDIMD,
        ).pack(side="left")

        self.weergave = ctk.CTkSegmentedButton(
            frame,
            values=["Storypoints", "Uren"],
            selected_color=PAARS,
            selected_hover_color=PAARS_HOVER,
            unselected_color=PANEEL,
            unselected_hover_color=RIJ,
            text_color=TEKST,
            corner_radius=10,
            command=self.toon_sprint,
        )
        self.weergave.set("Storypoints")
        self.weergave.pack(side="right")

    def build_table(self):
        frame = ctk.CTkFrame(
            self.window,
            fg_color=PANEEL,
            corner_radius=12,
        )
        frame.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=20,
            pady=10,
        )

        ctk.CTkLabel(
            frame,
            text="Capaciteit per medewerker",
            font=("Segoe UI", 14, "bold"),
            text_color=TEKST,
        ).pack(anchor="w", padx=15, pady=12)

        self.fouten_label = ctk.CTkLabel(
            frame,
            text="",
            text_color="#F2A3A3",
            fg_color=RIJ,
            corner_radius=8,
            justify="left",
            anchor="w",
            wraplength=620,
            font=("Segoe UI", 12),
        )

        self.koppen_frame = ctk.CTkFrame(
            frame,
            fg_color="transparent",
        )
        self.koppen_frame.pack(
            fill="x",
            padx=(10, 26),
            pady=5,
        )

        self.medewerkers_frame = ctk.CTkScrollableFrame(
            frame,
            fg_color="transparent",
            scrollbar_button_color=PAARS,
            scrollbar_button_hover_color=PAARS_HOVER,
        )
        self.medewerkers_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10),
        )

    def build_table_header(self, werkstromen):
        for widget in self.koppen_frame.winfo_children():
            widget.destroy()

        rij = ctk.CTkFrame(self.koppen_frame, fg_color="transparent")
        rij.pack(fill="x")

        ctk.CTkLabel(
            rij,
            text="MEDEWERKER",
            anchor="w",
            text_color=GEDIMD,
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left", fill="x", expand=True, padx=10)

        for werkstroom in werkstromen:
            ctk.CTkLabel(
                rij,
                text=werkstroom.upper(),
                width=71,
                anchor="center",
                text_color=GEDIMD,
                font=("Segoe UI", 12, "bold"),
            ).pack(side="left", padx=3)

    def build_table_row(self, medewerker, werkstromen, veld):
        rij = ctk.CTkFrame(
            self.medewerkers_frame,
            fg_color=RIJ,
            corner_radius=8,
        )
        rij.pack(fill="x", pady=4)

        ctk.CTkLabel(
            rij,
            text=medewerker["naam"],
            anchor="w",
            text_color=TEKST,
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=10,
            pady=10,
        )

        for werkstroom in werkstromen:
            waarde = medewerker[veld].get(werkstroom, 0)
            ctk.CTkLabel(
                rij,
                text=str(waarde),
                width=71,
                anchor="center",
                text_color="#B49BCE",
            ).pack(side="left", padx=3)

    def build_navigation(self):
        frame = ctk.CTkFrame(self.window, fg_color="transparent")
        frame.grid(row=4, column=0, sticky="ew", padx=20, pady=15)

        self.vorige_knop = ctk.CTkButton(
            frame,
            text="‹  Vorige",
            width=130,
            height=38,
            corner_radius=10,
            fg_color=PANEEL,
            hover_color=RIJ,
            command=lambda: self.wijzig_sprint(-1),
        )
        self.vorige_knop.pack(side="left", expand=True, padx=5)

        self.huidige_knop = ctk.CTkButton(
            frame,
            text="Huidige sprint",
            width=130,
            height=38,
            corner_radius=10,
            fg_color=PAARS,
            hover_color=PAARS_HOVER,
            command=lambda: self.wijzig_sprint(0),
        )
        self.huidige_knop.pack(side="left", expand=True, padx=5)

        self.volgende_knop = ctk.CTkButton(
            frame,
            text="Volgende  ›",
            width=130,
            height=38,
            corner_radius=10,
            fg_color=PANEEL,
            hover_color=RIJ,
            command=lambda: self.wijzig_sprint(1),
        )
        self.volgende_knop.pack(side="left", expand=True, padx=5)

    def vernieuw_sprints(self):
        geselecteerde_sprint = (
            self.sprints[self.index]["naam"]
            if self.sprints and 0 <= self.index < len(self.sprints)
            else None
        )
        self.vernieuw_knop.configure(state="disabled")

        try:
            sprints = haal_sprintresultaten_op()

            for sprint in sprints:
                if isinstance(sprint["begindatum"], str):
                    sprint["begindatum"] = date.fromisoformat(
                        sprint["begindatum"]
                    )
                if isinstance(sprint["einddatum"], str):
                    sprint["einddatum"] = date.fromisoformat(
                        sprint["einddatum"]
                    )

            vandaag = date.today()
            huidige_index = next(
                (
                    i for i, sprint in enumerate(sprints)
                    if sprint["einddatum"] >= vandaag
                ),
                len(sprints) - 1,
            )

            self.sprints = sprints
            self.huidige_index = huidige_index

            self.index = next(
                (
                    i for i, sprint in enumerate(sprints)
                    if sprint["naam"] == geselecteerde_sprint
                ),
                huidige_index,
            )

            self.toon_sprint()

        except Exception as fout:
            messagebox.showerror(
                "Vernieuwen mislukt",
                str(fout),
                parent=self.window,
            )

        finally:
            self.vernieuw_knop.configure(state="normal")

    def wijzig_sprint(self, stap):
        if stap == 0:
            self.index = self.huidige_index
        else:
            nieuw_index = self.index + stap
            if 0 <= nieuw_index < len(self.sprints):
                self.index = nieuw_index

        self.toon_sprint()

    def toon_sprint(self, _waarde=None):
        for widget in self.medewerkers_frame.winfo_children():
            widget.destroy()

        if not 0 <= self.index < len(self.sprints):
            self.sprint_naam.configure(text="Geen sprint beschikbaar")
            self.sprint_datums.configure(text="")
            self.build_table_header([])
            self.update_navigation()
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
            for werkstroom, waarde in medewerker[veld].items()
            if waarde > 0
        })

        self.sprint_naam.configure(text=sprint["naam"].upper())
        self.sprint_datums.configure(
            text=(
                f"{sprint['begindatum']:%d %b} – "
                f"{sprint['einddatum']:%d %b}"
            )
        )

        fouten = sprint.get("fouten", [])

        if fouten:
            self.koppen_frame.pack_forget()
            self.medewerkers_frame.pack_forget()

            tekst = (
                "Deze sprint kan niet worden berekend. "
                "Los eerst de volgende fouten op:\n\n"
            )
            tekst += "\n".join(f"• {fout}" for fout in fouten)

            self.fouten_label.configure(text=tekst)
            self.fouten_label.pack(
                fill="x",
                padx=10,
                pady=(5, 10),
            )
        else:
            self.fouten_label.pack_forget()

            self.koppen_frame.pack(
                fill="x",
                padx=(10, 26),
                pady=5,
            )
            self.medewerkers_frame.pack(
                fill="both",
                expand=True,
                padx=10,
                pady=(0, 10),
            )

            self.build_table_header(werkstromen)

            for medewerker in sprint["netto_uren"]:
                self.build_table_row(medewerker, werkstromen, veld)

        self.update_navigation()

    def update_navigation(self):
        self.vorige_knop.configure(
            state="normal" if self.index > 0 else "disabled"
        )
        self.volgende_knop.configure(
            state=(
                "normal"
                if self.index < len(self.sprints) - 1
                else "disabled"
            )
        )
        self.huidige_knop.configure(
            state=(
                "disabled"
                if self.index == self.huidige_index
                else "normal"
            )
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
            if sprint["einddatum"] >= vandaag
        ),
        len(sprints) - 1,
    )

    SprintInfo(sprints, huidige_index).window.mainloop()
