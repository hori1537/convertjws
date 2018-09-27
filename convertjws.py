#/usr/bin/python
#coding:utf-8


import os
import struct
from sys import exit
import csv
import numpy
import tkinter
import tkinter.filedialog
from time import sleep

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
        # バイナリデータにおいてアドレス0xC80からデータが始まる
        f.seek(0xC80)
        
        x = f.read(int(x_point_number * 4))
        
        spectra_csv = numpy.array(struct.unpack("{0}f".format(int(x_point_number)), x))
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
        with open(filename + "s-1.jws", "rb") as f_s:
            # xの開始、終端、ステップをヘッダーから取得する。
            #print("filename: " , filename + "s-1.jws")

            # intensityデータを取得する
            f_s.seek(0xC80)
            x_s = f_s.read(int(x_point_number * 4))        
            spectra_csv_s = numpy.array(struct.unpack("{0}f".format(int(x_point_number)), x_s))
            spectra_csv_s =  numpy.array(spectra_csv_s,ndmin=2)

        with open(filename + "p-1.jws", "rb") as f_p:
            # xの開始、終端、ステップをヘッダーから取得する。
            #print("filename: " , filename + "p-1.jws")

            # intensityデータを取得する
            f_p.seek(0xC80)
            x_p = f_p.read(int(x_point_number * 4))        
            spectra_csv_p = numpy.array(struct.unpack("{0}f".format(int(x_point_number)), x_p))
            spectra_csv_p =  numpy.array(spectra_csv_p,ndmin=2)

        spectra_csv_s_p = (spectra_csv_s + spectra_csv_p) * 0.5
        body_csv_s_p = numpy.hstack((wavelength_csv.T, spectra_csv_s_p.T))
        header_csv_s_p = ['wavelength', filename + 's_p']
        print("filename: " , filename + "SP")

        
        # データをcsvに書きだす。
        with open("data-SP/" + filename + "SP.csv", "w", newline='') as expoted_data_obj_s_p:
            writer_csv = csv.writer(expoted_data_obj_s_p)
            writer_csv.writerow(header_csv_s_p)
            writer_csv.writerows(body_csv_s_p)
    
        #for all data csv
        header_allcsv_s_p.append(filename + 's_p')
        body_allcsv_s_p = numpy.hstack([body_allcsv_s_p,spectra_csv_s_p.T])


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
