import json, zhon.hanzi, string

ignored_list = [
    "竹里馆", "夜归鹿门歌", "菩萨蛮.其二", "阁夜",
    "沁园春.长沙", "雨巷", "再别康桥", "荆轲刺秦王",
    "记念刘和珍君", "秋兴八首其一", "咏怀古迹其三", "马嵬",
    "寡人之于国也", "水龙吟.登建康赏心亭", "醉花阴", "廉颇蔺相如列传"
]
ignored_list = set(ignored_list)

def is_ignored(s) :
    return s in ignored_list

title_filter = string.punctuation + zhon.hanzi.punctuation + ' '
title_filter = set(title_filter)

comprehension_filter = string.punctuation + zhon.hanzi.punctuation + '$0123456789'
comprehension_filter = set(title_filter)

def str_cmp(a, b, filter) :
    _a = ''.join(ch for ch in a if ch not in filter)
    _b = ''.join(ch for ch in b if ch not in filter)
    return _a == _b

def judge_title(a, b) :
    return str_cmp(a, b, title_filter)

def judge_duplicate(poem, comprehension) :
    try :
        comprehensions = poem['comprehensions']
    except KeyError :
        return True
    
    for i in comprehensions :
        if str_cmp(i['content'], comprehension["content"], comprehension_filter) :
            return False
    
    return True

def process_comprehension(comprehension) :
    if is_ignored(comprehension["title"]) :
        return 1

    for i in universal_repositories :
        if judge_title(i["title"], comprehension["title"] ):

            if not judge_duplicate(i, comprehension) : 
                return -2

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

            return 0

    return -1


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
