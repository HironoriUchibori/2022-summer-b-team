json_obj = {'prefectures': []}
with open("trip_maker/static/text/prefectures.txt") as file:
    json_obj['prefectures'].append(file.readline)

