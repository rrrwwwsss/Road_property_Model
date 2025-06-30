# 只是更新镜像里的代码
FROM htc/highway_property:250606

# 替换模型代码目录（用新的代码覆盖旧的）
COPY road_property_rightsmodel/ /app/road_property_rightsmodel/

WORKDIR /app/road_property_rightsmodel
CMD ["python", "main.py"]
