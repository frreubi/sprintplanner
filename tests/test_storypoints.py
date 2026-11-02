import unittest
from berekeningen import bereken_storypoints


class TestStorypoints(unittest.TestCase):
    def test_standaardwerkstroom_zonder_percentage(self):
        with self.assertRaises(ValueError):
            bereken_storypoints(
                standaard_werkstroom="ops",
                netto_uren=40,
                dev=100,
                ops=0,
                func=0,
                uren_per_storypoint=4,
            )


    def test_verdeling_bij_gelijke_resten(self):
        resultaat = bereken_storypoints(
            standaard_werkstroom="dev",
            netto_uren=40,
            dev=25,
            ops=75,
            func=0,
            uren_per_storypoint=4,
        )

        self.assertEqual(
            resultaat,
            {"totaal": 10, "dev": 3, "ops": 7, "func": 0}
        )


    def test_resterende_uren_buiten_sprintwerk(self):
        resultaat = bereken_storypoints(
            standaard_werkstroom="dev",
            netto_uren=40,
            dev=60,
            ops=0,
            func=0,
            uren_per_storypoint=4,
        )

        self.assertEqual(
            resultaat,
            {"totaal": 6, "dev": 6, "ops": 0, "func": 0}
        )


    def test_geen_sprintwerk(self):
        resultaat = bereken_storypoints(
            standaard_werkstroom=None,
            netto_uren=40,
            dev=0,
            ops=0,
            func=0,
            uren_per_storypoint=4,
        )

        self.assertEqual(
            resultaat,
            {"totaal": 0, "dev": 0, "ops": 0, "func": 0}
        )


    def test_medewerker_zonder_standaardwerkstroom(self):
        resultaat = bereken_storypoints(
            standaard_werkstroom=None,
            netto_uren=40,
            dev=50,
            ops=0,
            func=0,
            uren_per_storypoint=4,
        )

        self.assertEqual(
            resultaat,
            {"totaal": 5, "dev": 5, "ops": 0, "func": 0}
        )


    def test_totaal_storypoints_half_naar_boven(self):
        resultaat = bereken_storypoints(
            standaard_werkstroom="dev",
            netto_uren=10,
            dev=100,
            ops=0,
            func=0,
            uren_per_storypoint=4,
        )

        self.assertEqual(
            resultaat,
            {"totaal": 3, "dev": 3, "ops": 0, "func": 0}
        )


    def test_verdeling_over_drie_werkstromen(self):
        resultaat = bereken_storypoints(
            standaard_werkstroom="dev",
            netto_uren=40,
            dev=50,
            ops=30,
            func=20,
            uren_per_storypoint=4,
        )

        self.assertEqual(
            resultaat,
            {"totaal": 10, "dev": 5, "ops": 3, "func": 2}
        )


    def test_correctie_naar_kleinste_werkstroom(self):
        resultaat = bereken_storypoints(
            standaard_werkstroom="func",
            netto_uren=44,
            dev=40,
            ops=40,
            func=20,
            uren_per_storypoint=4,
        )

        self.assertEqual(
            resultaat,
            {"totaal": 11, "dev": 4, "ops": 4, "func": 3}
        )


    def test_correctie_bij_overschot(self):
        resultaat = bereken_storypoints(
            standaard_werkstroom="dev",
            netto_uren=40,
            dev=45,
            ops=35,
            func=20,
            uren_per_storypoint=4,
        )

        self.assertEqual(
            resultaat,
            {"totaal": 10, "dev": 5, "ops": 3, "func": 2}
        )


if __name__ == "__main__":
    unittest.main()