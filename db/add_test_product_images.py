import random


if __name__ == "__main__":
    print('''INSERT INTO ProductFiles (pid, url, index, type)''')
    print("VALUES")
    for i in range(10000):
        for j in range(1, random.randint(2,5)):
            img_num = random.randint(1,200)
            url = str(img_num) + ".jpg"
            line = "(" + str(i) + ", \'" + url + "\', " + str(j) + ", \'IMG\')," 
            print(line)