import datetime

from models import DumpActivities


def sort_activities(dump: DumpActivities):
    # createTime is str in the format of "2021-10-01 00:00", so we need to convert it to datetime object
    dump.activities.sort(key=lambda x: datetime.datetime.strptime(x.createTime, '%Y-%m-%d %H:%M'), reverse=True)


if __name__ == '__main__':
    with open('all_activities.json', 'r') as f:
        activities = DumpActivities.model_validate_json(f.read())
        sort_activities(activities)
        
        with open('all_activities_sorted.json', 'w') as f:
            f.write(activities.model_dump_json(indent=4))