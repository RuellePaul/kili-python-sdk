# pylint: disable=missing-docstring

import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from kili.services.export.format.yolo.common import (
    _convert_from_kili_to_yolo_format,
    _process_asset,
    _write_class_file,
)
from tests.services.export.fakes.fake_content_repository import FakeContentRepository
from tests.services.export.fakes.fake_data import (
    asset_image_1,
    asset_video,
    category_ids,
)


class YoloTestCase(TestCase):
    def test_process_asset_for_job_image_not_served_by_kili(self):
        with TemporaryDirectory() as images_folder:
            with TemporaryDirectory() as labels_folder:
                fake_content_repository = FakeContentRepository("https://contentrep", {}, False)
                asset_remote_content, video_filenames = _process_asset(
                    asset_image_1,
                    images_folder,
                    labels_folder,
                    category_ids,
                    fake_content_repository,
                )

                nb_files = len(
                    [
                        name
                        for name in os.listdir(labels_folder)
                        if os.path.isfile(os.path.join(labels_folder, name))
                    ]
                )

                assert os.path.isfile(os.path.join(labels_folder, "car_1.txt"))
                assert nb_files == 1
                assert asset_remote_content == [
                    [
                        "car_1",
                        "https://storage.googleapis.com/label-public-staging/car/car_1.jpg",
                        "car_1.txt",
                    ]
                ]
                assert len(video_filenames) == 0

    def test_process_asset_for_job_frame_not_served_by_kili(self):
        with TemporaryDirectory() as images_folder:
            with TemporaryDirectory() as labels_folder:
                fake_content_repository = FakeContentRepository("https://contentrep", {}, False)
                asset_remote_content, video_filenames = _process_asset(
                    asset_video, images_folder, labels_folder, category_ids, fake_content_repository
                )

                nb_files = len(
                    [
                        name
                        for name in os.listdir(labels_folder)
                        if os.path.isfile(os.path.join(labels_folder, name))
                    ]
                )

                assert nb_files == 4

                for i in range(nb_files):
                    assert os.path.isfile(os.path.join(labels_folder, f"video_1_{i+1}.txt"))

                expected_content = [
                    [
                        "video_1",
                        "https://storage.googleapis.com/label-public-staging/video1/video1.mp4",
                        f"video_1_{i+1}.txt",
                    ]
                    for i in range(4)
                ]
                assert asset_remote_content == expected_content

                expected_video_filenames = [f"video_1_{i+1}" for i in range(4)]
                assert len(video_filenames) == 4
                assert video_filenames == expected_video_filenames

    def test_convert_from_kili_to_yolo_format(self):
        converted_annotations = _convert_from_kili_to_yolo_format(
            "JOB_0", asset_image_1["latestLabel"], category_ids
        )
        expected_annotations = [
            (0, 0.501415026274802, 0.5296278884310182, 0.6727472455849373, 0.5381320101586394)
        ]
        assert len(converted_annotations) == 1
        assert converted_annotations == expected_annotations

    def test_write_class_file_yolo_v4(self):
        with TemporaryDirectory() as directory:
            _write_class_file(directory, category_ids, "yolo_v4")
            assert os.path.isfile(os.path.join(directory, "classes.txt"))
            with open(os.path.join(directory, "classes.txt"), "rb") as created_file:
                with open("./tests/services/export/expected/classes.txt", "rb") as expected_file:
                    assert expected_file.read() == created_file.read()

    def test_write_class_file_yolo_v5(self):
        with TemporaryDirectory() as directory:
            _write_class_file(directory, category_ids, "yolo_v5")
            assert os.path.isfile(os.path.join(directory, "data.yaml"))
            with open(os.path.join(directory, "data.yaml"), "rb") as created_file:
                with open("./tests/services/export/expected/data_v5.yaml", "rb") as expected_file:
                    assert expected_file.read() == created_file.read()

    def test_write_class_file_yolo_v7(self):
        with TemporaryDirectory() as directory:
            _write_class_file(directory, category_ids, "yolo_v7")
            assert os.path.isfile(os.path.join(directory, "data.yaml"))
            with open(os.path.join(directory, "data.yaml"), "rb") as created_file:
                with open("./tests/services/export/expected/data_v7.yaml", "rb") as expected_file:
                    assert expected_file.read() == created_file.read()