# pylint: disable=missing-docstring
import glob
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import pytest

from kili.services import export_labels
from kili.services.export.exceptions import NoCompatibleJobError, NotCompatibleOptions
from tests.services.export.fakes.fake_kili import FakeKili


def get_file_tree(folder: str):
    """
    Returns the file tree in the shape of a dictionary.
    Example:
    {
        "images": {"remote_assets.csv": {}},
        "JOB_0": {
            "labels": {
                "car_1.txt": {},
            },
            "data.yaml": {},
        },
        "JOB_1": {"labels": {}, "data.yaml": {}},
        "JOB_2": {"labels": {}, "data.yaml": {}},
        "JOB_3": {"labels": {}, "data.yaml": {}},
        "README.kili.txt": {},
    }
    """
    dct = {}
    filepaths = [
        f.replace(os.path.join(folder, ""), "")
        for f in glob.iglob(folder + "**/**", recursive=True)
    ]
    for f_p in filepaths:
        p = dct
        for x in f_p.split("/"):
            if len(x):
                p = p.setdefault(x, {})
    return dct


@pytest.mark.parametrize(
    "name,test_case",
    [
        (
            "Export to YOLO v5 format with splitted files",
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "yolo_v5",
                    "split_option": "split",
                },
                "file_tree_expected": {
                    "images": {"remote_assets.csv": {}},
                    "JOB_0": {
                        "labels": {
                            "car_1.txt": {},
                        },
                        "data.yaml": {},
                    },
                    "JOB_1": {"labels": {}, "data.yaml": {}},
                    "JOB_2": {"labels": {}, "data.yaml": {}},
                    "JOB_3": {"labels": {}, "data.yaml": {}},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "Export to YOLO v5 format with merged file",
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "yolo_v5",
                    "split_option": "merged",
                },
                "file_tree_expected": {
                    "images": {"remote_assets.csv": {}},
                    "labels": {"car_1.txt": {}},
                    "data.yaml": {},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "Export to YOLO v4 format with merged file",
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "yolo_v4",
                    "split_option": "merged",
                },
                "file_tree_expected": {
                    "images": {"remote_assets.csv": {}},
                    "labels": {"car_1.txt": {}},
                    "classes.txt": {},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "Export to Kili raw format",
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "raw",
                },
                "file_tree_expected": {
                    "labels": {"car_1.json": {}},
                    "README.kili.txt": {},
                },
            },
        ),
        (
            "Export to COCO format",
            {
                "export_kwargs": {
                    "project_id": "semantic_segmentation",
                    "label_format": "coco",
                },
                "file_tree_expected": {
                    "data": {
                        "car_1.jpg": {},
                        "car_2.jpg": {},
                    },
                    "JOB_0": {
                        "labels.json": {},
                    },
                    "README.kili.txt": {},
                },
            },
        ),
    ],
)
def test_export_service(name, test_case):
    with TemporaryDirectory() as export_folder:
        with TemporaryDirectory() as extract_folder:
            path_zipfile = Path(export_folder) / "export.zip"
            path_zipfile.parent.mkdir(parents=True, exist_ok=True)

            fake_kili = FakeKili()
            default_kwargs = {
                "asset_ids": [],
                "split_option": "merged",
                "export_type": "latest",
                "single_file": False,
                "output_file": str(path_zipfile),
                "disable_tqdm": True,
                "log_level": "INFO",
            }

            default_kwargs.update(test_case["export_kwargs"])

            export_labels(
                fake_kili,
                **default_kwargs,
            )

            Path(extract_folder).mkdir(parents=True, exist_ok=True)
            with ZipFile(path_zipfile, "r") as z_f:
                z_f.extractall(extract_folder)

            file_tree_result = get_file_tree(extract_folder)

            file_tree_expected = test_case["file_tree_expected"]

            assert file_tree_result == file_tree_expected


@pytest.mark.parametrize(
    "name,test_case,error",
    [
        (
            "Export text classification to Yolo format to throw error",
            {
                "export_kwargs": {
                    "project_id": "text_classification",
                    "label_format": "yolo_v4",
                    "split_option": "merged",
                },
            },
            NoCompatibleJobError,
        ),
        (
            "Export Yolo format with single file to throw error",
            {
                "export_kwargs": {
                    "project_id": "object_detection",
                    "label_format": "yolo_v4",
                    "split_option": "merged",
                    "single_file": True,
                },
            },
            NotCompatibleOptions,
        ),
    ],
)
def test_export_service_errors(name, test_case, error):
    with TemporaryDirectory() as export_folder:
        path_zipfile = Path(export_folder) / "export.zip"
        path_zipfile.parent.mkdir(parents=True, exist_ok=True)

        fake_kili = FakeKili()
        default_kwargs = {
            "asset_ids": [],
            "split_option": "merged",
            "export_type": "latest",
            "single_file": False,
            "output_file": str(path_zipfile),
            "disable_tqdm": True,
            "log_level": "INFO",
        }

        default_kwargs.update(test_case["export_kwargs"])
        with pytest.raises(error):
            export_labels(
                fake_kili,
                **default_kwargs,
            )