import math
from collections import Counter

class DecisionTree:
    def __init__(self):
        self.tree = {}

    def entropy(self, labels):
        # Calcula a entropia de um conjunto de labels
        counts = Counter(labels)
        probabilities = [count / len(labels) for count in counts.values()]
        return -sum(p * math.log2(p) for p in probabilities)

    def information_gain(self, data, feature, target):
        # Calcula o ganho de informação de uma feature
        total_entropy = self.entropy(data[target])
        values, counts = zip(*Counter(data[feature]).items())
        weighted_entropy = sum((count / len(data)) * self.entropy(data[data[feature] == value][target]) for value, count in zip(values, counts))
        return total_entropy - weighted_entropy

    def id3(self, data, features, target):
        # Algoritmo ID3 para construir a árvore de decisão
        if len(set(data[target])) == 1:
            return data[target].iloc[0]
        if not features:
            return Counter(data[target]).most_common(1)[0][0]
        best_feature = max(features, key=lambda f: self.information_gain(data, f, target))
        tree = {best_feature: {}}
        for value in set(data[best_feature]):
            subset = data[data[best_feature] == value]
            subtree = self.id3(subset, [f for f in features if f != best_feature], target)
            tree[best_feature][value] = subtree
        return tree

    def fit(self, data, features, target):
        # Treina a árvore de decisão
        self.tree = self.id3(data, features, target)

    def predict(self, sample):
        # Faz uma previsão para uma amostra
        node = self.tree
        while isinstance(node, dict):
            feature = next(iter(node))
            node = node[feature][sample[feature]]
        return node