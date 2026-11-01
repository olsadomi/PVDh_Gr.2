"""
PART I - Data preprocessing (15%)

Input:   data/raw/Bizneset_2026-10-05.xlsx  (+ ASK population 2024)
Output:  data/processed/arbk_clean.csv      -> input of Part II

The modules follow the order of the course tasks:
    s01_data_collection          - read the raw data, CSV copy
    s02_data_types               - conceptual + technical data types, conversions
    s03_data_quality             - completeness, uniqueness, validity, consistency, timeliness
    s04_cleaning                 - duplicates, standardisation, splitting composite columns
    s05_missing_values           - missingness mechanism (MCAR/MAR) and handling strategy
    s06_integration              - join with ASK population and regions; NACE dimension
    s07_feature_engineering      - new features
    s08_discretization           - three discretization methods compared
    s09_binarization             - one-hot, top-k, binary flags
    s10_transformation           - log(1+x), min-max, z-score
    s11_aggregation              - tables by municipality, year, sector
    s12_sampling                 - simple random vs stratified sample
    s13_dimensionality_reduction - feature subset selection + PCA
    s14_export                   - save the clean dataset and data dictionary

Run:  python -m part1_preprocessing
Boundary with Part II: this part fixes the STRUCTURE. Extreme values are NOT touched; Part II handles them.
"""
