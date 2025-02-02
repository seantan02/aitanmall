import torch
import sys
sys.path.insert(0,"/var/www/stage-aitanmall.tech/")

from AI.main import helper
from AI.model.bigram import BigramLanguageModel

# with open("/var/www/stage-aitanmall.tech/AI/data.txt", "r") as f:
#     data_content = f.read()

with open("/var/www/stage-aitanmall.tech/AI/data.txt", "r") as f:
    data_content = f.read()

data_content = data_content.replace("\r", "").replace("\t", "").replace("  ", " ")

given_string = data_content.split("\n")

vocab = []
torch_data=""
char_size = 2
for string in given_string:
    #clean the string removing \n \r \t
    if len(string)>0:
        torch_data += string+"\n"
        # mid_char_size = int(get_biggest_vocabulary_char_size(string)/2)
        vocab += helper.tokenize(char_size, string)

vocabulary = sorted(list(set(vocab)))
characterized_enum_dict = helper.characterize_list_of_enum(vocabulary)
emumed_characters_dict = helper.enumerate_list_of_string(vocabulary)

# test = "Hey how are you brother?"

# print(encode(char_size, test, characterized_enum_dict))

data = torch.tensor(helper.encode(char_size,torch_data,characterized_enum_dict, emumed_characters_dict, vocabulary), dtype=torch.long)
#training data
n = int(0.9*len(data))
training_data = data[:n]
validation_data = data[n:]

torch.manual_seed(1337)
batch_size = 4
block_size = 8

xb, yb = helper.get_batch("train", training_data, validation_data)
        
gpt = BigramLanguageModel(vocab_size=len(vocabulary))
logits, loss = gpt(xb, yb)

#generate from the model
idx = torch.zeros((1, 1), dtype=torch.long)

#save model
torch.save(gpt, '/var/www/stage-aitanmall.tech/AI/GPT/eng_v1.pth')