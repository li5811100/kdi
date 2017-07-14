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
    #����һ���б������洢���
    list = []
    #�ж�·���Ƿ����
    if (os.path.exists(path)):
        #��ȡ��Ŀ¼�µ������ļ����ļ���Ŀ¼
        files = os.listdir(path)
        for file in files:
            #�õ����ļ�������Ŀ¼��·��
            m = os.path.join(path,file)
            #�жϸ�·�����Ƿ����ļ���
            if (os.path.isdir(m)):
                h = os.path.split(m)
                #print(h[1])
                list.append(h[1])
        #print(list)
        return list
def Filefolder(path):
    for parent,dirnames,filenames in os.walk(path):
        print(dirnames)

    # ��ȡͼ���ļ�
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

    # ����ļ����ھ�ɾ��
    if (os.path.exists(filepath + "\\" + shotname + ".dbf")):
        os.remove(filepath + "\\" + shotname + ".dbf")
    if (os.path.exists(filepath + "\\" + shotname + ".prj")):
        os.remove(filepath + "\\" + shotname + ".prj")
    if (os.path.exists(filepath + "\\" + shotname + ".shp")):
        os.remove(filepath + "\\" + shotname + ".shp")
    if (os.path.exists(filepath + "\\" + shotname + ".shx")):
        os.remove(filepath + "\\" + shotname + ".shx")
        # ����
    # Ϊ��֧������·�������������������
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    # Ϊ��ʹ���Ա��ֶ�֧�����ģ�������������
    gdal.SetConfigOption("SHAPE_ENCODING", "CP936")
    # ע�����е�����
    ogr.RegisterAll()
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.CreateDataSource(filepath)
    shapLayer = ds.CreateLayer(shotname, geom_type=ogr.wkbPolygon);
    # ����ֶ�1��Ψһ���룩
    fieldDefn1 = ogr.FieldDefn('id', ogr.OFTString)
    fieldDefn1.SetWidth(4)
    shapLayer.CreateField(fieldDefn1);
    # ����ֶ�2 �����������ͣ�
    fieldDefn2 = ogr.FieldDefn('SensorType', ogr.OFTString)
    fieldDefn2.SetWidth(20)
    shapLayer.CreateField(fieldDefn2);
    # ����ֶ�3 ���ļ����ƣ�
    fieldDefn3 = ogr.FieldDefn('FileName', ogr.OFTString)
    fieldDefn3.SetWidth(40)
    shapLayer.CreateField(fieldDefn3);
    # ����ֶ�4 ����Ʒ����
    fieldDefn4 = ogr.FieldDefn('Level', ogr.OFTString)
    shapLayer.CreateField(fieldDefn4);
    # ����ֶ�5 �����ڣ������գ�
    fieldDefn5 = ogr.FieldDefn('Date', ogr.OFTString)
    shapLayer.CreateField(fieldDefn5);
    # ����ֶ�6 ���ļ�·����
    fieldDefn6 = ogr.FieldDefn('FilePath', ogr.OFTString)
    fieldDefn6.SetWidth(50)
    shapLayer.CreateField(fieldDefn6);
    # ָ��ͶӰ
    sr = osr.SpatialReference();
    sr.ImportFromEPSG(32650);
    prjFile = open(filepath + "\\" + shotname + ".prj", 'w');
    sr.MorphToESRI();
    prjFile.write(sr.ExportToWkt());
    prjFile.close();
    ds.Destroy()

def WriteRegionIntoShape(ShapeFileNameAndPath,polygon,id,SensorType,FileName,Level,Date,FilePath):
    # Ϊ��֧������·�������������������
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    # Ϊ��ʹ���Ա��ֶ�֧�����ģ�������������
    gdal.SetConfigOption("SHAPE_ENCODING", "CP936")
    # ע�����е�����
    ogr.RegisterAll()
    # ���ݸ�ʽ������
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.Open(ShapeFileNameAndPath, True);
    shapLayer = ds.GetLayerByIndex(0);
    defn = shapLayer.GetLayerDefn();
    feature = ogr.Feature(defn);
    # �������
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

#�ж��ļ��ĺ�׺
def endWith(s, *endstring):
    array = map(s.endswith, endstring)
    if True in array:
        return True
    else:
        return False

#��CSV�ļ����������
def AddInfoIntoCSV(CSVfileNameAndPath,id, SensorType, FileName, Level, Date, FilePath):
    csvfile=open(CSVfileNameAndPath, "a",newline='')
    writer = csv.writer(csvfile)
    writer.writerow([id, SensorType, FileName, Level, Date, FilePath])
    csvfile.close()

#����CSV�ļ�
def CreateCSVFile(File_Path_and_Name):
    with open(File_Path_and_Name, 'w',newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Id', 'Sensor', 'Name', 'Level', 'Date', 'Path'])
    csvfile.close()

#������Ҫ�صĽ���
def IsOverLayer(polygon1,polygon2):
    intersection = polygon1.Intersection(polygon2)
    area1=polygon1.GetArea()
    area2=intersection.GetArea()
    if(area2>0.5*area1):
        return True;
    else:
        return False;

#���������ļ�,fullPathAndFileָ�ļ������ļ�����·����ShapeFileNameAndPath�����ɽ����SHAPEFILE�ļ�һ��������·�����ļ�����
#CSVfileNameAndPath�����ɽ����CSV�ļ�һ��������·�����ļ�����
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
                                    if isShp == False:  # ��һ�ξͻ�ȡ��Χ������Ͳ���ȡ��;
                                        isShp = True;
                        else:
                            list6 = os.listdir(tempPath + '\\' + item5);
                            for item6 in list6:
                                FilePathAndName=tempPath + '\\' + item5 +'\\'+item6;
                                if os.path.isfile(FilePathAndName):
                                    if endWith(FilePathAndName, '.tif', '.TIF'):
                                        Level=Level+item5;
                                        if isImage==False:   #��һ�ξͻ�ȡ��Χ������Ͳ���ȡ��
                                            polygon = readImageRectangle(FilePathAndName);
                                            isImage=True;
                                            # print("dd/mm/yyyy ��ʽ��  %s/%s/%s" % (Date.day, Date.month,Date.year)
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


#��ѯ�Ľ�������������shapefile�ļ������ļ��������ݣ�
def BuildingSortShapefile(FileName):
    (filepath, tempfilename) = os.path.split(FileName);
    (shotname, extension) = os.path.splitext(tempfilename);

    #����ļ����ھ�ɾ��
    if (os.path.exists(filepath+"\\"+shotname+".dbf")):
        os.remove(filepath+"\\"+shotname+".dbf")
    if (os.path.exists(filepath+"\\"+shotname+".prj")):
        os.remove(filepath+"\\"+shotname+".prj")
    if (os.path.exists(filepath+"\\"+shotname+".shp")):
        os.remove(filepath+"\\"+shotname+".shp")
    if (os.path.exists(filepath+"\\"+shotname+".shx")):
        os.remove(filepath+"\\"+shotname+".shx")
    #����

    # Ϊ��֧������·�������������������
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    # Ϊ��ʹ���Ա��ֶ�֧�����ģ�������������
    gdal.SetConfigOption("SHAPE_ENCODING", "CP936")

    # ע�����е�����
    ogr.RegisterAll()
    driver = ogr.GetDriverByName('ESRI Shapefile')

    ds = driver.CreateDataSource(filepath)
    shapLayer = ds.CreateLayer(shotname, geom_type=ogr.wkbPolygon);
    # ����ֶ�1������ţ�
    fieldDefn1 = ogr.FieldDefn('�����', ogr.OFTString)
    fieldDefn1.SetWidth(50)
    shapLayer.CreateField(fieldDefn1);
    # ����ֶ�2 ��������ƣ�
    fieldDefn2 = ogr.FieldDefn('�������', ogr.OFTString)
    fieldDefn2.SetWidth(50)
    shapLayer.CreateField(fieldDefn2);
    # ����ֶ�3 �������ţ�
    fieldDefn3 = ogr.FieldDefn('������', ogr.OFTString)
    fieldDefn3.SetWidth(50)
    shapLayer.CreateField(fieldDefn3);
    # ����ֶ�4 ���������ƣ�
    fieldDefn4 = ogr.FieldDefn('��������', ogr.OFTString)
    shapLayer.CreateField(fieldDefn4);
    # ָ��ͶӰ
    sr = osr.SpatialReference();
    sr.ImportFromEPSG(32650);
    prjFile = open(filepath+"\\"+shotname+".prj", 'w');
    sr.MorphToESRI();
    prjFile.write(sr.ExportToWkt());
    prjFile.close();
    ds.Destroy()

#��Դ�ļ�����Ӳ�ѯ��Ҫ��
def CopyFeatureIntoShapefile(SourceNameFile,TargetNameFile,type,name):
    # Ϊ��֧������·�������������������
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    # Ϊ��ʹ���Ա��ֶ�֧�����ģ�������������
    gdal.SetConfigOption("SHAPE_ENCODING", "CP936")
    # ע�����е�����
    ogr.RegisterAll()
    ###################################################################
    driver1 = ogr.GetDriverByName('ESRI Shapefile')
    ds1 = driver1.Open(TargetNameFile, True);
    shapLayer1 = ds1.GetLayerByIndex(0);
    defn1 = shapLayer1.GetLayerDefn();
    ###################################################################
    # ���ݸ�ʽ������
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.Open(SourceNameFile);
    if ds is None:
        print('Could not open'+SourceNameFile)
        sys.exit(1)
        # ��ȡ��0��ͼ��
    layer0 = ds.GetLayerByIndex(0);
    defn = layer0.GetLayerDefn()
    iFieldCount = defn.GetFieldCount()
    feature = layer0.GetNextFeature()
    # ���濪ʼ����ͼ���е�Ҫ��
    while feature is not None:
        # ��ȡҪ���е����Ա�����
        ##################д��########################
        feature1 = ogr.Feature(defn1);
        feature1.SetField("�����", type);
        feature1.SetField("�������", name);
        ###############################################
        for index in range(iFieldCount):
            if feature.IsFieldSet(index):
                oField = defn.GetFieldDefn(index)
                fieldName = oField.GetName();
                #print(fieldName)
                value =feature.GetField(index);
                #print(value)
                #################д��#######################
                if fieldName == "�����":
                    feature1.SetField("������", value);
                if fieldName == "�������":
                    feature1.SetField("��������", value);
                ############################################
        geometry = feature.GetGeometryRef()
        ####################д��######################
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

    line = f.readline()  # �����ļ��� readline()����
    while line:
        classDescription=line.split()
        collection.append(classDescription)
        line = f.readline()
    f.close()
    #collection.pop();
    return(sensor,date,x1,y1,x2,y2,x3,y3,x4,y4,level,collection)  #���ش��������ݵĻ�ȡ���ڡ��ĵ㷶Χ�������������ϵ����

def outshapefile(target,SearchPath,File,subtype,type,name):
    notExisted=False;
    BuildingSortShapefile(target); #����Ŀ���ļ�
    for i in range(len(subtype)): #�������ļ���Ҫ��һ��һ��������Ŀ���ļ���
        Shape_Path_and_File=SearchPath+"\\"+"shp"+"\\"+File+"_"+subtype[i]+".shp"
        if (os.path.exists(Shape_Path_and_File)):
            CopyFeatureIntoShapefile(Shape_Path_and_File,target,type,name)
        else:
            notExisted = True;
            print("\nError : the targeted source image do not have ",subtype[i], " in its shapefile")

    if notExisted==True:
        exit(1)



def SensorSearch(sensor,SourceNameFile):
    # Ϊ��֧������·�������������������
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    # Ϊ��ʹ���Ա��ֶ�֧�����ģ�������������
    gdal.SetConfigOption("SHAPE_ENCODING", "CP936")
    # ע�����е�����
    ogr.RegisterAll()
    isSearch = False;  # �Ƿ��ҵ���ƥ��Ľ��
    indexList = [];
    # ���ݸ�ʽ������
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.Open(SourceNameFile);
    if ds is None:
        print('Could not open' + SourceNameFile)
        sys.exit(1)
    # ��ȡ��0��ͼ��
    layer = ds.GetLayerByIndex(0);
    feature = layer.GetNextFeature()
    # ���濪ʼ����ͼ���е�Ҫ��
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
    # Ϊ��֧������·�������������������
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    # Ϊ��ʹ���Ա��ֶ�֧�����ģ�������������
    gdal.SetConfigOption("SHAPE_ENCODING", "CP936")
    # ע�����е�����
    ogr.RegisterAll()
    isSearch = False;  # �Ƿ��ҵ���ƥ��Ľ��
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

    # ���ݸ�ʽ������
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.Open(SourceNameFile);
    if ds is None:
        print('Could not open' + SourceNameFile)
        sys.exit(1)
    # ��ȡ��0��ͼ��
    layer = ds.GetLayerByIndex(0);

    # �������indexListSpatial
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
    # Ϊ��֧������·�������������������
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    # Ϊ��ʹ���Ա��ֶ�֧�����ģ�������������
    gdal.SetConfigOption("SHAPE_ENCODING", "CP936")
    # ע�����е�����
    ogr.RegisterAll();
    # ���ݸ�ʽ������
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.Open(SourceNameFile);
    if ds is None:
        print('Could not open' + SourceNameFile)
        sys.exit(1)

    layer = ds.GetLayerByIndex(0);
    pos = 0
    det = 0;
    # �������indexListSpatial
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



# ShapeFileNameAndPath:ǰ���ļ����ɵ�һ����SHAPEFILE�ļ���FullPathandName�����ļ����ڵ�·����ResultPath���ɽ�����ڵ�·��
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

    (sourcePath,sourceFile,sourceLevel) = DateSearch(date, indexListSpatial, ShapeFileNameAndPath)  # �ҵ�ʱ������Ľ�����

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