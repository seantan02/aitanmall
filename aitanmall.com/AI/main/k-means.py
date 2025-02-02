from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

tagged_data = [("How's your day buddy?", "greeting"), 
               ("How do you like the day?", "greeting"),
               ("I am fine thank you!", "greeting_response"),
               ("I am great. thanks.", "greeting_response")]

sentences, true_labels = zip(*tagged_data)

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(sentences)

# corpus = ["Hey how are you?",
#           "I think you are kinda cute",
#           "How is your day?",
#           "How's it going?",
#           "So far so good. Thanks.",
#           "Not too bad. Thanks."]

# vectorizer = TfidfVectorizer()
# X = vectorizer.fit_transform(corpus)

# Create a list to hold the total within-cluster sum of square for each number of clusters
wcss = []

# Iterate from 1 to 10 clusters
#if the fall of kmeans.inertia is constant and non-zero, we will take it
best_inertia = None
previous_inertia = None
for i in range(1, len(tagged_data)+1):
    #calculate the changes of kmeans.inertia from previous one
    kmeans = KMeans(n_clusters=i, init='k-means++', random_state=0)
    kmeans.fit(X)

    current_inertia = kmeans.inertia_
    wcss.append(current_inertia)

    if previous_inertia == None:
        previous_inertia = current_inertia
        continue
    else:
        difference = ((previous_inertia - current_inertia)/previous_inertia)*100
        if difference <= 10 or current_inertia <= 0.1:
            print(f"Best cluster inertia {previous_inertia}. Cluster number: {i-1}")
            break
    previous_inertia = current_inertia

print(wcss)