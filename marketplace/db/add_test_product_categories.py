import random


if __name__ == "__main__":
    print('''INSERT INTO ProductOwner(pid, uid)''')
    print("VALUES")
    for i in range(10000):
        line = "(" + str(i) + "," + str(0) + ")," 
        print(line)
