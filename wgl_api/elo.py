from openskill.models import BradleyTerryFull

STARTING_ELO = 1500

MODEL = BradleyTerryFull(
    mu=STARTING_ELO,
    sigma=STARTING_ELO / 3,
    beta=STARTING_ELO / 6,
    tau=STARTING_ELO / 300,
)
