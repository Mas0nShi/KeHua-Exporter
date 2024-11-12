import os
import time
import requests
import tqdm
from pathlib import Path

from models import ActivitiesModel, DumpActivities
from timeline_sort import sort_activities

# log prefix color

'''
+ means success
- means info
! means warning
x means error
so, the log prefix color is:
+ green
- cyan
! yellow
x red
'''

class LogPrefix:
    SUCCESS = '[\033[92m+\033[0m]'
    INFO = '[\033[96m-\033[0m]'
    WARNING = '[\033[93m!\033[0m]'
    ERROR = '[\033[91mx\033[0m]'
    
class Log:
    @staticmethod
    def success(*args, **kwargs):
        print(LogPrefix.SUCCESS, *args, **kwargs)
    
    @staticmethod
    def info(*args, **kwargs):
        print(LogPrefix.INFO, *args, **kwargs)
    
    @staticmethod
    def warning(*args, **kwargs):
        print(LogPrefix.WARNING, *args, **kwargs)
        
    @staticmethod
    def error(*args, **kwargs):
        print(LogPrefix.ERROR, *args, **kwargs)
        
    


class KehuaClient:
    apiHost: str = "https://www.tideswing.fun"
    imageHost = "https://cdn.tideswing.fun"
    apiReq: requests.Session
    imageReq: requests.Session
    # videoReq: requests.Session
    
    def __init__(self, token: str):
        self.apiReq = requests.Session()
        self.apiReq.headers['User-Agent'] = "ke hua/1.12.5 (iPhone; iOS 18.0.1; AppStore)"
        self.apiReq.headers['authorization'] = f"Bearer {token}" if not token.startswith("Bearer ") else token
        
        assert self.apiReq.headers['authorization'].startswith("Bearer "), 'Token must start with "Bearer "'
        
        self.imageReq = requests.Session()
        self.imageReq.headers['User-Agent'] = "ke hua/1.12.5 (iPhone; iOS 18.0.1; AppStore)"
        # todo: implement video download
        # self.videoReq = requests.Session()
        # self.videoReq.headers['User-Agent'] = "AppleCoreMedia/1.0.0.22A3370 (iPhone; U; CPU OS 18_0_1 like Mac OS X; en_us)"
    
    @staticmethod
    def decorate_timestamp_header(func):
        def wrapper(*args, **kwargs):
            args[0].apiReq.headers['request-timestamp'] = str(int(time.time() * 1000))
            return func(*args, **kwargs)
        return wrapper
    

    @decorate_timestamp_header
    def get_activities(self, page: int, row: int = 20) -> ActivitiesModel:
        response = self.apiReq.get(f"{self.apiHost}/v1/api/activities", params={
            'page': str(page),
            'row': str(row)
        })
        
        response.raise_for_status()
        
        return ActivitiesModel(**response.json())


    def download_image(self, path: str) -> bytes:
        response = self.imageReq.get(f"{self.imageHost}/{path}")
        response.raise_for_status()
        return response.content
    
    
if __name__ == "__main__":
    # load token from env
    token = os.getenv('KEHUA_TOKEN')
    client = KehuaClient(token)
    activities = client.get_activities(1, 20)
    Log.success('Successfully retrieved activities')
    total_activities = activities.result.totalRow
    total_pages = activities.result.totalPage
    Log.info(f'Total activities: {total_activities}')
    Log.info(f'Total pages: {total_pages}')
    # -
    Log.info('Start retrieving all activities, this may take a while...')
    all_activities = []
    for page in tqdm.tqdm(range(1, total_pages + 1), colour='#59B97D'):
        row = 20
        if page == total_pages:
            row = total_activities % 20
        activities = client.get_activities(page, row)
        all_activities.extend(activities.result.list)
    
    # Now you have all activities in `all_activities` list
    Log.success(f'Successfully retrieved all activities: {len(all_activities)} / {total_activities}')
    
    dumpModel = DumpActivities(activities=all_activities)
    # Sort activities
    Log.info('Sorting activities...')
    sort_activities(dumpModel)
    Log.success('Successfully sorted activities')
    out_path = Path('output')
    if not out_path.exists():
        out_path.mkdir(parents=True)
    with open(out_path / 'all_activities.json', 'w') as f:
        f.write(dumpModel.model_dump_json(indent=4))
    Log.success('Successfully saved all activities to all_activities.json')
    
    Log.info('Start downloading assets(images/videos)...')
    
    
    for activity in tqdm.tqdm(dumpModel.activities, colour='#59B97D'):
        if activity.video.path:
            Log.warning(f'Video download is not implemented yet, skipping video download for activity {activity.id}')
            continue
        
        if activity.activitiesImages:
            for image in activity.activitiesImages:
                path = Path(f'output/assets/{image}')
                if path.exists():
                    Log.warning(f'File {path} already exists, skipping download')
                    continue
                if not path.parent.exists():
                    path.parent.mkdir(parents=True)
                image_data = client.download_image(image)
                with open(path, 'wb') as f:
                    f.write(image_data)
    
    Log.success('Successfully downloaded images')
    
    Log.success('All done!')