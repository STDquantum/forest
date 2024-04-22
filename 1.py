import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from os import system as sys


def tree_type_analyse(data):
    tree_type = list(data['Tree Type'])
    tree_dic = {}
    for i in tree_type:
        tree_dic[i] = tree_type.count(i)
    tree_list = list(tree_dic.items())
    tree_list.sort(key=lambda x: x[1], reverse=True)
    tree_type_count = len(tree_list)
    tree_count = sum(tree_dic.values())
    sorted_tree = []
    sorted_count = []

    print('\nyou have planted {0} trees, There are {1} types of trees'.format(
        tree_count, tree_type_count))
    print("")
    print('Tree Type\t      counts')
    print('===============================')
    for i in range(0, len(tree_list)):
        tree, count = tree_list[i]
        if i <= 9:
            sorted_tree.append(tree)
            sorted_count.append(count)
        print('{tree:<{len}}\t{count}'.format(tree=tree, len=22 -
                                              len(tree.encode('GBK'))+len(tree), count=count))
    plt.bar(sorted_tree, sorted_count, color='grey')
    plt.xlabel('Tree Type')
    plt.ylabel('counts')
    plt.title('Number of tree types')
    plt.show()


def tree_tag_analyse(data):
    tree_tag = list(data['Tag'])
    start_time = list(data['Start Time'])
    end_time = list(data['End Time'])
    duration = []
    time1 = []
    time2 = []
    dic_tag = {}
    for i in start_time:
        x = i.split(' ')[3].split(':')
        time1.append(int(x[0]) * 60 * 60 + int(x[1]) * 60 + int(x[2]))
    # print(time1)

    for i in end_time:
        x = i.split(' ')[3].split(':')
        time2.append(int(x[0]) * 60 * 60 + int(x[1]) * 60 + int(x[2]))
    # print(time2)

    for i in range(0, len(time1)):
        if time1[i] > time2[i]:
            duration.append(24 * 60 * 60 - time1[i] + time2[i])
        else:
            duration.append(time2[i] - time1[i])
    # print(duration)

    total_duration = sum(duration)
    for i in range(0, len(duration)):
        if tree_tag[i] in dic_tag.keys():
            dic_tag[tree_tag[i]] += duration[i] / 60 / 60
        else:
            dic_tag[tree_tag[i]] = duration[i] / 60 / 60
    # print(dic_tag)

    explode = [0.01] * len(dic_tag.keys())
    color = ['grey', 'salmon', 'lime', 'lightskyblue',
             'gold', 'red', 'yellow', 'green', 'silver', 'pink']
    plt.pie(dic_tag.values(), explode = explode, labels = dic_tag.keys(), autopct = '%1.1f%%', colors = color)
    plt.title('Tag distribution')
    # plt.show()

    return duration


def success_rate_analyse(data):
    tree_is_success = list(data['Is Success'])
    success = tree_is_success.count(True)
    fail = tree_is_success.count(False)
    print('{0} trees were planted: {1} successful and {2} failed'.format(
        len(tree_is_success), success, fail))
    print('the success rate is {0:.2f}%'.format(
        success/len(tree_is_success)*100))


def day_and_month_analyse(data, duration):
    start_time = list(data['Start Time'])
    month = []
    week = []
    dic_month = {'Jan': 0, 'Feb': 0, 'Mar': 0, 'Apr': 0, 'May': 0,
                 'Jun': 0, 'Jul': 0, 'Aug': 0, 'Sep': 0, 'Oct': 0, 'Nov': 0, 'Dec': 0}
    dic_week = {'Mon': 0, 'Tue': 0, 'Wed': 0,
                'Thu': 0, 'Fri': 0, 'Sat': 0, 'Sun': 0, }
    for i in start_time:
        month.append(i.split(' ')[1])
        week.append(i.split(' ')[0])
    # print(month)
    # print(week)
    for i in range(0, len(month)):
        dic_month[month[i]] += duration[i]/60/60
        dic_week[week[i]] += duration[i]/60/60
    # print(dic_month)
    # print(dic_week)
    plt.subplot(1, 2, 1)
    plt.plot(dic_month.keys(), dic_month.values(),
             color='red', marker='o', markerfacecolor='blue')
    plt.xlabel('month')
    plt.ylabel('hour')
    plt.title('Month duration')
    plt.subplot(1, 2, 2)
    plt.plot(dic_week.keys(), dic_week.values(),
             color='blue', marker='o', markerfacecolor='red')
    plt.xlabel('week')
    plt.ylabel('hour')
    plt.title('Week duration')
    plt.show()


def test2():
    data = pd.read_csv(
        'D:\\phpstudy\\azhe\\forest\\databases\\Plants of 405720329@qq.com (STDquantum).csv')
    # data = pd.read_csv(
    #     'D:\\phpstudy\\azhe\\forest\\Plants of 405720329@qq.com (STDquantum) (1).csv')
    tree_type_analyse(data)
    duration = tree_tag_analyse(data)
    success_rate_analyse(data)
    day_and_month_analyse(data, duration)


def main():
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决中文显示问题
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    test2()


if __name__ == '__main__':
    main()
    sys("pause")
