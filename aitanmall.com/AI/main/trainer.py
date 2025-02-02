import torch
import time
import sys
sys.path.insert(0,"/var/www/stage-aitanmall.tech/")
from AI.main import helper
import os

eval_iters = 200
eval_interval = 5
B, T, C = 4, 8, 2

#load our model back to train it
# GPT = torch.load('/var/www/stage-aitanmall.tech/AI/GPT/v2_latest.pth')
model_file_path = '/var/www/stage-aitanmall.tech/AI/GPT/eng_v1_latest.pth'
if os.path.isfile(model_file_path):
    GPT = torch.load(model_file_path)
else:
    GPT = torch.load('/var/www/stage-aitanmall.tech/AI/GPT/eng_v1.pth')

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

data = torch.tensor(helper.encode(char_size,torch_data,characterized_enum_dict, emumed_characters_dict, vocabulary), dtype=torch.long)
#training data
n = int(0.9*len(data))
training_data = data[:n]
validation_data = data[n:]

#now ew create a PyTorch optimizer
optimizer = torch.optim.AdamW(GPT.parameters(), lr=1e-2)

batch_size = 32
i = 0
while i < 1:
    for steps in range(1000):
        #sample a batch of data
        xb, yb = helper.get_batch("train", training_data, validation_data, batch_size=batch_size)
        # if steps % eval_interval == 0:
        #     loss=helper.estimate_loss(GPT, eval_iters,training_data, validation_data)
        #     print(f"Losses average is {loss}")
        #evaluate the loss
        logits, loss = GPT(xb, yb)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
    i+=1
    
print(loss.item())

# input = torch.tensor([helper.encode(char_size,"Apa khabar?",characterized_enum_dict, emumed_characters_dict, vocabulary)], dtype=torch.long)

# print(helper.decode(GPT.generate(idx = input, max_new_tokens=100)[0].tolist(), emumed_characters_dict))

torch.save(GPT, '/var/www/stage-aitanmall.tech/AI/GPT/eng_v1_latest.pth')
