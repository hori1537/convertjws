#/usr/bin/python
#coding:utf-8


import os
import struct
from sys import exit
import sys
import csv

import numpy
import tkinter
import tkinter.filedialog
from time import sleep

# to fasten the exe
# refer http://sctibacromn.hatenablog.com/entry/2019/01/03/194035


print('jwsファイルをcsvに一括変換します')
sleep(0.5)
print('csvファイルはdataフォルダに保存されます')
sleep(0.5)
print('　')

#######################################################################################
for i in range(3):
    try:
        print('測定開始波長（低波長側）を入力してください。 デフォルト値：300 ')
        x_for_first_point = input()
        if x_for_first_point == "":
            x_for_first_point = 300
        
        x_for_first_point = int(x_for_first_point)

        print('測定開始波長（高波長側）を入力してください。　デフォルト値：2500')
        x_for_last_point = input()
        if x_for_last_point == "":
            x_for_last_point = 2500

        x_for_last_point = int(x_for_last_point)

        print('測定波長刻みを入力してください。　デフォルト値：5')
        x_step = input()
        if x_step == "":
            x_step = 5
        x_step = int(x_step)

        # (2500-300)/ 5 + 1 = 441 *測定波長の数
        x_point_number = (x_for_last_point - x_for_first_point) / x_step + 1
        
    except:
        if i!=2:
            print('入力データが整数値ではありません。再度入力してください')
    else:
        break
else:
    print('入力データが整数値ではありません。プログラムを終了します。')
    sleep(2)
    exit()

print('')
print('測定開始波長',x_for_first_point)
print('測定終了波長',x_for_last_point)
print('測定波長刻み',x_step)
sleep(0.5)

#######################################################################################
for i in range(3):
    try:
        print('S偏光データとP偏光データを合成しますか。yes/no デフォルト値：yes ')
        answer = input()
        if answer in ['yes','y','ye','']:
            is_synthesizing = True
            sleep(0.2)
            print('S偏光データとP偏光データを合成します')

        elif answer in ['no','n']:
            is_synthesizing = False
            sleep(0.2)
            print('データを合成しません')
    except:
        if i!=2:
            print('再度入力してください')
    else:
        break
else:
    print('プログラムを終了します。')
    sleep(2)
    exit()


#######################################################################################

tk = tkinter.Tk()
tk.withdraw()
currentdirectory = os.getcwd()

print('jwsファイルを選んでください')
sleep(0.3)

jwsfile_path  = tkinter.filedialog.askopenfilename(initialdir = currentdirectory, 
title = 'jwsファイルを１つ選択してください。　同フォルダ内のすべてのjwsファイルを変換します。', filetypes = [('jws File', '*.jws')])
jwsfolder_path = os.path.dirname(jwsfile_path)
os.chdir(jwsfolder_path)

try:
    filelist = os.walk(jwsfolder_path).__next__()[2]
except:
    filelist = os.walk(jwsfolder_path).next()[2]

#拡張子が.jwsであるファイルを抽出
filelist_jws = [os.path.splitext(i)[0] for i in filelist if os.path.splitext(i)[1]=='.jws']

#ファイル名末尾がs-1やp-1であるファイルを抽出
filelist_jws_s = [i for i in filelist_jws if i[-3:] == 's-1' or i[-3:] == 'S-1']
filelist_jws_p = [i for i in filelist_jws if i[-3:] == 'p-1' or i[-3:] == 'P-1']

#ファイル名末尾がs-1やp-1であるファイルを抽出し、末尾を除いたファイル名を取得
#.lowerで大文字を全て小文字に変換
filelist_jws_s_ext = [i[:-3].lower() for i in filelist_jws if i[-3:] == 's-1' or i[-3:] == 'S-1']
filelist_jws_p_ext = [i[:-3].lower() for i in filelist_jws if i[-3:] == 'p-1' or i[-3:] == 'P-1']

#S偏光、P偏光データの共通ファイル名が等しいファイルを抽出
filelist_s_p = set(filelist_jws_s_ext) & set(filelist_jws_p_ext)

# データを格納するフォルダを作成する
if os.path.exists("data") == False:
    try:
        os.mkdir("data")
        print("dataフォルダを作成しました")
    except:
        print("dataフォルダの作成に失敗しました")
else:
        print("dataフォルダはすでに存在しています")
        
# データを格納するフォルダを作成する
if os.path.exists("data-SP") == False:
    try:
        os.mkdir("data-SP")
        print("data-SPフォルダを作成しました")
    except:
        print("data-SPフォルダの作成に失敗しました")
else:
        print("data-SPフォルダはすでに存在しています")


wavelength_csv = numpy.arange(x_for_last_point, x_for_first_point - x_step, -x_step)
wavelength_csv = numpy.array(wavelength_csv, ndmin=2)

header_allcsv = ['wavelength']
header_allcsv_s_p = ['wavelength']
body_allcsv = wavelength_csv.T
body_allcsv_s_p = wavelength_csv.T

sleep(0.3)
print('変換を開始します')
sleep(0.3)

# 各ファイルごとに処理をする
for filename in filelist_jws:

    with open(filename + ".jws", "rb") as f:
        # xの開始、終端、ステップをヘッダーから取得する。
        print("filename: " , filename)

        # intensityデータを取得する
        # バイナリデータにおいてデータが始まるアドレスが0xC80、0xE00の2パターンありそう
        #0xC80から始まる場合は、0xB80 から4D 00 6F 00 64 00 75 のバイナリデータ
        #0xE00から始まる場合は、0xD80 から4D 00 6F 00 64 00 75 のバイナリデータ
        #上記をもとに条件分岐する
        
        
        data = ""


        is_datainfo_A00 = False
        
        is_blank_C00 = False
        is_blank_C40 = False
        is_blank_C80 = False
        
        
        is_data_C00 = False
        is_data_C40 = False
        is_data_C80 = False
        
        
        is_datainfo_C00 = False
        is_AC0 = False
        
        x_A00 = ""
        x_AC0 = ""

        x_C00 = ""
        x_C01 = ""
        x_C02 = ""
        x_C03 = ""
        x_C04 = ""
        x_C05 = ""
        x_C06 = ""

        x_C40 = ""
        x_C41 = ""
        x_C42 = ""
        x_C43 = ""
        x_C44 = ""
        x_C45 = ""
        x_C46 = ""

        x_C80 = ""
        x_C81 = ""
        x_C82 = ""
        x_C83 = ""
        x_C84 = ""
        x_C85 = ""
        x_C86 = ""




        f.seek(0xA00)
        x_A00 = f.read(8)
        #print('x_A00')
        #print(x_A00)
        if x_A00 == b'D\x00a\x00t\x00a\x00':
            #print('x_A00')
            #print(x_A00)
            is_datainfo_A00 = True
            #print('datainfo start at A00')


        f.seek(0xC00)
        x_C00 = f.read(1)
        f.seek(0xC01)
        x_C01 = f.read(1)
        f.seek(0xC02)
        x_C02 = f.read(1)
        f.seek(0xC03)
        x_C03 = f.read(1)
        f.seek(0xC04)
        x_C04 = f.read(1)
        f.seek(0xC05)
        x_C05 = f.read(1)
        f.seek(0xC06)
        x_C06 = f.read(1)


        if  1*(x_C00 == b'\x00') +\
            1*(x_C01 == b'\x00') +\
            1*(x_C02 == b'\x00') +\
            1*(x_C03 == b'\x00') +\
            1*(x_C04 == b'\x00') +\
            1*(x_C05 == b'\x00') +\
            1*(x_C06 == b'\x00') >= 3:

            is_blank_C00 = True
            #print('C00 is blank')
        else :
            pass
            #print('C00 is not blank')

        # check the C40 - C45
        f.seek(0xC40)
        x_C40 = f.read(1)
        f.seek(0xC41)
        x_C41 = f.read(1)
        f.seek(0xC42)
        x_C42 = f.read(1)
        f.seek(0xC43)
        x_C43 = f.read(1)
        f.seek(0xC44)
        x_C44 = f.read(1)
        f.seek(0xC45)
        x_C45 = f.read(1)
        f.seek(0xC46)
        x_C46 = f.read(1)

        if  1*(x_C40 == b'\x00') +\
            1*(x_C41 == b'\x00') +\
            1*(x_C42 == b'\x00') +\
            1*(x_C43 == b'\x00') +\
            1*(x_C44 == b'\x00') +\
            1*(x_C45 == b'\x00') +\
            1*(x_C46 == b'\x00') >= 3:

            is_blank_C40 = True
            #print('C00 is blank')
        else :
            pass
            #print('C00 is not blank')    

        # check the C80 - C85
        f.seek(0xC80)
        x_C80 = f.read(1)
        f.seek(0xC81)
        x_C81 = f.read(1)
        f.seek(0xC82)
        x_C82 = f.read(1)
        f.seek(0xC83)
        x_C83 = f.read(1)
        f.seek(0xC84)
        x_C84 = f.read(1)
        f.seek(0xC85)
        x_C85 = f.read(1)
        f.seek(0xC86)
        x_C86 = f.read(1)


        if  1*(x_C80 == b'\x00') +\
            1*(x_C81 == b'\x00') +\
            1*(x_C82 == b'\x00') +\
            1*(x_C83 == b'\x00') +\
            1*(x_C84 == b'\x00') +\
            1*(x_C85 == b'\x00') +\
            1*(x_C86 == b'\x00') >= 3:

            is_blank_C80 = True
            #print('C00 is blank')
        else :
            pass
            #print('C00 is not blank')  

        #print(is_blank_C00)
        #print(is_blank_C40)
        #print(is_blank_C80)



        if is_datainfo_A00 == True and is_blank_C00 == False:
            is_data_C00 = True
            #print('C00からデータあり')
        
        elif is_datainfo_A00 == True and  is_blank_C00 == True and is_blank_C40 == False :
            is_data_C40 = True
            #print('C40からデータあり')
        
        elif is_datainfo_A00 == True and is_blank_C00 == True and is_blank_C40 == True and is_blank_C80 == False:
            is_data_C80 = True
            #print('C80からデータあり')
        
        else:
            pass
            #print('想定の範囲外です')




        f.seek(0xC00)
        x_C00 = f.read(8)
        #print(x_C00)
        if x_C00 == b'D\x00a\x00t\x00a\x00':
            is_datainfo_C00 = True
            #print('datainfo start at C00')

        if  is_data_C00 == True:
            #print('from 0xC00, not seperate')
            f.seek(0xC00)
            x = f.read(int(x_point_number * 4))
            data = x

        elif is_data_C40 == True:
            #print('from 0xC40, not seperate')
            f.seek(0xC40)
            x = f.read(int(x_point_number * 4))
            data = x
  
        elif is_data_C80 == True:
            #print('from 0xC80, not seperate')
            f.seek(0xC80)
            x = f.read(int(x_point_number * 4))
            data = x
        
        elif is_datainfo_A00 == True :
            pass
            

        if is_datainfo_C00 == True :
            #DataInfoの前のバイト数が256の場合と320の場合がある。
            #無理やり場合分け
            
            #320の場合は
            is_AC0 = False
            f.seek(0xAC0)
            x_AC0 = f.read(4)
            
            #print('x_AC0')
            #print(x_AC0)
            
            if x_AC0 != b'\x00\x00\x00\x00' :
                #x_AC0が０ではない
                #AC0からデータが始まっている場合
                #print('x_AC0')
                
                #print(x_AC0)
                is_AC0 = True
            else:
                is_AC0 = False
                
            #print('is_AC0')
            
            #print(is_AC0)

            if is_AC0 == True:
                #print('1st data series from 0xAC0 2nd data series from E00')

                f.seek(0xAC0)
                x = f.read(320)

                f.seek(0xE00)
                y = f.read(int(x_point_number * 4)- 320)

            
            elif is_AC0 == False:
                #print('1st data series from 0xB00 2nd data series from E00')
            
                f.seek(0xB00)
                x = f.read(256)

                f.seek(0xE00)
                y = f.read(int(x_point_number * 4)- 256)

            data = x + y
                
        #print('is_datainfo_A00', is_datainfo_A00)
        #print('is_blank_C00', is_blank_C00)
        #print('is_blank_C40', is_blank_C40)
        #print('is_blank_C80', is_blank_C80)
        #print('is_datainfo_C00', is_datainfo_C00)
        #print('is_AC0', is_AC0)
        #print('data')
        #print(data)

        spectra_csv = numpy.array(struct.unpack("{0}f".format(int(x_point_number)), data))
        spectra_csv = numpy.array(spectra_csv,ndmin=2)
        body_csv = numpy.hstack((wavelength_csv.T,spectra_csv.T))
        
        header_csv = ['wavelength',filename]
    
        #for all data csv
        header_allcsv.append(filename)
        body_allcsv = numpy.hstack([body_allcsv,spectra_csv.T])
        
    # データをcsvに書きだす。
    with open("data/" + filename + ".csv", "w", newline='') as expoted_data_obj:
        writer_csv = csv.writer(expoted_data_obj)
        writer_csv.writerow(header_csv)
        writer_csv.writerows(body_csv)
        
if is_synthesizing == True:
    for filename in filelist_s_p:
        spectra_s = []
        spectra_p = []
        

        with open('data/' + filename + "s-1.csv", "r") as f_s:
            reader_s = csv.reader(f_s)
            header_s = next(reader_s)
            
            for row_s in reader_s:
                row_s_fl = [float(n) for n in row_s]
                spectra_s.append(row_s_fl)
            
            spectra_s = numpy.array(spectra_s)
            spectra_s = spectra_s[:,1]
            #print(spectra_s)

        with open('data/' + filename + "p-1.csv", "r") as f_p:
            reader_p = csv.reader(f_p)
            header_p = next(reader_p)
            
            for row_p in reader_p:
                row_p_fl = [float(n) for n in row_p]
                spectra_p.append(row_p_fl)

            spectra_p = numpy.array(spectra_p)
            spectra_p = spectra_p[:,1]            
            #print(spectra_p)


        spectra_s = numpy.array(spectra_s)
        spectra_p = numpy.array(spectra_p)

        #print(spectra_s)
        #print(spectra_p)

        spectra_csv_s_p = (spectra_s + spectra_p ) * 0.5
        
        wavelength_csv = numpy.array(wavelength_csv)

        spectra_csv_s_p = numpy.array(spectra_csv_s_p)
        spectra_csv_s_p = spectra_csv_s_p.reshape(441,1)

        body_csv_s_p = numpy.hstack((wavelength_csv.T, spectra_csv_s_p))
        header_csv_s_p = ['wavelength', filename + 's_p']
        print("filename: " , filename + "SP")
        
        # データをcsvに書きだす。
        with open("data-SP/" + filename + "SP.csv", "w", newline='') as expoted_data_obj_s_p:
            writer_csv = csv.writer(expoted_data_obj_s_p)
            writer_csv.writerow(header_csv_s_p)
            writer_csv.writerows(body_csv_s_p)
    
        #for all data csv
        header_allcsv_s_p.append(filename + 's_p')
        body_allcsv_s_p = numpy.hstack([body_allcsv_s_p,spectra_csv_s_p])


with open('all.csv', 'w', newline='') as exported_alldata_obj:
    writer_allcsv = csv.writer(exported_alldata_obj)
    writer_allcsv.writerow(header_allcsv)
    writer_allcsv.writerows(body_allcsv)

if is_synthesizing == True:
    with open( 'all_s_p.csv', 'w', newline='') as exported_alldata_obj_s_p:
        writer_allcsv_s_p = csv.writer(exported_alldata_obj_s_p)
        writer_allcsv_s_p.writerow(header_allcsv_s_p)
        writer_allcsv_s_p.writerows(body_allcsv_s_p)

print('csvファイルへの変換を完了しました。')
sleep(1)