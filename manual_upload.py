import csv
import glob
import re
import shutil
import sys
from flask import *
import os
app = Flask(__name__)
app.secret_key = 'secret'
@app.route('/', methods=['POST','GET'])
def main_program():
    if request.method == "POST":
        foldername= request.form.get('foldername')
        file_name = [file for file in os.listdir(foldername) if ".csv" in file]
        filename = foldername+"\\"+file_name[0]
        print(filename)
        rows = []
        with open(filename, 'r') as csvfile:
            csvreader = csv.reader(csvfile)

            for row in csvreader:
                rows.append(row[0])
        final_list = []
        lengthofnewlines = []
        for i in range(0,len(rows),2):
            batches = []
            sub_folder = foldername + "\\" + rows[i]
            notes = rows[i+1]
            extension = [ str(img.split('.')[-1]) for img in os.listdir(sub_folder) ]
            old_images_names = [str(img.split('.')[-2]) for img in os.listdir(sub_folder)]
            image_names = [ str(img.split('.')[-2]).replace(" ", "_").replace(".", "_").replace("-", "_").replace("(","_").replace(")","_") for img in os.listdir(sub_folder) ]
            print("before sub folder name", os.listdir(sub_folder))
            for img in range(len(image_names)):
                os.rename(os.path.join(sub_folder,old_images_names[img]+"."+extension[img]), os.path.join(sub_folder,image_names[img]+"."+extension[img]))
            print(sub_folder)

            for img1 in (os.listdir(sub_folder)):
                source = sub_folder+"\\"+img1
                destination = r"D:\projects\autoUploads\static"
                try:
                    shutil.copy2(source, destination)
                    # print("File copied successfully.")
                except shutil.SameFileError:
                    print("Source and destination represents the same file.")
                except IsADirectoryError:
                    print("Destination is a directory.")
                except PermissionError:
                    print("Permission denied.", sys.exc_info())
                except:
                    print("Error occurred while copying file.", sys.exc_info())
                batches.append("image")
                batches.append(img1)
            print("after sub folder name",os.listdir(sub_folder))
            batches.append("text")
            notes = "Title : \nDescription : "+notes+"\nPrice : "
            batches.append(notes)
            final_list.append(batches)
            lengthofnewlines.append(5)
            print('notes ', notes)
        print('final list ', final_list)

        return render_template('index_alternate.html', final_list = final_list, folder_path=foldername, lengthofnewlines = lengthofnewlines)
    return render_template('file_path_page_manual.html')
@app.route('/submitted', methods=['POST','GET'])
def submitted_result():
    if request.method =="POST":
        print('len of list ', len(request.form.getlist('attack')))
        print('list of check box selected ', request.form.getlist('checkboxtodelete'))
        checkboxDelete = request.form.getlist('checkboxtodelete')
        list_from_html = request.form.getlist('attack')
        temp_list = []
        final_list = []
        multi_image = []
        for i in range(0, len(list_from_html), 2):
            if list_from_html[i] == 'image':
                if list_from_html[i + 1][-1] == "@":
                    list_from_html[i + 1] = list_from_html[i + 1][:-1]
                for check_img in checkboxDelete:
                    if list_from_html[i + 1] == check_img:
                        list_from_html[i + 1] += "@D"
                temp_list.append(list_from_html[i + 1])
            elif list_from_html[i] == 'text':
                text = list_from_html[i + 1]

                final_sub_list = []
                j = 0
                while (j < len(temp_list)):
                    final_sub_list_sub = []
                    if temp_list[j].find('@') != -1:
                        print('image has @', temp_list[j])
                        batch = []
                        if temp_list[j].split('@')[1] == 'D' or temp_list[j].split('@')[1] == 'd':
                            print('Delete product ', temp_list[j])
                            final_sub_list_sub.append(temp_list[j].split('@')[0])
                            final_sub_list_sub.append(text + " update as DPDU")
                            final_sub_list.append(final_sub_list_sub)
                            j += 1
                            continue
                        else:
                            number = int(temp_list[j].split('@')[1].split('.')[0])
                            index = j + 1
                            tempBatchlist = []
                            tempBatchlist.append(temp_list[j].split('@')[0])
                            numbers = []
                            numbers.append(int(temp_list[j].split('@')[1].split('.')[1]))

                            while (index < len(temp_list)):
                                if temp_list[index].find('@') != -1 and temp_list[index].split('@')[1] != 'D' and \
                                        temp_list[index].split('@')[1] != 'd':
                                    string_to_search = temp_list[index]

                                    splitingmainnumber = string_to_search.split('@')[1]
                                    main_number = splitingmainnumber.split('.')[0]

                                    num_in_string = int(main_number)
                                    if num_in_string == number:
                                        tempBatchlist.append(temp_list[index].split('@')[0])
                                        numbers.append(int(splitingmainnumber.split('.')[1]))
                                        print('temp list after remove ', temp_list)
                                        temp_list.pop(index)
                                        index = j
                                index += 1
                            print('temp batch list ', tempBatchlist)
                            print('numbers ', numbers)
                            for ij in range(0, len(numbers)):
                                for ji in range(ij, len(numbers)):
                                    if numbers[ij] > numbers[ji]:
                                        temp = tempBatchlist[ij]
                                        tempBatchlist[ij] = tempBatchlist[ji]
                                        tempBatchlist[ji] = temp
                                        temp = numbers[ij]
                                        numbers[ij] = numbers[ji]
                                        numbers[ji] = temp
                            for batching in tempBatchlist:
                                batch.append(batching)
                            batch.append(text + " wst")
                            print('batches ', batch)
                            final_sub_list.append(batch)
                    else:

                        if text.find('@Delete') == -1 and text.find('@delete') == -1 and text.find('@DELETE') == -1:
                            final_sub_list_sub.append(temp_list[j])
                            final_sub_list_sub.append(text)
                        else:
                            final_sub_list_sub.append(temp_list[j])
                            final_text_du = text + " update as DPDU"
                            if final_text_du.find('@Delete') != -1:
                                final_text_du = str(
                                    final_text_du.split('@Delete')[0] + " " + final_text_du.split('@Delete')[1])
                            elif final_text_du.find('@delete') != -1:
                                final_text_du = str(
                                    final_text_du.split('@delete')[0] + " " + final_text_du.split('@delete')[1])
                            elif final_text_du.find('@DELETE') != -1:
                                final_text_du = str(
                                    final_text_du.split('@DELETE')[0] + " " + final_text_du.split('@DELETE')[1])
                            final_sub_list_sub.append(final_text_du)

                        final_sub_list.append(final_sub_list_sub)
                    j += 1
                temp_list = []
                final_list.append(final_sub_list)
        print('final list ', final_list)
        folder_path = request.form.get('folder_path')
        folder_path = os.path.join(folder_path,'\\dsac')
        os.mkdir(folder_path,0o666)
        file_name = folder_path+"\\" + 'updated.csv'
        title = ['Date1', 'Date2', 'Time', 'UserPhone', 'UserName', 'MessageBody', 'MediaType', 'MediaLink',
                 'QuotedMessage', 'QuotedMessageDate', 'QuotedMessageTime']
        with open(file_name, 'w', newline='', encoding="utf-8") as csvfile:
            # creating a csv writer object
            csvwriter = csv.writer(csvfile)

            # writing the fields
            csvwriter.writerow(title)

            # writing the data rows
            for rows in final_list:
                for row in rows:
                    for ind in range(0, len(row)):
                        if ind != len(row) - 1:

                            csvwriter.writerow(["", "", "", "", "", row[ind], "image", "", "", "", ""])
                        else:
                            row[ind] = str(row[ind].split(r"\n"))
                            # print('row ind ', row[ind][2:-2])
                            csvwriter.writerow(["", "", "", "", "", row[ind][2:-2], "", "", "", "", ""])
        dir = r'D:\projects\autoUploads\static'


        for direct in os.listdir(dir):
            path = dir+"\\"+direct
            destination = folder_path+"\\"+direct
            dest = shutil.move(path, destination, copy_function=shutil.copytree)
        # shutil.make_archive( folder_path+"dsaca", 'zip', folder_path)

    return redirect("/")

# pri = r"D:\download\uploading_groups\autocheck\dsac"
#
# file_name = [file  for file in os.listdir(pri) if ".csv" in file]
# print('file name ', file_name)
if __name__ == '__main__':
    app.run(debug = True, port=6568)