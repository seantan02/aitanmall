import torch
from torch.jit import script, trace
import torch.nn as nn
from torch import optim
import torch.nn.functional as F
import csv
import random
import re
import os
import unicodedata
import codecs
from io import open
import itertools
import math
import json
import sys
sys.path.insert(0,"/var/www/stage-aitanmall.tech/")
from AI.seq2seq.main import helper
from AI.seq2seq.main.classes.encoder import EncoderRNN
from AI.seq2seq.main.classes.decoder import LuongAttnDecoderRNN
from AI.seq2seq.main.classes.evaluation import GreedySearchDecoder
from AI.seq2seq.main.classes.vocab import Voc, PAD_token, SOS_token, EOS_token
from AI.seq2seq.main.device import device


MAX_LENGTH = 20  # Maximum sentence length to consider
MIN_COUNT = 1
max_length = MAX_LENGTH
min_count = MIN_COUNT


data_file_path = os.path.join("/var","www","stage-aitanmall.tech","AI","seq2seq","data","clean","data0.txt")
data_pairs = helper.read_clean_txt_file(data_file_path)

# Load/Assemble voc and pairs
corpus_name = "malay-dialog"
corpus = os.path.join("data", corpus_name)

save_dir = os.path.join("/var","www","stage-aitanmall.tech","AI","seq2seq","models")
voc, pairs = helper.loadPrepareData(corpus, corpus_name, data_pairs, save_dir, max_length)

# Trim voc and pairs
pairs = helper.trimRareWords(voc, pairs, min_count)

# Example for validation
small_batch_size = 5
# random.choise makes a list of pairs randomly according to small_batch_size
batches = helper.batch2TrainData(voc, [random.choice(pairs) for _ in range(small_batch_size)])
input_variable, lengths, target_variable, mask, max_target_len = batches

model_name = 'malay_dialog_model'
attn_model = 'dot'
#``attn_model = 'general'``
#``attn_model = 'concat'``
hidden_size = 500
encoder_n_layers = 2
decoder_n_layers = 2
dropout = 0.1
batch_size = 64

# Set checkpoint to load from; set to None if starting from scratch
loadFilename = None
checkpoint_iter = 4000

loadFilename = os.path.join(save_dir,model_name)+"-"+corpus_name

if os.path.exists(loadFilename):
    # If loading on same machine the model was trained on
    checkpoint = torch.load(loadFilename)
    # If loading a model trained on GPU to CPU
    #checkpoint = torch.load(loadFilename, map_location=torch.device('cpu'))
    encoder_sd = checkpoint['en']
    decoder_sd = checkpoint['de']
    encoder_optimizer_sd = checkpoint['en_opt']
    decoder_optimizer_sd = checkpoint['de_opt']
    embedding_sd = checkpoint['embedding']
    voc.__dict__ = checkpoint['voc_dict']
else:
    checkpoint=None

print('Building encoder and decoder ...')
# Initialize word embeddings
embedding = nn.Embedding(voc.num_words, hidden_size)
if os.path.exists(loadFilename):
    embedding.load_state_dict(embedding_sd)
# Initialize encoder & decoder models
encoder = EncoderRNN(hidden_size, embedding, encoder_n_layers, dropout)
decoder = LuongAttnDecoderRNN(attn_model, embedding, hidden_size, voc.num_words, decoder_n_layers, dropout)
if os.path.exists(loadFilename):
    encoder.load_state_dict(encoder_sd)
    decoder.load_state_dict(decoder_sd)
# Use appropriate device
encoder = encoder.to(device)
decoder = decoder.to(device)
print('Models built and ready to go!')

# Configure training/optimization
clip = 50.0
teacher_forcing_ratio = 1.0
learning_rate = 0.0001
decoder_learning_ratio = 5.0
n_iteration = 50
print_every = 5
save_every = 25

# Ensure dropout layers are in train mode
encoder.train()
decoder.train()

# Initialize optimizers
print('Building optimizers ...')
encoder_optimizer = optim.Adam(encoder.parameters(), lr=learning_rate)
decoder_optimizer = optim.Adam(decoder.parameters(), lr=learning_rate * decoder_learning_ratio)
if os.path.exists(loadFilename):
    encoder_optimizer.load_state_dict(encoder_optimizer_sd)
    decoder_optimizer.load_state_dict(decoder_optimizer_sd)

# If you have CUDA, configure CUDA to call
for state in encoder_optimizer.state.values():
    for k, v in state.items():
        if isinstance(v, torch.Tensor):
            state[k] = v.cpu()

for state in decoder_optimizer.state.values():
    for k, v in state.items():
        if isinstance(v, torch.Tensor):
            state[k] = v.cpu()

# Run training iterations
print("Starting Training!")
helper.trainIters(model_name, voc, pairs, encoder, decoder, encoder_optimizer, decoder_optimizer,
           embedding, encoder_n_layers, decoder_n_layers, save_dir, n_iteration, batch_size,
           print_every, save_every, clip, max_length, corpus_name, loadFilename, checkpoint, device=device)

encoder.eval()
decoder.eval()

# Initialize search module
searcher = GreedySearchDecoder(encoder, decoder)
helper.evaluateInput(encoder, decoder, searcher, voc, max_length, device)