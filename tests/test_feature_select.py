import os
import random
import tempfile

import numpy as np
import pandas as pd
import pytest

from pycytominer.feature_select import feature_select

random.seed(123)

# Get temporary directory
tmpdir = tempfile.gettempdir()

# Setup testing files
output_test_file_csv = os.path.join(tmpdir, "test.csv")
output_test_file_parquet = os.path.join(tmpdir, "test.parquet")

data_df = pd.DataFrame({
    "x": [1, 3, 8, 5, 2, 2],
    "y": [1, 2, 8, 5, 2, 1],
    "z": [9, 3, 8, 9, 2, 9],
    "zz": [0, -3, 8, 9, 6, 9],
}).reset_index(drop=True)

data_na_df = pd.DataFrame({
    "x": [np.nan, 3, 8, 5, 2, 2],
    "xx": [np.nan, 3, 8, 5, 2, 2],
    "y": [1, 2, 8, np.nan, 2, np.nan],
    "yy": [1, 2, 8, 10, 2, 100],
    "z": [9, 3, 8, 9, 2, np.nan],
    "zz": [np.nan, np.nan, 8, np.nan, 6, 9],
}).reset_index(drop=True)

data_feature_infer_df = pd.DataFrame({
    "Metadata_x": [np.nan, np.nan, 8, np.nan, 2, np.nan],
    "Cytoplasm_xx": [np.nan, 3, 8, 5, 2, 2],
    "Nuclei_y": [1, 2, 8, np.nan, 2, np.nan],
    "Nuclei_yy": [1, 2, 8, 10, 2, 100],
    "Cytoplasm_z": [9, 3, 8, 9, 2, np.nan],
    "Cells_zz": [np.nan, np.nan, 8, np.nan, 6, 9],
}).reset_index(drop=True)

a_feature = [1] * 99 + [2]
b_feature = [1, 2] * 50
c_feature = [1, 2] * 25 + random.sample(range(1, 1000), 50)
d_feature = random.sample(range(1, 1000), 100)

data_unique_test_df = pd.DataFrame({
    "a": a_feature,
    "b": b_feature,
    "c": c_feature,
    "d": d_feature,
}).reset_index(drop=True)

data_outlier_df = pd.DataFrame({
    "Metadata_plate": ["a", "a", "a", "a", "b", "b", "b", "b"],
    "Metadata_treatment": [
        "drug",
        "drug",
        "control",
        "control",
        "drug",
        "drug",
        "control",
        "control",
    ],
    "Cells_x": [1, 2, -8, 2, 5, 5, 5, -1],
    "Cytoplasm_y": [3, -1, 7, 4, 5, -9, 6, 1],
    "Nuclei_z": [-1, 8, 2, 5, -6, 20, 2, -2],
    "Cells_zz": [14, -46, 1, 60, -30, -10000, 2, 2],
}).reset_index(drop=True)


def test_feature_select_noise_removal():
    """
    Testing noise_removal feature selection operation
    """
    # Set perturbation groups for the test dataframes
    data_df_groups = ["a", "a", "a", "b", "b", "b"]

    # Tests on data_df
    result1 = feature_select(
        profiles=data_df,
        features=data_df.columns.tolist(),
        samples="all",
        operation="noise_removal",
        noise_removal_perturb_groups=data_df_groups,
        noise_removal_stdev_cutoff=2.5,
    )
    result2 = feature_select(
        profiles=data_df,
        features=data_df.columns.tolist(),
        operation="noise_removal",
        noise_removal_perturb_groups=data_df_groups,
        noise_removal_stdev_cutoff=2,
    )
    result3 = feature_select(
        profiles=data_df,
        features=data_df.columns.tolist(),
        operation="noise_removal",
        noise_removal_perturb_groups=data_df_groups,
        noise_removal_stdev_cutoff=3.5,
    )

    expected_result1 = data_df[["x", "y"]]
    expected_result2 = data_df[[]]
    expected_result3 = data_df[["x", "y", "z", "zz"]]

    pd.testing.assert_frame_equal(result1, expected_result1)
    pd.testing.assert_frame_equal(result2, expected_result2)
    pd.testing.assert_frame_equal(result3, expected_result3)

    # Test on data_unique_test_df, which has 100 rows
    data_unique_test_df_groups = []

    # Create a 100 element list containing 10 replicates of 10 perturbations
    for elem in ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]:
        data_unique_test_df_groups.append([elem] * 10)

    # Unstack so it's just a single list
    data_unique_test_df_groups = [
        item for sublist in data_unique_test_df_groups for item in sublist
    ]

    result4 = feature_select(
        profiles=data_unique_test_df,
        features=data_unique_test_df.columns.tolist(),
        operation="noise_removal",
        noise_removal_perturb_groups=data_unique_test_df_groups,
        noise_removal_stdev_cutoff=3.5,
    )
    result5 = feature_select(
        profiles=data_unique_test_df,
        features=data_unique_test_df.columns.tolist(),
        operation="noise_removal",
        noise_removal_perturb_groups=data_unique_test_df_groups,
        noise_removal_stdev_cutoff=500,
    )

    expected_result4 = data_unique_test_df[["a", "b"]]
    expected_result5 = data_unique_test_df[["a", "b", "c", "d"]]

    pd.testing.assert_frame_equal(result4, expected_result4)
    pd.testing.assert_frame_equal(result5, expected_result5)

    # Test the same as above, except that data_unique_test_df_groups is now made into a metadata column
    data_unique_test_df2 = data_unique_test_df.copy()
    data_unique_test_df2["perturb_group"] = data_unique_test_df_groups
    result4b = feature_select(
        profiles=data_unique_test_df2,
        features=data_unique_test_df.columns.tolist(),
        operation="noise_removal",
        noise_removal_perturb_groups="perturb_group",
        noise_removal_stdev_cutoff=3.5,
    )
    result5b = feature_select(
        profiles=data_unique_test_df2,
        features=data_unique_test_df.columns.tolist(),
        operation="noise_removal",
        noise_removal_perturb_groups="perturb_group",
        noise_removal_stdev_cutoff=500,
    )

    expected_result4b = data_unique_test_df2[["a", "b", "perturb_group"]]
    expected_result5b = data_unique_test_df2[["a", "b", "c", "d", "perturb_group"]]

    pd.testing.assert_frame_equal(result4b, expected_result4b)
    pd.testing.assert_frame_equal(result5b, expected_result5b)

    # Test assertion errors for the user inputting the perturbation groupings
    bad_perturb_list = ["a", "a", "b", "b", "a", "a", "b"]

    with pytest.raises(
        ValueError
    ):  # When the inputted perturb list doesn't match the length of the data
        feature_select(
            data_df,
            features=data_df.columns.tolist(),
            operation="noise_removal",
            noise_removal_perturb_groups=bad_perturb_list,
            noise_removal_stdev_cutoff=3,
        )

    with pytest.raises(
        ValueError
    ):  # When the perturb list is inputted as string, but there is no such metadata column in the population_df
        feature_select(
            profiles=data_df,
            features=data_df.columns.tolist(),
            operation="noise_removal",
            noise_removal_perturb_groups="bad_string",
            noise_removal_stdev_cutoff=2.5,
        )

    with pytest.raises(
        TypeError
    ):  # When the perturbation groups are not either a list or metadata column string
        feature_select(
            profiles=data_df,
            features=data_df.columns.tolist(),
            operation="noise_removal",
            noise_removal_perturb_groups=12345,
            noise_removal_stdev_cutoff=2.5,
        )

    with pytest.raises(
        ValueError
    ):  # When the perturbation group doesn't match b/c samples argument used
        # Add metadata_sample column
        data_sample_id_df = data_df.assign(
            Metadata_sample=[f"sample_{x}" for x in range(0, data_df.shape[0])]
        )
        feature_select(
            profiles=data_sample_id_df,
            features=data_df.columns.tolist(),
            samples="Metadata_sample != 'sample_1'",
            operation="noise_removal",
            noise_removal_perturb_groups=data_df_groups,
            noise_removal_stdev_cutoff=2.5,
        )


def test_feature_select_get_na_columns():
    """
    Testing feature_select and get_na_columns pycytominer function
    """
    result = feature_select(
        data_na_df, features=data_na_df.columns.tolist(), operation="drop_na_columns"
    )
    expected_result = pd.DataFrame({"yy": [1, 2, 8, 10, 2, 100]})
    pd.testing.assert_frame_equal(result, expected_result)

    result = feature_select(
        data_na_df,
        features=data_na_df.columns.tolist(),
        operation="drop_na_columns",
        na_cutoff=1,
    )
    pd.testing.assert_frame_equal(result, data_na_df)

    result = feature_select(
        data_na_df,
        features=data_na_df.columns.tolist(),
        operation="drop_na_columns",
        na_cutoff=0.3,
    )
    expected_result = pd.DataFrame({
        "x": [np.nan, 3, 8, 5, 2, 2],
        "xx": [np.nan, 3, 8, 5, 2, 2],
        "yy": [1, 2, 8, 10, 2, 100],
        "z": [9, 3, 8, 9, 2, np.nan],
    })
    pd.testing.assert_frame_equal(result, expected_result)


def test_feature_select_get_na_columns_feature_infer():
    """
    Testing feature_select and get_na_columns pycytominer function
    """
    result = feature_select(
        data_feature_infer_df,
        features="infer",
        operation="drop_na_columns",
        na_cutoff=0.3,
    )
    expected_result = pd.DataFrame({
        "Metadata_x": [np.nan, np.nan, 8, np.nan, 2, np.nan],
        "Cytoplasm_xx": [np.nan, 3, 8, 5, 2, 2],
        "Nuclei_yy": [1, 2, 8, 10, 2, 100],
        "Cytoplasm_z": [9, 3, 8, 9, 2, np.nan],
    })
    pd.testing.assert_frame_equal(result, expected_result)

    result = feature_select(
        data_feature_infer_df,
        features=data_feature_infer_df.columns.tolist(),
        operation="drop_na_columns",
        na_cutoff=0.3,
    )
    expected_result = pd.DataFrame({
        "Cytoplasm_xx": [np.nan, 3, 8, 5, 2, 2],
        "Nuclei_yy": [1, 2, 8, 10, 2, 100],
        "Cytoplasm_z": [9, 3, 8, 9, 2, np.nan],
    })
    pd.testing.assert_frame_equal(result, expected_result)


def test_feature_select_variance_threshold():
    """
    Testing feature_select and variance_threshold pycytominer function
    """
    result = feature_select(
        data_unique_test_df,
        features=data_unique_test_df.columns.tolist(),
        operation="variance_threshold",
        unique_cut=0.01,
    )
    expected_result = pd.DataFrame({
        "b": b_feature,
        "c": c_feature,
        "d": d_feature,
    }).reset_index(drop=True)
    pd.testing.assert_frame_equal(result, expected_result)

    na_data_unique_test_df = data_unique_test_df.copy()
    na_data_unique_test_df.iloc[list(range(0, 50)), 1] = np.nan
    result = feature_select(
        na_data_unique_test_df,
        features=na_data_unique_test_df.columns.tolist(),
        operation=["drop_na_columns", "variance_threshold"],
    )
    expected_result = pd.DataFrame({"c": c_feature, "d": d_feature}).reset_index(
        drop=True
    )
    pd.testing.assert_frame_equal(result, expected_result)

    na_data_unique_test_df = data_unique_test_df.copy()
    na_data_unique_test_df.iloc[list(range(0, 50)), 1] = np.nan

    result = feature_select(
        na_data_unique_test_df,
        features=na_data_unique_test_df.columns.tolist(),
        operation=["variance_threshold", "drop_na_columns"],
    )
    expected_result = pd.DataFrame({"c": c_feature, "d": d_feature}).reset_index(
        drop=True
    )
    pd.testing.assert_frame_equal(result, expected_result)


def test_feature_select_correlation_threshold():
    """
    Testing feature_select and correlation_threshold pycytominer function
    """

    result = feature_select(
        data_df, features=data_df.columns.tolist(), operation="correlation_threshold"
    )
    expected_result = data_df.drop(["y"], axis="columns")
    pd.testing.assert_frame_equal(result, expected_result)

    data_cor_thresh_na_df = data_df.copy()
    data_cor_thresh_na_df.iloc[0, 2] = np.nan

    result = feature_select(
        data_cor_thresh_na_df,
        features=data_cor_thresh_na_df.columns.tolist(),
        operation=["drop_na_columns", "correlation_threshold"],
    )
    expected_result = data_df.drop(["z", "y"], axis="columns")
    pd.testing.assert_frame_equal(result, expected_result)


def test_feature_select_all():
    data_all_test_df = data_unique_test_df.assign(zz=a_feature)
    data_all_test_df.iloc[1, 4] = 2
    data_all_test_df.iloc[list(range(0, 50)), 1] = np.nan

    result = feature_select(
        profiles=data_all_test_df,
        features=data_all_test_df.columns.tolist(),
        operation=["drop_na_columns", "correlation_threshold"],
        corr_threshold=0.7,
    )
    expected_result = pd.DataFrame({
        "c": c_feature,
        "d": d_feature,
        "zz": a_feature,
    }).reset_index(drop=True)
    expected_result.iloc[1, 2] = 2
    pd.testing.assert_frame_equal(result, expected_result)

    # Get temporary directory
    tmpdir = tempfile.gettempdir()

    # Write file to output
    data_file = os.path.join(tmpdir, "test_feature_select.csv")
    data_all_test_df.to_csv(data_file, index=False, sep=",")
    out_file = os.path.join(tmpdir, "test_feature_select_out.csv")
    _ = feature_select(
        profiles=data_file,
        features=data_all_test_df.columns.tolist(),
        operation=["drop_na_columns", "correlation_threshold"],
        corr_threshold=0.7,
        output_file=out_file,
    )
    from_file_result = pd.read_csv(out_file)
    pd.testing.assert_frame_equal(from_file_result, expected_result)

    result = feature_select(
        profiles=data_all_test_df,
        features=data_all_test_df.columns.tolist(),
        operation=["drop_na_columns", "correlation_threshold", "variance_threshold"],
        corr_threshold=0.7,
    )
    expected_result = pd.DataFrame({"c": c_feature, "d": d_feature}).reset_index(
        drop=True
    )
    pd.testing.assert_frame_equal(result, expected_result)


def test_feature_select_compress():
    compress_file = os.path.join(tmpdir, "test_feature_select_compress.csv.gz")
    _ = feature_select(
        data_na_df,
        features=data_na_df.columns.tolist(),
        operation="drop_na_columns",
        output_file=compress_file,
        compression_options={"method": "gzip"},
    )
    expected_result = pd.DataFrame({"yy": [1, 2, 8, 10, 2, 100]})
    result = pd.read_csv(compress_file)

    pd.testing.assert_frame_equal(result, expected_result)


def test_feature_select_blocklist():
    """
    Testing feature_select and get_na_columns pycytominer function
    """

    data_blocklist_df = pd.DataFrame({
        "Nuclei_Correlation_Manders_AGP_DNA": [1, 3, 8, 5, 2, 2],
        "y": [1, 2, 8, 5, 2, 1],
        "Nuclei_Correlation_RWC_ER_RNA": [9, 3, 8, 9, 2, 9],
        "zz": [0, -3, 8, 9, 6, 9],
    }).reset_index(drop=True)

    result = feature_select(data_blocklist_df, features="infer", operation="blocklist")
    expected_result = pd.DataFrame({"y": [1, 2, 8, 5, 2, 1], "zz": [0, -3, 8, 9, 6, 9]})
    pd.testing.assert_frame_equal(result, expected_result)

    result = feature_select(
        data_blocklist_df,
        features=data_blocklist_df.columns.tolist(),
        operation="blocklist",
    )
    expected_result = pd.DataFrame({"y": [1, 2, 8, 5, 2, 1], "zz": [0, -3, 8, 9, 6, 9]})
    pd.testing.assert_frame_equal(result, expected_result)


def test_feature_select_drop_outlier():
    """
    Testing feature_select and get_na_columns pycytominer function
    """
    result = feature_select(
        data_outlier_df, features="infer", operation="drop_outliers"
    )
    expected_result = data_outlier_df.drop(["Cells_zz"], axis="columns")
    pd.testing.assert_frame_equal(result, expected_result)

    result = feature_select(
        data_outlier_df, features="infer", operation="drop_outliers", outlier_cutoff=30
    )
    expected_result = data_outlier_df.drop(["Cells_zz"], axis="columns")
    pd.testing.assert_frame_equal(result, expected_result)

    result = feature_select(
        data_outlier_df,
        features=["Cells_x", "Cytoplasm_y"],
        operation="drop_outliers",
        outlier_cutoff=15,
    )
    pd.testing.assert_frame_equal(result, data_outlier_df)


def test_output_type():
    """
    Testing feature_select pycytominer function
    """
    # dictionary with the output name associated with the file type
    output_dict = {"csv": output_test_file_csv, "parquet": output_test_file_parquet}

    # test both output types available with output function
    for _type, outname in output_dict.items():
        # Test output
        feature_select(
            data_df,
            features=data_df.columns.tolist(),
            operation="blocklist",
            output_file=outname,
            output_type=_type,
        )

    # read files in with pandas
    csv_df = pd.read_csv(output_test_file_csv)
    parquet_df = pd.read_parquet(output_test_file_parquet)

    # check to make sure the files were read in corrrectly as a pd.Dataframe
    assert isinstance(csv_df, pd.DataFrame)
    assert isinstance(parquet_df, pd.DataFrame)

    # check to make sure both dataframes are the same regardless of the output_type
    pd.testing.assert_frame_equal(csv_df, parquet_df)


def test_samples_parameter_in_feature_select():
    # Create a list of 100 elements with 10 replicates of 10 perturbations
    data_unique_test_df_groups = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
    data_unique_test_df_groups = [
        elem for elem in data_unique_test_df_groups for _ in range(10)
    ]

    # Make a copy of the test DataFrame
    data_unique_test_df3 = data_unique_test_df.copy()
    data_unique_test_df3_features = data_unique_test_df3.columns.tolist()

    # Add a metadata column for creating a sample query
    data_unique_test_df3["Metadata_sample"] = ["A", "B"] * 50

    # Define the sample query
    sample_query = "Metadata_sample == 'A'"

    # Add a perturb group metadata column for noise removal operation
    data_unique_test_df3["perturb_group"] = data_unique_test_df_groups

    # establishing all operations that use "samples" parameter
    # note that blocklist does not use samples parameter
    all_operations = [
        "noise_removal",
        "drop_na_columns",
        "variance_threshold",
        "correlation_threshold",
        "drop_outliers",
    ]
    for operation_idx, operation in enumerate(all_operations):
        # testing single operation
        results6a = feature_select(
            profiles=data_unique_test_df3,
            features=data_unique_test_df3_features,
            operation=operation,
            samples=sample_query,
            noise_removal_perturb_groups="perturb_group",
            noise_removal_stdev_cutoff=500,
        )

        # checking if no rows were not removed
        assert results6a.shape[0] == data_unique_test_df3.shape[0], (
            f"Row counts do not match: {results6a[0]} != {data_unique_test_df3.shape[0]} in operation: {operation}"
        )

        # testing multiple operations (continually appends operations)
        concat_operations = all_operations[: operation_idx + 1]
        results6b = feature_select(
            profiles=data_unique_test_df3,
            features=data_unique_test_df3_features,
            operation=concat_operations,
            samples=sample_query,
            noise_removal_perturb_groups="perturb_group",
            noise_removal_stdev_cutoff=500,
        )

        # checking if no rows were not removed
        assert results6b.shape[0] == data_unique_test_df3.shape[0], (
            f"Row counts do not match: {results6a[0]} != {data_unique_test_df3.shape[0]} in operation: {concat_operations}"
        )
