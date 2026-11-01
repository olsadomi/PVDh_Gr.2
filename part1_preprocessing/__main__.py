"""PART I - runs all steps in order.   Usage:  python -m part1_preprocessing"""
import time

from part1_preprocessing import (s01_data_collection, s02_data_types, s03_data_quality, s04_cleaning,
                                 s05_missing_values, s06_integration, s07_feature_engineering, s08_discretization,
                                 s09_binarization, s10_transformation, s11_aggregation, s12_sampling,
                                 s13_dimensionality_reduction, s14_export)


def main():
    t0 = time.time()
    raw = s01_data_collection.read_raw_data()
    pop = s01_data_collection.read_population()

    df = s02_data_types.convert_types(raw)
    s03_data_quality.assess_quality(df, standard_municipalities=set(pop["municipality"]))
    df, _log = s04_cleaning.clean(df)
    df = s05_missing_values.handle(df)
    df, dim_nace = s06_integration.integrate(df, pop)
    df = s07_feature_engineering.create_features(df)
    df = s08_discretization.discretize(df)
    s09_binarization.binarize(df)
    df = s10_transformation.transform(df)
    tables = s11_aggregation.aggregate(df)
    strat = s12_sampling.sample(df)
    s13_dimensionality_reduction.select_features(df, strat)
    s13_dimensionality_reduction.pca_municipalities(tables["agg_municipality_sector"])
    s14_export.export(df, dim_nace)
    print(f"\nDONE: PART I finished in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()

