class Status:
    """Values of `Statusi i biznesit` (the embedded date in 'Pasiv-09/06/2022' is split off in cleaning)."""
    REGISTERED = "Regjistruar"
    PASSIVE = "Pasiv"
    CLOSED = "Shuar"
    LIQUIDATION = "Ne proces te likuidimit"
    ALL = [REGISTERED, PASSIVE, CLOSED, LIQUIDATION]


class LegalType:
    """Values of `Lloji i biznesit`."""
    SOLE = "Biznes individual"
    LLC = "Shoqëri me përgjegjësi të kufizuara"
    JSC = "Shoqëri aksionare"
    GENERAL_PARTNERSHIP = "Ortakëri e përgjithshme"
    LIMITED_PARTNERSHIP = "Ortakëri e kufizuar"
    PUBLIC = "Ndërmarrje publike"
    SOCIALLY_OWNED = "Ndërmarrje shoqërore"
    AKM = "Ndërmarrje tjera nën juridiksion të AKM"
    COOPERATIVE = "Kooperativa Bujqësore"
    FOREIGN_BRANCH = "Dega e Shoqërisë së Huaj"
    REPRESENTATIVE_OFFICE = "Zyra e Përfaqësisë në Kosovë"
    ALL = [SOLE, LLC, JSC, GENERAL_PARTNERSHIP, LIMITED_PARTNERSHIP, PUBLIC, SOCIALLY_OWNED, AKM,
           COOPERATIVE, FOREIGN_BRANCH, REPRESENTATIVE_OFFICE]


class FormGroup:
    """Derived column `legal_form_group`: the 11 legal types grouped into 4 (7 types have < 1% each)."""
    INDIVIDUAL = "Individual"
    COMPANY = "Shoqëri tregtare"
    PARTNERSHIP = "Ortakëri"
    OTHER = "Tjetër"
    ORDER = [INDIVIDUAL, PARTNERSHIP, COMPANY, OTHER]


UNKNOWN = "E panjohur"   # filled into categories where the value is missing

GENDER_STRUCTURE = {"none": "Pa pronar fizik", "male": "Vetëm meshkuj", "female": "Vetëm femra", "mixed": "E përzier"}
AGE_GROUPS = ["<1 vit", "1–3 vjet", "3–5 vjet", "5–10 vjet", "10–20 vjet", "20+ vjet"]
REGISTRATION_PERIODS = ["2000–2007 (para pavarësisë)", "2008–2019", "2020–2021 (pandemia)", "2022–2026"]

# `Months` is published with English month names in the file
MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], start=1)}
