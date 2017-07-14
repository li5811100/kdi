#!/usr/bin/python
# -*- coding: gbk -*-
'''''
Created on 2017-7-12

@author: LiuPC, LiLW
'''
import time
import datetime
import os, sys
import os.path
import numpy
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
import csv

import argparse

#from osgeo import *

def out_date(year,day):
    fir_day = datetime.datetime(year,1,1)
    zone = datetime.timedelta(days=day-1)
    return datetime.datetime.strftime(fir_day + zone, "%Y%m%d")

def traversalDir_FirstDir(path):
    #定义一个列表，用来存储结果
    list = []
    #判断路径是否存在
    if (os.path.exists(path)):
        #获取该目录下的所有文件或文件夹目录
        files = os.listdir(path)
        for file in files:
            #得到该文件下所有目录的路径
            m = os.path.join(path,file)
            #判断该路径下是否是文件夹
            if (os.path.isdir(m)):
                h = os.path.split(m)
                #print(h[1])
                list.append(h[1])
        #print(list)
        return list
def Filefolder(path):
    for parent,dirnames,filenames in os.walk(path):
        print(dirnames)

    # 读取图像文件
def readImageRectangle(FilePathAndName):
    inDataset = gdal.Open(FilePathAndName);
    cols = inDataset.RasterXSize;
    rows = inDataset.RasterYSize;
    bands = inDataset.RasterCount;
    projection = inDataset.GetProjection();
    GeoTransform = inDataset.GetGeoTransform();
    x1 = GeoTransform[0] + 0 * GeoTransform[1] + 0 * GeoTransform[2];
    y1 = GeoTransform[3] + 0 * GeoTransform[4] + 0 * GeoTransform[5];
    x2 = GeoTransform[0] + cols * GeoTransform[1];
    y2 = GeoTransform[3] + rows * GeoTransform[5];
    ring = ogr.Geometry(ogr.wkbLinearRing);
    ring.AddPoint(x1, y1);
    ring.AddPoint(x2,y1);
    ring.AddPoint(x2, y2);
    ring.AddPoint(x1, y2);
    ring.AddPoint(x1, y1);
    # Create polygon
    poly = ogr.Geometry(ogr.wkbPolygon);
    poly.AddGeometry(ring);
    return poly;


def CreateRegionFile(FileName):
    (filepath, tempfilename) = os.path.split(FileName);
    (shotname, extension) = os.path.splitext(tempfilename);

    # 如果文件存在就删除
    if (os.path.exists(filepath + "\\" + shotname + ".dbf")):
        os.remove(filepath + "\\" + shotname + ".dbf")
    if (os.path.exists(filepath + "\\" + shotname + ".prj")):
        os.remove(filepath + "\\" + shotname + ".prj")
    if (os.path.exists(filepath + "\\" + shotname + ".shp")):
        os.remove(filepath + "\\" + shotname + ".shp")
    if (os.path.exists(filepath + "\\" + shotname + ".shx")):
        os.remove(filepath + "\\" + shotname + ".shx")
        # 结束
    # 为了支持中文路径，请添加下面这句代码
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    # 为了使属性表字段支持中文，请添加下面这句
    gdal.SetConfigOption("SHAPE_ENCODING", "CP936")
    # 注册所有的驱动
    ogr.RegisterAll()
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.CreateDataSource(filepath)
    shapLayer = ds.CreateLayer(shotname, geom_type=ogr.wkbPolygon);
    # 添加字段1（唯一编码）
    fieldDefn1 = ogr.FieldDefn('id', ogr.OFTString)
    fieldDefn1.SetWidth(4)
    shapLayer.CreateField(fieldDefn1);
    # 添加字段2 （传感器类型）
    fieldDefn2 = ogr.FieldDefn('SensorType', ogr.OFTString)
    fieldDefn2.SetWidth(20)
    shapLayer.CreateField(fieldDefn2);
    # 添加字段3 （文件名称）
    fieldDefn3 = ogr.FieldDefn('FileName', ogr.OFTString)
    fieldDefn3.SetWidth(40)
    shapLayer.CreateField(fieldDefn3);
    # 添加字段4 （产品级别）
    fieldDefn4 = ogr.FieldDefn('Level', ogr.OFTString)
    shapLayer.CreateField(fieldDefn4);
    # 添加字段5 （日期：年月日）
    fieldDefn5 = ogr.FieldDefn('Date', ogr.OFTString)
    shapLayer.CreateField(fieldDefn5);
    # 添加字段6 （文件路径）
    fieldDefn6 = ogr.FieldDefn('FilePath', ogr.OFTString)
    fieldDefn6.SetWidth(50)
    shapLayer.CreateField(fieldDefn6);
    # 指定投影
    sr = osr.SpatialReference();
    sr.ImportFromEPSG(32650);
    prjFile = open(filepath + "\\" + shotname + ".prj", 'w');
    sr.MorphToESRI();
    prjFile.write(sr.ExportToWkt());
    prjFile.close();
    ds.Destroy()

def WriteRegionIntoShape(ShapeFileNameAndPath,polygon,id,SensorType,FileName,Level,Date,FilePath):
    # 为了支持中文路径，请添加下面这句代码
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    # 为了使属性表字段支持中文，请添加下面这句
    gdal.SetConfigOption("SHAPE_ENCODING", "CP936")
    # 注册所有的驱动
    ogr.RegisterAll()
    # 数据格式的驱动
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.Open(ShapeFileNameAndPath, True);
    shapLayer = ds.GetLayerByIndex(0);
    defn = shapLayer.GetLayerDefn();
    feature = ogr.Feature(defn);
    # 添加属性
    feature.SetField("id", id);
    feature.SetField("SensorType", SensorType);
    feature.SetField("FileName", FileName);
    feature.SetField("Level", Level);
    feature.SetField("Date", Date);
    feature.SetField("FilePath", FilePath);
    feature.SetGeometry(polygon);
    shapLayer.CreateFeature(feature);
    feature.Destroy();
    ds.Destroy();

#判断文件的后缀
def endWith(s, *endstring):
    array = map(s.endswith, endstring)
    if True in array:
        return True
    else:
        return False

#在CSV文件中添加内容
def AddInfoIntoCSV(CSVfileNameAndPath,id, SensorType, FileName, Level, Date, FilePath):
    csvfile=open(CSVfileNameAndPath, "a",newline='')
    writer = csv.writer(csvfile)
    writer.writerow([id, SensorType, FileName, Level, Date, FilePath])
    csvfile.close()

#创建CSV文件
def CreateCSVFile(File_Path_and_Name):
    with open(File_Path_and_Name, 'w',newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Id', 'Sensor', 'Name', 'Level', 'Date', 'Path'])
    csvfile.close()

#求两个要素的交集
def IsOverLayer(polygon1,polygon2):
    intersection = polygon1.Intersection(polygon2)
    area1=polygon1.GetArea()
    area2=intersection.GetArea()
    if(area2>0.5*area1):
        return True;
    else:
        return False;

#遍历解译文件,fullPathAndFile指文件解译文件的总路径，ShapeFileNameAndPath是生成解译后SHAPEFILE文件一览表（包括路径和文件名）
#CSVfileNameAndPath是生成解译后CSV文件一览表（包括路径和文件名）
def GoThroughFilePath(fullPathAndFile,ShapeFileNameAndPath,CSVfileNameAndPath):
    CreateRegionFile(ShapeFileNameAndPath);
    CreateCSVFile(CSVfileNameAndPath);
    i = 0;
    FileName = "";
    level = "1";
    Date = "2013-10-10";
    FilePath = "";
    list = traversalDir_FirstDir(fullPathAndFile)
    for item1 in list:
        SensorType = item1;
        if SensorType != 'GF5-SIMU':
            print('not a proper sensorType!!!')
            print("only GF5-SIMU is supported now!!!")
            exit(-1)
        list1 = traversalDir_FirstDir(fullPathAndFile + '\\' + item1)
        for item2 in list1:
            list2 = traversalDir_FirstDir(fullPathAndFile + '\\' + item1+'\\'+item2)  #
            for item3 in list2:
                # id.append(i);
                FileName = item3;

                if SensorType == 'GF5-SIMU':
                    Date=out_date(int(item3[20:24]), int(item3[24:27]));
                else:
                    print("only GF5-SIMU is supported now!!!")
                    exit(-1)

                Level = '';
                isImage=False;
                isShp = False;
                FilePath = fullPathAndFile + '\\' + item1 + '\\' + item2 + '\\' + item3;
                list4 = os.listdir(fullPathAndFile + '\\' + item1 + '\\' + item2 + '\\'+item3)
                for item4 in list4:
                    tempPath=fullPathAndFile + '\\' + item1 + '\\' + item2 + '\\'+item3+ '\\' + item4;
                    list5 = os.listdir(tempPath)
                    for item5 in list5:
                        if item4 == 'shp':
                            FilePathAndName = tempPath + '\\' + item5
                            if os.path.isfile(FilePathAndName):
                                if endWith(FilePathAndName, '.shp', '.SHP'):
                                    if isShp == False:  # 第一次就获取范围，后面就不获取了;
                                        isShp = True;
                        else:
                            list6 = os.listdir(tempPath + '\\' + item5);
                            for item6 in list6:
                                FilePathAndName=tempPath + '\\' + item5 +'\\'+item6;
                                if os.path.isfile(FilePathAndName):
                                    if endWith(FilePathAndName, '.tif', '.TIF'):
                                        Level=Level+item5;
                                        if isImage==False:   #第一次就获取范围，后面就不获取了
                                            polygon = readImageRectangle(FilePathAndName);
                                            isImage=True;
                                            # print("dd/mm/yyyy 格式是  %s/%s/%s" % (Date.day, Date.month,Date.year)
                                            #break;
                if not isShp:
                    print("Warning: no shapefile is found in the " + FilePath)

                if isImage:
                    id = i;
                    i = i + 1;
                    FilePath = fullPathAndFile + '\\' + item1 + '\\' + item2 + '\\' + item3;
                    WriteRegionIntoShape(ShapeFileNameAndPath, polygon, id, SensorType, FileName, Level, Date,FilePath);
                    AddInfoIntoCSV(CSVfileNameAndPath, id, SensorType, FileName, Level, Date, FilePath)
                else:
                    print("Warning: no image is found in the " + FilePath)


#查询的结果，按类别生成shapefile文件（该文件不含数据）
def BuildingSortShapefile(FileName):
    (filepath, tempfilename) = os.path.split(FileName);
    (shotname, extension) = os.path.splitext(tempfilename);

    #如果文件存在就删除
    if (os.path.exists(filepath+"\\"+shotname+".dbf")):
        os.remove(filepath+"\\"+shotname+".dbf")
    if (os.path.exists(filepath+"\\"+shotname+".prj")):
        os.remove(filepath+"\\"+shotname+".prj")
    if (os.path.exists(filepath+"\\"+shotname+".shp")):
        os.remove(filepath+"\\"+shotname+".shp")
    if (os.path.exists(filepath+"\\"+shotname+".shx")):
        os.remove(filepath+"\\"+shotname+".shx")
    #结束

    # 为了支持中文路径，请添加下面这句代码
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    # 为了使属性表字段支持中文，请添加下面这句
    gdal.SetConfigOption("SHAPE_ENCODING", "CP936")

    # 注册所有的驱动
    ogr.RegisterAll()
    driver = ogr.GetDriverByName('ESRI Shapefile')

    ds = driver.CreateDataSource(filepath)
    shapLayer = ds.CreateLayer(shotname, geom_type=ogr.wkbPolygon);
    # 添加字段1（类别编号）
    fieldDefn1 = ogr.FieldDefn('类别编号', ogr.OFTString)
    fieldDefn1.SetWidth(50)
    shapLayer.CreateField(fieldDefn1);
    # 添加字段2 （类别名称）
    fieldDefn2 = ogr.FieldDefn('类别名称', ogr.OFTString)
    fieldDefn2.SetWidth(50)
    shapLayer.CreateField(fieldDefn2);
    # 添加字段3 （子类编号）
    fieldDefn3 = ogr.FieldDefn('子类编号', ogr.OFTString)
    fieldDefn3.SetWidth(50)
    shapLayer.CreateField(fieldDefn3);
    # 添加字段4 （子类名称）
    fieldDefn4 = ogr.FieldDefn('子类名称', ogr.OFTString)
    shapLayer.CreateField(fieldDefn4);
    # 指定投影
    sr = osr.SpatialReference();
    sr.ImportFromEPSG(32650);
    prjFile = open(filepath+"\\"+shotname+".prj", 'w');
    sr.MorphToESRI();
    prjFile.write(sr.ExportToWkt());
    prjFile.close();
    ds.Destroy()

#在源文件中添加查询的要素
def CopyFeatureIntoShapefile(SourceNameFile,TargetNameFile,type,name):
    # 为了支持中文路径，请添加下面这句代码
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    # 为了使属性表字段支持中文，请添加下面这句
    gdal.SetConfigOption("SHAPE_ENCODING", "CP936")
    # 注册所有的驱动
    ogr.RegisterAll()
    ###################################################################
    driver1 = ogr.GetDriverByName('ESRI Shapefile')
    ds1 = driver1.Open(TargetNameFile, True);
    shapLayer1 = ds1.GetLayerByIndex(0);
    defn1 = shapLayer1.GetLayerDefn();
    ###################################################################
    # 数据格式的驱动
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.Open(SourceNameFile);
    if ds is None:
        print('Could not open'+SourceNameFile)
        sys.exit(1)
        # 获取第0个图层
    layer0 = ds.GetLayerByIndex(0);
    defn = layer0.GetLayerDefn()
    iFieldCount = defn.GetFieldCount()
    feature = layer0.GetNextFeature()
    # 下面开始遍历图层中的要素
    while feature is not None:
        # 获取要素中的属性表内容
        ##################写入########################
        feature1 = ogr.Feature(defn1);
        feature1.SetField("类别编号", type);
        feature1.SetField("类别名称", name);
        ###############################################
        for index in range(iFieldCount):
            if feature.IsFieldSet(index):
                oField = defn.GetFieldDefn(index)
                fieldName = oField.GetName();
                #print(fieldName)
                value =feature.GetField(index);
                #print(value)
                #################写入#######################
                if fieldName == "类别编号":
                    feature1.SetField("子类编号", value);
                if fieldName == "类别名称":
                    feature1.SetField("子类名称", value);
                ############################################
        geometry = feature.GetGeometryRef()
        ####################写入######################
        feature1.SetGeometry(geometry);
        shapLayer1.CreateFeature(feature1);
        feature1.Destroy();
        ##############################################
        feature = layer0.GetNextFeature()

    #feature.Destroy()
    ds.Destroy()
    ds1.Destroy()

def GetLevelNo(levelInStr):
    levelInNo = 0
    if levelInStr == "DN":
        levelInNo = '1'
    if levelInStr == "RAD":
        levelInNo = '2'
    if levelInStr == "TOA":
        levelInNo = '3'
    if levelInStr == "TOC":
        levelInNo = '4'
    return levelInNo

def GetLevelStr(levelInNo):
    GetLevelStr = 0
    if levelInNo == "1":
        GetLevelStr = 'DN'
    if levelInNo == "2":
        GetLevelStr = 'RAD'
    if levelInNo == "3":
        GetLevelStr = 'TOA'
    if levelInNo == "4":
        GetLevelStr = 'TOC'
    return GetLevelStr

def ReadQueryFile(FullPathandName):
    Sensor=""
    Date=""
    Hierarchy=""
    x1=0.0
    y1=0.0
    x2=0.0
    y2=0.0
    x3=0.0
    y3=0.0
    x4=0.0
    y4=0.0
    print("Searching based on input image:")
    collection=[]
    f = open(FullPathandName, "r")
    line = f.readline()
    sensorInList = line.split()
    sensor = sensorInList[0]
    print("sensor = " + sensor)
    line = f.readline()
    dateInList = line.split()
    date = dateInList[0];
    print("date = " + date)
    line = f.readline()
    levelInList = line.split()
    level = GetLevelNo(levelInList[0])
    print("level = " + GetLevelStr(level))
    line = f.readline()
    (x1,y1)=line.split()
    print("LT = " + x1 + ' ' + y1)
    line = f.readline()
    (x2, y2) = line.split()
    print("RT = " + x2 + ' '+ y2)
    line = f.readline()
    (x3, y3) = line.split()
    print("RB = " + x3 + ' ' + y3)
    line = f.readline()
    (x4, y4) = line.split()
    print("LB = " + x4 + ' ' + y4)

    line = f.readline()  # 调用文件的 readline()方法
    while line:
        classDescription=line.split()
        collection.append(classDescription)
        line = f.readline()
    f.close()
    #collection.pop();
    return(sensor,date,x1,y1,x2,y2,x3,y3,x4,y4,level,collection)  #返回待处理数据的获取日期、四点范围、处理级别、类别体系描述

def outshapefile(target,SearchPath,File,subtype,type,name):
    notExisted=False;
    BuildingSortShapefile(target); #建立目标文件
    for i in range(len(subtype)): #将子类文件的要素一个一个拷贝到目标文件中
        Shape_Path_and_File=SearchPath+"\\"+"shp"+"\\"+File+"_"+subtype[i]+".shp"
        if (os.path.exists(Shape_Path_and_File)):
            CopyFeatureIntoShapefile(Shape_Path_and_File,target,type,name)
        else:
            notExisted = True;
            print("\nError : the targeted source image do not have ",subtype[i], " in its shapefile")

    if notExisted==True:
        exit(1)



def SensorSearch(sensor,SourceNameFile):
    # 为了支持中文路径，请添加下面这句代码
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    # 为了使属性表字段支持中文，请添加下面这句
    gdal.SetConfigOption("SHAPE_ENCODING", "CP936")
    # 注册所有的驱动
    ogr.RegisterAll()
    isSearch = False;  # 是否找到了匹配的结果
    indexList = [];
    # 数据格式的驱动
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.Open(SourceNameFile);
    if ds is None:
        print('Could not open' + SourceNameFile)
        sys.exit(1)
    # 获取第0个图层
    layer = ds.GetLayerByIndex(0);
    feature = layer.GetNextFeature()
    # 下面开始遍历图层中的要素
    index = 0;
    while feature is not None:
        featureSensor = feature.GetField(1);
        if featureSensor == sensor:
            isSearch=True;
            indexList.append(index);
        feature = layer.GetNextFeature()
        index +=1;
    ds.Destroy()
    return (isSearch,indexList)


def SpatialSearch(x1, y1, x2, y2, x3, y3, x4, y4,indexListSensor,SourceNameFile):
    # 为了支持中文路径，请添加下面这句代码
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    # 为了使属性表字段支持中文，请添加下面这句
    gdal.SetConfigOption("SHAPE_ENCODING", "CP936")
    # 注册所有的驱动
    ogr.RegisterAll()
    isSearch = False;  # 是否找到了匹配的结果
    indexList = [];

    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint((float)(x1), (float)(y1));
    ring.AddPoint((float)(x2), (float)(y2));
    ring.AddPoint((float)(x3), (float)(y3));
    ring.AddPoint((float)(x4), (float)(y4));
    ring.AddPoint((float)(x1), (float)(y1));
    # Create polygon
    poly = ogr.Geometry(ogr.wkbPolygon);
    poly.AddGeometry(ring)

    # 数据格式的驱动
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.Open(SourceNameFile);
    if ds is None:
        print('Could not open' + SourceNameFile)
        sys.exit(1)
    # 获取第0个图层
    layer = ds.GetLayerByIndex(0);

    # 逐个遍历indexListSpatial
    for i in range(len(indexListSensor)):
        index = indexListSensor[i];
        feature = layer.GetFeature(index)
        featureDate = feature.GetField(4)
        if feature is not None:
            geometry = feature.GetGeometryRef()
            if IsOverLayer(poly, geometry):
                isSearch = True;
                indexList.append(index);
    ds.Destroy()
    return (isSearch,indexList)

def DateSearch(date, indexListSpatial, SourceNameFile):
    # 为了支持中文路径，请添加下面这句代码
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    # 为了使属性表字段支持中文，请添加下面这句
    gdal.SetConfigOption("SHAPE_ENCODING", "CP936")
    # 注册所有的驱动
    ogr.RegisterAll();
    # 数据格式的驱动
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.Open(SourceNameFile);
    if ds is None:
        print('Could not open' + SourceNameFile)
        sys.exit(1)

    layer = ds.GetLayerByIndex(0);
    pos = 0
    det = 0;
    # 逐个遍历indexListSpatial
    for i in range(len(indexListSpatial)):
        index = indexListSpatial[i];
        feature = layer.GetFeature(index)
        featureDate = feature.GetField(4)
        year = date[0:4];
        month = date[4:6];
        day = date[6:8];
        d1 = datetime.datetime((int)(year), (int)(month), (int)(day))
        d2 = datetime.datetime(int(featureDate[0:4]), int(featureDate[4:6]), int(featureDate[6:8]))
        if i == 0:
            det = abs((d1 - d2).days);
            pos = 0;
            level = feature.GetField(3);
            path = feature.GetField(5);
            file = feature.GetField(2);
        else:
            det1 = abs((d1 - d2).days);
            if det1 <= det:
                det = det1;
                pos = index;
                level = feature.GetField(3);
                path = feature.GetField(5);
                file = feature.GetField(2);
    ds.Destroy()
    return (path,file,level)



# ShapeFileNameAndPath:前面文件生成的一览表SHAPEFILE文件，FullPathandName索引文件所在的路径，ResultPath生成结果所在的路径
def getSearchResult(ShapeFileNameAndPath,FullPathandName,ResultPath):
    (sensor,date, x1, y1, x2, y2, x3, y3, x4, y4, level,collection) = ReadQueryFile(FullPathandName);

    (isSearchSensor, indexListSensor) = SensorSearch(sensor, ShapeFileNameAndPath);
    if isSearchSensor == False:
        print("\nError: no source image from " + sensor + " is found !!!")
        return;

    (isSearchSpatial, indexListSpatial) = SpatialSearch(x1, y1, x2, y2, x3, y3, x4, y4, indexListSensor,ShapeFileNameAndPath);
    if isSearchSpatial == False:
        print("\nError: no source image within the spatial range is found !!!")
        return;

    (sourcePath,sourceFile,sourceLevel) = DateSearch(date, indexListSpatial, ShapeFileNameAndPath)  # 找到时间最近的解译结果

    if level in sourceLevel:
        list = os.listdir(sourcePath + "\\sou\\" + level);
        for item in list:
            FilePathAndName = sourcePath+ "\\sou\\" + level + '\\' + item;
            if os.path.isfile(FilePathAndName):
                if endWith(FilePathAndName, '.tif', '.TIF'):
                    sourceFullPath = FilePathAndName;
                    break;
    else:
        print("\nError: the selected source image do not include level " + level + " product !!!")
        return;

    for i in range(len(collection)):
        description = collection[i];
        # des=desciption.split()
        type = description[0]
        name = description[1]
        subtype = []
        for j in range(len(description)):
            if j > 1:
                subtype.append(description[j])
        outshapefile(ResultPath + type + ".shp", sourcePath, sourceFile, subtype,type,name);

    print("\nsearching is done!")

    print("targeted source image is " + sourceFullPath + "!!")

def statisticsKDI(kdPath):
    GoThroughFilePath(kdPath, kdPath+"\\statistics.shp",kdPath+"\\statistics.csv")
    print("statistics of KB is successfully updated!\n")

def searchKDI(kdPath,searchFile,dstPath):
    statisticsKDI(kdPath)
    kbstaDir = kdPath+"\\statistics.shp"
    getSearchResult(kbstaDir,searchFile,dstPath)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--kdPath", type=str, default='G:\\WRD_DATA_20161010\\KB', help="path to the kd root")
    parser.add_argument("--searchFile", type=str, default="G:\\WRD_DATA_20161010\\VALIDATION\\search\\Search.txt", help="full path to the search file")
    parser.add_argument("--dstPath", type=str, default="G:\\WRD_DATA_20161010\\VALIDATION\\search\\", help="path including the built shp")
    args = parser.parse_args()
    searchKDI(args.kdPath,args.searchFile,args.dstPath)

#http://pcjericks.github.io/py-gdalogr-cookbook/geometry.html
#https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html