# 机械图纸特征信息智能提取分析系统

该项目为机械图纸特征信息智能提取分析系统的代码备份

# 技术路线

获取图纸 → 
文本检测（CRAFT）→ 
检测结果后处理 → 
制作图纸数据集  →  
训练模型进行文本识别（ResNet + BiLSTM + CTC） → 
识别结果导出（Excel）→ 
针对轴类进行特征匹配 → 
以加工工艺为导向输出工艺清单（Excel）

![image](https://user-images.githubusercontent.com/81545188/126886332-339ad9b9-35fc-4436-98bc-cccc1cac6a75.png)




# 当前进度

获取图纸 √
文本检测（CRAFT）√
检测结果后处理 √
制作图纸数据集  √ 
训练模型进行文本识别（ResNet + BiLSTM + CTC） √
识别结果导出（Excel）√
针对轴类进行特征匹配 进行中…… 



# Acknowledgement and References


深度学习平台：[Pytorch](https://pytorch.org/)
文本检测模型：[CRAFT](https://github.com/clovaai/CRAFT-pytorch), 文本识别框架：[deep-text-recognition-benchmark](https://github.com/clovaai/deep-text-recognition-benchmark)

