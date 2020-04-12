filetxt = "test.txt"
filecsv = "test.csv"
test_tt = "test_tt.txt"


def parse(path):
    file = open(path, encoding="utf-8", mode="r")
    complete_file = file.read()
    file = open(path, encoding="utf-8", mode="r")
    line_file = file.readlines()
    parsed_file = []
    if "|" in complete_file:
        if ";" in complete_file or "	" in complete_file:
            return False
        else:
            char = "|"
    elif ";" in complete_file:
        if "|" in complete_file or "	" in complete_file:
            return False
        else:
            char = ";"
    elif "	" in complete_file:
        if ";" in complete_file or "|" in complete_file:
            return False
        else:
            char = "	"
    else:
        for line in line_file:
            line = line.replace("\ufeff", "")
            line = line.replace("\n", "")
            line = line.replace(" ", "")
            parsed_file.append(line)
        return parsed_file
    for line in line_file:
        line = line.replace("\ufeff", "")
        line = line.replace("\n", "")
        line = line.replace(" ", "")
        parsed_file.append(line.split(char))
    return parsed_file


if __name__ == '__main__':
    print(parse(filetxt))
    print(parse(filecsv))
    print(parse(test_tt))
