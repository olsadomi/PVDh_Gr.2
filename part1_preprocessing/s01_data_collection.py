"""Step 1 - Data collection.

Source:       ARBK (Kosovo Business Registration Agency) Open Data, snapshot 05.10.2026 (Excel, sheet 'Bizneset').
Integration:  ASK (Kosovo Agency of Statistics), "Population of Kosovo 2024", municipal estimates (31.12.2024), Table 3.

All columns are read as TEXT (dtype=str) so pandas does not guess types (leading zeros in IDs and date
formats are preserved). Types are defined explicitly in step 2.
"""

