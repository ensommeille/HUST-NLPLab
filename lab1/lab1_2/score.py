import torch
import pickle


def entity_split(x, y, id2tag, entities, cur):
    start, end = -1, -1
    for j in range(len(x)):
        if id2tag[y[j]] == 'B':
            start = cur + j
        elif id2tag[y[j]] == 'M' and start != -1:
            continue
        elif id2tag[y[j]] == 'E' and start != -1:
            end = cur + j
            entities.add((start, end))
            start, end = -1, -1
        elif id2tag[y[j]] == 'S':
            entities.add((cur + j, cur + j))
            start, end = -1, -1
        else:
            start, end = -1, -1


# 检查 GPU 是否可用
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 加载模型并移动到 GPU
model = torch.load('save/model.pkl')
model = model.to(device)

# 加载数据
with open('data/datasave.pkl', 'rb') as inp:
    word2id = pickle.load(inp)
    id2word = pickle.load(inp)
    tag2id = pickle.load(inp)
    id2tag = pickle.load(inp)
    x_train = pickle.load(inp)
    y_train = pickle.load(inp)
    x_test = pickle.load(inp)
    y_test = pickle.load(inp)

# 准备测试数据
test_data = []
with open('data/test.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        x = torch.LongTensor(1, len(line)).to(device)
        # 修改 mask 的数据类型为 torch.bool
        mask = torch.ones_like(x, dtype=torch.bool).to(device)
        length = [len(line)]
        for i in range(len(line)):
            if line[i] in word2id:
                x[0, i] = word2id[line[i]]
            else:
                x[0, i] = len(word2id)
        test_data.append((x, mask, length))

# 进行预测
predictions = []
with torch.no_grad():
    model.eval()
    for x, mask, length in test_data:
        predict_list = model.infer(x, mask, length)
        def move_to_cpu(item):
            if isinstance(item, torch.Tensor):
                return item.cpu()
            elif isinstance(item, list):
                return [move_to_cpu(sub_item) for sub_item in item]
            return item
        predict = move_to_cpu(predict_list)[0]
        predictions.append(predict)

# 计算 F1-score
entity_predict = set()
entity_label = set()
cur = 0
for i in range(len(x_test)):
    entity_split(x_test[i], predictions[i], id2tag, entity_predict, cur)
    entity_split(x_test[i], y_test[i], id2tag, entity_label, cur)
    cur += len(x_test[i])

right_predict = [i for i in entity_predict if i in entity_label]
if len(right_predict) != 0:
    precision = float(len(right_predict)) / len(entity_predict)
    recall = float(len(right_predict)) / len(entity_label)
    f1_score = (2 * precision * recall) / (precision + recall)
else:
    precision = 0
    recall = 0
    f1_score = 0

# 将结果输出到文件
with open('evaluation_results.txt', 'w', encoding='utf-8') as out_file:
    out_file.write(f"Precision: {precision}\n")
    out_file.write(f"Recall: {recall}\n")
    out_file.write(f"F1-score: {f1_score}\n")
