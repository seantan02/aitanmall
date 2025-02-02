import os
import sys
import re
sys.path.insert(0,"/var/www/stage-aitanmall.tech/")


def get_file_extension(filename):
    _, extension = os.path.splitext(filename)
    return extension

def remove_special_char_from_txt_file(data_file_path):
    special_char = ["@", "#","$", "%", "^", "&", "*", "(", ")","!","http"]
    data = ""
    num_lines = 0
    for line in open(data_file_path, 'r', encoding='utf-8'):
        line = line.strip().replace("\n", "").replace("\t", "").replace("\r", "")
        splitted_line = line.split()
        #to make sure index never go out of range
        splitted_lin_len = len(splitted_line)
        #cleaned line
        cleaned_line = ""
        i = 0
        while i < splitted_lin_len:
            this_word_ignored = False
            word = splitted_line[i]
            for char in special_char:
                if char in word:
                    removed_word = splitted_line.pop(i)
                    #update both length and i
                    splitted_lin_len -= 1
                    i -= 1
                    this_word_ignored = True
                    break
            if not this_word_ignored:
                word.strip().replace("\n", "").replace("\t", "").replace("\r", "")
                cleaned_line += word+" "
            i += 1
        if re.search('[a-zA-Z]', cleaned_line) != None:
            num_lines += 1
            data += cleaned_line+"\n"

    return data, num_lines

raw_data_file_path = os.path.join("/var","www","stage-aitanmall.tech","AI","seq2seq","data","raw","data1.txt")
cleaned_file_path = os.path.join("/var","www","stage-aitanmall.tech","AI","seq2seq","data","clean","data1.txt")


raw_file_extension = get_file_extension(raw_data_file_path)

if raw_file_extension == ".txt":
    #first read the file and assume each line is one sentence
    raw_file_content, num_lines = remove_special_char_from_txt_file(raw_data_file_path)
    if num_lines %2 == 0:
        #save file 
        with open(cleaned_file_path, "w") as f:
            f.write(raw_file_content)
            f.close()
    else:
        with open(cleaned_file_path, "a") as f:
            splitted_cleaned_data = raw_file_content.split("\n")
            for i in range(len(splitted_cleaned_data)-1):
                f.write(splitted_cleaned_data[i]+"\n")

            f.close()