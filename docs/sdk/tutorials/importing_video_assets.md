<!-- FILE AUTO GENERATED BY docs/utils.py DO NOT EDIT DIRECTLY -->
<a href="https://colab.research.google.com/github/kili-technology/kili-python-sdk/blob/master/recipes/importing_video_assets.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# How to import video assets to a Kili project

In this tutorial, we will learn how to import video assets to Kili.

Here are the steps that we will follow:

1. Setting up a simple Kili project to work with
2. Importing video assets to Kili
  1. Uploading a video asset using a path to a local file
  2. Uploading a video asset using an URL
  3. Uploading a video asset to label each frame separately
  4. Uploading a list of local images as one video asset
  5. Uploading a list of image URLs as one video asset
  6. Uploading a video asset with a custom sampling rate
3. Cleanup

## Setting up a simple Kili project to work with

### Installing and instantiating Kili

First, let's install and import the required modules.


```python
!pip install  kili
```


```python
from kili.client import Kili
import getpass
import os
```

Now, let's set up variables needed to create an instance of the Kili object.

We will need your API key and Kili's API endpoint.

If you are unsure how to look up your API key, refer to [https://docs.kili-technology.com/docs/creating-an-api-key](https://docs.kili-technology.com/docs/creating-an-api-key).


```python
if "KILI_API_KEY" not in os.environ:
    KILI_API_KEY = getpass.getpass("Please enter your API key: ")
else:
    KILI_API_KEY = os.environ["KILI_API_KEY"]
```

With variables set up, we can now create an instance of the Kili object.


```python
kili = Kili(
    api_key=KILI_API_KEY,  # no need to pass the API_KEY if it is already in your environment variables
    # api_endpoint="https://cloud.kili-technology.com/api/label/v2/graphql",
    # the line above can be uncommented and changed if you are working with an on-premise version of Kili
)
```

### Creating a basic Kili project

To create a Kili project, you must first set up its interface.

We will create a video project with just one simple classification job and two categories: `OBJECT_A` and `OBJECT_B`.

To learn more about Kili project interfaces, refer to [https://docs.kili-technology.com/docs/customizing-project-interface](https://docs.kili-technology.com/docs/customizing-project-interface).


```python
interface = {
    "jobs": {
        "JOB_0": {
            "content": {
                "categories": {
                    "OBJECT_A": {"children": [], "name": "Object A", "id": "category3"},
                    "OBJECT_B": {"children": [], "name": "Object B", "id": "category4"},
                },
                "input": "radio",
            },
            "instruction": "Categories",
            "isChild": False,
            "mlTask": "CLASSIFICATION",
            "models": {},
            "isVisible": True,
            "required": 1,
            "isNew": False,
        }
    }
}

result = kili.create_project(
    title="Test Project",
    description="Project Description",
    input_type="VIDEO",
    json_interface=interface,
)
```

For further processing, we will need to find out what our project ID is.

We can easily retrieve it from the project creation response message:


```python
project_id = result["id"]
print("Project ID: ", project_id)
```

    Project ID:  cld90h71d0ha50jptd28xfjg1


## Importing video assets to Kili

Now, let's add some video assets to be labeled.
You can videos using URLs or use your local assets.

We will use a free off-the-shelf asset from the Internet.

### Uploading a video asset using a path to a local file

To show an example of how to upload a local video, we must first download it:


```python
import urllib.request

urllib.request.urlretrieve(
    "https://storage.googleapis.com/label-public-staging/asset-test-sample/video/short_video.mp4",
    "test.mp4",
)
```

Now, we can easily upload the video to our project:


```python
assets = kili.append_many_to_dataset(
    project_id=project_id, content_array=["./test.mp4"], external_id_array=["video_1_from_local"]
)
```

### Uploading a video asset using an URL

You can of course upload videos using URLs as well. To do so, simply replace `'./test.mp4'` with the URL of the video that you want to upload.


```python
url = "https://storage.googleapis.com/label-public-staging/asset-test-sample/video/short_video.mp4"

assets = kili.append_many_to_dataset(
    project_id=project_id, content_array=[url], external_id_array=["video_2_from_url"]
)
```

### Uploading a video asset to label each frame separately

To upload your video and be able to label frames separately, as individual images, refer to this code:


```python
url = "https://storage.googleapis.com/label-public-staging/asset-test-sample/video/short_video.mp4"

assets = kili.append_many_to_dataset(
    project_id=project_id,
    content_array=[url],
    external_id_array=["video_2_from_url_split_frames"],
    json_metadata_array=[{"processingParameters": {"shouldUseNativeVideo": False}}],
)
```

### Uploading a list of local images as one video asset

We can create a video, by using local images as frames. Let's first download some images from the Internet:


```python
urllib.request.urlretrieve(
    "https://storage.googleapis.com/label-public-staging/Frame/vid2_frame/video2-img000001.jpg",
    "image_1.jpg",
)
urllib.request.urlretrieve(
    "https://storage.googleapis.com/label-public-staging/Frame/vid2_frame/video2-img000002.jpg",
    "image_2.jpg",
)
urllib.request.urlretrieve(
    "https://storage.googleapis.com/label-public-staging/Frame/vid2_frame/video2-img000003.jpg",
    "image_3.jpg",
)
```

Now, let's put them together as one video:


```python
assets = kili.append_many_to_dataset(
    project_id=project_id,
    json_content_array=[["./image_1.jpg", "./image_2.jpg", "./image_3.jpg"]],
    external_id_array=["video_3_from_local_images"],
    json_metadata_array=[{"processingParameters": {"shouldUseNativeVideo": False}}],
)
```

### Uploading a list of image URLs as one video asset

You can of course upload videos using URLs as well. To do so, simply replace `'./test.mp4'` with a set of URLs of images that you want to upload as a video.


```python
url1 = "https://storage.googleapis.com/label-public-staging/Frame/vid2_frame/video2-img000001.jpg"
url2 = "https://storage.googleapis.com/label-public-staging/Frame/vid2_frame/video2-img000002.jpg"
url3 = "https://storage.googleapis.com/label-public-staging/Frame/vid2_frame/video2-img000003.jpg"

assets = kili.append_many_to_dataset(
    project_id=project_id,
    json_content_array=[[url1, url2, url3]],
    external_id_array=["video_4_from_image_urls"],
    json_metadata_array=[{"processingParameters": {"shouldUseNativeVideo": False}}],
)
```

### Uploading a video asset with a custom sampling rate

To upload a video with a custom sampling rate (let's say, 10 frames per second), use this code:


```python
assets = kili.append_many_to_dataset(
    project_id=project_id,
    content_array=["./test.mp4"],
    external_id_array=["video_5_custom"],
    json_metadata_array=[{"processingParameters": {"framesPlayedPerSecond": 10}}],
)
```

## Cleanup

To clean up, we need to simply remove the project that we created.


```python
kili.delete_project(project_id);
```

## Summary

Done. We've successfully set up a video project, defined its interface, and uploaded a bunch of assets to it, using various Kili's upload methods. Well done!