"""Static business constants for JS Windshields — Dharmapuri branch."""
from pathlib import Path

CLAIM_FORMS_DIR = Path(__file__).parent.parent / "claim_forms"

# Workshop details
WORKSHOP_NAME = "JS WINDSHIELDS"
WORKSHOP_ADDRESS = "5/215, Sagadevan Complex, Lakkiampatty, Dharmapuri - 636705"
WORKSHOP_MOBILE = "9080742507"

# Bank details (for cashless claims)
BANK_ACCOUNT_NO = "259080742507"
BANK_NAME = "INDUSIND BANK"
BANK_IFSC = "INDB0000202"
BANK_BRANCH = "DHARMAPURI"

# Declaration
DECLARATION_PLACE = "Dharmapuri"

# Accident description templates
ACCIDENT_DESCRIPTIONS = {
    "stone_hit": (
        "While the vehicle was in motion, a flying stone projected from a preceding "
        "moving truck struck the front windshield, resulting in damage."
    ),
    "branch_moving": (
        "A tree branch fell onto the front windshield while the vehicle was in motion, "
        "causing damage."
    ),
    "branch_parked": (
        "A tree branch fell onto the front windshields while the vehicle was parked, "
        "causing damage."
    ),
}

# Occupants count by accident type
OCCUPANTS = {
    "stone_hit": "1",
    "branch_moving": "1",
    "branch_parked": "0",
}
