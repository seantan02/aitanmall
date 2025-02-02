import torch

def tokenize(char_size, given_string):
    tokenized_string = []

    for index in range(len(given_string)):
        sub_word = given_string[index:index+char_size]
        tokenized_string.append(sub_word)

    return tokenized_string

def get_biggest_vocabulary(given_string):
    biggest_vocabulary = None
    char_size = 1
    while True:
        vocab_size_increased=False
        vocabulary = list(set(tokenize(char_size, given_string)))
        if biggest_vocabulary == None or len(vocabulary) > len(biggest_vocabulary):
            biggest_vocabulary = vocabulary
            vocab_size_increased = True
        char_size += 2
        if vocab_size_increased == False:
            return list(set(tokenize(int(char_size/2), given_string)))

def get_biggest_vocabulary_char_size(given_string):
    biggest_vocabulary = None
    char_size = 1
    while True:
        vocab_size_increased=False
        vocabulary = list(set(tokenize(char_size, given_string)))
        if biggest_vocabulary == None or len(vocabulary) > len(biggest_vocabulary):
            biggest_vocabulary = vocabulary
            vocab_size_increased = True
        char_size += 2
        if vocab_size_increased == False:
            return char_size

def enumerate_list_of_string(string_list) -> dict:
    """
    This method assign a integer to each string in a list and output a dictionary which enum is KEY, value is VALUE
    """
    enumed_string = {string:enum for string,enum in enumerate(string_list)}
    return enumed_string

def characterize_list_of_enum(string_list) -> dict:
    """
    This method assign a char to each enum in a list and output a dictionary which char is KEY,  enum is VALUE
    """
    enumed_string = {enum:string for string,enum in enumerate(string_list)}
    return enumed_string

def encode(char_size, string, characterized_enum_dict:dict, emumed_characters_dict, sorted_vocabulary:list):
    output = []
    for index in range(0, len(string), char_size):
        sub_word = string[index:index+char_size]
        if sub_word in characterized_enum_dict:
            output.append(characterized_enum_dict[sub_word])
        else:
            # #If it is a new vocab, we add to our sorted vocab in the correct position
            # #add the unknown vocab into our sorted vocab in the correct position
            # temp_vocab = sorted_vocabulary
            # insertion_positon_found = False
            # while True:
            #     temp_vocab_length = len(temp_vocab)
            #     midpoint = temp_vocab_length//2
            #     mid_value = temp_vocab[midpoint]
            #     if midpoint+1 >= temp_vocab_length:
            #         mid_value_right = None
            #     else:
            #         mid_value_right = temp_vocab[midpoint+1]
                
            #     if mid_value_right != None:
            #         #subword bigger than both side, we go to right
            #         if sub_word > mid_value and sub_word > mid_value_right:
            #             if midpoint+2 >= temp_vocab_length:
            #                 #shift everything including mid_value_right to one right
            #                 sorted_vocab_length = len(sorted_vocabulary)
            #                 i2 = 0
            #                 for i in range(midpoint+1, sorted_vocab_length):
            #                     sorted_vocabulary[sorted_vocab_length] = sorted_vocabulary[sorted_vocab_length-i2]
            #                     i2+=1
            #                 sorted_vocabulary[midpoint+1] = sub_word
            #                 break
            #             else:
            #                 temp_vocab = temp_vocab[midpoint+2:]
            #         elif sub_word < mid_value and sub_word < mid_value_right:
            #             temp_vocab = temp_vocab[:midpoint]
            #         elif sub_word > mid_value and sub_word < mid_value_right:
            #             #shift everything including mid_value_right to one right
            #             sorted_vocab_length = len(sorted_vocabulary)
            #             i2 = 0
            #             for i in range(midpoint+1, sorted_vocab_length):
            #                 sorted_vocabulary[sorted_vocab_length] = sorted_vocabulary[sorted_vocab_length-i2]
            #                 i2+=1
            #             sorted_vocabulary[midpoint+1] = sub_word
            #             break
            #     else:
            #         if sub_word > mid_value:


            sorted_vocabulary.append(sub_word)
            sorted_vocabulary = sorted(sorted_vocabulary)
            index_of_new_vocab = sorted_vocabulary.index(sub_word)
            #add to our mapping
            characterized_enum_dict[sub_word] = index_of_new_vocab
            emumed_characters_dict[index_of_new_vocab] = sub_word

            output.append(index_of_new_vocab)
    return output

def decode(list_of_enum, emumed_characters_dict):
    output = ""
    for index in range(len(list_of_enum)):
        enum = list_of_enum[index]
        output += emumed_characters_dict[enum]

    return output

def get_batch(split, training_data, validation_data, block_size = 8, batch_size = 4):
    data = training_data if split == "train" else validation_data
    ix = torch.randint(len(data) - block_size, (batch_size,))
    x = torch.stack([data[i:i+block_size] for i in ix])
    y = torch.stack([data[i+1:i+block_size+1] for i in ix])
    return x, y

@torch.no_grad()
def estimate_loss(model,eval_iters, training_data, validation_data, block_size = 8, batch_size = 4):
    out = {}
    model.eval()
    for split in ["train", "val"]:
        losses = torch.zeros(eval_iters)
        for k in range(eval_iters):
            X, Y = get_batch(split,training_data,validation_data,block_size,batch_size)
            logits, loss = model(X, Y)
            losses[k] = losses.mean()
        out[split] = losses.mean()
    model.train()
    return out