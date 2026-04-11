import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

class UserAgentClassifier(nn.Module):
    def __init__(self, input_size, num_classes):
        super(UserAgentClassifier, self).__init__()
        self.fc = nn.Linear(input_size, num_classes)

    def forward(self, x):
        return self.fc(x)

class UserAgentDataset(Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y

    def __len__(self):
        return self.X.shape[0]

    def __getitem__(self, idx):
        return torch.tensor(self.X[idx].toarray(), dtype=torch.float32).squeeze(0), torch.tensor(self.y[idx], dtype=torch.long)

class BotAnalysis:
    def __init__(self, train=False):
        if train:
            data = pd.read_csv('user_agents.csv')
            self.vectorizer = CountVectorizer()
            X = self.vectorizer.fit_transform(data['user_agent'])

            self.label_encoder = LabelEncoder()
            y = self.label_encoder.fit_transform(data['label'])

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            self.train_dataset = UserAgentDataset(X_train, y_train)
            self.test_dataset = UserAgentDataset(X_test, y_test)
            self.train_loader = DataLoader(self.train_dataset, batch_size=128, shuffle=True)
            self.test_loader = DataLoader(self.test_dataset, batch_size=128, shuffle=False)

            input_size = X_train.shape[1]
            num_classes = len(set(y))
            self.model = UserAgentClassifier(input_size, num_classes)

            criterion = nn.CrossEntropyLoss()
            optimizer = optim.Adam(self.model.parameters(), lr=0.001)

            for epoch in range(3):  # Reduced from 10 to 3
                self.model.train()
                for inputs, labels in self.train_loader:
                    optimizer.zero_grad()
                    outputs = self.model(inputs)
                    loss = criterion(outputs, labels)
                    loss.backward()
                    optimizer.step()

            self.model.eval()
            correct = 0
            total = 0
            with torch.no_grad():
                for inputs, labels in self.test_loader:
                    outputs = self.model(inputs)
                    _, predicted = torch.max(outputs.data, 1)
                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()
            # print(f"Test Accuracy: {100 * correct / total}%")

        else:
            self.model = UserAgentClassifier(input_size=50, num_classes=2)
            self.model.eval()
            self.vectorizer = CountVectorizer()

    def preprocess_input(self, input_string):
        vector = self.vectorizer.transform([input_string])
        padded = torch.tensor(vector.toarray(), dtype=torch.float32)
        return padded

    def analyze(self, input_string):
        padded_sequence = self.preprocess_input(input_string)
        with torch.no_grad():
            prediction = self.model(padded_sequence)
            scores = torch.sigmoid(prediction)
            score_final = round(float(scores.squeeze()[1]) * 100, 2)
        return score_final

if __name__ == "__main__":
    bot_analyzer = BotAnalysis(train=True)
    score = bot_analyzer.analyze("Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/68.0.3440.106 Safari/537.36")
    print(score)
        
