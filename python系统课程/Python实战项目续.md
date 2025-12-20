# Python实战项目（续）

## 3.3 数据清洗与存储（续）

2. **数据存储策略**：
   - 设计数据库模式
   - 实现数据分区策略
   - 构建索引优化查询

```python
# MongoDB数据存储示例
from pymongo import MongoClient
import pandas as pd
from datetime import datetime

# 连接MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['scraped_data']

# 定义集合（相当于表）
news_collection = db['news']
products_collection = db['products']

# 数据插入函数
def store_data(data, collection, batch_size=1000):
    """
    将数据存储到MongoDB，支持批量插入
    """
    # 添加时间戳
    for item in data:
        if 'created_at' not in item:
            item['created_at'] = datetime.now()
    
    # 批量插入
    if len(data) > batch_size:
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            collection.insert_many(batch)
    else:
        collection.insert_many(data)

# 创建索引
def create_indexes(collection, indexes):
    """
    为集合创建索引以优化查询
    """
    for index in indexes:
        collection.create_index(index['fields'], **index['options'])

# 示例：创建新闻数据的索引
news_indexes = [
    {'fields': [('title', 'text'), ('content', 'text')], 'options': {'name': 'text_index'}},
    {'fields': [('publish_date', -1)], 'options': {'name': 'date_index'}},
    {'fields': [('source', 1)], 'options': {'name': 'source_index'}}
]

create_indexes(news_collection, news_indexes)
```

3. **数据质量监控**：
   - 实现数据完整性检查
   - 构建异常检测机制
   - 设计数据质量报告

#### 学习要点

- ETL流程设计与实现
- 大规模数据处理技术
- 数据库优化策略
- 数据质量管理

## 4. 人工智能应用

### 4.1 图像识别

图像识别项目帮助你掌握计算机视觉技术：

#### 项目概述

- **功能特点**：图像分类、物体检测、人脸识别、OCR文字识别
- **技术栈**：TensorFlow/PyTorch + OpenCV + Flask + Docker
- **难度级别**：★★★★☆（进阶级）

#### 开发流程

1. **数据准备与预处理**：
   - 收集和标注图像数据
   - 图像增强与预处理
   - 数据集划分

```python
# 图像预处理示例
import cv2
import numpy as np
import os
from sklearn.model_selection import train_test_split

def load_and_preprocess_images(data_dir, target_size=(224, 224)):
    images = []
    labels = []
    label_map = {}
    
    # 遍历数据目录
    for label_idx, label in enumerate(os.listdir(data_dir)):
        label_dir = os.path.join(data_dir, label)
        if not os.path.isdir(label_dir):
            continue
        
        label_map[label_idx] = label
        
        # 遍历每个类别下的图像
        for img_file in os.listdir(label_dir):
            img_path = os.path.join(label_dir, img_file)
            try:
                # 读取图像
                img = cv2.imread(img_path)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 转换为RGB
                
                # 调整大小
                img = cv2.resize(img, target_size)
                
                # 归一化
                img = img / 255.0
                
                images.append(img)
                labels.append(label_idx)
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
    
    # 转换为numpy数组
    X = np.array(images)
    y = np.array(labels)
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    return X_train, X_test, y_train, y_test, label_map
```

2. **模型构建与训练**：
   - 设计神经网络架构
   - 实现训练流程
   - 模型评估与优化

```python
# 使用PyTorch构建图像分类模型
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from torchvision import models, transforms

# 定义模型
class ImageClassifier(nn.Module):
    def __init__(self, num_classes):
        super(ImageClassifier, self).__init__()
        # 使用预训练的ResNet50
        self.model = models.resnet50(pretrained=True)
        
        # 冻结特征提取层
        for param in self.model.parameters():
            param.requires_grad = False
        
        # 替换分类器
        num_features = self.model.fc.in_features
        self.model.fc = nn.Sequential(
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        return self.model(x)

# 训练函数
def train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs=10):
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)
    
    for epoch in range(num_epochs):
        print(f'Epoch {epoch+1}/{num_epochs}')
        print('-' * 10)
        
        # 训练阶段
        model.train()
        running_loss = 0.0
        running_corrects = 0
        
        for inputs, labels in train_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            
            # 梯度清零
            optimizer.zero_grad()
            
            # 前向传播
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            loss = criterion(outputs, labels)
            
            # 反向传播和优化
            loss.backward()
            optimizer.step()
            
            # 统计
            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)
        
        epoch_loss = running_loss / len(train_loader.dataset)
        epoch_acc = running_corrects.double() / len(train_loader.dataset)
        
        print(f'Train Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')
        
        # 验证阶段
        model.eval()
        running_loss = 0.0
        running_corrects = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs = inputs.to(device)
                labels = labels.to(device)
                
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                loss = criterion(outputs, labels)
                
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)
        
        epoch_loss = running_loss / len(val_loader.dataset)
        epoch_acc = running_corrects.double() / len(val_loader.dataset)
        
        print(f'Val Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')
    
    return model
```

3. **应用部署**：
   - 构建Web API
   - 实现实时图像处理
   - 部署到生产环境

#### 学习要点

- 深度学习模型设计
- 图像处理技术
- 模型部署与优化
- 实时处理系统设计

### 4.2 自然语言处理

自然语言处理项目帮助你掌握文本分析技术：

#### 项目概述

- **功能特点**：文本分类、情感分析、命名实体识别、文本生成
- **技术栈**：NLTK + spaCy + Transformers + FastAPI
- **难度级别**：★★★★☆（进阶级）

#### 开发流程

1. **数据准备与预处理**：
   - 文本清洗与标准化
   - 分词与特征提取
   - 构建训练数据集

```python
# 文本预处理示例
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# 下载必要的NLTK资源
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

def preprocess_text(text):
    # 转换为小写
    text = text.lower()
    
    # 移除特殊字符和数字
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    
    # 分词
    tokens = word_tokenize(text)
    
    # 移除停用词
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    
    # 词形还原
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
    # 重新组合为文本
    processed_text = ' '.join(tokens)
    
    return processed_text

# 使用Transformers进行文本分类
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

def build_sentiment_analyzer():
    # 加载预训练的BERT模型和分词器
    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
    model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
    
    def analyze_sentiment(text):
        # 预处理文本
        processed_text = preprocess_text(text)
        
        # 编码文本
        inputs = tokenizer(processed_text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        
        # 预测
        with torch.no_grad():
            outputs = model(**inputs)
        
        # 获取预测结果
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        positive_score = predictions[0][1].item()
        negative_score = predictions[0][0].item()
        
        # 返回情感分析结果
        sentiment = "positive" if positive_score > negative_score else "negative"
        confidence = max(positive_score, negative_score)
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "positive_score": positive_score,
            "negative_score": negative_score
        }
    
    return analyze_sentiment
```

2. **模型构建与训练**：
   - 实现NLP模型
   - 微调预训练模型
   - 评估与优化

3. **应用开发**：
   - 构建API服务
   - 实现文本分析功能
   - 设计用户界面

#### 学习要点

- 自然语言处理技术
- 预训练模型的使用与微调
- 文本特征工程
- NLP应用设计

### 4.3 推荐系统

推荐系统项目帮助你掌握个性化推荐技术：

#### 项目概述

- **功能特点**：协同过滤、内容推荐、混合推荐、实时推荐
- **技术栈**：Pandas + Scikit-learn + Surprise + Flask + Redis
- **难度级别**：★★★★☆（进阶级）

#### 开发流程

1. **数据收集与分析**：
   - 用户行为数据收集
   - 物品特征提取
   - 数据探索分析

```python
# 协同过滤推荐系统示例
import pandas as pd
import numpy as np
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split

# 加载评分数据
ratings_data = pd.read_csv('ratings.csv')

# 创建Surprise数据集
reader = Reader(rating_scale=(1, 5))
dataset = Dataset.load_from_df(ratings_data[['user_id', 'item_id', 'rating']], reader)

# 划分训练集和测试集
trainset, testset = train_test_split(dataset, test_size=0.2)

# 构建SVD模型
model = SVD(n_factors=100, n_epochs=20, lr_all=0.005, reg_all=0.02)
model.fit(trainset)

# 预测函数
def predict_rating(user_id, item_id):
    prediction = model.predict(user_id, item_id)
    return prediction.est

# 为用户生成推荐
def get_recommendations(user_id, item_ids, n=10):
    # 为用户预测所有物品的评分
    predictions = []
    for item_id in item_ids:
        # 检查用户是否已经评价过该物品
        if not ratings_data[(ratings_data['user_id'] == user_id) & 
                           (ratings_data['item_id'] == item_id)].empty:
            continue
        
        predicted_rating = predict_rating(user_id, item_id)
        predictions.append((item_id, predicted_rating))
    
    # 按预测评分排序并返回前N个推荐
    predictions.sort(key=lambda x: x[1], reverse=True)
    return predictions[:n]
```

2. **推荐算法实现**：
   - 协同过滤算法
   - 基于内容的推荐
   - 混合推荐策略

3. **系统集成与部署**：
   - 构建推荐API
   - 实现实时推荐
   - 设计A/B测试框架

#### 学习要点

- 推荐系统原理与算法
- 用户行为分析
- 实时推荐架构
- 推荐系统评估方法

## 5. 数据科学与机器学习项目

### 5.1 预测分析系统

预测分析项目帮助你掌握数据建模与预测技术：

#### 项目概述

- **功能特点**：时间序列预测、回归分析、分类预测、异常检测
- **技术栈**：Pandas + NumPy + Scikit-learn + XGBoost + Streamlit
- **难度级别**：★★★★☆（进阶级）

#### 开发流程

1. **数据准备与特征工程**：
   - 数据收集与整合
   - 特征选择与转换
   - 处理缺失值与异常值

```python
# 特征工程示例
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

def build_preprocessing_pipeline(numeric_features, categorical_features):
    """构建数据预处理流水线"""
    # 数值特征处理：填充缺失值并标准化
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    # 类别特征处理：填充缺失值并进行独热编码
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    # 组合所有特征处理器
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    
    return preprocessor

# 时间序列特征生成
def create_time_features(df, date_column):
    """从日期列创建时间特征"""
    df = df.copy()
    df['date'] = pd.to_datetime(df[date_column])
    
    # 提取各种时间特征
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['day_of_week'] = df['date'].dt.dayofweek
    df['day_of_year'] = df['date'].dt.dayofyear
    df['quarter'] = df['date'].dt.quarter
    df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
    
    # 创建滞后特征（例如前1天、前7天的值）
    df['lag_1'] = df.sort_values('date')['target'].shift(1)
    df['lag_7'] = df.sort_values('date')['target'].shift(7)
    
    # 创建滚动窗口特征（例如过去7天的平均值）
    df['rolling_mean_7'] = df.sort_values('date')['target'].shift(1).rolling(window=7).mean()
    
    return df
```

2. **模型开发与评估**：
   - 选择合适的算法
   - 模型训练与调优
   - 交叉验证与性能评估

```python
# 模型开发与评估示例
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import ElasticNet
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb

def train_and_evaluate_models(X_train, y_train, X_test, y_test):
    """训练多个模型并评估性能"""
    # 定义要评估的模型
    models = {
        'ElasticNet': ElasticNet(random_state=42),
        'RandomForest': RandomForestRegressor(random_state=42),
        'GradientBoosting': GradientBoostingRegressor(random_state=42),
        'XGBoost': xgb.XGBRegressor(random_state=42)
    }
    
    results = {}
    
    # 训练并评估每个模型
    for name, model in models.items():
        # 交叉验证
        cv_scores = cross_val_score(model, X_train, y_train, 
                                   cv=5, scoring='neg_mean_squared_error')
        cv_rmse = np.sqrt(-cv_scores.mean())
        
        # 在完整训练集上训练
        model.fit(X_train, y_train)
        
        # 在测试集上评估
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        results[name] = {
            'cv_rmse': cv_rmse,
            'test_mae': mae,
            'test_rmse': rmse,
            'test_r2': r2,
            'model': model
        }
    
    return results

# 超参数调优
def tune_model(model, param_grid, X_train, y_train):
    """使用网格搜索进行超参数调优"""
    grid_search = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        cv=5,
        scoring='neg_mean_squared_error',
        n_jobs=-1
    )
    
    grid_search.fit(X_train, y_train)
    
    print(f"Best parameters: {grid_search.best_params_}")
    print(f"Best score: {np.sqrt(-grid_search.best_score_)}")
    
    return grid_search.best_estimator_
```

3. **系统部署与监控**：
   - 构建预测API
   - 实现模型监控
   - 设计可视化仪表板

#### 学习要点

- 特征工程技术
- 模型选择与评估
- 超参数调优
- 模型部署与监控

### 5.2 数据可视化平台

数据可视化项目帮助你掌握数据呈现与分析技术：

#### 项目概述

- **功能特点**：交互式图表、地理信息可视化、实时数据展示、自定义报表
- **技术栈**：Plotly + Dash + Pandas + Flask + PostgreSQL
- **难度级别**：★★★☆☆（中级）

#### 开发流程

1. **数据源集成**：
   - 连接多种数据源
   - 实现数据转换
   - 构建数据管道

2. **可视化组件开发**：
   - 设计交互式图表
   - 实现地图可视化
   - 构建仪表板布局

```python
# Dash应用示例
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# 加载示例数据
df = pd.read_csv('sales_data.csv')

# 初始化Dash应用
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

# 定义应用布局
app.layout = html.Div([
    html.H1("销售数据分析仪表板"),
    
    html.Div([
        html.Div([
            html.Label("选择日期范围:"),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=df['date'].min(),
                end_date=df['date'].max(),
                max_date_allowed=df['date'].max(),
                min_date_allowed=df['date'].min(),
            )
        ], className="six columns"),
        
        html.Div([
            html.Label("选择产品类别:"),
            dcc.Dropdown(
                id='category-dropdown',
                options=[{'label': cat, 'value': cat} for cat in df['category'].unique()],
                value=df['category'].unique(),
                multi=True
            )
        ], className="six columns"),
    ], className="row"),
    
    html.Div([
        html.Div([
            dcc.Graph(id='sales-time-series')
        ], className="six columns"),
        
        html.Div([
            dcc.Graph(id='category-pie-chart')
        ], className="six columns"),
    ], className="row"),
    
    html.Div([
        html.Div([
            dcc.Graph(id='region-bar-chart')
        ], className="twelve columns"),
    ], className="row"),
    
    html.Div([
        html.Div([
            dcc.Graph(id='sales-heatmap')
        ], className="twelve columns"),
    ], className="row"),
])

# 回调函数：更新时间序列图表
@app.callback(
    Output('sales-time-series', 'figure'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('category-dropdown', 'value')]
)
def update_time_series(start_date, end_date, categories):
    filtered_df = df[(df['date'] >= start_date) & 
                     (df['date'] <= end_date) & 
                     (df['category'].isin(categories))]
    
    fig = px.line(filtered_df.groupby('date')['sales'].sum().reset_index(), 
                 x='date', y='sales', title='销售额时间趋势')
    return fig

# 回调函数：更新饼图
@app.callback(
    Output('category-pie-chart', 'figure'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('category-dropdown', 'value')]
)
def update_pie_chart(start_date, end_date, categories):
    filtered_df = df[(df['date'] >= start_date) & 
                     (df['date'] <= end_date) & 
                     (df['category'].isin(categories))]
    
    category_sales = filtered_df.groupby('category')['sales'].sum().reset_index()
    fig = px.pie(category_sales, values='sales', names='category', 
                title='各类别销售额占比')
    return fig

# 启动服务器
if __name__ == '__main__':
    app.run_server(debug=True)
```

3. **用户界面与交互**：
   - 实现过滤与排序
   - 设计用户交互流程
   - 构建报表导出功能

#### 学习要点

- 数据可视化原则
- 交互式应用开发
- 前端框架使用
- 用户体验设计

## 6. DevOps与自动化项目

### 6.1 自动化测试框架

自动化测试项目帮助你掌握软件质量保障技术：

#### 项目概述

- **功能特点**：单元测试、集成测试、UI测试、性能测试
- **技术栈**：Pytest + Selenium