import torch
from torch import nn
from torch.optim import Adam
import random
# import sys
# sys.path.insert(0,"/var/www/stage-aitanmall.tech/")

# from AI.main.npl_chatbot import vocab

n_epochs = 10

# VOCAB = vocab.build_fairseq_vocab('/var/www/stage-aitanmall.tech/AI/data/v1.txt')
# print(VOCAB)
# Data preprocessing

class TabularDataset():
    def __init__(self, examples, fields):
        self.examples = examples
        self.fields = dict(fields)

class Field():
    def __init__(self):
        super().__init__()

class BucketIterator():
    def __init__(self, dataset, batch_size=1, device=None):
        super().__init__(dataset, batch_size=batch_size, device=device)

SRC = Field(tokenize = 'spacy', init_token = '<sos>', eos_token = '<eos>', lower = True)
TRG = Field(tokenize = 'spacy', init_token = '<sos>', eos_token = '<eos>', lower = True)

fields = {'src': ('src', SRC), 'trg': ('trg', TRG)}

# Assume we're using a TabularDataset here
data = TabularDataset(path='/var/www/stage-aitanmall.tech/AI/data/v1.json', format='json', fields=fields)

SRC.build_vocab(data)
TRG.build_vocab(data)

vocab_size = len(TRG.vocab)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

train_iterator, test_iterator = BucketIterator.splits(
    (data, data), 
    batch_size = 64,
    device = device)

# Model creation
class Seq2Seq(nn.Module):
    def __init__(self, encoder, decoder, device):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder
        self.device = device
        
    def forward(self, src, trg, teacher_forcing_ratio = 0.5):
       # src = [src len, batch size]
        # trg = [trg len, batch size]
        # teacher_forcing_ratio is probability to use teacher forcing
        # e.g. if teacher_forcing_ratio is 0.75 we use ground-truth inputs 75% of the time

        batch_size = trg.shape[1]
        trg_len = trg.shape[0]
        trg_vocab_size = self.decoder.output_dim
        
        # tensor to store decoder outputs
        outputs = torch.zeros(trg_len, batch_size, trg_vocab_size).to(self.device)
        
        # last hidden state of the encoder is used as the initial hidden state of the decoder
        hidden, cell = self.encoder(src)
        
        # first input to the decoder is the <sos> tokens
        input = trg[0,:]
        
        for t in range(1, trg_len):

            # insert input token embedding, previous hidden and previous cell states
            # receive output tensor (predictions) and new hidden and cell states
            output, hidden, cell = self.decoder(input, hidden, cell)
            
            # place predictions in a tensor holding predictions for each token
            outputs[t] = output
            
            # decide if we are going to use teacher forcing or not
            teacher_force = random.random() < teacher_forcing_ratio
            
            # get the highest predicted token from our predictions
            top1 = output.argmax(1) 
            
            # if teacher forcing, use actual next token as next input
            # if not, use predicted token
            input = trg[t] if teacher_force else top1
        
        return outputs

# Model creation
class Encoder(nn.Module):
    def __init__(self, input_dim, emb_dim, hid_dim, n_layers, dropout):
        super().__init__()

        self.hid_dim = hid_dim
        self.n_layers = n_layers

        self.embedding = nn.Embedding(input_dim, emb_dim)
        self.rnn = nn.LSTM(emb_dim, hid_dim, n_layers, dropout = dropout)
        self.dropout = nn.Dropout(dropout)

    def forward(self, src):

        # src = [src len, batch size]

        embedded = self.dropout(self.embedding(src))

        # embedded = [src len, batch size, emb dim]

        outputs, (hidden, cell) = self.rnn(embedded)

        # outputs = [src len, batch size, hid dim * n directions]
        # hidden = [n layers * n directions, batch size, hid dim]
        # cell = [n layers * n directions, batch size, hid dim]

        return hidden, cell

class Decoder(nn.Module):
    def __init__(self, output_dim, emb_dim, hid_dim, n_layers, dropout):
        super().__init__()

        self.output_dim = output_dim
        self.hid_dim = hid_dim
        self.n_layers = n_layers

        self.embedding = nn.Embedding(output_dim, emb_dim)
        self.rnn = nn.LSTM(emb_dim, hid_dim, n_layers, dropout = dropout)
        self.fc_out = nn.Linear(hid_dim, output_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, input, hidden, cell):

        # input = [batch size]
        # hidden = [n layers * n directions, batch size, hid dim]
        # cell = [n layers * n directions, batch size, hid dim]

        input = input.unsqueeze(0)

        # input = [1, batch size]

        embedded = self.dropout(self.embedding(input))

        # embedded = [1, batch size, emb dim]

        output, (hidden, cell) = self.rnn(embedded, (hidden, cell))

        # output = [seq len, batch size, hid dim * n directions]
        # hidden = [n layers * n directions, batch size, hid dim]
        # cell = [n layers * n directions, batch size, hid dim]

        prediction = self.fc_out(output.squeeze(0))

        # prediction = [batch size, output dim]

        return prediction, hidden, cell

# Assuming we have an Encoder and Decoder class
encoder = Encoder(vocab_size, 200, 200, 3, 0.2)
decoder = Decoder(vocab_size, 200, 200, 3, 0.2)

model = Seq2Seq(encoder, decoder, device).to(device)

# Training
optimizer = Adam(model.parameters())

criterion = nn.CrossEntropyLoss(ignore_index = TRG.vocab.stoi[TRG.pad_token])

for epoch in range(n_epochs):
    for i, batch in enumerate(train_iterator):
        src = batch.src
        trg = batch.trg

        output = model(src, trg)
        output_dim = output.shape[-1]
        
        output = output[1:].view(-1, output_dim)
        trg = trg[1:].view(-1)

        loss = criterion(output, trg)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

# Save the model
torch.save(model.state_dict(), '/var/www/stage-aitanmall.tech/AI/NPLGPT/v1.pth')