#!/usr/bin/env python
#coding=utf-8

import sys;
import os;
import re;
from HHBlockVo import HHBlockVo

__author__ = 'hanhan'

class HHCheckBlockClass(object):
    """docstring for CodeStandard  实现了 遍历查找 工程中 自我实现 block 中 使用self 的错误，每个block 中只查找一处，现在 出去了部分系统block（动画block）"""

    def trim(self,docstring):
        if not docstring:
            return ''
        #expandtabs() 把tab 替换成‘’ splitlines()按换行分隔
        lines = docstring.expandtabs().splitlines()
        #int支持的最大值，溢出校验
        indent = sys.maxint
        for line in lines[1:]:
            #lstrip()去除头部空格知道不是空格
            stripped = line.lstrip()
            if stripped:
                indent = min(indent, len(line) - len(stripped))
        
        trimmed = [lines[0].strip()]
        if indent < sys.maxint:
            for line in lines[1:]:
                trimmed.append(line[indent:].rstrip())
        while trimmed and not trimmed[-1]:
            trimmed.pop()
        while trimmed and not trimmed[0]:
            trimmed.pop(0)
        return '\n'.join(trimmed);

    def checkFileNamee(self,filename):
        if os.path.isdir(filename):
            if not filename.endswith('/'):
                filename += '/';
            for file in os.listdir(filename):
                if os.path.isdir(filename + file):
                    self.checkFileNamee(filename + file);
                else:
                    self.checkFileLinee(filename + file);
        else :
            self.checkFileLinee(filename)

    def checkContainIntance(self,check_string):
        """
        检查某行是否已经定义弱引用实例
        """
        test_string = '__weak\s+\w+\s+\*\w+\s+=\s+self'
        if re.search(test_string,check_string) != None:
            return True
        else:
            return False

    def retWeakInstanceName(self,lineContext):
        """
        :param lineContext:
        :return:已由用户设置的弱引用实例名称
        """
        test_string = '\*\w+\s+='
        result_match = re.findall(test_string,lineContext)
        result = result_match[0]
        result = result.replace('*','')
        result = result.replace('=','')
        result = result.replace(' ','')
        return  result

    #codeFile 需要修改的文件路径，lineBlock:block为出现block的行数
    def writeCodeIntoFlie(self,codeFile,lineBlockStart,lineBlockEnd,justReplace):
        """
        :param codeFile:
        :param lineBlockStart:
        :param lineBlockEnd:
        :param justReplace: 
        :return:
        """
        (filepath,tempfilename) = os.path.split(codeFile);
        (shotname,extension) = os.path.splitext(tempfilename);

        if extension != '.m' :
            return  0;
        dealNumber = 0;
        filerRead = open(codeFile,'r');
        allLines = filerRead.readlines();
        filerRead.close();
        insertWeak = -1;
        insertLineNumber = 0;
        i = 0;
        print  'block开始行   == %s' %lineBlockStart;
        print  'block结束行   == %s' %lineBlockEnd;

        beforeList = allLines[lineBlockStart-5: lineBlockStart-1];
        #通过检查前5行，找到可以插入初始化weak变量的行数

        p=re.compile('\s\s\s+')
        print '\033[1;32;32m'+'*' * 100
        for eachLine in beforeList:
            prtLine = re.sub(p,'',eachLine.lstrip())
            print  '查找可插入行== %s ' %prtLine
        print '*' * 100 +'\033[0m'


        print '\033[1;31;31m'+'*' * 100
        rpSelfString = "instancePython";
        hasInstance = False
        for eachLine in beforeList:
            if hasInstance:
                continue
            if self.checkContainIntance(eachLine):
                hasInstance = True#已有__weak 实例声明，不需要再写入
                print  '查询可插入行 line %s== 已有__weak 实例声明，不需要再写入 ' %(lineBlockStart - (5-(i+1)))
                rpSelfString = self.retWeakInstanceName(eachLine)
                insertWeak = -1
                continue
            if (eachLine.find(";") != -1) or (re.search('\w+',eachLine) == None) :
                print  '找到可插入行  == %s' %re.sub(p,'',eachLine.lstrip());
                insertWeak = i;
            else:
                if eachLine.find("[") != -1 :
                    print  '找到可插入行[[[  == %s' %re.sub(p,'',eachLine.lstrip());
                    insertWeak = i-1;
            i += 1;
        if insertWeak >-1:
            insertLineNumber = lineBlockStart - (5-insertWeak);
            print  '确定可插入行:在第%s行，行内容是  == %s' %(insertLineNumber,re.sub(p,'',allLines[insertLineNumber].lstrip()));

        lineNumber = 0;
        writeString = []; #写入string
        filer = open(codeFile,'w');

        for eachLine in allLines:
            #在block中替换掉self
            if lineNumber >= lineBlockStart and lineNumber <= lineBlockEnd:
                fself = ('[^\w]self')
                if re.search(fself,eachLine) != None:
                    eachLine = eachLine.replace('self',rpSelfString)
                    print  '替换修改block写法：在第%s行,改后结果 == %s' %(lineNumber,re.sub(p,'',eachLine.lstrip()));
            writeString.append(eachLine)

            #如果上一个block 是 ani Block 并且紧连着下一个block，这里认为 当前的block 与 上一个block 是同一个ani 方法的延续，不做处理
            if self.lastBlockVo._blockType == 0:
                if shotname == "Tao800BrandDeaListModel":
                    print "Tao800BrandDeaListModel 的 block lineNumber = %s,Tao800BrandDeaListModel = %s, insertWeak = %s" %(lineNumber,insertLineNumber,insertWeak);
                if lineNumber == insertLineNumber and insertWeak >-1 :
                    writeString.append("    " + "__weak "+ shotname + " * instancePython = self; \n");
                    dealNumber = 1;
            else:
                if justReplace == 0 or  (lineBlockStart - self.lastBlockVo._startLine > 2) :
                    if lineNumber == insertLineNumber and insertWeak >-1 :
                        writeString.append("    " + "__weak "+ shotname + " * instancePython = self; \n");
                        dealNumber = 1;
                else:
                    print "行数为：%s行的block同行数为:%s行的block 为同一个animation 方法的延续，不做处理" %(self.lastBlockVo._startLine,
                     lineBlockStart);
            lineNumber += 1;
            #在block开始处写入weak 弱引用设置
        print '*' * 100 +'\033[0m'
        tpStr = ''.join(writeString)
        filer.write(tpStr)
        filer.close();
        return  dealNumber;

    def checkFileLinee(self,filename):
        """
        检查文件是否含有block错误
        :param filename:
        :return:
        """
	   # 调用系统方法获取文件信息
        (filepath,tempfilename) = os.path.split(filename);
        (shotname,extension) = os.path.splitext(tempfilename);
        # file type 扩展名，文件后缀
        if extension == '.m' :#extension == '.h' or extension == '.m' :
            filer = open(filename,'r');
            allLines = filer.readlines();
            filer.close();

            lineCount = 0;          #行数
            blockTag = 0;           #block 标记
            blockKuoHao = 0;        #block 括号计数
            blockHasSelf = 0;       #block 中有self
            lineBlockStart = 0;     #block 开始行数
            lineBlockEnd = 0;       #block 结束行数
            dealNumber = 0;         #处理过的次数
            lastAniBlock = 0;       #记录上一个为系统block，和justReplace 组合使用
            justReplace = 0;        #从属 block 只替换，不插入

            for eachLine in allLines:
                lineCount = lineCount + 1;
                blockstring = ''
                if eachLine != " " :
                    eachLine = eachLine.replace(" ",""); #移除空格
                    eachLine = self.trim(eachLine);      #移除tab
                    #print  'line %s  $$$  %s' %(lineCount, eachLine);
                    if blockTag == 1 :
                        fself = ('[^\w]self')
                        if re.search(fself,eachLine) != None:
                            self.blockError += 1
                            blockHasSelf += 1;
                            print '检测文件 %s'%filename
                            if lastAniBlock == 1:
                                self.sysBlockError += 1
                                tempError = '系统blockError:第%s行 文件%s%s ##\n' %(lineCount,shotname,extension)
                                self.otherBlockErrorString.append(tempError)
                            else:
                                tempError = '!!!blockError:第%s行 文件%s%s ## \n' %(lineCount,shotname,extension)
                                self.blockErrorString.append(tempError)
                        if eachLine.find("}") != -1 or eachLine.find("{") != -1:
                            blockKuoHao -= eachLine.count("}")
                            blockKuoHao += eachLine.count("{")
                            if blockKuoHao <= 0:
                                blockTag = 0;
                                lineBlockEnd  = lineCount;
                                #如果是 ani Block
                                if lastAniBlock == 1:
                                    self.lastBlockVo._startLine = lineBlockStart;
                                    self.lastBlockVo._endLine = lineBlockEnd;
                                    self.lastBlockVo._blockType = lastAniBlock;
                                elif (lineBlockEnd - lineBlockStart >0) and blockHasSelf >0 and lastAniBlock == 0:
                                    dealNumber +=self.writeCodeIntoFlie(filename,lineBlockStart+dealNumber,lineBlockEnd+dealNumber,justReplace);

                    if (eachLine.find("^(") != -1 or eachLine.find("^{") != -1) and eachLine.find("failure:") == -1 and blockTag != 1 :
                        if eachLine.find("dispatch") != -1 or eachLine.startswith('//'):
                            #print  '系统 block 忽略';
                            lastAniBlock = 0;
                            pass
                        elif eachLine.count('^')>1:
                            errorStr = '发现多个block标记，请自行检查处理 位置：文件%s%s ## 第 %s 行\n' %(shotname,extension,lineCount)
                            self.blockErrorString.append(errorStr)
                            lastAniBlock = 0;
                            pass
                        elif eachLine.count('^') == 1:
                            if eachLine.find("animations:") != -1 :
                                lastAniBlock = 1;
                            else:
                                lastAniBlock = 0;
                            # if eachLine.find("failure:") != -1 :
                            #     justReplace = 1;
                            # else :
                            #     justReplace = 0;

                            #print  '系统 block 忽略';
                            blockHasSelf = 0;
                            lineBlockStart = lineCount;
                            blockTag = 1;
                            #print  '%s%s 第 %s 行 有 block  start' %(shotname,extension,lineCount);
                            blockStringlist = eachLine.split('^')[1:]
                            for tipCode in blockStringlist:
                                blockKuoHao += tipCode.count("{")
                                blockKuoHao -= tipCode.count("}")
                                if blockKuoHao <= 0:
                                    blockTag = 0;
                                    lineBlockEnd  = lineCount;
                                    if lineBlockEnd - lineBlockStart >0 and blockHasSelf >0 and lastAniBlock == 0:
                                        dealNumber += self.writeCodeIntoFlie(self,filename,lineBlockStart+dealNumber,lineBlockEnd+dealNumber,justReplace);


    def setlastBlockVo(self,blockVo):
        self.lastBlockVo = blockVo;
    def getlastBlockVo(self):
        return  self.lastBlockVo;

    def __init__(self):
        self.blockError = 0 #block 错误计数
        self.sysBlockError = 0 #系统 block 错误计数
        self.blockErrorString = []
        self.otherBlockErrorString = [] #未处理block 信息
        self.lastBlockVo= HHBlockVo();
        filename = '/Users/LeAustinHan/PycharmProjects/PythonCheckBlock/tao800/tao800/tao800/Source'
        #raw_input('Enterr dir name: ');
        self.checkFileNamee(filename);

        (filepathr,tempfilenamer) = os.path.split(filename);
        (shotnamer,extensionr) = os.path.splitext(tempfilenamer);

        fileReport = open('HH%sBlockReport.txt'%tempfilenamer,'w');
        tpStr = '%s目录下block 问题分析 \n' %tempfilenamer
        tpStr = tpStr+'******************************常规block问题 start******************************\n'
        tpStr = tpStr+''.join(self.blockErrorString)
        tpStr = tpStr+'******************************常规block问题 end  ******************************\n'
        tpStr = tpStr+'******************************异常block问题 start******************************\n'
        tpStr = tpStr + ''.join(self.otherBlockErrorString)
        tpStr = tpStr+'******************************异常block问题   end******************************\n'
        tpStr = tpStr+'******************************      问题汇总     ******************************\n'
        strr = '检测出所有.h和.m文件的block中有self  %s处  \n' %self.blockError
        tpStr = tpStr+strr
        sysBlockCountStr = '其中，检测出系统block（含animation和dispatch）中有self:%s处 \n' %self.sysBlockError
        tpStr = tpStr+sysBlockCountStr
        otherBlockCountStr = '其他非系统 block中有self:%s处' %(self.blockError-self.sysBlockError)
        tpStr = tpStr+otherBlockCountStr
        tpStr = tpStr+'******************************    问题汇总结束   ******************************\n'
        fileReport.write(tpStr)
        fileReport.close();

        self.fileResult = sys.path[0];
        self.fileResult += '/HH%sBlockReport.txt'%tempfilenamer;

        os.system('open  %s' %self.fileResult);