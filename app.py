import io
import seaborn as sns
import matplotlib.pyplot as plt
from flask import Flask, render_template, request
import preprocessor
import helper
import matplotlib
import json
matplotlib.use('Agg')

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('upload.html')


@app.route('/preprocess', methods=['POST'])
def preprocess():
    file = request.files['file']
    bytes_data = file.read()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)
    print(df)

    user_list = df['user'].unique().tolist()
    user_list_json = json.dumps(user_list)

    return render_template('user.html', user_list=user_list_json)


@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['file']
    bytes_data = file.read()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)
    print(df)
    # fetch unique users
    user_list = df['user'].unique().tolist()
    print("unique user listt", user_list)

    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    # user_list.remove('+91 93285 86261')
    # user_list.remove('+91 99874 03026')
    user_list.sort()
    user_list.insert(0, "Overall")
    print("unique user listt after", user_list)

    selected_user = request.form.get('selectedUser')
    print(selected_user)
    # Stats Area
    num_messages, words, num_media_messages, num_links = helper.fetch_stats(
        selected_user, df)

    print(num_messages, words, num_media_messages, num_links)

    # Monthly Timeline
    timeline = helper.monthly_timeline(selected_user, df)
    plt.figure()
    plt.plot(timeline['time'], timeline['message'], color='green')
    plt.xticks(rotation='vertical')
    plt.savefig('./static/timeline.png')
    plt.close()

    # Daily Timeline
    daily_timeline = helper.daily_timeline(selected_user, df)
    plt.figure()
    plt.plot(daily_timeline['only_date'],
             daily_timeline['message'], color='black')
    plt.xticks(rotation='vertical')
    plt.savefig('./static/daily_timeline.png')
    plt.close()
    # Daily Timeline
    daily_timeline = helper.daily_timeline(selected_user, df)
    fig, ax = plt.subplots()
    ax.plot(daily_timeline['only_date'],
            daily_timeline['message'], color='black')
    plt.xticks(rotation='vertical')
    plt.savefig('./static/daily_timeline.png')
    plt.close()

    # Activity Map
    busy_day = helper.week_activity_map(selected_user, df)
    print("BUSYYY", busy_day, "fdrfskrhfskr")
    plt.figure()
    plt.bar(busy_day.index, busy_day.values, color='purple')
    plt.xticks(rotation='vertical')
    plt.savefig('./static/busy_day.png')
    plt.close()

    most_common_word = helper.most_common_words(selected_user, df)
    print(most_common_word)
    # Weekly Activity Map
    # print(selected_user)
    user_heatmap = helper.activity_heatmap(selected_user, df)
    fig, ax = plt.subplots()
    # print(user_heatmap)
    ax = sns.heatmap(user_heatmap)
    plt.savefig('./static/activity_heatmap.png')
    plt.close()

    # Most Busy Users
    if selected_user == 'Overall':
        x, new_df = helper.most_busy_users(df)
        print("dssds", x, "desfsfs")
        fig, ax = plt.subplots()
        ax.bar(x.index, x.values, color='red')
        plt.xticks(rotation='vertical')
        plt.savefig('most_busy_users.png')
        plt.close()

    return render_template('results.html',
                           num_messages=num_messages,
                           words=words, x=x if selected_user == 'Overall' else "dss",

                           num_media_messages=num_media_messages,
                           num_links=num_links, most=most_common_word)


if __name__ == '__main__':
    app.run()
