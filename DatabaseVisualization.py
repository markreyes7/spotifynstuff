from sklearn.linear_model import LinearRegression
from collections import Counter
import psycopg2
import os
import matplotlib.pyplot as plt


connection = psycopg2.connect(user=os.environ['USER'],
                              password=os.environ['PASSWORD'],
                              host=os.environ['HOST'],
                              port=os.environ['PORT'],
                              database=os.environ['DATABASE'])


def set_time_frame():
    time_framed = str(input("Enter a time of the day (Morning, Afternoon, Evening, Night, Late Night)"))
    if time_framed.lower() == "morning":
        time_start = "05:00:00"
        time_end = "12:00:00"
        time_of_day_title = "morning"
        return time_start, time_end, time_of_day_title
    elif time_framed.lower() == "afternoon":
        time_start = "12:00:00"
        time_end = "17:00:00"
        time_of_day_title = "afternoon"
        return time_start, time_end, time_of_day_title
    elif time_framed.lower() == "evening":
        time_start = "17:00:00"
        time_end = "21:00:00"
        time_of_day_title = "evening"
        return time_start, time_end, time_of_day_title
    elif time_framed.lower() == "night":
        time_start = "21:00:00"
        time_end = "24:00:00"
        time_of_day_title = "evening"
        return time_start, time_end, time_of_day_title
    elif time_framed.lower() == "late night":
        time_start = "01:00:00"
        time_end = "05:00:00"
        time_of_day_title = "late night"
        return time_start, time_end, time_of_day_title
    else:

        print("not valid")


def search_artist_of_timeframe(time_to):
    cursor = connection.cursor()
    postgres_insert_query = """SELECT artist_name FROM artist WHERE time_listened BETWEEN %s AND %s"""
    insert_str = (time_to[0], time_to[1])
    cursor.execute(postgres_insert_query, insert_str)
    records = cursor.fetchall()
    cnt = Counter()
    array = []

    for i in records:
        array.append(i[0])
        print(i)
    for index in array:
        cnt[index] += 1
    lists = sorted(cnt.items())
    return lists, time_to[2]


def show_graph_of_artists(lists):

    x, y = zip(*lists[0])
    fig, ax = plt.subplots()
    ax.margins(x=-0.285, y=2, tight=False)
    ax.bar(x, y)
    ax.set_title(lists[1])

    plt.show()



list_of_artists = search_artist_of_timeframe(set_time_frame())
show_graph_of_artists(list_of_artists)
