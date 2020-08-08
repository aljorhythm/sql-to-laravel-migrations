

string = "abcdefg"

for i, x in enumerate(string):
    for j, y in enumerate(string):
        if i >= j:
            continue
        
        # print( x, y ,string[:i], string[i+1:j], string[j+1:])
        sub = string[:i] + string[i+1:j] + string[j+1:]
        print(sub)