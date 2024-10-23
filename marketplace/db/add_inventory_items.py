import random


if __name__ == "__main__":
    print('''INSERT INTO Inventory''')
    print("VALUES")
    for i in range(100):
        j = random.randint(1,200)
        line = "(" + "100" + ", \'" + str(i) + "\', " + str(j) + ")," 
        print(line)