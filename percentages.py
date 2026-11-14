
class Percentageverdeling:
    def __init__(self, percentage_id, verdeling):
        if not isinstance(percentage_id, str) or not percentage_id.strip():
            raise ValueError("Percentage-ID is verplicht.")

        if not isinstance(verdeling, dict) or not verdeling:
            raise ValueError("Een percentageverdeling moet minimaal één werkstroom bevatten.")

        for werkstroom, percentage in verdeling.items():
            if not isinstance(werkstroom, str) or not werkstroom.strip():
                raise ValueError("Werkstroom-ID is verplicht.")

            if not isinstance(percentage, (int, float)) or isinstance(percentage, bool):
                raise ValueError("Percentages moeten getallen zijn.")

            if not 0 < percentage <= 1:
                raise ValueError("Percentages moeten groter zijn dan 0 en maximaal 1 zijn.")

        if sum(verdeling.values()) > 1:
            raise ValueError("De totale percentageverdeling mag niet groter zijn dan 100%.")

        self.percentage_id = percentage_id.strip()
        self.verdeling = {
            werkstroom.strip(): percentage
            for werkstroom, percentage in verdeling.items()
        }
