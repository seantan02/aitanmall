import torch

class Head(torch.nn.Module):

    def __init__(self, head_size, block_size = 8, n_embed = 32):
        super().__init__()
        #each token directly reads the next token
        self.key = torch.nn.Linear(n_embed, head_size, bias=False)
        self.query = torch.nn.Linear(n_embed, head_size, bias=False)
        self.value = torch.nn.Linear(n_embed, head_size, bias=False)
        self.register_buffer("tril", torch.tril(torch.ones(block_size, block_size)))

    def forward(self,x):
        B, T, C = x.shape
        k = self.key(x)
        q = self.query(x)
        #compute weight
        weight = q @ k.transpose(-2, -1) * C**-0.5
        weight = weight.masked_fill(self.tril[:T, :T] == 0, float("-inf"))
        weight = torch.nn.functional.softmax(weight, dim=-1)

        v = self.value(x)
        output = weight @ v
        return output

class MultiheadAttention(torch.nn.Module):
    def __init__(self, num_heads, head_size, n_embed = 32, dropout =0.2):
        super().__init__()
        self.heads = torch.nn.ModuleList([Head(head_size) for _ in range(num_heads)])
        self.proj = torch.nn.Linear(num_heads*head_size, n_embed)
        self.dropout = torch.nn.Dropout(dropout)

    def forward(self, x):
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        out = self.dropout(self.proj(out))
        return out

class FeedForward(torch.nn.Module):
    def __init__(self, n_embed, dropout = 0.2) -> None:
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(n_embed, n_embed),
            torch.nn.ReLU(),
            torch.nn.Linear(n_embed, n_embed),
            torch.nn.Dropout(dropout),
        )

    def forward(self, x):
        return self.net(x)

class Block(torch.nn.Module):
    """Transformer block"""
    def __init__(self, n_embed, n_head):
        super().__init__()
        head_size = n_embed//n_head
        self.sa = MultiheadAttention(n_head, head_size)
        self.ffwd = FeedForward(n_embed)
        self.ln1 = torch.nn.LayerNorm(n_embed)
        self.ln2 = torch.nn.LayerNorm(n_embed)

    def forward(self, x):
        x = x + self.sa(self.ln1(x))
        x = x + self.ffwd(self.ln2(x))

        return x

class BigramLanguageModel(torch.nn.Module):

    def __init__(self, vocab_size, block_size = 8, n_embed = 32, n_layer =6, n_head =6):
        super().__init__()
        #each token directly reads the next token
        
        self.token_embedding_table = torch.nn.Embedding(vocab_size, n_embed)
        self.position_embedding_table = torch.nn.Embedding(block_size, n_embed)
        self.blocks = torch.nn.Sequential(*[Block(n_embed, n_head) for _ in range(n_layer)])
        self.ln_f = torch.nn.LayerNorm(n_embed)
        self.lm_head = torch.nn.Linear(n_embed, vocab_size)
    def forward(self, idx, targets=None):
        B, T = idx.shape
        
        tok_embed = self.token_embedding_table(idx)
        pos_embed = self.position_embedding_table(torch.arange(T))
        x = tok_embed + pos_embed
        x = self.blocks(x)
        x = self.ln_f(x)
        
        logits = self.lm_head(x) #(B,T,C) dimension

        if targets is None:
            loss = None
        else:
            B, T, C = logits.shape
            logits = logits.view(B*T, C)
            targets = targets.view(B*T)
            loss = torch.nn.functional.cross_entropy(logits, targets)

        return logits,loss

    def generate(self, idx, max_new_tokens, block_size = 8):
        #idx is the (B, T) array of indices in cuyrrent context
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -block_size:]
            #get the prediction
            logits, loss = self(idx_cond)
            #focus only on the last time step
            logits = logits[:, -1, :]
            #apply softmax to get the probabilities
            probs = torch.nn.functional.softmax(logits, dim=-1) #B, C
            #sample from the distribution
            idx_next = torch.multinomial(probs, num_samples = 1)
            idx = torch.cat((idx, idx_next), dim = 1)
        return idx