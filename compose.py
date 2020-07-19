# 本文件用于将 poems.json 和 comprehensions.json 合并为 universal.json

import json, zhon.hanzi, string

# 屏蔽掉 comprehensions.json 有而 poems.json 无的内容
ignored_list = [
    "竹里馆", "夜归鹿门歌", "菩萨蛮.其二", "阁夜",
    "沁园春.长沙", "雨巷", "再别康桥", "荆轲刺秦王",
    "记念刘和珍君", "秋兴八首其一", "咏怀古迹其三", "马嵬",
    "寡人之于国也", "水龙吟.登建康赏心亭", "醉花阴", "廉颇蔺相如列传"
]
ignored_list = set(ignored_list)

def is_ignored(s) :
    return s in ignored_list

# 标题比较需要跳过的内容
title_filter = string.punctuation + zhon.hanzi.punctuation + ' '
title_filter = set(title_filter)

# 理解性默写去重比较需要跳过的内容
comprehension_filter = string.punctuation + zhon.hanzi.punctuation + '$0123456789'
comprehension_filter = set(title_filter)

# 带有过滤器的字符串比较器
def str_cmp(a, b, filter) :
    _a = ''.join(ch for ch in a if ch not in filter)
    _b = ''.join(ch for ch in b if ch not in filter)
    return _a == _b

# 判断标题一致
def judge_title(a, b) :
    x = 'tag' in a
    y = 'tag' in b
    
    # 如果一个有 tag 一个无 tag 则他们必不匹配
    if x ^ y :
        return False

    t = str_cmp(a['title'], b['title'], title_filter)

    # 如果他们都没有 tag 的话那只需要匹配标题
    if not x and not y :
        return t

    # 如果他们都有 tag 的话需要匹配 tag
    return t and a['tag'] == b['tag']
    

# 判断理解性默写是否重复
def judge_duplicate(poem, comprehension) :
    try :
        comprehensions = poem['comprehensions']
    except KeyError :
        return True
    
    for i in comprehensions :
        if str_cmp(i['content'], comprehension["content"], comprehension_filter) :
            return False
    
    return True

# 检查 s 是否出现在 poem 中
def search_sentence(poem, s) :
    if isinstance(poem, list) :
        ret = False
        for i in poem :
            ret = ret or search_sentence(i, s)
        return ret
    elif isinstance(poem, str) :
        return s == poem
    else :
        return False

# 检查理解性默写答案
def check_answer(poem, comprehension) :
    for i in comprehension["answer"] :
        if isinstance(i, str):
            if not search_sentence(poem["normal"], i) :
                return -1
        elif isinstance(i, list) :
            for j in i :
                if not search_sentence(poem["content"], j) :
                    return -1
        else :
            return -2

    return 0

# 合并理解性默写题目
def process_comprehension(comprehension) :
    if is_ignored(comprehension["title"]) :
        return 1    # 在屏蔽列表中

    for i in universal_repositories :
        if judge_title(i, comprehension):

            if not judge_duplicate(i, comprehension) : 
                return -2 # 题目重复

            status = check_answer(i, comprehension)
            if status == -1 :
                print("[警告] 理解性默写题目答案与文本不合")
                print(comprehension)

            if status == -2 :
                print("[警告] 理解性默写题目格式错误")
                print(comprehension)
                return -3


            if "source" not in i :
                try :
                    i["source"] = comprehension["source"]
                except KeyError :
                    pass

            if "author" not in i :
                try :
                    i["author"] = comprehension["author"]
                except KeyError :
                    pass

            single_record = {}
            single_record["content"] = comprehension["content"]
            single_record["answer"] = comprehension["answer"]

            try :
                comprehensions = i['comprehensions']
            except KeyError :
                i['comprehensions'] = []
                comprehensions = i['comprehensions']

            comprehensions.append(single_record)

            return 0 # 正常处理

    return -1 # 在 poems.json 中不存在对应的内容

# 主程序
if __name__ == "__main__":

    normal_file = open("normal/poems.json", "rt", encoding='utf-8')
    normal = json.loads(normal_file.read())
    normal_file.close()

    comprehensions_file = open("comprehensions/comprehensions.json", "rt", encoding='utf-8')
    comprehensions = json.loads(comprehensions_file.read())
    comprehensions_file.close()

    universal = {}
    universal_repositories = []
    universal["$schema"] = "https://reciter.binkic.com/universal/schema.json"
    universal["repositories"] = universal_repositories


    for i in normal["poems"] :
        single_record = {}
        single_record["title"] = i["title"]
        single_record["normal"] = i["content"]
        try :
            single_record["source"] = i["source"]
        except KeyError :
            pass
        try :
            single_record["author"] = i["author"]
        except KeyError :
            pass
        try :
            single_record["tag"] = i["tag"]
        except KeyError :
            pass
        
        # 索引：title -> tag
        
        # single_record["comprehensions"] = []
        universal_repositories.append(single_record)

    for comprehension in comprehensions["comprehensions"] :
        status = process_comprehension(comprehension)
        if status == -1 :
            print(comprehension)

    for i in range(0,len(universal_repositories)) :
        old = universal_repositories[i]
        new = {}

        for j in ["title", "author", "source", "normal", "comprehensions"] :
            try :
                new[j] = old[j]
            except KeyError :
                pass

        universal_repositories[i] = new

    save = open("universal/universal.json", "w+", encoding='utf-8')
    save.write( json.dumps(universal, indent = 4 , ensure_ascii = False ) )
    save.close()
