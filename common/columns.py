"""Column names exactly as they appear in the ARBK source file (kept unchanged).

All code refers to the source columns through these constants. Columns created by the pipeline
(e.g. `status`, `age_years`, `legal_form_group`) have English names.
"""


class C:
    ID = "Nr. i biznesit"
    NAME = "Emri i biznesit"
    TRADE_NAME = "Emri tregtare"
    LEGAL_TYPE = "Lloji i biznesit"
    NACE = "Aktiv. Nace2 - Përshkrimi"
    SECTOR = "Sektori"
    EMPLOYEES = "Nr. punëtorëve"
    SIZE = "Madhësia"
    OWNERS_M = "Total M"
    OWNERS_F = "Total F"
    MUNICIPALITY = "Qyteti"
    STATUS = "Statusi i biznesit"
    YEAR = "Years"
    MONTH = "Months"
    CLOSURE_DATE = "Data Shuarjes"

    SOURCE = [ID, NAME, TRADE_NAME, LEGAL_TYPE, NACE, SECTOR, EMPLOYEES, SIZE, OWNERS_M, OWNERS_F,
              MUNICIPALITY, STATUS, YEAR, MONTH, CLOSURE_DATE]
