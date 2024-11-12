from pydantic import BaseModel
from typing import List, Optional

class Video(BaseModel):
    cdn: Optional[str] = ""
    path: Optional[str] = ""
    token: Optional[str] = ""
    imagePath: Optional[str] = ""
    imageCdn: Optional[str] = ""
    duration: int = 0
    width: int = 0
    height: int = 0
    videoUserId: Optional[str] = ""


class BgdImage(BaseModel):
    bgdImageId: int = 0
    type: int = 0
    styleId: int = 0
    image: Optional[str] = ""
    width: int = 0
    height: int = 0


class PinInfo(BaseModel):
    pin: bool = False


class Activity(BaseModel):
    id: int
    activitiesText: str
    activitiesState: str
    activitiesImages: Optional[List[str]] = None
    createTime: str
    thumbsUpCount: int
    commentCount: int
    activitiesType: str
    video: Video
    activitiesImageInfo: List = []
    bgdImage: BgdImage
    commentUserCount: int
    pinInfo: PinInfo


class ActivitiesResult(BaseModel):
    count: int
    page: int
    totalPage: int
    totalRow: int
    firstPage: bool
    lastPage: bool
    list: List[Activity]


class ActivitiesModel(BaseModel):
    result: ActivitiesResult
    

class DumpActivities(BaseModel):
    activities: List[Activity]
